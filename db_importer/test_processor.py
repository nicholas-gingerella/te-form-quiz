import logging
from jmdict_processor import JMdictProcessor, DatabaseConfig
import xml.etree.ElementTree as ET

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_processing(xml_file: str, num_entries: int = 5):
    """Test XML processing with a limited number of entries."""
    
    # Database configuration - adjust these values as needed
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
        # Parse XML
        logging.info(f"Parsing {xml_file}")
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Get limited number of entries
        entries = root.findall('entry')[:num_entries]
        
        for i, entry in enumerate(entries, 1):
            logging.info(f"\nProcessing entry {i} of {num_entries}")
            
            # Get basic entry info
            ent_seq = entry.find('ent_seq').text
            logging.info(f"Entry sequence: {ent_seq}")
            
            # Get kanji elements
            k_eles = entry.findall('k_ele')
            if k_eles:
                logging.info("Kanji elements:")
                for k_ele in k_eles:
                    keb = k_ele.find('keb').text
                    logging.info(f"  - {keb}")
            
            # Get reading elements
            r_eles = entry.findall('r_ele')
            if r_eles:
                logging.info("Reading elements:")
                for r_ele in r_eles:
                    reb = r_ele.find('reb').text
                    logging.info(f"  - {reb}")
            
            # Get sense elements
            senses = entry.findall('sense')
            if senses:
                logging.info("Sense elements:")
                for j, sense in enumerate(senses, 1):
                    logging.info(f"  Sense {j}:")
                    
                    # Get POS info
                    pos_elements = sense.findall('pos')
                    if pos_elements:
                        pos_list = [pos.text for pos in pos_elements]
                        logging.info(f"    POS: {', '.join(pos_list)}")
                    
                    # Get glosses
                    glosses = sense.findall('gloss')
                    if glosses:
                        gloss_list = [gloss.text for gloss in glosses]
                        logging.info(f"    Glosses: {', '.join(gloss_list)}")
            
            # Process the entry
            processed_entry = processor._process_entry(entry)
            logging.debug(f"Processed entry structure: {processed_entry}")
            
            # Test conjugation generation if applicable
            pos_list = set()
            for sense in processed_entry['sense_elements']:
                pos_list.update(sense['pos'])
            
            conjugatable_pos = {pos for pos in pos_list 
                              if any(pos.startswith(p) for p in 
                                   ['v1', 'v5', 'adj-i', 'adj-na'])}
            
            if conjugatable_pos:
                logging.info(f"Found conjugatable POS: {conjugatable_pos}")
                base_form = (processed_entry['kanji_elements'][0]['kanji'] 
                           if processed_entry['kanji_elements'] 
                           else processed_entry['reading_elements'][0]['reading'])
                
                for pos in conjugatable_pos:
                    logging.info(f"Generating conjugations for {base_form} ({pos})")
                    conjugations = processor._generate_conjugations(base_form, pos)
                    logging.info(f"Generated conjugations: {conjugations}")
        
        logging.info("\nTest processing completed successfully")
        
    except Exception as e:
        logging.error(f"Error during test processing: {str(e)}", exc_info=True)
    
    finally:
        processor.close()

if __name__ == '__main__':
    test_processing('JMdict_e.xml', num_entries=10000)