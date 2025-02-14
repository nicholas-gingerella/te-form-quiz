JMDICT_MAPPING = {
    "nouns": {
        "名詞": ["n", "num", "pn", "n-pref", "n-suf"],
        "接頭詞": ["pref"],
        "接尾詞": ["suf"]
    },
    "i-adjectives": {
        "形容詞": ["adj-i", "adj-ix", "adj-shiku", "adj-ku"]
    },
    "na-adjectives": {
        "形容動詞": ["adj-na"],
        "連体詞": ["adj-f", "adj-no", "adj-pn"]
    },
    "verbs": {
        "動詞": [
            "v1", "v1-s", "v2a-s", "v2b-k", "v2d-s", "v2g-k", "v2g-s", "v2h-k", "v2h-s", "v2k-k", "v2k-s", "v2m-s", "v2n-s", "v2r-k", "v2r-s", "v2s-s", "v2t-k", "v2t-s", "v2w-s", "v2y-k", "v2y-s", "v2z-s",
            "v4b", "v4g", "v4h", "v4k", "v4m", "v4r", "v4s", "v4t",
            "v5aru", "v5b", "v5g", "v5k", "v5k-s", "v5m", "v5n", "v5r", "v5r-i", "v5s", "v5t", "v5u", "v5u-s",
            "vi", "vk", "vn", "vr", "vs", "vs-c", "vs-i", "vs-s", "vt", "vz"
        ]
    },
    "other": {
        "副詞": ["adv", "adv-to"],
        "助動詞": ["aux", "aux-adj", "aux-v", "cop"],
        "接続詞": ["conj"],
        "助詞": ["prt"],
        "感動詞": ["int"],
        "記号": ["unc"]
    }
}

def get_jmdict_equivalents(category, japanese_identifier):
    return JMDICT_MAPPING.get(category, {}).get(japanese_identifier, [])

def get_word_type(japanese_identifier):
    """
    Returns the broad category (noun, verb, etc.) for a given Japanese identifier
    Args:
        japanese_identifier: The Japanese part of speech (e.g., '名詞', '動詞')
    Returns:
        String: 'noun', 'verb', 'i-adjective', 'na-adjective', or 'other'
    """
    for category, mappings in JMDICT_MAPPING.items():
        if japanese_identifier in mappings:
            # Remove the 's' from the end of the category name
            return category.rstrip('s')
    return 'other'

# Example usage
if __name__ == "__main__":
    test_identifiers = ['名詞', '動詞', '形容詞', '形容動詞', '副詞']
    for identifier in test_identifiers:
        word_type = get_word_type(identifier)
        print(f"Japanese POS: {identifier} → Type: {word_type}")