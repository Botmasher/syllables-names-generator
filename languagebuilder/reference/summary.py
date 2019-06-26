class Summary:
    def __init__(self, language):
        self.language = language

    def summarize_inventory(self):
        phonemes = self.language.phonology.phonemes.get()
        print("Phonemes")
        vowels = set()
        consonants = set()
        for phoneme in phonemes:
            features = self.language.phonetics.get_features(phoneme['ipa'])
            if 'consonant' in features:
                consonants.add(phoneme)
            if 'vowel' in features:
                vowels.add(phoneme)
        print(f"vowels: {', '.join(vowels)}")
        print(f"consonants: {', '.join(consonants)}")
        print("Letters")
        for phoneme in phonemes:
            letters = ", ".join(phoneme['letters'])
            print(f"{phoneme['ipa']}: {letters}")
        return phonemes
    
    def summarize_change(self):
        return

    def summarize_grammar(self):
        return

    def summarize_sentences(self):
        return