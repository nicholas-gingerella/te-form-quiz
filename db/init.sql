-- Create enum for JLPT levels
CREATE TYPE jlpt_level AS ENUM ('N5', 'N4', 'N3', 'N2', 'N1');

-- Create enum for word types
CREATE TYPE word_type AS ENUM ('verb', 'i-adjective', 'na-adjective', 'noun', 'adverb', 'particle');

-- Create enum for verb groups
CREATE TYPE verb_group AS ENUM ('ru', 'u', 'irregular');

-- Words table
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    kanji TEXT,  -- Nullable because some words are kana-only
    hiragana TEXT NOT NULL,
    romaji TEXT NOT NULL,
    type word_type NOT NULL,
    group_type verb_group,  -- Only for verbs
    english TEXT[] NOT NULL,  -- Array of possible meanings
    jlpt_level jlpt_level NOT NULL,
    commonness INTEGER,  -- Lower number = more common
    examples TEXT[],  -- Array of example sentences
    tags TEXT[],  -- Array of tags (e.g., 'daily-life', 'business', 'formal')
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conjugations table for verbs and adjectives
CREATE TABLE conjugations (
    id SERIAL PRIMARY KEY,
    word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
    form_type TEXT NOT NULL CHECK (
        form_type IN (
            'non_past',
            'past',
            'te',
            'tai',
            'conditional',
            'potential',
            'passive',
            'causative',
            'imperative',
            'volitional'
        )
    ),
    form_style TEXT NOT NULL CHECK (
        form_style IN (
            'plain',
            'polite',
            'humble',
            'honorific'
        )
    ),
    polarity TEXT NOT NULL CHECK (polarity IN ('positive', 'negative')),
    conjugated_form TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Example sentences table
CREATE TABLE example_sentences (
    id SERIAL PRIMARY KEY,
    word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
    japanese TEXT NOT NULL,
    hiragana TEXT NOT NULL,
    english TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Word relationships table (for related words, antonyms, etc.)
CREATE TABLE word_relationships (
    id SERIAL PRIMARY KEY,
    word_id1 INTEGER REFERENCES words(id) ON DELETE CASCADE,
    word_id2 INTEGER REFERENCES words(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL CHECK (
        relationship_type IN (
            'synonym',
            'antonym',
            'related',
            'similar_meaning',
            'similar_pronunciation'
        )
    ),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(word_id1, word_id2, relationship_type)
);

-- Create indexes
CREATE INDEX idx_words_jlpt ON words(jlpt_level);
CREATE INDEX idx_words_type ON words(type);
CREATE INDEX idx_words_commonness ON words(commonness);
CREATE INDEX idx_conjugations_word_id ON conjugations(word_id);
CREATE INDEX idx_examples_word_id ON example_sentences(word_id);
CREATE INDEX idx_word_relationships_word_id1 ON word_relationships(word_id1);
CREATE INDEX idx_word_relationships_word_id2 ON word_relationships(word_id2);

-- Create GIN indexes for array fields and text search
CREATE INDEX idx_words_tags ON words USING gin(tags);
CREATE INDEX idx_words_english ON words USING gin(english);

-- Create function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_words_updated_at
    BEFORE UPDATE ON words
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conjugations_updated_at
    BEFORE UPDATE ON conjugations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_examples_updated_at
    BEFORE UPDATE ON example_sentences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();