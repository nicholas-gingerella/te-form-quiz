import logging
from jmdict_processor import JMdictProcessor, DatabaseConfig
import xml.etree.ElementTree as ET
import json
from pprint import pformat
from datetime import datetime

class FileOutput:
    def __init__(self, filename):
        self.filename = filename
        # Open file in write mode and create/truncate it
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"JMdict Processing Test Results - {datetime.now()}\n\n")
    
    def write(self, content):
        # Append content to file
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(str(content) + "\n")

def print_section(output, title, content=""):
    """Helper function to print sections clearly"""
    output.write("\n" + "="*80)
    output.write(f"{title}")
    output.write("="*80)
    if content:
        output.write(str(content))

def setup_logging(timestamp):
    """Set up logging configuration."""
    # Clear any existing handlers
    logging.getLogger().handlers = []
    
    # Create handlers
    file_handler = logging.FileHandler(f'debug_log_{timestamp}.txt', encoding='utf-8')
    console_handler = logging.StreamHandler()
    
    # Set levels
    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

def test_detailed_processing(xml_file: str, num_entries: int = 2):
    """Test XML processing with detailed output for verification."""
    
    # Create timestamp for file names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Set up logging
    setup_logging(timestamp)
    
    # Create output file for test results
    output = FileOutput(f'jmdict_test_results_{timestamp}.txt')
    
    db_config = DatabaseConfig(
        host='localhost',
        database='japanese_quiz',
        user='user',
        password='password'
    )
    
    processor = JMdictProcessor(
        db_config=db_config,
        conjugation_rules_path='conjugation_rules.yaml'
    )
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        entries = root.findall('entry')[:num_entries]
        
        for i, entry in enumerate(entries, 1):
            print_section(output, f"Entry {i}")
            
            # Basic Entry Info
            ent_seq = entry.find('ent_seq').text
            output.write(f"Entry Sequence Number: {ent_seq}")
            
            # Kanji Elements
            output.write("\nKanji Elements:")
            k_eles = entry.findall('k_ele')
            if k_eles:
                for k_ele in k_eles:
                    keb = k_ele.find('keb').text
                    ke_inf = [e.text for e in k_ele.findall('ke_inf')]
                    ke_pri = [e.text for e in k_ele.findall('ke_pri')]
                    output.write(f"  Kanji: {keb}")
                    if ke_inf:
                        output.write(f"  Info: {ke_inf}")
                    if ke_pri:
                        output.write(f"  Priority: {ke_pri}")
            else:
                output.write("  No kanji elements")
            
            # Reading Elements
            output.write("\nReading Elements:")
            r_eles = entry.findall('r_ele')
            for r_ele in r_eles:
                reb = r_ele.find('reb').text
                re_nokanji = r_ele.find('re_nokanji') is not None
                re_restr = [e.text for e in r_ele.findall('re_restr')]
                re_inf = [e.text for e in r_ele.findall('re_inf')]
                re_pri = [e.text for e in r_ele.findall('re_pri')]
                
                output.write(f"  Reading: {reb}")
                if re_nokanji:
                    output.write("  No kanji: Yes")
                if re_restr:
                    output.write(f"  Restrictions: {re_restr}")
                if re_inf:
                    output.write(f"  Info: {re_inf}")
                if re_pri:
                    output.write(f"  Priority: {re_pri}")
            
            # Sense Elements
            output.write("\nSense Elements:")
            senses = entry.findall('sense')
            for j, sense in enumerate(senses, 1):
                output.write(f"\n  Sense {j}:")
                
                pos = [e.text for e in sense.findall('pos')]
                if pos:
                    output.write(f"    Part of Speech: {pos}")
                
                field = [e.text for e in sense.findall('field')]
                if field:
                    output.write(f"    Field: {field}")
                
                misc = [e.text for e in sense.findall('misc')]
                if misc:
                    output.write(f"    Misc: {misc}")
                
                glosses = [gloss.text for gloss in sense.findall('gloss')]
                if glosses:
                    output.write(f"    Glosses: {glosses}")
            
            # Process entry and show full structure
            processed_entry = processor._process_entry(entry)
            output.write("\nProcessed Entry Structure:")
            output.write(pformat(processed_entry, indent=2, width=80))
            
            # Generate and display conjugations if applicable
            pos_list = set()
            for sense in processed_entry['sense_elements']:
                mapped_pos = [processor._map_pos(pos) for pos in sense['pos']]
                pos_list.update(mapped_pos)
            
            conjugatable_pos = {pos for pos in pos_list 
                              if pos in ['adj-i', 'adj-na'] or 
                              pos.startswith(('v1', 'v5'))}
            
            if conjugatable_pos:
                output.write("\nConjugations:")
                base_form = (processed_entry['kanji_elements'][0]['kanji'] 
                           if processed_entry['kanji_elements'] 
                           else processed_entry['reading_elements'][0]['reading'])
                
                for pos in conjugatable_pos:
                    output.write(f"\n  Conjugations for {base_form} ({pos}):")
                    conjugations = processor._generate_conjugations(base_form, pos)
                    if conjugations:
                        for conj in conjugations:
                            output.write(f"\n    Type: {conj['conjugation_type']}")
                            output.write(f"    Form: {conj['form']}")
                            output.write(f"    Kanji: {conj['kanji_form']}")
                            output.write(f"    Hiragana: {conj['hiragana']}")
                            output.write(f"    Katakana: {conj['katakana']}")
                            output.write(f"    Romaji: {conj['romaji']}")
                    else:
                        output.write("    No conjugations generated")
            
            # Different writing systems for each reading
            output.write("\nWriting Systems for Readings:")
            for reading in processed_entry['reading_elements']:
                readings = processor._get_readings(reading['reading'])
                output.write(f"\n  Original: {reading['reading']}")
                output.write(f"  Hiragana: {readings['hiragana']}")
                output.write(f"  Katakana: {readings['katakana']}")
                output.write(f"  Romaji: {readings['romaji']}")
            
            output.write("\n" + "-"*80 + "\n")
            
    except Exception as e:
        logging.error(f"Error during detailed test: {str(e)}", exc_info=True)
    
    finally:
        processor.close()
        logging.info(f"Results written to {output.filename}")

if __name__ == '__main__':
    test_detailed_processing('JMdict_e.xml', num_entries=20000)