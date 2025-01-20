class JapaneseConjugator:
    def __init__(self):
        # Verb group endings
        self.godan_endings = {
            'v5u': 'う',
            'v5k': 'く',
            'v5g': 'ぐ',
            'v5s': 'す',
            'v5t': 'つ',
            'v5n': 'ぬ',
            'v5b': 'ぶ',
            'v5m': 'む',
            'v5r': 'る'
        }
        
        # Mapping for godan verb stem changes
        self.godan_stem_map = {
            'う': {'a': 'わ', 'i': 'い', 'e': 'え', 'o': 'お'},
            'く': {'a': 'か', 'i': 'き', 'e': 'け', 'o': 'こ'},
            'ぐ': {'a': 'が', 'i': 'ぎ', 'e': 'げ', 'o': 'ご'},
            'す': {'a': 'さ', 'i': 'し', 'e': 'せ', 'o': 'そ'},
            'つ': {'a': 'た', 'i': 'ち', 'e': 'て', 'o': 'と'},
            'ぬ': {'a': 'な', 'i': 'に', 'e': 'ね', 'o': 'の'},
            'ぶ': {'a': 'ば', 'i': 'び', 'e': 'べ', 'o': 'ぼ'},
            'む': {'a': 'ま', 'i': 'み', 'e': 'め', 'o': 'も'},
            'る': {'a': 'ら', 'i': 'り', 'e': 'れ', 'o': 'ろ'}
        }

    def get_verb_stem(self, word, verb_type):
        """Get the stem of a verb based on its type."""
        if verb_type in self.godan_endings:
            return word[:-1]
        elif verb_type in ['v1', 'vk']:  # ichidan and kuru verbs
            return word[:-1]
        return word

    def conjugate_verb(self, word, verb_type):
        """Generate conjugations for a verb."""
        conjugations = {}
        
        # Get the basic stem
        stem = self.get_verb_stem(word, verb_type)
        
        if verb_type in self.godan_endings:  # Godan verbs
            ending = word[-1]
            stem_map = self.godan_stem_map[ending]
            
            conjugations.update({
                'present': word,
                'present_negative': stem + stem_map['a'] + 'ない',
                'past': stem + stem_map['i'] + 'た',
                'past_negative': stem + stem_map['a'] + 'なかった',
                'te_form': stem + stem_map['i'] + 'て',
                'potential': stem + stem_map['e'] + 'る',
                'passive': stem + stem_map['a'] + 'れる',
                'causative': stem + stem_map['a'] + 'せる',
                'imperative': stem + stem_map['e'],
                'volitional': stem + stem_map['o'] + 'う'
            })
            
        elif verb_type == 'v1':  # Ichidan verbs
            conjugations.update({
                'present': word,
                'present_negative': stem + 'ない',
                'past': stem + 'た',
                'past_negative': stem + 'なかった',
                'te_form': stem + 'て',
                'potential': stem + 'られる',
                'passive': stem + 'られる',
                'causative': stem + 'させる',
                'imperative': stem + 'ろ',
                'volitional': stem + 'よう'
            })
            
        elif verb_type == 'vk':  # Kuru verb (irregular)
            if word == '来る':
                conjugations.update({
                    'present': '来る',
                    'present_negative': '来ない',
                    'past': '来た',
                    'past_negative': '来なかった',
                    'te_form': '来て',
                    'potential': '来られる',
                    'passive': '来られる',
                    'causative': '来させる',
                    'imperative': '来い',
                    'volitional': '来よう'
                })

        return conjugations

    def conjugate_adjective(self, word, adj_type):
        """Generate conjugations for an adjective."""
        conjugations = {}
        
        if adj_type == 'adj-i':  # i-adjectives
            stem = word[:-1]  # Remove い
            conjugations.update({
                'present': word,
                'present_negative': stem + 'くない',
                'past': stem + 'かった',
                'past_negative': stem + 'くなかった',
                'te_form': stem + 'くて',
                'adverbial': stem + 'く'
            })
            
        elif adj_type == 'adj-na':  # na-adjectives
            conjugations.update({
                'present': word,
                'present_negative': word + 'ではない',
                'past': word + 'だった',
                'past_negative': word + 'ではなかった',
                'te_form': word + 'で',
                'adverbial': word + 'に'
            })
            
        return conjugations

def process_dictionary_entry(entry):
    """Process a dictionary entry and return conjugations if applicable."""
    conjugator = JapaneseConjugator()
    results = []
    
    # Get the word's basic form
    kanji = entry.get('kanji', [])
    kana = entry.get('kana', [])
    word_text = kanji[0]['text'] if kanji else kana[0]['text']
    
    # Collect all unique parts of speech across all senses
    all_pos = set()
    for sense in entry.get('sense', []):
        all_pos.update(sense.get('partOfSpeech', []))
    
    # Process unique verb types
    verb_types = {p for p in all_pos if p.startswith('v') and 
                 p in ['v5u', 'v5k', 'v5g', 'v5s', 'v5t', 'v5n', 'v5b', 'v5m', 'v5r', 'v1', 'vk']}
    
    # Process unique adjective types
    adj_types = {p for p in all_pos if p.startswith('adj') and 
                p in ['adj-i', 'adj-na']}
    
    # Generate conjugations for each unique type
    for verb_type in verb_types:
        conjugations = conjugator.conjugate_verb(word_text, verb_type)
        results.append({
            'word': word_text,
            'type': verb_type,
            'conjugations': conjugations
        })
            
    for adj_type in adj_types:
        conjugations = conjugator.conjugate_adjective(word_text, adj_type)
        results.append({
            'word': word_text,
            'type': adj_type,
            'conjugations': conjugations
        })
                
    return results

# Example usage
if __name__ == "__main__":
    import json
    
    # Read the JSON file
    with open('jmdict_with_examples.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Process all entries in the dictionary
    for entry in data['words']:
        results = process_dictionary_entry(entry)
        if results:  # Only print entries that have conjugations
            for result in results:
                print(f"\nWord: {result['word']}")
                print(f"Type: {result['type']}")
                print("Conjugations:")
                for form, conjugation in result['conjugations'].items():
                    print(f"  {form}: {conjugation}")
                print("-" * 40)