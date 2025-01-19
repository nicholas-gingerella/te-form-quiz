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

    def _process_entry(self, entry: ET.Element) -> Dict:
        """Process a single entry from the XML."""
        ent_seq = int(entry.find('ent_seq').text)
        
        # Process kanji elements
        kanji_elements = []
        for k_ele in entry.findall('k_ele'):
            kanji = {
                'kanji': k_ele.find('keb').text,
                'info': [e.text for e in k_ele.findall('ke_inf')],
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
                'info': [e.text for e in r_ele.findall('re_inf')],
                'priority': [e.text for e in r_ele.findall('re_pri')]
            }
            reading_elements.append(reading)
        
        # Process sense elements
        sense_elements = []
        for sense in entry.findall('sense'):
            sense_data = {
                'pos': [pos.text for pos in sense.findall('pos')],
                'field': [field.text for field in sense.findall('field')],
                'misc': [misc.text for misc in sense.findall('misc')],
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

    def _insert_batch(self, entries: List[Dict]):
        """Insert a batch of entries into the database."""
        try:
            # Start transaction
            self.cur.execute("BEGIN")
            
            # Insert entries and get their IDs
            entry_values = [(e['ent_seq'],) for e in entries]
            self.cur.execute("""
                CREATE TEMPORARY TABLE temp_entries (
                    ent_seq INTEGER
                ) ON COMMIT DROP
            """)
            
            execute_values(
                self.cur,
                "INSERT INTO temp_entries (ent_seq) VALUES %s",
                entry_values
            )
            
            self.cur.execute("""
                INSERT INTO entries (ent_seq)
                SELECT ent_seq FROM temp_entries
                RETURNING id, ent_seq
            """)
            
            entry_ids = {row[1]: row[0] for row in self.cur.fetchall()}
            
            # Process each entry's components
            for entry in entries:
                entry_id = entry_ids[entry['ent_seq']]
                
                # Insert kanji elements
                self._insert_kanji_elements(entry_id, entry['kanji_elements'])
                
                # Insert reading elements
                self._insert_reading_elements(entry_id, entry['reading_elements'])
                
                # Insert sense elements and related data
                self._insert_sense_elements(entry_id, entry['sense_elements'])
                
                # Generate and insert conjugations if applicable
                self._process_conjugations(entry_id, entry)
            
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
            
            # Insert metadata
            if k_ele['info']:
                execute_values(
                    self.cur,
                    """
                    INSERT INTO kanji_metadata (kanji_element_id, info_type)
                    VALUES %s
                    """,
                    [(kanji_id, info) for info in k_ele['info']]
                )

    def _insert_reading_elements(self, entry_id: int, reading_elements: List[Dict]):
        """Insert reading elements for an entry."""
        for i, r_ele in enumerate(reading_elements, 1):
            # Convert reading to different scripts
            readings = self._get_readings(r_ele['reading'])
            
            self.cur.execute("""
                INSERT INTO reading_elements 
                (entry_id, reading, reading_type, no_kanji, priority_order)
                VALUES 
                (%s, %s, %s, %s, %s)
                RETURNING id
            """, (entry_id, r_ele['reading'], 'hiragana', r_ele['no_kanji'], i))
            
            reading_id = self.cur.fetchone()[0]
            
            # Insert additional reading types
            for reading_type, reading in readings.items():
                if reading_type != 'hiragana':  # Already inserted above
                    self.cur.execute("""
                        INSERT INTO reading_elements 
                        (entry_id, reading, reading_type, no_kanji, priority_order)
                        VALUES 
                        (%s, %s, %s, %s, %s)
                    """, (entry_id, reading, reading_type, r_ele['no_kanji'], i))

    def _insert_sense_elements(self, entry_id: int, sense_elements: List[Dict]):
        """Insert sense elements and related data for an entry."""
        for i, sense in enumerate(sense_elements, 1):
            self.cur.execute("""
                INSERT INTO sense_elements (entry_id, sense_order)
                VALUES (%s, %s)
                RETURNING id
            """, (entry_id, i))
            
            sense_id = self.cur.fetchone()[0]
            
            # Insert parts of speech
            if sense['pos']:
                execute_values(
                    self.cur,
                    """
                    INSERT INTO sense_pos (sense_id, pos_id)
                    SELECT %s, id FROM pos WHERE code = ANY(%s)
                    """,
                    [(sense_id, sense['pos'])]
                )
            
            # Insert fields
            if sense['field']:
                execute_values(
                    self.cur,
                    """
                    INSERT INTO sense_fields (sense_id, field_id)
                    SELECT %s, id FROM fields WHERE code = ANY(%s)
                    """,
                    [(sense_id, sense['field'])]
                )
            
            # Insert glosses
            if sense['glosses']:
                execute_values(
                    self.cur,
                    """
                    INSERT INTO glosses (sense_id, gloss_text, lang, gloss_type)
                    VALUES %s
                    """,
                    [(sense_id, g['text'], g['lang'], g['type']) 
                     for g in sense['glosses']]
                )

    def _process_conjugations(self, entry_id: int, entry: Dict):
        """Generate and insert conjugations for applicable words."""
        # Get parts of speech from all senses
        pos_list = set()
        for sense in entry['sense_elements']:
            pos_list.update(sense['pos'])
        
        # Filter for conjugatable parts of speech
        conjugatable_pos = {pos for pos in pos_list 
                          if any(pos.startswith(p) for p in 
                               ['v1', 'v5', 'adj-i', 'adj-na'])}
        
        if not conjugatable_pos:
            return
        
        # Get base form (use first kanji if available, otherwise first reading)
        base_form = (entry['kanji_elements'][0]['kanji'] 
                    if entry['kanji_elements'] 
                    else entry['reading_elements'][0]['reading'])
        
        # Generate conjugations for each applicable part of speech
        for pos in conjugatable_pos:
            conjugations = self._generate_conjugations(base_form, pos)
            self._insert_conjugations(entry_id, conjugations)

    def _generate_conjugations(self, word: str, pos: str) -> List[Dict]:
        """Generate all conjugations for a word based on its part of speech."""
        results = []
        
        # Get appropriate rule set
        if pos.startswith('v5'):
            rule_set = self.conjugation_rules['verb_rules']['godan'][pos]
        elif pos.startswith('v1'):
            rule_set = self.conjugation_rules['verb_rules']['ichidan'][pos]
        elif pos == 'adj-i':
            rule_set = self.conjugation_rules['adjective_rules']['i_adjectives'][pos]
        elif pos == 'adj-na':
            rule_set = self.conjugation_rules['adjective_rules']['na_adjectives'][pos]
        else:
            return results
        
        # Apply conjugation patterns
        for conj_type, patterns in rule_set['conjugations'].items():
            for form, pattern in patterns.items():
                conjugated = self._apply_pattern(word, pattern['pattern'])
                readings = self._get_readings(conjugated)
                
                results.append({
                    'conjugation_type': conj_type,
                    'form': form,
                    'kanji_form': conjugated,
                    **readings
                })
        
        return results

    def _apply_pattern(self, word: str, pattern: str) -> str:
        """Apply a conjugation pattern to a word."""
        # Basic implementation - will need refinement
        if word.endswith('る'):
            return word[:-1] + pattern
        if word.endswith('う'):
            return word[:-1] + pattern
        # Add more ending patterns as needed
        return word + pattern

    def _get_readings(self, word: str) -> Dict[str, str]:
        """Generate different readings of a word."""
        result = self.kakasi.convert(word)
        
        return {
            'hiragana': result[0]['hira'],
            'katakana': result[0]['kana'],
            'romaji': result[0]['roma']
        }

    def _insert_conjugations(self, entry_id: int, conjugations: List[Dict]):
        """Insert conjugations for an entry."""
        if not conjugations:
            return
            
        execute_values(
            self.cur,
            """
            INSERT INTO conjugations 
            (entry_id, kanji_form, hiragana_reading, katakana_reading, romaji_reading)
            VALUES %s
            """,
            [(entry_id, c['kanji_form'], c['hiragana'], c['katakana'], c['romaji']) 
             for c in conjugations]
        )

    def close(self):
        """Close database connection."""
        self.cur.close()
        self.conn.close()

def main():
    # Configuration
    db_config = DatabaseConfig(
        host='localhost',
        database='japanese_quiz',
        user='user',
        password='password'
    )
    
    # Initialize processor
    processor = JMdictProcessor(
        db_config=db_config,
        conjugation_rules_path='conjugation_rules.yaml'
    )
    
    try:
        # Process the file
        processor.process_file('JMdict_e.xml', batch_size=1000)
        
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        raise
        
    finally:
        processor.close()

if __name__ == '__main__':
    main()