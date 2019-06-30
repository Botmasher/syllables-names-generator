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

    def combine_exponent_pieces(self, pre=None, mid=None, post=None, bound=True):
        """Concatenate all pieces of an exponent into one sequence list for display
        or readability, using language spacing and affix symbols to mark them
        off from each other."""
        # fetch and decide material between pieces
        separator = self.language.affix_symbol if bound else ""
        spacer = self.language.spacing_symbol
        
        # build flat pieces sequence with separated material
        pieces = []
        pieces += pre if pre else []
        if pre:
            pieces += separator
        if mid or post:
            pieces += spacer
        if mid:
            pieces += separator
        pieces += mid if mid else []
        if mid:
            pieces += separator
        if mid and post:
            pieces += spacer
        if post:
            pieces += separator
        pieces += post if post else []

        # remove extra beginning or trailing spacers
        if pieces[0] == spacer:
            pieces = pieces[1:]
        if pieces[-1] == spacer:
            pieces = pieces[:-1]

        return pieces

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
                'definition': definition,
                'properties': exponent['properties'],
                'bound': exponent['bound'],
                'pos': exponent['pos']
            }

        return summary

    def print_grammar(self, spell_after_change=True, print_display=True):
        """Build a display text summary of the language's grammatical words and
        word pieces, return the text and optionally log the text out."""
        exponents = self.summarize_exponents(spell_after_change=spell_after_change)

        # build map of exponent ids nested under pos:category:grammemes
        # NOTE: None entry for zero word class    
        exponents_by_pos = {}
        for exponent_id, exponent_entry in exponents.items():
            exponent_pos = exponent_entry['pos'] if exponent_entry['pos'] else None
            # TODO: place each exponent once only
            #   - make optimal decisions about multiproperty exponents
            #   - determine which property should be top
            #   - nest others below that one
            exponents_by_pos.setdefault(exponent_pos, {})
            for category in exponent_entry['properties']:
                exponents_by_pos[exponent_pos].setdefault(category, {})
                for grammeme in exponent_entry['properties'][category]:
                    exponents_by_pos[exponent_pos][category].setdefault(grammeme, set())
                    exponents_by_pos[exponent_pos][category][grammeme].add(exponent_id)

        # use exponents by word class to print display text
        display = "-- Grammar Summary --"
        for pos in exponents_by_pos:
            if not pos:
                display += "General:\n"
            else:
                display += f"{pos}:\n"
            for category in exponents_by_pos[pos]:
                # split affixes from adpositions
                affixes = set()
                adpositions = set()
                for exponent_id in exponents_by_pos[pos][category].values():
                    if exponents[exponent_id]['bound']:
                        affixes.add(exponent_id)
                    else:
                        adpositions.add(exponent_id)
                display += f"{category} affixes:\n"
                for affix_id in affixes:
                    exponent = exponents[affix_id]
                    display += f"{exponent['spelling']}\t{exponent['definition']}\n"
                display += f"{category} adpositions/particles:"
                for adposition_id in adpositions:
                    exponent = exponents[adposition_id]
                    display += f"{exponent['spelling']}\t{exponent['definition']}\n"
        
        display += "-- End Grammar Summary --"
        print_display and print(display)

        return display

    def print_sentences(self):
        return