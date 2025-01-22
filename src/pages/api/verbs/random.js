// pages/api/verbs/random.js
const db = require('../../lib/db');

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Query to get random common verbs with their conjugations
    const query = `
      WITH random_verbs AS (
        SELECT DISTINCT e.id, 
               wf.form_text as dictionary_form,
               wf.form_type,
               sp.pos as verb_type
        FROM entries e
        JOIN writing_forms wf ON e.id = wf.entry_id
        JOIN senses s ON e.id = s.entry_id
        JOIN sense_pos sp ON s.id = sp.sense_id
        WHERE sp.pos LIKE 'v%'
        AND wf.is_common = true
        ORDER BY RANDOM()
        LIMIT 20
      )
      SELECT rv.*,
             c.form as conjugation_form,
             c.kanji as conjugated_kanji,
             c.kana as conjugated_kana
      FROM random_verbs rv
      JOIN conjugations c ON rv.id = c.entry_id
      WHERE c.form = 'te_form'
      ORDER BY rv.dictionary_form;
    `;

    const result = await db.query(query);
    
    const verbs = result.rows.map(row => ({
      id: row.id,
      dictionaryForm: {
        kanji: row.form_type === 'kanji' ? row.dictionary_form : '',
        kana: row.form_type === 'kana' ? row.dictionary_form : ''
      },
      verbType: row.verb_type,
      teForm: {
        kanji: row.conjugated_kanji,
        kana: row.conjugated_kana
      }
    }));

    res.status(200).json(verbs);
  } catch (error) {
    console.error('Database error:', error);
    res.status(500).json({ message: 'Error fetching verbs' });
  }
}