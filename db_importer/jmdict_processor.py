import xml.etree.ElementTree as ET
import psycopg2
from psycopg2.extras import execute_values
import yaml
import pykakasi
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@dataclass
class DatabaseConfig:
    host: str
    database: str
    user: str
    password: str
    port: int = 5432

class JMdictProcessor:
    def __init__(self, db_config: DatabaseConfig, conjugation_rules_path: str):
        self.db_config = db_config
        self.kakasi = pykakasi.kakasi()
        
        # Load conjugation rules
        with open(conjugation_rules_path, 'r', encoding='utf-8') as f:
            self.conjugation_rules = yaml.safe_load(f)
        
        # Initialize database connection
        self.conn = psycopg2.connect(
            host=db_config.host,
            database=db_config.database,
            user=db_config.user,
            password=db_config.password,
            port=db_config.port
        )
        self.cur = self.conn.cursor()

    def _strip_entity_refs(self, text: str) -> str:
        """Strip XML entity references from text."""
        if text and text.startswith('&') and text.endswith(';'):
            return text[1:-1]
        return text
    
    def _update_frequency_rating(self, entry_id: int):
        """Calculate and update the frequency rating for an entry."""
        try:
            self.cur.execute("""
                WITH rating_scores AS (
                    SELECT 
                        CASE 
                            WHEN rating_type LIKE 'news%' THEN 5
                            WHEN rating_type LIKE 'ichi%' THEN 4
                            WHEN rating_type LIKE 'spec%' THEN 3
                            WHEN rating_type LIKE 'gai%' THEN 2
                            ELSE 1
                        END as score
                    FROM frequency_ratings
                    WHERE entry_id = %s
                )
                UPDATE entries 
                SET frequency_rating = COALESCE(
                    (SELECT MAX(score) FROM rating_scores),
                    0  -- Default rating if no scores found
                )
                WHERE id = %s
            """, (entry_id, entry_id))
        except Exception as e:
            logging.error(f"Error updating frequency rating for entry {entry_id}: {str(e)}")
            # Don't raise the exception, just log it

    def _map_pos(self, pos: str) -> str:
        """Map full text POS to parts_of_speech code."""
        logging.debug(f"Mapping POS: {pos}")
        pos_mapping = {
            'adjective (keiyoushi)': 'adj-i',
            'adjectival nouns or quasi-adjectives (keiyodoshi)': 'adj-na',
            'adj-i': 'adj-i',
            'adj-na': 'adj-na',
            "Godan verb with 'u' ending": 'v5u',
            "Godan verb with 'ku' ending": 'v5k',
            "Godan verb with 'gu' ending": 'v5g',
            "Godan verb with 'su' ending": 'v5s',
            "Godan verb with 'tsu' ending": 'v5t',
            "Godan verb with 'nu' ending": 'v5n',
            "Godan verb with 'bu' ending": 'v5b',
            "Godan verb with 'mu' ending": 'v5m',
            "Godan verb with 'ru' ending": 'v5r',
            'Ichidan verb': 'v1'
        }
        mapped = pos_mapping.get(pos, pos)
        logging.debug(f"Mapped {pos} to {mapped}")
        return mapped

    def _process_entry(self, entry: ET.Element) -> Dict:
        """Process a single entry from the XML."""
        ent_seq = int(entry.find('ent_seq').text)
        logging.debug(f"Processing entry {ent_seq}")
        
        # Process kanji elements
        kanji_elements = []
        for k_ele in entry.findall('k_ele'):
            kanji = {
                'kanji': k_ele.find('keb').text,
                'info': [self._strip_entity_refs(e.text) for e in k_ele.findall('ke_inf')],
                'priority': [e.text for e in k_ele.findall('ke_pri')]
            }
            kanji_elements.append(kanji)
        
        # Process reading elements
        reading_elements = []
        for r_ele in entry.findall('r_ele'):
            reading = {
                'reading': r_ele.find('reb').text,
                'no_kanji': bool(r_ele.find('re_nokanji')),
                'restrictions': [e.text for e in r_ele.findall('re_restr')],
                'info': [self._strip_entity_refs(e.text) for e in r_ele.findall('re_inf')],
                'priority': [e.text for e in r_ele.findall('re_pri')]
            }
            reading_elements.append(reading)
        
        # Process sense elements
        sense_elements = []
        for sense in entry.findall('sense'):
            # Extract and process POS with detailed logging
            pos_elements = sense.findall('pos')
            pos_values = []
            for pos in pos_elements:
                raw_pos = pos.text
                logging.debug(f"Raw POS value: {raw_pos}")
                pos_values.append(raw_pos)
            
            sense_data = {
                'pos': pos_values,
                'field': [self._strip_entity_refs(field.text) for field in sense.findall('field')],
                'misc': [self._strip_entity_refs(misc.text) for misc in sense.findall('misc')],
                'glosses': []
            }
            
            for gloss in sense.findall('gloss'):
                gloss_data = {
                    'text': gloss.text,
                    'lang': gloss.get('{http://www.w3.org/XML/1998/namespace}lang', 'eng'),
                    'type': gloss.get('g_type')
                }
                sense_data['glosses'].append(gloss_data)
            
            sense_elements.append(sense_data)
        
        return {
            'ent_seq': ent_seq,
            'kanji_elements': kanji_elements,
            'reading_elements': reading_elements,
            'sense_elements': sense_elements
        }

    def _process_conjugations(self, entry_id: int, entry: Dict):
        """Generate and insert conjugations for applicable words."""
        # Get parts of speech from all senses
        pos_list = set()
        for sense in entry['sense_elements']:
            original_pos = sense['pos']
            logging.info(f"Original POS values: {original_pos}")
            mapped_pos = [self._map_pos(pos) for pos in original_pos]
            logging.info(f"Mapped POS values: {mapped_pos}")
            pos_list.update(mapped_pos)
        
        # Filter for conjugatable parts of speech
        conjugatable_pos = {pos for pos in pos_list 
                          if pos in ['adj-i', 'adj-na'] or 
                          pos.startswith(('v1', 'v5'))}
        
        if not conjugatable_pos:
            logging.debug(f"No conjugatable POS found in: {pos_list}")
            return
        
        logging.info(f"Found conjugatable POS: {conjugatable_pos}")
        
        # Get base form (use first kanji if available, otherwise first reading)
        base_form = (entry['kanji_elements'][0]['kanji'] 
                    if entry['kanji_elements'] 
                    else entry['reading_elements'][0]['reading'])
        
        # Generate conjugations for each applicable part of speech
        for pos in conjugatable_pos:
            logging.info(f"Generating conjugations for {base_form} ({pos})")
            conjugations = self._generate_conjugations(base_form, pos)
            if conjugations:
                logging.info(f"Generated {len(conjugations)} conjugations")
                for conj in conjugations:
                    logging.debug(f"Conjugation: {conj}")
                self._insert_conjugations(entry_id, conjugations)
            else:
                logging.warning(f"No conjugations generated for {base_form} ({pos})")

    def _generate_conjugations(self, word: str, pos: str) -> List[Dict]:
        """Generate all conjugations for a word based on its part of speech."""
        results = []
        logging.info(f"Generating conjugations for word: {word}, POS: {pos}")
        
        # Get appropriate rule set
        rule_set = None
        if pos == 'adj-i':
            logging.info("Found i-adjective, getting rule set")
            rule_set = self.conjugation_rules['adjective_rules']['i_adjectives']['adj-i']
        elif pos == 'adj-na':
            logging.info("Found na-adjective, getting rule set")
            rule_set = self.conjugation_rules['adjective_rules']['na_adjectives']['adj-na']
        elif pos.startswith('v5'):
            logging.info("Found godan verb, getting rule set")
            rule_set = self.conjugation_rules['verb_rules']['godan'].get(pos)
        elif pos.startswith('v1'):
            logging.info("Found ichidan verb, getting rule set")
            rule_set = self.conjugation_rules['verb_rules']['ichidan'].get(pos)
        
        if not rule_set:
            logging.warning(f"No conjugation rules found for POS: {pos}")
            return results
        
        conjugations = rule_set.get('conjugations', {})
        logging.info(f"Found rule set with conjugations: {list(conjugations.keys())}")
        
        # Get base form without the ending
        if 'base_ending' in rule_set:
            base_ending = rule_set['base_ending']
            if word.endswith(base_ending):
                base = word[:-len(base_ending)]
            else:
                base = word
        else:
            base = word

        # Apply conjugation patterns
        for conj_type, patterns in conjugations.items():
            logging.debug(f"Processing conjugation type: {conj_type}")
            
            # Handle forms with plain/polite variants
            if isinstance(patterns, dict) and ('plain' in patterns or 'polite' in patterns):
                for form, pattern_data in patterns.items():
                    result = {
                        'conjugation_type': conj_type,
                        'form': form,
                        'kanji_form': base + pattern_data['kanji'],
                        'hiragana_reading': base + pattern_data['hiragana'],
                        'katakana_reading': base + pattern_data['katakana'],
                        'romaji_reading': base + pattern_data['romaji']
                    }
                    results.append(result)
            
            # Handle forms without plain/polite variants (like te_form)
            else:
                result = {
                    'conjugation_type': conj_type,
                    'form': 'plain',
                    'kanji_form': base + patterns['kanji'],
                    'hiragana_reading': base + patterns['hiragana'],
                    'katakana_reading': base + patterns['katakana'],
                    'romaji_reading': base + patterns['romaji']
                }
                results.append(result)

        return results

    def _apply_pattern(self, word: str, pattern: Dict[str, str], pos: str) -> Dict[str, str]:
        """Apply conjugation patterns to a word."""
        # This method is no longer needed since we handle the conjugations directly
        # in _generate_conjugations, but we'll keep it for compatibility
        logging.warning("_apply_pattern is deprecated with new conjugation rules format")

    def _get_readings(self, word: str) -> Dict[str, str]:
        """Generate different readings of a word."""
        result = self.kakasi.convert(word)
        
        return {
            'hiragana': result[0]['hira'],
            'katakana': result[0]['kana'],
            'romaji': result[0]['passport']
        }

    def _insert_conjugations(self, entry_id: int, conjugations: List[Dict]):
        """Insert conjugations for an entry."""
        if not conjugations:
            return
            
        execute_values(
            self.cur,
            """
            INSERT INTO conjugations 
            (entry_id, conjugation_type, form, kanji_form, hiragana_reading, 
            katakana_reading, romaji_reading)
            VALUES %s
            """,
            [(entry_id,
            c['conjugation_type'],
            c['form'],
            c['kanji_form'],
            c['hiragana_reading'],
            c['katakana_reading'],
            c['romaji_reading'])
            for c in conjugations]
        )

    def close(self):
        """Close database connection."""
        self.cur.close()
        self.conn.close()


    def process_file(self, xml_file_path: str, batch_size: int = 1000):
        """Process the JMdict XML file in batches."""
        logging.info(f"Starting to process {xml_file_path}")
        
        # Parse XML
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        entries_processed = 0
        entries_batch = []
        
        for entry in root.findall('entry'):
            processed_entry = self._process_entry(entry)
            entries_batch.append(processed_entry)
            
            if len(entries_batch) >= batch_size:
                self._insert_batch(entries_batch)
                entries_processed += len(entries_batch)
                logging.info(f"Processed {entries_processed} entries")
                entries_batch = []
        
        # Insert any remaining entries
        if entries_batch:
            self._insert_batch(entries_batch)
            entries_processed += len(entries_batch)
        
        logging.info(f"Completed processing {entries_processed} entries")

    def _insert_batch(self, entries: List[Dict]):
        """Insert a batch of entries into the database."""
        try:
            # Start transaction
            self.cur.execute("BEGIN")
            
            # Create temporary table for batch insert
            self.cur.execute("""
                CREATE TEMPORARY TABLE temp_entries (
                    ent_seq INTEGER,
                    frequency_rating INTEGER
                ) ON COMMIT DROP
            """)
            
            # Insert entries and get their IDs
            entry_values = [(e['ent_seq'], None) for e in entries]  # We'll calculate frequency rating later
            execute_values(
                self.cur,
                "INSERT INTO temp_entries (ent_seq, frequency_rating) VALUES %s",
                entry_values
            )
            
            # Insert into main entries table
            self.cur.execute("""
                INSERT INTO entries (ent_seq, frequency_rating)
                SELECT ent_seq, frequency_rating FROM temp_entries
                RETURNING id, ent_seq
            """)
            
            entry_ids = {row[1]: row[0] for row in self.cur.fetchall()}
            
            # Process each entry's components
            for entry in entries:
                entry_id = entry_ids[entry['ent_seq']]
                
                # Insert kanji elements and frequency ratings
                self._insert_kanji_elements(entry_id, entry['kanji_elements'])
                
                # Insert reading elements and their variations
                self._insert_reading_elements(entry_id, entry['reading_elements'])
                
                # Insert sense elements and all related data
                self._insert_sense_elements(entry_id, entry['sense_elements'])
                
                # Generate and insert conjugations if applicable
                self._process_conjugations(entry_id, entry)
                
                # Calculate and update frequency rating based on priorities
                self._update_frequency_rating(entry_id)
            
            # Commit transaction
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error inserting batch: {str(e)}")
            raise

    def _insert_kanji_elements(self, entry_id: int, kanji_elements: List[Dict]):
        """Insert kanji elements for an entry."""
        for i, k_ele in enumerate(kanji_elements, 1):
            self.cur.execute("""
                INSERT INTO kanji_elements (entry_id, kanji, priority_order)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (entry_id, k_ele['kanji'], i))
            
            kanji_id = self.cur.fetchone()[0]
            
            # Insert usage notes for irregular kanji usage
            if k_ele['info']:
                execute_values(
                    self.cur,
                    """
                    INSERT INTO usage_notes 
                    (entry_id, note_type, note_text)
                    VALUES %s
                    """,
                    [(entry_id, 'kanji_usage', info) for info in k_ele['info']]
                )
            
            # Insert priority/frequency information
            if k_ele['priority']:
                execute_values(
                    self.cur,
                    """
                    INSERT INTO frequency_ratings 
                    (entry_id, rating_type, source)
                    VALUES %s
                    """,
                    [(entry_id, pri, 'kanji_priority') for pri in k_ele['priority']]
                )

    def _insert_reading_elements(self, entry_id: int, reading_elements: List[Dict]):
        """Insert reading elements for an entry."""
        for i, r_ele in enumerate(reading_elements, 1):
            # Convert reading to different scripts
            readings = self._get_readings(r_ele['reading'])
            
            # Insert hiragana reading (original)
            execute_values(
                self.cur,
                """
                INSERT INTO reading_elements 
                (entry_id, reading, reading_type, no_kanji, priority_order)
                VALUES %s
                """,
                [(entry_id, r_ele['reading'], 'hiragana', r_ele['no_kanji'], i)]
            )
            
            # Insert katakana and romaji readings
            additional_readings = [
                (entry_id, readings['katakana'], 'katakana', r_ele['no_kanji'], i),
                (entry_id, readings['romaji'], 'romaji', r_ele['no_kanji'], i)
            ]
            
            execute_values(
                self.cur,
                """
                INSERT INTO reading_elements 
                (entry_id, reading, reading_type, no_kanji, priority_order)
                VALUES %s
                """,
                additional_readings
            )
            
            # Insert priority information into frequency_ratings if available
            if r_ele['priority']:
                execute_values(
                    self.cur,
                    """
                    INSERT INTO frequency_ratings 
                    (entry_id, rating_type, source)
                    VALUES %s
                    """,
                    [(entry_id, pri, 'reading_priority') for pri in r_ele['priority']]
                )

    def _insert_sense_elements(self, entry_id: int, sense_elements: List[Dict]):
        """Insert sense elements and related data for an entry."""
        for i, sense in enumerate(sense_elements, 1):
            # Insert sense element
            self.cur.execute("""
                INSERT INTO sense_elements (entry_id, sense_order)
                VALUES (%s, %s)
                RETURNING id
            """, (entry_id, i))
            
            sense_id = self.cur.fetchone()[0]
            
            # Insert parts of speech
            if sense['pos']:
                # First get the IDs for the parts of speech
                pos_ids = []
                for pos_code in sense['pos']:
                    self.cur.execute("""
                        SELECT id FROM parts_of_speech WHERE code = %s
                    """, (self._map_pos(pos_code),))
                    result = self.cur.fetchone()
                    if result:
                        pos_ids.append(result[0])
                
                # Then insert the relationships
                if pos_ids:
                    pos_values = [(sense_id, pos_id) for pos_id in pos_ids]
                    execute_values(
                        self.cur,
                        """
                        INSERT INTO sense_parts_of_speech (sense_id, part_of_speech_id)
                        VALUES %s
                        """,
                        pos_values
                    )
            
            # Insert subject fields
            if sense['field']:
                # First get the IDs for the fields
                field_ids = []
                for field_code in sense['field']:
                    self.cur.execute("""
                        SELECT id FROM subject_fields WHERE code = %s
                    """, (self._strip_entity_refs(field_code),))
                    result = self.cur.fetchone()
                    if result:
                        field_ids.append(result[0])
                
                # Then insert the relationships
                if field_ids:
                    field_values = [(sense_id, field_id) for field_id in field_ids]
                    execute_values(
                        self.cur,
                        """
                        INSERT INTO sense_subject_fields (sense_id, subject_field_id)
                        VALUES %s
                        """,
                        field_values
                    )
            
            # Insert definitions
            if sense['glosses']:
                definition_values = [
                    (sense_id, g['text'], g['lang'], g['type']) 
                    for g in sense['glosses']
                ]
                execute_values(
                    self.cur,
                    """
                    INSERT INTO definitions 
                    (sense_id, definition_text, language, definition_type)
                    VALUES %s
                    """,
                    definition_values
                )

    def initialize_reference_tables(self):
        """Initialize reference tables with required data."""
        logging.info("Initializing reference tables...")
        
        try:
            # Initialize parts of speech
            pos_data = [
                ('adj-i', 'い-adjective', 'Adjective (keiyoushi)'),
                ('adj-na', 'な-adjective', 'Adjectival nouns or quasi-adjectives (keiyodoshi)'),
                ('v1', 'Ichidan verb', 'Ichidan verb (one-step verb)'),
                ('v5u', 'Godan verb with u ending', 'Godan verb with u ending'),
                ('v5k', 'Godan verb with ku ending', 'Godan verb with ku ending'),
                ('v5g', 'Godan verb with gu ending', 'Godan verb with gu ending'),
                ('v5s', 'Godan verb with su ending', 'Godan verb with su ending'),
                ('v5t', 'Godan verb with tsu ending', 'Godan verb with tsu ending'),
                ('v5n', 'Godan verb with nu ending', 'Godan verb with nu ending'),
                ('v5b', 'Godan verb with bu ending', 'Godan verb with bu ending'),
                ('v5m', 'Godan verb with mu ending', 'Godan verb with mu ending'),
                ('v5r', 'Godan verb with ru ending', 'Godan verb with ru ending'),
                ('n', 'Noun', 'Common noun (futsuumeishi)'),
                ('adv', 'Adverb', 'Adverb (fukushi)'),
                ('prt', 'Particle', 'Particle'),
                ('conj', 'Conjunction', 'Conjunction'),
                ('int', 'Interjection', 'Interjection (kandoushi)'),
                ('pref', 'Prefix', 'Prefix'),
                ('suf', 'Suffix', 'Suffix'),
                ('ctr', 'Counter', 'Counter word'),
                ('exp', 'Expression', 'Expression'),
                ('aux', 'Auxiliary', 'Auxiliary'),
                ('unc', 'Unclassified', 'Unclassified')
            ]
            
            logging.info("Populating parts_of_speech table...")
            execute_values(
                self.cur,
                """
                INSERT INTO parts_of_speech (code, name, description)
                VALUES %s
                ON CONFLICT (code) DO NOTHING
                """,
                pos_data
            )
            
            # Initialize subject fields
            field_data = [
                ('agric', 'Agriculture', 'Terms related to agriculture'),
                ('anat', 'Anatomy', 'Anatomical terms'),
                ('archit', 'Architecture', 'Architectural terms'),
                ('art', 'Art', 'Art terms'),
                ('astron', 'Astronomy', 'Astronomical terms'),
                ('baseb', 'Baseball', 'Baseball terms'),
                ('biol', 'Biology', 'Biological terms'),
                ('bot', 'Botany', 'Botanical terms'),
                ('bus', 'Business', 'Business terms'),
                ('chem', 'Chemistry', 'Chemistry terms'),
                ('comp', 'Computing', 'Computer terminology'),
                ('econ', 'Economics', 'Economic terms'),
                ('engr', 'Engineering', 'Engineering terms'),
                ('food', 'Food', 'Food and cooking terms'),
                ('geom', 'Geometry', 'Geometric terms'),
                ('law', 'Law', 'Legal terms'),
                ('ling', 'Linguistics', 'Linguistic terms'),
                ('MA', 'Martial Arts', 'Martial arts terms'),
                ('math', 'Mathematics', 'Mathematical terms'),
                ('med', 'Medicine', 'Medical terms'),
                ('mil', 'Military', 'Military terms'),
                ('music', 'Music', 'Musical terms'),
                ('physics', 'Physics', 'Physics terms'),
                ('sports', 'Sports', 'Sports terms'),
                ('sumo', 'Sumo', 'Sumo terms')
            ]
            
            logging.info("Populating subject_fields table...")
            execute_values(
                self.cur,
                """
                INSERT INTO subject_fields (code, name, description)
                VALUES %s
                ON CONFLICT (code) DO NOTHING
                """,
                field_data
            )
            
            # Commit the changes
            self.conn.commit()
            logging.info("Reference tables initialized successfully")
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error initializing reference tables: {str(e)}")
            raise

def main():
    # Configuration
    db_config = DatabaseConfig(
        host='localhost',
        database='japanese_dictionary',
        user='user',
        password='password'
    )
    
    # Initialize processor
    processor = JMdictProcessor(
        db_config=db_config,
        conjugation_rules_path='conjugation_rules.yaml'
    )
    
    try:
        # Initialize reference tables
        logging.info("Initializing database reference tables...")
        processor.initialize_reference_tables()
        
        # Process the dictionary file
        logging.info("Starting dictionary file processing...")
        processor.process_file('JMdict_e.xml', batch_size=1000)
        
        logging.info("Processing completed successfully")
        
    except Exception as e:
        logging.error(f"Error during processing: {str(e)}")
        raise
        
    finally:
        processor.close()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    main()