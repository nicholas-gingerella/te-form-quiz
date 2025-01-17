import { XMLParser } from 'fast-xml-parser';
import { VerbDeconjugator } from 'jp-verb-deconjugator';

export async function loadDictionary() {
  try {
    // Fetch the XML file from the public directory
    const response = await fetch('/JMdict_e');
    const xmlData = await response.text();

    // Parse XML
    const parser = new XMLParser({
      ignoreAttributes: false,
      parseAttributeValue: true,
    });

    const dict = parser.parse(xmlData);
    const deconjugator = new VerbDeconjugator();

    // Filter for verbs and adjectives
    const words = dict.JMdict.entry.filter(entry => {
      const pos = Array.isArray(entry.sense?.pos) ? entry.sense.pos : [entry.sense?.pos];
      return pos?.some(p => p?.includes('v') || p?.includes('adj'));
    });

    // Process only the first 50 entries for testing
    const processedWords = words.slice(0, 50).map(entry => {
      const reading = Array.isArray(entry.r_ele) ? entry.r_ele[0].reb : entry.r_ele.reb;
      let conjugationInfo = null;

      // Check if it's a verb
      const pos = Array.isArray(entry.sense.pos) ? entry.sense.pos : [entry.sense.pos];
      const isVerb = pos.some(p => p?.includes('v'));

      if (isVerb) {
        const deconjugationResults = deconjugator.deconjugate(reading);
        if (deconjugationResults.length > 0) {
          conjugationInfo = {
            root: deconjugationResults[0].derivationHistory[0],
            type: deconjugationResults[0].verbType
          };
        }
      }

      return {
        kanji: Array.isArray(entry.k_ele) ? entry.k_ele[0]?.keb : entry.k_ele?.keb || reading,
        reading: reading,
        type: isVerb ? 'verb' : 'adjective',
        meaning: Array.isArray(entry.sense.gloss) ? entry.sense.gloss[0] : entry.sense.gloss,
        pos: pos,
        conjugations: conjugationInfo
      };
    });

    console.log('Processed first 50 entries:', processedWords);
    return processedWords;
  } catch (error) {
    console.error('Error loading dictionary:', error);
    throw error;
  }
}