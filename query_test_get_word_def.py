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

# Example usage
if __name__ == "__main__":
    word = "考える"
    definitions = get_word_definition(word)
    
    print(f"\nDefinitions for {word}:")
    if definitions:
        # Use list comprehension instead of explicit loop
        definition_list = [row['definition'] for row in definitions]
        # Print each definition on a new line with bullet points
        for definition in definition_list:
            print(f"• {definition}")
    else:
        print("No definitions found or an error occurred.")