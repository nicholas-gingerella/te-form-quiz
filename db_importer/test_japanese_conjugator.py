import unittest
from japanese_conjugator import JapaneseConjugator, process_dictionary_entry

class TestJapaneseConjugator(unittest.TestCase):
    def setUp(self):
        self.conjugator = JapaneseConjugator()
        
    def verify_all_conjugations(self, test_entry, expected_conjugations):
        """Helper method to verify all conjugation patterns"""
        results = process_dictionary_entry(test_entry)
        self.assertTrue(results, "No conjugations were generated")
        conjugations = results[0]['conjugations']
        
        for form, expected in expected_conjugations.items():
            self.assertEqual(conjugations[form]['kanji'], expected['kanji'],
                           f"Incorrect kanji conjugation for {form}")
            self.assertEqual(conjugations[form]['kana'], expected['kana'],
                           f"Incorrect kana conjugation for {form}")

    def test_godan_u_verb(self):
        # Test う verb (買う - to buy)
        kau_test = {
            'kanji': [{'text': '買う'}],
            'kana': [{'text': 'かう'}],
            'sense': [{'partOfSpeech': ['v5u']}]
        }
        expected = {
            'present': {'kanji': '買う', 'kana': 'かう'},
            'present_negative': {'kanji': '買わない', 'kana': 'かわない'},
            'past': {'kanji': '買った', 'kana': 'かった'},
            'past_negative': {'kanji': '買わなかった', 'kana': 'かわなかった'},
            'te_form': {'kanji': '買って', 'kana': 'かって'},
            'potential': {'kanji': '買える', 'kana': 'かえる'},
            'passive': {'kanji': '買われる', 'kana': 'かわれる'},
            'causative': {'kanji': '買わせる', 'kana': 'かわせる'},
            'imperative': {'kanji': '買え', 'kana': 'かえ'},
            'volitional': {'kanji': '買おう', 'kana': 'かおう'}
        }
        self.verify_all_conjugations(kau_test, expected)

    def test_godan_mu_verb(self):
        # Test む verb (飲む - to drink)
        nomu_test = {
            'kanji': [{'text': '飲む'}],
            'kana': [{'text': 'のむ'}],
            'sense': [{'partOfSpeech': ['v5m']}]
        }
        expected = {
            'present': {'kanji': '飲む', 'kana': 'のむ'},
            'present_negative': {'kanji': '飲まない', 'kana': 'のまない'},
            'past': {'kanji': '飲んだ', 'kana': 'のんだ'},
            'past_negative': {'kanji': '飲まなかった', 'kana': 'のまなかった'},
            'te_form': {'kanji': '飲んで', 'kana': 'のんで'},
            'potential': {'kanji': '飲める', 'kana': 'のめる'},
            'passive': {'kanji': '飲まれる', 'kana': 'のまれる'},
            'causative': {'kanji': '飲ませる', 'kana': 'のませる'},
            'imperative': {'kanji': '飲め', 'kana': 'のめ'},
            'volitional': {'kanji': '飲もう', 'kana': 'のもう'}
        }
        self.verify_all_conjugations(nomu_test, expected)

    def test_godan_ru_verb(self):
        # Test る verb (乗る - to ride)
        noru_test = {
            'kanji': [{'text': '乗る'}],
            'kana': [{'text': 'のる'}],
            'sense': [{'partOfSpeech': ['v5r']}]
        }
        expected = {
            'present': {'kanji': '乗る', 'kana': 'のる'},
            'present_negative': {'kanji': '乗らない', 'kana': 'のらない'},
            'past': {'kanji': '乗った', 'kana': 'のった'},
            'past_negative': {'kanji': '乗らなかった', 'kana': 'のらなかった'},
            'te_form': {'kanji': '乗って', 'kana': 'のって'},
            'potential': {'kanji': '乗れる', 'kana': 'のれる'},
            'passive': {'kanji': '乗られる', 'kana': 'のられる'},
            'causative': {'kanji': '乗らせる', 'kana': 'のらせる'},
            'imperative': {'kanji': '乗れ', 'kana': 'のれ'},
            'volitional': {'kanji': '乗ろう', 'kana': 'のろう'}
        }
        self.verify_all_conjugations(noru_test, expected)

    def test_godan_tsu_verb(self):
        # Test つ verb (立つ - to stand)
        tatsu_test = {
            'kanji': [{'text': '立つ'}],
            'kana': [{'text': 'たつ'}],
            'sense': [{'partOfSpeech': ['v5t']}]
        }
        expected = {
            'present': {'kanji': '立つ', 'kana': 'たつ'},
            'present_negative': {'kanji': '立たない', 'kana': 'たたない'},
            'past': {'kanji': '立った', 'kana': 'たった'},
            'past_negative': {'kanji': '立たなかった', 'kana': 'たたなかった'},
            'te_form': {'kanji': '立って', 'kana': 'たって'},
            'potential': {'kanji': '立てる', 'kana': 'たてる'},
            'passive': {'kanji': '立たれる', 'kana': 'たたれる'},
            'causative': {'kanji': '立たせる', 'kana': 'たたせる'},
            'imperative': {'kanji': '立て', 'kana': 'たて'},
            'volitional': {'kanji': '立とう', 'kana': 'たとう'}
        }
        self.verify_all_conjugations(tatsu_test, expected)

    def test_godan_ku_verb(self):
        # Test く verb (書く - to write)
        kaku_test = {
            'kanji': [{'text': '書く'}],
            'kana': [{'text': 'かく'}],
            'sense': [{'partOfSpeech': ['v5k']}]
        }
        expected = {
            'present': {'kanji': '書く', 'kana': 'かく'},
            'present_negative': {'kanji': '書かない', 'kana': 'かかない'},
            'past': {'kanji': '書いた', 'kana': 'かいた'},
            'past_negative': {'kanji': '書かなかった', 'kana': 'かかなかった'},
            'te_form': {'kanji': '書いて', 'kana': 'かいて'},
            'potential': {'kanji': '書ける', 'kana': 'かける'},
            'passive': {'kanji': '書かれる', 'kana': 'かかれる'},
            'causative': {'kanji': '書かせる', 'kana': 'かかせる'},
            'imperative': {'kanji': '書け', 'kana': 'かけ'},
            'volitional': {'kanji': '書こう', 'kana': 'かこう'}
        }
        self.verify_all_conjugations(kaku_test, expected)

    def test_godan_gu_verb(self):
        # Test ぐ verb (泳ぐ - to swim)
        oyogu_test = {
            'kanji': [{'text': '泳ぐ'}],
            'kana': [{'text': 'およぐ'}],
            'sense': [{'partOfSpeech': ['v5g']}]
        }
        expected = {
            'present': {'kanji': '泳ぐ', 'kana': 'およぐ'},
            'present_negative': {'kanji': '泳がない', 'kana': 'およがない'},
            'past': {'kanji': '泳いだ', 'kana': 'およいだ'},
            'past_negative': {'kanji': '泳がなかった', 'kana': 'およがなかった'},
            'te_form': {'kanji': '泳いで', 'kana': 'およいで'},
            'potential': {'kanji': '泳げる', 'kana': 'およげる'},
            'passive': {'kanji': '泳がれる', 'kana': 'およがれる'},
            'causative': {'kanji': '泳がせる', 'kana': 'およがせる'},
            'imperative': {'kanji': '泳げ', 'kana': 'およげ'},
            'volitional': {'kanji': '泳ごう', 'kana': 'およごう'}
        }
        self.verify_all_conjugations(oyogu_test, expected)

    def test_ichidan_verb(self):
        # Test る verb (食べる - to eat)
        taberu_test = {
            'kanji': [{'text': '食べる'}],
            'kana': [{'text': 'たべる'}],
            'sense': [{'partOfSpeech': ['v1']}]
        }
        expected = {
            'present': {'kanji': '食べる', 'kana': 'たべる'},
            'present_negative': {'kanji': '食べない', 'kana': 'たべない'},
            'past': {'kanji': '食べた', 'kana': 'たべた'},
            'past_negative': {'kanji': '食べなかった', 'kana': 'たべなかった'},
            'te_form': {'kanji': '食べて', 'kana': 'たべて'},
            'potential': {'kanji': '食べられる', 'kana': 'たべられる'},
            'passive': {'kanji': '食べられる', 'kana': 'たべられる'},
            'causative': {'kanji': '食べさせる', 'kana': 'たべさせる'},
            'imperative': {'kanji': '食べろ', 'kana': 'たべろ'},
            'volitional': {'kanji': '食べよう', 'kana': 'たべよう'}
        }
        self.verify_all_conjugations(taberu_test, expected)

    def test_kuru_verb(self):
        # Test irregular verb (来る - to come)
        kuru_test = {
            'kanji': [{'text': '来る'}],
            'kana': [{'text': 'くる'}],
            'sense': [{'partOfSpeech': ['vk']}]
        }
        expected = {
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
        }
        self.verify_all_conjugations(kuru_test, expected)

    def test_i_adjective(self):
        # Test い adjective (大きい - big)
        ookii_test = {
            'kanji': [{'text': '大きい'}],
            'kana': [{'text': 'おおきい'}],
            'sense': [{'partOfSpeech': ['adj-i']}]
        }
        expected = {
            'present': {'kanji': '大きい', 'kana': 'おおきい'},
            'present_negative': {'kanji': '大きくない', 'kana': 'おおきくない'},
            'past': {'kanji': '大きかった', 'kana': 'おおきかった'},
            'past_negative': {'kanji': '大きくなかった', 'kana': 'おおきくなかった'},
            'te_form': {'kanji': '大きくて', 'kana': 'おおきくて'},
            'adverbial': {'kanji': '大きく', 'kana': 'おおきく'}
        }
        self.verify_all_conjugations(ookii_test, expected)

    def test_na_adjective(self):
        # Test な adjective (きれい - pretty)
        kirei_test = {
            'kanji': [{'text': '綺麗'}],
            'kana': [{'text': 'きれい'}],
            'sense': [{'partOfSpeech': ['adj-na']}]
        }
        expected = {
            'present': {'kanji': '綺麗', 'kana': 'きれい'},
            'present_negative': {'kanji': '綺麗じゃない', 'kana': 'きれいじゃない'},
            'past': {'kanji': '綺麗だった', 'kana': 'きれいだった'},
            'past_negative': {'kanji': '綺麗じゃなかった', 'kana': 'きれいじゃなかった'},
            'te_form': {'kanji': '綺麗で', 'kana': 'きれいで'},
            'adverbial': {'kanji': '綺麗に', 'kana': 'きれいに'}
        }
        self.verify_all_conjugations(kirei_test, expected)

if __name__ == '__main__':
    unittest.main()