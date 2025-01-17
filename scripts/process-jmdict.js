import fs from 'fs';
import { XMLParser } from 'fast-xml-parser';
import { VerbDeconjugator } from 'jp-verb-deconjugator';
import path from 'path';

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
function determineWordType(posTags) {
  const posSet = new Set(posTags);
  
  if (posSet.has('v1') || posSet.has('v5') || posSet.has('vk') || posSet.has('vs')) {
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
  const deconjugator = new VerbDeconjugator();
  
  let wordInserts = [];
  let conjugationInserts = [];
  let exampleInserts = [];
  
  console.log('Processing entries...');
  
  dict.JMdict[0].entry.forEach((entry, index) => {
    try {
      // Get basic word information
      const kanji = entry.k_ele?.[0]?.keb?.[0] || null;
      const hiragana = entry.r_ele[0].reb[0];
      const pos = entry.sense?.[0]?.pos?.flat() || [];
      
      // Skip if no valid part of speech
      const wordType = determineWordType(pos);
      if (!wordType) return;
      
      // Determine JLPT level
      let jlptLevel = null;
      for (const level of ['N5', 'N4', 'N3', 'N2', 'N1']) {
        if (JLPT_WORDS[level].has(kanji || hiragana)) {
          jlptLevel = level;
          break;
        }
      }
      if (!jlptLevel) return; // Skip if not in JLPT lists
      
      // Get English meanings
      const meanings = entry.sense?.[0]?.gloss?.map(g => g._) || [];
      if (meanings.length === 0) return;
      
      // Get verb group if applicable
      const verbGroup = wordType === 'verb' ? determineVerbGroup(pos) : null;
      
      // Create word insert
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
          tags
        ) VALUES (
          ${kanji ? `'${escapeSQLString(kanji)}'` : 'NULL'},
          '${escapeSQLString(hiragana)}',
          '',
          '${wordType}'::word_type,
          ${verbGroup ? `'${verbGroup}'::verb_group` : 'NULL'},
          ${createPGArray(meanings)},
          '${jlptLevel}'::jlpt_level,
          ${index + 1},
          ARRAY['general']
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

processJMdict().catch(console.error);