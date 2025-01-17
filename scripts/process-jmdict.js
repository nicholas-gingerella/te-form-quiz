import fs from 'fs';
import { XMLParser } from 'fast-xml-parser';
import deconjugator from 'jp-verb-deconjugator';
import path from 'path';

function safeGetReading(entry) {
    if (!entry.r_ele) return null;
    
    // Handle both array and single object cases
    const rEle = Array.isArray(entry.r_ele) ? entry.r_ele[0] : entry.r_ele;
    if (!rEle || !rEle.reb) return null;
    
    // Get full reading, not just first character
    return Array.isArray(rEle.reb) ? rEle.reb[0] : rEle.reb;
  }
  
  function safeGetKanji(entry) {
    if (!entry.k_ele) return null;
    
    // Handle both array and single object cases
    const kEle = Array.isArray(entry.k_ele) ? entry.k_ele[0] : entry.k_ele;
    if (!kEle || !kEle.keb) return null;
    
    // Get full kanji, not just first character
    return Array.isArray(kEle.keb) ? kEle.keb[0] : kEle.keb;
  }
  
  function safeGetPos(entry) {
    if (!entry.sense) return [];
    
    // Handle both array and single object cases
    const sense = Array.isArray(entry.sense) ? entry.sense[0] : entry.sense;
    if (!sense || !sense.pos) return [];
    
    // Handle both array and single string cases
    return Array.isArray(sense.pos) ? sense.pos : [sense.pos];
  }
  
  function safeGetMeanings(entry) {
    if (!entry.sense) return [];
    
    // Handle both array and single object cases
    const sense = Array.isArray(entry.sense) ? entry.sense[0] : entry.sense;
    if (!sense || !sense.gloss) return [];
    
    // Handle both array and single string cases for gloss
    const glosses = Array.isArray(sense.gloss) ? sense.gloss : [sense.gloss];
    
    // If gloss has underscore property, use that, otherwise use the string directly
    return glosses.map(g => g._ || g);
  }
  

// JLPT word lists should be loaded from external files
// This is a simplified example
const JLPT_WORDS = {
  N5: new Set(['食べる', '行く', '来る']),
  N4: new Set(['走る', '泳ぐ', '笑う']),
  N3: new Set(['認める', '続く', '決める']),
  N2: new Set(['従う', '背く', '断る']),
  N1: new Set(['憂える', '潜む', '黙る'])
};

// Helper function to determine word type from JMdict POS tags
function determineWordType(posTags, hiragana) {
    const posSet = new Set(posTags);
    
    // Check if it's a katakana word first
    if (isKatakana(hiragana)) {
      return 'loan_word';
    }
    
    // Then check other types
    if (posSet.has('v1') || posSet.has('v5') || posSet.has('vk')) {
      return 'verb';
    }
    if (posSet.has('adj-i')) {
      return 'i-adjective';
    }
    if (posSet.has('adj-na')) {
      return 'na-adjective';
    }
    if (posSet.has('n')) {
      return 'noun';
    }
    if (posSet.has('adv')) {
      return 'adverb';
    }
    if (posSet.has('prt')) {
      return 'particle';
    }
    
    return null;
  }
  

// Helper function to determine verb group
function determineVerbGroup(posTags) {
  const posSet = new Set(posTags);
  
  if (posSet.has('v1')) {
    return 'ru';
  }
  if (posSet.has('v5')) {
    return 'u';
  }
  if (posSet.has('vk')) {
    return 'irregular';
  }
  return null;
}

