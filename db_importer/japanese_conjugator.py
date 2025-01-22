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
        if verb_type in self.godan_endings or verb_type in ['v1', 'vk']:
            return word[:-1]
        return word

    def conjugate_verb(self, word_kanji, word_kana, verb_type):
        """Generate conjugations for a verb with both kanji and kana forms."""
        conjugations = {}
        
        # Get the basic stems
        stem_kanji = self.get_verb_stem(word_kanji, verb_type) if word_kanji else ""
        stem_kana = self.get_verb_stem(word_kana, verb_type)
        
        if verb_type in self.godan_endings:  # Godan verbs
            ending_kanji = word_kanji[-1] if word_kanji else ""
            ending_kana = word_kana[-1]
            stem_map = self.godan_stem_map[ending_kana]  # Use kana ending for mapping
            
            # Special conjugation rules for certain verb endings
            if ending_kana in ['む', 'ぶ', 'ぬ']:  # m, b, n-row verbs
                past_kanji = stem_kanji + 'んだ' if word_kanji else ""
                past_kana = stem_kana + 'んだ'
                te_kanji = stem_kanji + 'んで' if word_kanji else ""
                te_kana = stem_kana + 'んで'
            elif ending_kana in ['つ', 'る', 'う']:  # t, r, u-row verbs
                past_kanji = stem_kanji + 'った' if word_kanji else ""
                past_kana = stem_kana + 'った'
                te_kanji = stem_kanji + 'って' if word_kanji else ""
                te_kana = stem_kana + 'って'
            elif ending_kana == 'く':  # k-row verbs
                past_kanji = stem_kanji + 'いた' if word_kanji else ""
                past_kana = stem_kana + 'いた'
                te_kanji = stem_kanji + 'いて' if word_kanji else ""
                te_kana = stem_kana + 'いて'
            elif ending_kana == 'ぐ':  # g-row verbs
                past_kanji = stem_kanji + 'いだ' if word_kanji else ""
                past_kana = stem_kana + 'いだ'
                te_kanji = stem_kanji + 'いで' if word_kanji else ""
                te_kana = stem_kana + 'いで'
            else:
                past_kanji = stem_kanji + stem_map['i'] + 'た' if word_kanji else ""
                past_kana = stem_kana + stem_map['i'] + 'た'
                te_kanji = stem_kanji + stem_map['i'] + 'て' if word_kanji else ""
                te_kana = stem_kana + stem_map['i'] + 'て'
            
            conjugations.update({
                'present': {'kanji': word_kanji, 'kana': word_kana},
                'present_negative': {
                    'kanji': stem_kanji + stem_map['a'] + 'ない' if word_kanji else "",
                    'kana': stem_kana + stem_map['a'] + 'ない'
                },
                'past': {
                    'kanji': past_kanji,
                    'kana': past_kana
                },
                'past_negative': {
                    'kanji': stem_kanji + stem_map['a'] + 'なかった' if word_kanji else "",
                    'kana': stem_kana + stem_map['a'] + 'なかった'
                },
                'te_form': {
                    'kanji': te_kanji,
                    'kana': te_kana
                },
                'potential': {
                    'kanji': stem_kanji + stem_map['e'] + 'る' if word_kanji else "",
                    'kana': stem_kana + stem_map['e'] + 'る'
                },
                'passive': {
                    'kanji': stem_kanji + stem_map['a'] + 'れる' if word_kanji else "",
                    'kana': stem_kana + stem_map['a'] + 'れる'
                },
                'causative': {
                    'kanji': stem_kanji + stem_map['a'] + 'せる' if word_kanji else "",
                    'kana': stem_kana + stem_map['a'] + 'せる'
                },
                'imperative': {
                    'kanji': stem_kanji + stem_map['e'] if word_kanji else "",
                    'kana': stem_kana + stem_map['e']
                },
                'volitional': {
                    'kanji': stem_kanji + stem_map['o'] + 'う' if word_kanji else "",
                    'kana': stem_kana + stem_map['o'] + 'う'
                }
            })
            
        elif verb_type == 'v1':  # Ichidan verbs
            conjugations.update({
                'present': {'kanji': word_kanji, 'kana': word_kana},
                'present_negative': {
                    'kanji': stem_kanji + 'ない' if word_kanji else "",
                    'kana': stem_kana + 'ない'
                },
                'past': {
                    'kanji': stem_kanji + 'た' if word_kanji else "",
                    'kana': stem_kana + 'た'
                },
                'past_negative': {
                    'kanji': stem_kanji + 'なかった' if word_kanji else "",
                    'kana': stem_kana + 'なかった'
                },
                'te_form': {
                    'kanji': stem_kanji + 'て' if word_kanji else "",
                    'kana': stem_kana + 'て'
                },
                'potential': {
                    'kanji': stem_kanji + 'られる' if word_kanji else "",
                    'kana': stem_kana + 'られる'
                },
                'passive': {
                    'kanji': stem_kanji + 'られる' if word_kanji else "",
                    'kana': stem_kana + 'られる'
                },
                'causative': {
                    'kanji': stem_kanji + 'させる' if word_kanji else "",
                    'kana': stem_kana + 'させる'
                },
                'imperative': {
                    'kanji': stem_kanji + 'ろ' if word_kanji else "",
                    'kana': stem_kana + 'ろ'
                },
                'volitional': {
                    'kanji': stem_kanji + 'よう' if word_kanji else "",
                    'kana': stem_kana + 'よう'
                }
            })
            
        elif verb_type == 'vk':  # Kuru verb (irregular)
            if word_kana == 'くる':
                conjugations.update({
                    'present': {'kanji': '来る', 'kana': 'くる'},
                    'present_negative': {'kanji': '来ない', 'kana': 'こない'},
                    'past': {'kanji': '来た', 'kana': 'きた'},
                    'past_negative': {'kanji': '来なかった', 'kana': 'こなかった'},
                    'te_form': {'kanji': '来て', 'kana': 'きて'},
                    'potential': {'kanji': '来られる', 'kana': 'こられる'},
                    'passive': {'kanji': '来られる', 'kana': 'こられる'},
                    'causative': {'kanji': '来させる', 'kana': 'こさせる'},
                    'imperative': {'kanji': '来い', 'kana': 'こい'},
                    'volitional': {'kanji': '来よう', 'kana': 'こよう'}
                })

        return conjugations

    def conjugate_adjective(self, word_kanji, word_kana, adj_type):
        """Generate conjugations for an adjective with both kanji and kana forms."""
        conjugations = {}
        
        if adj_type == 'adj-i':  # i-adjectives
            stem_kanji = word_kanji[:-1] if word_kanji else ""  # Remove い
            stem_kana = word_kana[:-1]  # Remove い
            
            conjugations.update({
                'present': {'kanji': word_kanji, 'kana': word_kana},
                'present_negative': {
                    'kanji': stem_kanji + 'くない' if word_kanji else "",
                    'kana': stem_kana + 'くない'
                },
                'past': {
                    'kanji': stem_kanji + 'かった' if word_kanji else "",
                    'kana': stem_kana + 'かった'
                },
                'past_negative': {
                    'kanji': stem_kanji + 'くなかった' if word_kanji else "",
                    'kana': stem_kana + 'くなかった'
                },
                'te_form': {
                    'kanji': stem_kanji + 'くて' if word_kanji else "",
                    'kana': stem_kana + 'くて'
                },
                'adverbial': {
                    'kanji': stem_kanji + 'く' if word_kanji else "",
                    'kana': stem_kana + 'く'
                }
            })
            
        elif adj_type == 'adj-na':  # na-adjectives
            conjugations.update({
                'present': {'kanji': word_kanji, 'kana': word_kana},
                'present_negative': {
                    'kanji': word_kanji + 'じゃない' if word_kanji else "",
                    'kana': word_kana + 'じゃない'
                },
                'past': {
                    'kanji': word_kanji + 'だった' if word_kanji else "",
                    'kana': word_kana + 'だった'
                },
                'past_negative': {
                    'kanji': word_kanji + 'じゃなかった' if word_kanji else "",
                    'kana': word_kana + 'じゃなかった'
                },
                'te_form': {
                    'kanji': word_kanji + 'で' if word_kanji else "",
                    'kana': word_kana + 'で'
                },
                'adverbial': {
                    'kanji': word_kanji + 'に' if word_kanji else "",
                    'kana': word_kana + 'に'
                }
            })
            
        return conjugations

