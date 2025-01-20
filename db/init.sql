-- Core Tables

-- Entries table: The main dictionary entry table
CREATE TABLE entries (
    id SERIAL PRIMARY KEY,
    ent_seq INTEGER UNIQUE NOT NULL,  -- Original JMdict sequence number
    frequency_rating INTEGER,         -- Overall frequency rating (can be calculated from priorities)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Kanji elements: Stores kanji forms of words
CREATE TABLE kanji_elements (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    kanji TEXT NOT NULL,             -- The kanji form
    priority_order SMALLINT,         -- Order of preferred kanji usage
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reading elements: Stores readings (pronunciation) of words
CREATE TABLE reading_elements (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    reading TEXT NOT NULL,           -- The reading in kana
    reading_type TEXT NOT NULL,      -- hiragana, katakana, or romaji
    no_kanji BOOLEAN DEFAULT FALSE,  -- True if this reading is not associated with kanji
    priority_order SMALLINT,         -- Order of preferred reading
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Parts of Speech: Reference table for word types
CREATE TABLE parts_of_speech (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,       -- Internal code (e.g., v5, adj-i)
    name TEXT NOT NULL,              -- Human readable name
    description TEXT NOT NULL,       -- Full description
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Subject Fields: Reference table for subject areas
CREATE TABLE subject_fields (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,       -- Internal code (e.g., comp, med)
    name TEXT NOT NULL,              -- Human readable name (e.g., Computing, Medicine)
    description TEXT NOT NULL,       -- Full description
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sense elements: Meanings and usage information
CREATE TABLE sense_elements (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    sense_order SMALLINT NOT NULL,   -- Order of definitions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Mapping between senses and parts of speech
CREATE TABLE sense_parts_of_speech (
    sense_id INTEGER REFERENCES sense_elements(id),
    part_of_speech_id INTEGER REFERENCES parts_of_speech(id),
    PRIMARY KEY (sense_id, part_of_speech_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Mapping between senses and subject fields
CREATE TABLE sense_subject_fields (
    sense_id INTEGER REFERENCES sense_elements(id),
    subject_field_id INTEGER REFERENCES subject_fields(id),
    PRIMARY KEY (sense_id, subject_field_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Definitions: Translations and meanings
CREATE TABLE definitions (
    id SERIAL PRIMARY KEY,
    sense_id INTEGER REFERENCES sense_elements(id),
    definition_text TEXT NOT NULL,    -- The actual definition/translation
    language TEXT DEFAULT 'eng',      -- Language code (e.g., eng, spa)
    definition_type TEXT,            -- Type (literal, figurative, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Usage information about words
CREATE TABLE usage_notes (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    note_type TEXT NOT NULL,         -- Type of note (archaic, irregular, etc.)
    note_text TEXT NOT NULL,         -- The actual note
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Example sentences
CREATE TABLE example_sentences (
    id SERIAL PRIMARY KEY,
    sense_id INTEGER REFERENCES sense_elements(id),
    japanese_text TEXT NOT NULL,     -- The Japanese sentence
    english_text TEXT NOT NULL,      -- English translation
    source TEXT,                     -- Source of the example
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- JLPT levels
CREATE TABLE jlpt_levels (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    level SMALLINT CHECK (level BETWEEN 1 AND 5),  -- N1-N5
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entry_id)
);

-- Word relationships (antonyms, synonyms, related terms)
CREATE TABLE word_relationships (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    related_entry_id INTEGER REFERENCES entries(id),
    relationship_type TEXT NOT NULL, -- antonym, synonym, related, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conjugations for verbs and adjectives
CREATE TABLE conjugations (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    conjugation_type TEXT NOT NULL,  -- te_form, past_positive, etc.
    form TEXT NOT NULL,             -- plain, polite, etc.
    kanji_form TEXT,                -- Conjugated form in kanji
    hiragana_reading TEXT NOT NULL, -- Conjugated form in hiragana
    katakana_reading TEXT NOT NULL, -- Conjugated form in katakana
    romaji_reading TEXT NOT NULL,   -- Conjugated form in romaji
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Word frequency/priority information
CREATE TABLE frequency_ratings (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES entries(id),
    rating_type TEXT NOT NULL,       -- news1/2, ichi1/2, spec1/2, etc.
    source TEXT NOT NULL,           -- Source of rating
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_kanji_elements_entry_id ON kanji_elements(entry_id);
CREATE INDEX idx_reading_elements_entry_id ON reading_elements(entry_id);
CREATE INDEX idx_sense_elements_entry_id ON sense_elements(entry_id);
CREATE INDEX idx_conjugations_entry_id ON conjugations(entry_id);
CREATE INDEX idx_definitions_sense_id ON definitions(sense_id);
CREATE INDEX idx_kanji_elements_kanji ON kanji_elements(kanji);
CREATE INDEX idx_reading_elements_reading ON reading_elements(reading);
CREATE INDEX idx_definitions_text ON definitions USING gin (to_tsvector('english', definition_text));