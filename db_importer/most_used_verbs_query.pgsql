-- get the 50 most used verbs in japanese
WITH ranked_words AS (
    SELECT DISTINCT ON (fd.frequency, COALESCE(wf_kanji.form_text, wf_kana.form_text))
        e.id,
        CASE 
            WHEN sp.pos = 'prt' OR wf_kanji.form_text IS NULL THEN NULL 
            ELSE wf_kanji.form_text 
        END as kanji_text,
        wf_kana.form_text as kana_text,
        fd.frequency,
        fd.rank,
        sp.pos as word_type,
        string_agg(DISTINCT g.gloss, '; ' ORDER BY g.gloss) as definition
    FROM frequency_data fd
    JOIN entries e ON fd.entry_id = e.id
    LEFT JOIN writing_forms wf_kanji ON 
        e.id = wf_kanji.entry_id AND 
        wf_kanji.form_type = 'kanji' AND
        wf_kanji.is_common = true
    LEFT JOIN writing_forms wf_kana ON 
        e.id = wf_kana.entry_id AND 
        wf_kana.form_type = 'kana' AND
        wf_kana.is_common = true
    LEFT JOIN senses s ON e.id = s.entry_id
    LEFT JOIN sense_pos sp ON s.id = sp.sense_id
    LEFT JOIN glosses g ON s.id = g.sense_id
    WHERE fd.source = 'web_corpus'
    AND s.sense_order = 1
    AND (wf_kanji.is_common = true OR wf_kana.is_common = true)
    AND sp.pos LIKE 'v%'  -- Only get verbs
    GROUP BY 
        e.id, 
        wf_kanji.form_text,  -- Added this
        wf_kana.form_text,   -- And this
        fd.frequency, 
        fd.rank, 
        sp.pos
)
SELECT 
    kanji_text as kanji,
    kana_text as kana,
    word_type,
    definition,
    frequency,
    rank
FROM ranked_words
WHERE kana_text IS NOT NULL
ORDER BY frequency DESC
LIMIT 50;