def process_dictionary_entry(entry):
    """Process a dictionary entry and return conjugations if applicable."""
    conjugator = JapaneseConjugator()
    results = []
    
    # Get both kanji and kana forms
    kanji = entry.get('kanji', [])
    kana = entry.get('kana', [])
    word_kanji = kanji[0]['text'] if kanji else ""
    word_kana = kana[0]['text'] if kana else ""
    
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
        conjugations = conjugator.conjugate_verb(word_kanji, word_kana, verb_type)
        results.append({
            'word': {'kanji': word_kanji, 'kana': word_kana},
            'type': verb_type,
            'conjugations': conjugations
        })
            
    for adj_type in adj_types:
        conjugations = conjugator.conjugate_adjective(word_kanji, word_kana, adj_type)
        results.append({
            'word': {'kanji': word_kanji, 'kana': word_kana},
            'type': adj_type,
            'conjugations': conjugations
        })
                
    return results

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
                print(f"\nWord: {result['word']['kanji']} ({result['word']['kana']})")
                print(f"Type: {result['type']}")
                print("Conjugations:")
                for form, conj in result['conjugations'].items():
                    if conj['kanji']:
                        print(f"  {form}: {conj['kanji']} ({conj['kana']})")
                    else:
                        print(f"  {form}: {conj['kana']}")
                print("-" * 40)