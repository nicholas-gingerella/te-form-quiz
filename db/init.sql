-- Core table for dictionary entries
CREATE TABLE entries (
    id TEXT PRIMARY KEY,  -- Using the JMdict ID
    is_common BOOLEAN DEFAULT FALSE
);

-- Writing forms (both kanji and kana)
CREATE TABLE writing_forms (
    entry_id TEXT REFERENCES entries(id),
    form_text TEXT NOT NULL,
    form_type TEXT NOT NULL,  -- 'kanji' or 'kana'
    is_common BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (entry_id, form_text, form_type)
);

-- Senses (meanings)
CREATE TABLE senses (
    id SERIAL PRIMARY KEY,
    entry_id TEXT REFERENCES entries(id),
    sense_order INTEGER NOT NULL
);

-- Parts of speech for each sense
CREATE TABLE sense_pos (
    sense_id INTEGER REFERENCES senses(id),
    pos TEXT NOT NULL,
    PRIMARY KEY (sense_id, pos)
);

-- Field categories for each sense
CREATE TABLE sense_fields (
    sense_id INTEGER REFERENCES senses(id),
    field TEXT NOT NULL,
    PRIMARY KEY (sense_id, field)
);

-- Glosses (definitions)
CREATE TABLE glosses (
    sense_id INTEGER REFERENCES senses(id),
    gloss TEXT NOT NULL,
    lang TEXT DEFAULT 'eng'
);

-- Example sentences
CREATE TABLE examples (
    id SERIAL PRIMARY KEY,
    entry_id TEXT REFERENCES entries(id),
    japanese TEXT NOT NULL,
    english TEXT NOT NULL
);

-- Conjugations
CREATE TABLE conjugations (
    entry_id TEXT REFERENCES entries(id),
    conjugation_type TEXT NOT NULL,  -- e.g., 'v5u', 'v1', 'adj-i'
    form TEXT NOT NULL,  -- e.g., 'present', 'past', 'te_form'
    kanji TEXT,
    kana TEXT NOT NULL,
    PRIMARY KEY (entry_id, conjugation_type, form)
);

-- Word relationships (synonyms, antonyms, etc.)
CREATE TABLE word_relationships (
    entry_id TEXT REFERENCES entries(id),
    related_id TEXT REFERENCES entries(id),
    relation_type TEXT NOT NULL,  -- 'synonym', 'antonym', etc.
    PRIMARY KEY (entry_id, related_id, relation_type)
);

CREATE TABLE jlpt_levels (
    entry_id TEXT REFERENCES entries(id) PRIMARY KEY,
    level INTEGER CHECK (level BETWEEN 1 AND 5)
);

CREATE TABLE frequency_data (
    entry_id TEXT REFERENCES entries(id),
    source TEXT NOT NULL,  -- e.g., 'newspaper', 'web', 'netflix'
    rank INTEGER,
    frequency NUMERIC,
    PRIMARY KEY (entry_id, source)
);

CREATE INDEX IF NOT EXISTS idx_writing_forms_text ON writing_forms(form_text);
CREATE INDEX IF NOT EXISTS idx_senses_entry_id ON senses(entry_id);
CREATE INDEX IF NOT EXISTS idx_glosses_sense_id ON glosses(sense_id);
CREATE INDEX IF NOT EXISTS idx_examples_entry_id ON examples(entry_id);
CREATE INDEX IF NOT EXISTS idx_conjugations_entry_id ON conjugations(entry_id);
CREATE INDEX IF NOT EXISTS idx_word_relationships_entry_id ON word_relationships(entry_id);
CREATE INDEX IF NOT EXISTS frequency_rank_idx ON frequency_data(frequency);