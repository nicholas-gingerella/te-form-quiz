import psycopg2

def create_tables():
    # Database connection parameters
    db_params = {
        "dbname": "japanese_dictionary",
        "user": "user",
        "password": "password",
        "host": "localhost",
        "port": "5432"
    }

    # SQL commands to create tables
    commands = [
        """
        CREATE TABLE IF NOT EXISTS types (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL UNIQUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS words (
            id SERIAL PRIMARY KEY,
            kanji TEXT NOT NULL,
            frequency INTEGER,
            type_id INTEGER REFERENCES types(id),
            UNIQUE(kanji)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS definitions (
            id SERIAL PRIMARY KEY,
            word_id INTEGER REFERENCES words(id),
            definition TEXT NOT NULL
        )
        """,
        """
        -- Insert default word types if they don't exist
        INSERT INTO types (type)
        VALUES 
            ('noun'),
            ('verb'),
            ('i-adjective'),
            ('na-adjective'),
            ('other')
        ON CONFLICT (type) DO NOTHING;
        """
    ]

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Create each table
        for command in commands:
            cur.execute(command)

        # Commit the changes
        conn.commit()
        print("Tables created successfully!")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_tables()