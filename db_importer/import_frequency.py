import psycopg2
import csv
import logging
from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class FrequencyUpdater:
    def __init__(self, db_params: dict):
        """Initialize database connection."""
        self.conn = psycopg2.connect(**db_params)
        self.cursor = self.conn.cursor()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up database resources."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def read_frequency_data(self, filename: str) -> Dict[str, int]:
        """Read frequency data from the file."""
        frequency_data = {}
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:  # Changed to utf-8-sig to handle BOM
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        try:
                            freq = int(parts[0])
                            word = parts[1]
                            frequency_data[word] = freq
                        except ValueError as e:
                            logging.warning(f"Skipping line due to invalid frequency value: {parts[0]}")
            
            logging.info(f"Read {len(frequency_data)} words from frequency file")
            return frequency_data
        except Exception as e:
            logging.error(f"Error reading frequency file: {e}")
            raise

    def get_dictionary_words(self) -> List[Tuple[str, str]]:
        """Get all words from dictionary with their IDs, handling multiple writing forms."""
        query = """
        WITH word_forms AS (
            SELECT e.id,
                   wf.form_text,
                   wf.form_type,
                   ROW_NUMBER() OVER (PARTITION BY e.id ORDER BY wf.form_type) as rn
            FROM entries e
            JOIN writing_forms wf ON e.id = wf.entry_id
        )
        SELECT id, form_text
        FROM word_forms
        WHERE rn = 1
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching dictionary words: {e}")
            raise

    def update_frequencies(self, frequency_data: Dict[str, int]):
        """Update frequency data in the database."""
        # First, get all words from dictionary
        dictionary_words = self.get_dictionary_words()
        
        # Prepare batch update
        update_data = []
        for entry_id, word in dictionary_words:
            if word in frequency_data:
                update_data.append((entry_id, 'web_corpus', frequency_data[word]))

        # Clear existing frequency data for this source
        try:
            self.cursor.execute("""
                DELETE FROM frequency_data 
                WHERE source = 'web_corpus'
            """)
            
            # Batch insert new frequency data
            self.cursor.executemany("""
                INSERT INTO frequency_data (entry_id, source, frequency)
                VALUES (%s, %s, %s)
            """, update_data)
            
            # Update ranks
            self.cursor.execute("""
                WITH ranked AS (
                    SELECT 
                        entry_id,
                        source,
                        frequency,
                        RANK() OVER (ORDER BY frequency DESC) as calculated_rank
                    FROM frequency_data
                    WHERE source = 'web_corpus'
                )
                UPDATE frequency_data fd
                SET rank = r.calculated_rank
                FROM ranked r
                WHERE fd.entry_id = r.entry_id
                AND fd.source = r.source
            """)
            
            self.conn.commit()
            logging.info(f"Updated frequencies for {len(update_data)} words")
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error updating frequencies: {e}")
            raise

def main():
    # Database connection parameters from environment variables
    db_params = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    try:
        with FrequencyUpdater(db_params) as updater:
            # Read frequency data
            frequency_data = updater.read_frequency_data('word_frequency_report.txt')
            
            # Update database
            updater.update_frequencies(frequency_data)
            
        logging.info("Frequency update completed successfully")
        
    except Exception as e:
        logging.error(f"Process failed: {e}")
        raise

if __name__ == "__main__":
    main()