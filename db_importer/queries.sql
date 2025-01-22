-- Basic word lookup by kanji/kana (common forms only)
SELECT DISTINCT e.id, e.is_common, 
       wf.form_text, wf.form_type
FROM entries e
JOIN writing_forms wf ON e.id = wf.entry_id
WHERE EXISTS (
    SELECT 1 FROM writing_forms w2
    WHERE w2.entry_id = e.id AND w2.form_text = '食べる'
)
AND (e.is_common = true OR wf.is_common = true);

-- Get all common forms and meanings for a specific word
WITH target_word AS (
    SELECT DISTINCT e.id
    FROM entries e
    JOIN writing_forms wf ON e.id = wf.entry_id
    WHERE wf.form_text = '食べる'
)
SELECT wf.form_text, wf.form_type,
       s.sense_order,
       string_agg(DISTINCT sp.pos, ', ') as parts_of_speech,
       string_agg(DISTINCT g.gloss, ' | ') as meanings
FROM target_word tw
JOIN writing_forms wf ON tw.id = wf.entry_id
JOIN senses s ON tw.id = s.entry_id
LEFT JOIN sense_pos sp ON s.id = sp.sense_id
LEFT JOIN glosses g ON s.id = g.sense_id
WHERE wf.is_common = true
GROUP BY wf.form_text, wf.form_type, s.sense_order
ORDER BY wf.form_type, s.sense_order;

-- Get conjugations for a word (showing only common kanji forms)
SELECT c.conjugation_type, c.form, 
       CASE WHEN wf.is_common = true THEN c.kanji ELSE NULL END as kanji, 
       c.kana
FROM entries e
JOIN conjugations c ON e.id = c.entry_id
JOIN writing_forms wf ON e.id = wf.entry_id AND wf.form_text = c.kanji
WHERE wf.form_text = '食べる'
ORDER BY c.conjugation_type, c.form;

-- Search for common words by English meaning
SELECT DISTINCT e.id, 
       string_agg(DISTINCT 
           CASE WHEN wf.is_common THEN wf.form_text ELSE NULL END, 
           ' / ') as common_forms,
       g.gloss as matching_meaning
FROM entries e
JOIN writing_forms wf ON e.id = wf.entry_id
JOIN senses s ON e.id = s.entry_id
JOIN glosses g ON s.id = g.sense_id
WHERE g.gloss ILIKE '%eat%'
AND (e.is_common = true OR wf.is_common = true)
GROUP BY e.id, g.gloss
HAVING string_agg(DISTINCT 
           CASE WHEN wf.is_common THEN wf.form_text ELSE NULL END, 
           ' / ') IS NOT NULL
ORDER BY e.is_common DESC, common_forms;

-- Get example sentences for a word (common forms only)
SELECT DISTINCT e.japanese, e.english
FROM entries ent
JOIN examples e ON ent.id = e.entry_id
JOIN writing_forms wf ON ent.id = wf.entry_id
WHERE wf.form_text = '食べる'
AND wf.is_common = true;

-- Find all common verbs
SELECT DISTINCT wf.form_text, 
       string_agg(DISTINCT sp.pos, ', ') as verb_types
FROM entries e
JOIN writing_forms wf ON e.id = wf.entry_id
JOIN senses s ON e.id = s.entry_id
JOIN sense_pos sp ON s.id = sp.sense_id
WHERE sp.pos LIKE 'v%'
AND wf.is_common = true
GROUP BY wf.form_text
ORDER BY wf.form_text;

-- Find words by field/category (common forms only)
SELECT DISTINCT wf.form_text,
       sf.field,
       string_agg(DISTINCT g.gloss, ' | ') as meanings
FROM entries e
JOIN writing_forms wf ON e.id = wf.entry_id
JOIN senses s ON e.id = s.entry_id
JOIN sense_fields sf ON s.id = sf.sense_id
JOIN glosses g ON s.id = g.sense_id
WHERE sf.field = 'sports'  -- Change field as needed
AND wf.is_common = true
GROUP BY wf.form_text, sf.field
ORDER BY wf.form_text;

-- Statistics about common words

-- Count of common entries by part of speech
SELECT sp.pos, COUNT(DISTINCT e.id) as word_count
FROM entries e
JOIN writing_forms wf ON e.id = wf.entry_id
JOIN senses s ON e.id = s.entry_id
JOIN sense_pos sp ON s.id = sp.sense_id
WHERE wf.is_common = true
GROUP BY sp.pos
ORDER BY word_count DESC;

-- Count of common entries by field
SELECT sf.field, COUNT(DISTINCT e.id) as word_count
FROM entries e
JOIN writing_forms wf ON e.id = wf.entry_id
JOIN senses s ON e.id = s.entry_id
JOIN sense_fields sf ON s.id = sf.sense_id
WHERE wf.is_common = true
GROUP BY sf.field
ORDER BY word_count DESC;