// Helper function to escape SQL strings
function escapeSQLString(str) {
  if (!str) return '';
  return str.replace(/'/g, "''");
}

// Helper function to create array literal for Postgres
function createPGArray(arr) {
  if (!Array.isArray(arr)) {
    arr = [arr];
  }
  return `ARRAY[${arr.map(item => `'${escapeSQLString(item)}'`).join(', ')}]`;
}

// Helper function to generate conjugations
function generateConjugations(deconjugationResult, verbGroup) {
  // This is where you'd implement detailed conjugation rules
  // For now, returning a basic structure
  return {
    'non_past': {
      'plain': {
        'positive': deconjugationResult.derivationHistory[0],
        'negative': deconjugationResult.derivationHistory[0] + 'ない'
      },
      'polite': {
        'positive': deconjugationResult.derivationHistory[0] + 'ます',
        'negative': deconjugationResult.derivationHistory[0] + 'ません'
      }
    }
    // Add more conjugation forms as needed
  };
}

function getWordTags(entry, hiragana, kanji) {
    const tags = ['general'];
    
    // Check if it's a loan word (katakana only)
    if (isKatakana(hiragana) && (!kanji || kanji === hiragana)) {
      tags.push('loan_word');
    }
  
    // Add word origin if available
    const originLang = entry.sense?.[0]?.lsource?.[0]?.lang;
    if (originLang) {
      tags.push(`origin:${originLang}`);
    }
  
    // Add field of use tags if available
    const field = entry.sense?.[0]?.field;
    if (field) {
      const fields = Array.isArray(field) ? field : [field];
      fields.forEach(f => tags.push(`field:${f}`));
    }
  
    return tags;
  }

  function isKatakana(text) {
    return /^[ァ-ンー]+$/.test(text);
  }
  
  function shouldSkipEntry(entry, kanji, hiragana, pos) {
    // Skip entries with no readings
    if (!hiragana) return true;
  
    // Skip entries with no part of speech
    if (!pos || pos.length === 0) return true;
  
    // Create sets for easier checking
    const posSet = new Set(pos);
    
    // Skip if entry contains any of these parts of speech
    const skipPos = new Set([
      'webpage',
      'unclassified',
      'symbol',
      'punctuation',
      'suffix',
      'prefix',
      'aux',
      'aux-v',
      'aux-adj'
    ]);
  
    if ([...posSet].some(p => [...skipPos].some(skip => p.includes(skip)))) {
      return true;
    }
  
    // Skip entries that are just symbols, numbers, or punctuation
    const symbolRegex = /^[０-９Ａ-Ｚａ-ｚ〇♪☆×※＊○●◎〒→×]*$/;
    if (kanji && symbolRegex.test(kanji)) return true;
  
    // Skip entries that are primarily proper nouns
    if (posSet.has('proper noun')) return true;
  
    // Skip very long compounds (likely not common vocabulary)
    if (hiragana.length > 15) return true;
  
    return false;
  }

  async function processJMdict() {
    console.log('Reading JMdict file...');
    const xmlData = fs.readFileSync(path.join(process.cwd(), 'public', 'JMdict_e'), 'utf8');
    
    console.log('Parsing XML...');
    const parser = new XMLParser({
      ignoreAttributes: false,
      parseAttributeValue: true,
      arrayMode: true
    });
    
    const dict = parser.parse(xmlData);

    // Debug the initial structure
  console.log('Top level keys:', Object.keys(dict));
  console.log('JMdict type:', typeof dict.JMdict);
  
  // Let's look at the first few entries in detail
  if (dict.JMdict?.entry) {
    console.log('First entry raw structure:', JSON.stringify(dict.JMdict.entry[0], null, 2));
  }

  const entries = dict.JMdict?.entry || [];
  console.log('Number of entries found:', entries.length);

  if (entries.length === 0) {
    console.error('No entries found in the XML file');
    return;
  }

  let wordInserts = [];
  let conjugationInserts = [];
  let exampleInserts = [];

  entries.forEach((entry, index) => {
    try {
      const hiragana = safeGetReading(entry);
      const kanji = safeGetKanji(entry);
      const pos = safeGetPos(entry);
      const meanings = safeGetMeanings(entry);

      // Check if we should skip this entry
      if (shouldSkipEntry(entry, kanji, hiragana, pos)) {
        return;
      }

      const wordType = determineWordType(pos);
      if (!wordType) {
        return;
      }

      // Get tags for the word
      const tags = getWordTags(entry, hiragana, kanji);

      // Only show debug output for entries we're actually going to process
      console.log(`\nProcessing entry ${index}:`);
      console.log('Full hiragana:', hiragana);
      console.log('Full kanji:', kanji);
      console.log('Part of speech tags:', pos);
      console.log('Meanings:', meanings);
      console.log('Word type:', wordType);
      console.log('Tags:', tags);

      // Create word insert with tags
      const wordInsert = `
      INSERT INTO words (
        kanji,
        hiragana,
        romaji,
        type,
        group_type,
        english,
        jlpt_level,
        commonness,
        tags,
        origin_language
      ) VALUES (
        ${kanji ? `'${escapeSQLString(kanji)}'` : 'NULL'},
        '${escapeSQLString(hiragana)}',
        '',
        '${determineWordType(pos, hiragana)}'::word_type,
        ${verbGroup ? `'${verbGroup}'::verb_group` : 'NULL'},
        ${createPGArray(meanings)},
        '${jlptLevel}'::jlpt_level,
        ${index + 1},
        ${createPGArray(tags)},
        ${entry.sense?.[0]?.lsource?.[0]?.lang ? `'${entry.sense[0].lsource[0].lang}'` : 'NULL'}
      ) RETURNING id;
    `;
      
      wordInserts.push(wordInsert);
      
      // Generate conjugations for verbs
      if (wordType === 'verb') {
        const deconjugationResults = deconjugator.deconjugate(hiragana);
        if (deconjugationResults.length > 0) {
          const conjugations = generateConjugations(deconjugationResults[0], verbGroup);
          Object.entries(conjugations).forEach(([formType, styles]) => {
            Object.entries(styles).forEach(([style, polarities]) => {
              Object.entries(polarities).forEach(([polarity, form]) => {
                const conjugationInsert = `
                  INSERT INTO conjugations (
                    word_id,
                    form_type,
                    form_style,
                    polarity,
                    conjugated_form
                  ) SELECT id, '${formType}', '${style}', '${polarity}', '${escapeSQLString(form)}'
                  FROM words WHERE kanji ${kanji ? `= '${escapeSQLString(kanji)}'` : 'IS NULL'}
                  AND hiragana = '${escapeSQLString(hiragana)}';
                `;
                conjugationInserts.push(conjugationInsert);
              });
            });
          });
        }
      }
      
      // Add example sentences if available
      entry.sense?.[0]?.example?.forEach(example => {
        if (example.text && example.translation) {
          const exampleInsert = `
            INSERT INTO example_sentences (
              word_id,
              japanese,
              hiragana,
              english
            ) SELECT id, '${escapeSQLString(example.text)}',
              '${escapeSQLString(example.text)}',
              '${escapeSQLString(example.translation)}'
            FROM words WHERE kanji ${kanji ? `= '${escapeSQLString(kanji)}'` : 'IS NULL'}
            AND hiragana = '${escapeSQLString(hiragana)}';
          `;
          exampleInserts.push(exampleInsert);
        }
      });
      
    } catch (error) {
      console.error(`Error processing entry:`, error);
    }
  });
  
  // Write SQL file
  const sqlContent = [
    '-- Insert words',
    ...wordInserts,
    '',
    '-- Insert conjugations',
    ...conjugationInserts,
    '',
    '-- Insert examples',
    ...exampleInserts
  ].join('\n');
  
  fs.writeFileSync(path.join(process.cwd(), 'db', '02-populate.sql'), sqlContent);
  console.log('SQL file generated successfully!');
}

processJMdict().catch(console.error);