from typing import Dict, List, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

class JapaneseDictionary:
    def __init__(self):
        self.db_params = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT', '5432')
        }
    
    def _get_connection(self):
        """Get a database connection with RealDictCursor for named columns."""
        return psycopg2.connect(**self.db_params, cursor_factory=RealDictCursor)
    
    def lookup_word(self, text: str) -> Dict[str, Any]:
        """Look up a word by its kanji or kana form."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Get basic word information
                cur.execute("""
                    SELECT DISTINCT e.id, e.is_common,
                           wf.form_text, wf.form_type, wf.is_common as form_common
                    FROM entries e
                    JOIN writing_forms wf ON e.id = wf.entry_id
                    WHERE EXISTS (
                        SELECT 1 FROM writing_forms w2
                        WHERE w2.entry_id = e.id AND w2.form_text = %s
                    )
                """, (text,))
                
                results = {}
                for row in cur.fetchall():
                    entry_id = row['id']
                    if entry_id not in results:
                        results[entry_id] = {
                            'id': entry_id,
                            'is_common': row['is_common'],
                            'writing_forms': [],
                            'senses': [],
                            'conjugations': [],
                            'examples': []
                        }
                    
                    # Add writing form
                    results[entry_id]['writing_forms'].append({
                        'text': row['form_text'],
                        'type': row['form_type'],
                        'is_common': row['form_common']
                    })
                
                # If we found any results, get additional information
                for entry_id in results:
                    # Get senses (meanings)
                    cur.execute("""
                        SELECT s.id, s.sense_order,
                               array_agg(DISTINCT sp.pos) as pos,
                               array_agg(DISTINCT sf.field) as fields,
                               array_agg(DISTINCT g.gloss) as glosses
                        FROM senses s
                        LEFT JOIN sense_pos sp ON s.id = sp.sense_id
                        LEFT JOIN sense_fields sf ON s.id = sf.sense_id
                        LEFT JOIN glosses g ON s.id = g.sense_id
                        WHERE s.entry_id = %s
                        GROUP BY s.id, s.sense_order
                        ORDER BY s.sense_order
                    """, (entry_id,))
                    
                    results[entry_id]['senses'] = [dict(row) for row in cur.fetchall()]
                    
                    # Get conjugations
                    cur.execute("""
                        SELECT conjugation_type, form, kanji, kana
                        FROM conjugations
                        WHERE entry_id = %s
                        ORDER BY conjugation_type, form
                    """, (entry_id,))
                    
                    results[entry_id]['conjugations'] = [dict(row) for row in cur.fetchall()]
                    
                    # Get examples
                    cur.execute("""
                        SELECT japanese, english
                        FROM examples
                        WHERE entry_id = %s
                    """, (entry_id,))
                    
                    results[entry_id]['examples'] = [dict(row) for row in cur.fetchall()]
                
                return results
    
    def search_by_meaning(self, text: str) -> Dict[str, Any]:
        """Search for words by their English meaning."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT e.id, e.is_common,
                           wf.form_text, wf.form_type, wf.is_common as form_common
                    FROM entries e
                    JOIN writing_forms wf ON e.id = wf.entry_id
                    JOIN senses s ON e.id = s.entry_id
                    JOIN glosses g ON s.id = g.sense_id
                    WHERE g.gloss ILIKE %s
                    ORDER BY e.is_common DESC, wf.form_text
                """, (f'%{text}%',))
                
                results = {}
                for row in cur.fetchall():
                    entry_id = row['id']
                    if entry_id not in results:
                        results[entry_id] = {
                            'id': entry_id,
                            'is_common': row['is_common'],
                            'writing_forms': [],
                            'senses': []
                        }
                    
                    results[entry_id]['writing_forms'].append({
                        'text': row['form_text'],
                        'type': row['form_type'],
                        'is_common': row['form_common']
                    })
                
                # Get detailed information for each entry