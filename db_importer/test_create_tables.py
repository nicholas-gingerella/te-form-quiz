import psycopg2
from psycopg2.extras import RealDictCursor

def test_database():
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
        cur = conn.cursor(cursor_factory=RealDictCursor)

        print("\n1. Testing connection and tables exist:")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = cur.fetchall()
        print("Available tables:", [table['table_name'] for table in tables])

        print("\n2. Checking pre-populated types:")
        cur.execute("SELECT * FROM types ORDER BY id;")
        types = cur.fetchall()
        for type_row in types:
            print(f"• {type_row['id']}: {type_row['type']}")

        print("\n3. Testing word insertion:")
        # Insert a test word
        cur.execute("""
            INSERT INTO words (kanji, frequency, type_id)
            VALUES ('食べる', 1000, (SELECT id FROM types WHERE type = 'verb'))
            ON CONFLICT (kanji) DO NOTHING
            RETURNING id;
        """)
        word_id = cur.fetchone()
        if word_id:
            word_id = word_id['id']
            print(f"Inserted word with ID: {word_id}")

            # Insert some definitions
            definitions = ["to eat", "to consume"]
            for definition in definitions:
                cur.execute("""
                    INSERT INTO definitions (word_id, definition)
                    VALUES (%s, %s);
                """, (word_id, definition))
            print("Inserted definitions")

        print("\n4. Testing word retrieval:")
        cur.execute("""
            SELECT w.kanji, w.frequency, t.type, array_agg(d.definition) as definitions
            FROM words w
            JOIN types t ON w.type_id = t.id
            JOIN definitions d ON w.id = d.word_id
            WHERE w.kanji = '食べる'
            GROUP BY w.kanji, w.frequency, t.type;
        """)
        result = cur.fetchone()
        if result:
            print(f"Word: {result['kanji']}")
            print(f"Frequency: {result['frequency']}")
            print(f"Type: {result['type']}")
            print("Definitions:")
            for definition in result['definitions']:
                print(f"• {definition}")

        # Commit the changes
        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_database()