import logging
from jmdict_processor import JMdictProcessor, DatabaseConfig
import xml.etree.ElementTree as ET

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('jmdict_import_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def test_import(xml_file: str, num_entries: int = 5):
    """Test importing a small number of entries."""
    
    # Database configuration - update these values
    db_config = DatabaseConfig(
        host='localhost',
        database='japanese_dictionary',  # Update to your database name
        user='user',            # Update to your username
        password='password'         # Update to your password
    )
    
    # Initialize processor
    processor = JMdictProcessor(
        db_config=db_config,
        conjugation_rules_path='conjugation_rules.yaml'
    )
    
    try:
        # Initialize reference tables first
        logging.info("Initializing reference tables...")
        processor.initialize_reference_tables()
        
        # Parse XML
        logging.info(f"Starting to parse {xml_file}")
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Get first n entries
        test_entries = []
        # for entry in root.findall('entry')[:num_entries]:
        for entry in root.findall('entry'):
            ent_seq = entry.find('ent_seq').text
            logging.info(f"\nProcessing entry {ent_seq}")
            
            # Log kanji if present
            kanji_elements = entry.findall('.//keb')
            if kanji_elements:
                logging.info("Kanji forms:")
                for keb in kanji_elements:
                    logging.info(f"  - {keb.text}")
            
            # Log readings
            readings = entry.findall('.//reb')
            if readings:
                logging.info("Readings:")
                for reb in readings:
                    logging.info(f"  - {reb.text}")
            
            # Log parts of speech
            pos_elements = entry.findall('.//pos')
            if pos_elements:
                logging.info("Parts of Speech:")
                for pos in pos_elements:
                    logging.info(f"  - {pos.text}")
            
            # Log definitions
            glosses = entry.findall('.//gloss')
            if glosses:
                logging.info("Definitions:")
                for gloss in glosses:
                    logging.info(f"  - {gloss.text}")
            
            # Process the entry
            processed_entry = processor._process_entry(entry)
            test_entries.append(processed_entry)
        
        # Try to insert the batch
        logging.info("\nAttempting to insert entries into database...")
        processor._insert_batch(test_entries)
        
        # Verify the data was inserted
        processor.cur.execute("""
            SELECT 
                e.id, 
                e.ent_seq,
                k.kanji,
                r.reading,
                d.definition_text
            FROM entries e
            LEFT JOIN kanji_elements k ON e.id = k.entry_id
            LEFT JOIN reading_elements r ON e.id = r.entry_id AND r.reading_type = 'hiragana'
            LEFT JOIN sense_elements s ON e.id = s.entry_id
            LEFT JOIN definitions d ON s.id = d.sense_id
            WHERE e.ent_seq = ANY(%s)
            ORDER BY e.id, k.id, r.id, s.id, d.id
        """, ([entry['ent_seq'] for entry in test_entries],))
        
        results = processor.cur.fetchall()
        
        logging.info("\nVerifying inserted data:")
        for row in results:
            logging.info(f"""
Entry ID: {row[0]}
Sequence: {row[1]}
Kanji: {row[2]}
Reading: {row[3]}
Definition: {row[4]}
---""")
        
    except Exception as e:
        logging.error(f"Error during test: {str(e)}", exc_info=True)
        raise
    
    finally:
        processor.close()

if __name__ == '__main__':
    setup_logging()
    test_import('JMdict_e.xml', num_entries=1000)