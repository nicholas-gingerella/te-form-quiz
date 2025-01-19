-- Core entry table
CREATE TABLE entries (
    id SERIAL PRIMARY KEY,
    ent_seq INTEGER UNIQUE NOT NULL,  -- Original JMDict sequence number
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Kanji elements table
CREATE TABLE kanji_elements (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    kanji TEXT NOT NULL,  -- The actual kanji/word (keb in XML)
    priority_order SMALLINT,  -- For ordering multiple kanji elements
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Kanji element metadata
CREATE TABLE kanji_metadata (
    id SERIAL PRIMARY KEY,
    kanji_element_id INTEGER REFERENCES kanji_elements(id),
    info_type TEXT NOT NULL,  -- ke_inf values like ateji, irregular usage, etc.
    priority TEXT,  -- ke_pri values like news1, ichi1, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reading elements table
CREATE TABLE reading_elements (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    reading TEXT NOT NULL,  -- The reading in kana (reb in XML)
    reading_type TEXT NOT NULL,  -- 'hiragana', 'katakana', or 'romaji'
    no_kanji BOOLEAN DEFAULT FALSE,  -- true if re_nokanji exists
    priority_order SMALLINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reading restrictions (links readings to specific kanji)
CREATE TABLE reading_restrictions (
    id SERIAL PRIMARY KEY,
    reading_element_id INTEGER REFERENCES reading_elements(id),
    kanji_element_id INTEGER REFERENCES kanji_elements(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reading element metadata
CREATE TABLE reading_metadata (
    id SERIAL PRIMARY KEY,
    reading_element_id INTEGER REFERENCES reading_elements(id),
    info_type TEXT NOT NULL,  -- re_inf values
    priority TEXT,  -- re_pri values
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Parts of speech table
CREATE TABLE pos (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,  -- The entity code like 'adj-i', 'v5u', etc.
    description TEXT NOT NULL,  -- Full description
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Fields (domains) table
CREATE TABLE fields (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,  -- The entity code like 'math', 'med', etc.
    description TEXT NOT NULL,  -- Full description
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sense elements table (meanings/definitions)
CREATE TABLE sense_elements (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    sense_order SMALLINT NOT NULL,  -- Order within the entry
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sense parts of speech (links sense to applicable parts of speech)
CREATE TABLE sense_pos (
    sense_id INTEGER REFERENCES sense_elements(id),
    pos_id INTEGER REFERENCES pos(id),
    PRIMARY KEY (sense_id, pos_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sense fields (links sense to applicable fields/domains)
CREATE TABLE sense_fields (
    sense_id INTEGER REFERENCES sense_elements(id),
    field_id INTEGER REFERENCES fields(id),
    PRIMARY KEY (sense_id, field_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Glosses (translations/definitions)
CREATE TABLE glosses (
    id SERIAL PRIMARY KEY,
    sense_id INTEGER REFERENCES sense_elements(id),
    gloss_text TEXT NOT NULL,
    lang TEXT DEFAULT 'eng',  -- ISO 639-2 language code
    gloss_type TEXT,  -- g_type values like 'lit', 'fig', 'expl'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Examples
CREATE TABLE examples (
    id SERIAL PRIMARY KEY,
    sense_id INTEGER REFERENCES sense_elements(id),
    source TEXT,  -- ex_srce
    japanese_text TEXT NOT NULL,  -- ex_text
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE example_sentences (
    id SERIAL PRIMARY KEY,
    example_id INTEGER REFERENCES examples(id),
    sentence TEXT NOT NULL,
    lang TEXT DEFAULT 'eng',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- JLPT levels (to be populated separately)
CREATE TABLE jlpt_levels (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    level SMALLINT CHECK (level BETWEEN 1 AND 5),  -- N1-N5
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entry_id)
);

-- For verb/adjective conjugations
CREATE TABLE conjugation_rules (
    id SERIAL PRIMARY KEY,
    pos_id INTEGER REFERENCES pos(id),
    rule_type TEXT NOT NULL,  -- e.g., 'present_positive', 'past_negative', etc.
    rule_pattern TEXT NOT NULL,  -- The actual conjugation pattern
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Storing pre-computed conjugations for faster lookup
CREATE TABLE conjugations (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    conjugation_rule_id INTEGER REFERENCES conjugation_rules(id),
    conjugated_form TEXT NOT NULL,
    reading TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_kanji_elements_entry_id ON kanji_elements(entry_id);
CREATE INDEX idx_reading_elements_entry_id ON reading_elements(entry_id);
CREATE INDEX idx_sense_elements_entry_id ON sense_elements(entry_id);
CREATE INDEX idx_conjugations_entry_id ON conjugations(entry_id);
CREATE INDEX idx_glosses_sense_id ON glosses(sense_id);
CREATE INDEX idx_kanji_elements_kanji ON kanji_elements(kanji);
CREATE INDEX idx_reading_elements_reading ON reading_elements(reading);
CREATE INDEX idx_glosses_text ON glosses USING gin (to_tsvector('english', gloss_text));