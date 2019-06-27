class Summary:
    def __init__(self, language):
        self.language = language

    def print_inventory(self):
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
    
    def print_rules(self):
        return

    # TODO: concatenate using language spacers/separators
    def combine_exponent_pieces(self, pre, mid, post, bound=True):
        return []

    def summarize_exponents(self, spell_after_change=True):
        summary = {}
        for exponent_id, exponent in self.language.grammar.exponents.get().items():
            # get sounds and spellings for grammatical pieces
            pre_sound = exponent['pre']
            mid_sound = exponent['mid']
            post_sound = exponent['post']
            pre_change = self.language.phonology.apply_rules(pre_sound)
            mid_change = self.language.phonology.apply_rules(mid_sound)
            post_change = self.language.phonology.apply_rules(post_sound)
            pre_spelling = self.language.phonology.spell(
                pre_change if spell_after_change else pre_sound,
                fallback_phonemes=pre_sound
            )
            mid_spelling = self.language.phonology.spell(
                mid_change if spell_after_change else mid_sound,
                mid_sound
            )
            post_spelling = self.language.phonology.spell(
                post_change if spell_after_change else post_sound,
                post_sound
            )
            definition = self.language.grammar.autodefine(exponent_id)

            # string pieces together
            sound = self.combine_exponent_pieces(
                pre_sound,
                mid_sound,
                post_sound,
                bound=exponent['bound']
            )
            change = self.combine_exponent_pieces(
                pre_change,
                mid_change,
                post_change,
                bound=exponent['bound']
            )
            spelling = self.combine_exponent_pieces(
                pre_spelling,
                mid_spelling,
                post_spelling,
                bound=exponent['bound']
            )

            summary[exponent_id] = {
                'sound': sound,
                'change': change,
                'spelling': spelling,
                'definition': definition
            }

        return summary

    def print_grammar(self):
        return

    def print_sentences(self):
        return