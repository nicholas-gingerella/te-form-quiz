import json
import psycopg2
from psycopg2.extras import execute_values
from japanese_conjugator import process_dictionary_entry
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

load_dotenv()

def process_entry(entry: Dict[str, Any], cur) -> None:
    """Process a single dictionary entry and insert it into the database."""
    entry_id = entry['id']
    
    # Check if any kanji or kana forms are marked as common
    kanji_common = any(k.get('common', False) for k in entry.get('kanji', []))
    kana_common = any(k.get('common', False) for k in entry.get('kana', []))
    is_common = kanji_common or kana_common
    
    # Insert entry
    cur.execute(
        "INSERT INTO entries (id, is_common) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (entry_id, is_common)
    )
    
    # Insert writing forms
    writing_forms = []
    for kanji in entry.get('kanji', []):
        writing_forms.append((
            entry_id,
            kanji['text'],
            'kanji',
            kanji.get('common', False)
        ))
    for kana in entry.get('kana', []):
        writing_forms.append((
            entry_id,
            kana['text'],
            'kana',
            kana.get('common', False)
        ))
    
    if writing_forms:
        execute_values(cur,
            "INSERT INTO writing_forms (entry_id, form_text, form_type, is_common) VALUES %s ON CONFLICT DO NOTHING",
            writing_forms
        )
    
    # Process senses
    for sense_idx, sense in enumerate(entry.get('sense', []), 1):
        # Insert sense
        cur.execute(
            "INSERT INTO senses (entry_id, sense_order) VALUES (%s, %s) RETURNING id",
            (entry_id, sense_idx)
        )
        sense_id = cur.fetchone()[0]
        
        # Insert parts of speech
        pos_values = [(sense_id, pos) for pos in sense.get('partOfSpeech', [])]
        if pos_values:
            execute_values(cur,
                "INSERT INTO sense_pos (sense_id, pos) VALUES %s ON CONFLICT DO NOTHING",
                pos_values
            )
        
        # Insert fields (categories)
        field_values = [(sense_id, field) for field in sense.get('field', [])]
        if field_values:
            execute_values(cur,
                "INSERT INTO sense_fields (sense_id, field) VALUES %s ON CONFLICT DO NOTHING",
                field_values
            )
        
        # Insert glosses
        gloss_values = [(sense_id, gloss['text'], gloss.get('lang', 'eng')) 
                       for gloss in sense.get('gloss', [])]
        if gloss_values:
            execute_values(cur,
                "INSERT INTO glosses (sense_id, gloss, lang) VALUES %s",
                gloss_values
            )
        
        # Insert examples
        examples = []
        for example in sense.get('examples', []):
            for sentence in example.get('sentences', []):
                if sentence.get('land') == 'jpn':
                    japanese = sentence['text']
                elif sentence.get('land') == 'eng':
                    english = sentence['text']
                    examples.append((entry_id, japanese, english))
        
        if examples:
            execute_values(cur,
                "INSERT INTO examples (entry_id, japanese, english) VALUES %s ON CONFLICT DO NOTHING",
                examples
            )
    
    # Process conjugations
    conjugation_results = process_dictionary_entry(entry)
    conjugation_values = []
    for result in conjugation_results:
        conj_type = result['type']
        for form, conj in result['conjugations'].items():
            conjugation_values.append((
                entry_id,
                conj_type,
                form,
                conj['kanji'],
                conj['kana']
            ))
    
    if conjugation_values:
        execute_values(cur,
            """INSERT INTO conjugations 
               (entry_id, conjugation_type, form, kanji, kana) 
               VALUES %s ON CONFLICT DO NOTHING""",
            conjugation_values
        )
    
    # Process word relationships (to be added in second pass)
    for sense in entry.get('sense', []):
        for related in sense.get('related', []):
            if isinstance(related, list) and len(related) >= 1:
                # Store for second pass - we need all entries to be inserted first
                pass

def create_indices(conn) -> None:
    """Create indices for better query performance."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_writing_forms_text ON writing_forms(form_text);
            CREATE INDEX IF NOT EXISTS idx_senses_entry_id ON senses(entry_id);
            CREATE INDEX IF NOT EXISTS idx_glosses_sense_id ON glosses(sense_id);
            CREATE INDEX IF NOT EXISTS idx_examples_entry_id ON examples(entry_id);
            CREATE INDEX IF NOT EXISTS idx_conjugations_entry_id ON conjugations(entry_id);
            CREATE INDEX IF NOT EXISTS idx_word_relationships_entry_id ON word_relationships(entry_id);
        """)
    conn.commit()

def main():
    # Database connection parameters from environment variables
    db_params = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    # Connect to database
    conn = psycopg2.connect(**db_params)
    
    try:        
        # Read and process the JSON file
        with open('jmdict-examples-eng-3.6.1.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # First pass: Process all entries
            total_entries = len(data['words'])
            print(f"Processing {total_entries} entries...")
            
            with conn.cursor() as cur:
                for i, entry in enumerate(data['words'], 1):
                    if i % 1000 == 0:
                        print(f"Processing entry {i}/{total_entries}")
                    process_entry(entry, cur)
                    
                    # Commit every 1000 entries
                    if i % 1000 == 0:
                        conn.commit()
            
            # Final commit for any remaining entries
            conn.commit()
            
            # Create indices after all data is inserted
            print("Creating indices...")
            create_indices(conn)
            
            print("Database population completed successfully!")
    
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main()