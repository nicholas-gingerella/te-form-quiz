import psycopg2
from psycopg2.extras import RealDictCursor

def get_word_definition(word):
    # Database connection parameters
    db_params = {
        "dbname": "japanese_dictionary",
        "user": "user",
        "password": "password",
        "host": "localhost",
        "port": "5432"
    }

    try:
        # Connect to database
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor(cursor_factory=RealDictCursor)  # Returns results as dictionaries

        # Your query
        query = """
            SELECT wf.form_text, g.gloss as definition
            FROM entries e
            JOIN writing_forms wf ON e.id = wf.entry_id
            JOIN senses s ON e.id = s.entry_id
            JOIN glosses g ON s.id = g.sense_id
            WHERE wf.form_text = %s;
        """
        
        # Execute query with parameter
        cur.execute(query, (word,))
        results = cur.fetchall()

        return results

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def process_frequency_report(filename, limit=100):
    """Process the word frequency report and look up definitions.
    Args:
        filename: Path to the word frequency report
        limit: Maximum number of words to process (default 100)
    """
    with open(filename, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= limit:  # Stop after processing limit words
                break
                
            # Parse the line
            parts = line.strip().split('\t')
            if len(parts) >= 2:  # Ensure we have at least frequency and word
                freq = parts[0]
                word = parts[1]
                
                # Get definitions
                definitions = get_word_definition(word)
                
                # Print results
                print(f"\n{i+1}. {word} (Frequency: {freq})")
                if definitions:
                    for definition in definitions:
                        print(f"  • {definition['definition']}")
                else:
                    print("  No definitions found")

if __name__ == "__main__":
    report_file = "db_importer/word_frequency_report.txt"
    process_frequency_report(report_file, limit=20)  # Process top 20 words