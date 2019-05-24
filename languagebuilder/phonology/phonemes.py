# TODO separate phonemes/letters/weights (language) from ipa-features (features) - do not handle features here!
class Phonemes():
    def __init__(self):
        self.phonemes = {}

    def has(self, ipa):
        return ipa in self.phonemes
    
    def get(self, ipa=None):
        """Return one phoneme or all if no specific one requested"""
        if ipa is None:
            return self.phonemes
        return self.phonemes.get(ipa, None)

    def add(self, ipa, letters, weight=0):
        """Store a new phoneme object"""
        # TODO: check ipa associated features

        #if not type(phoneme).__name__ == 'Phoneme':
        #    print(f"Phonemes failed to store invalid phoneme {phoneme}")
        #    return
        
        # use ipa symbol as key
        #ipa = phoneme.get_symbol()

        # do not overwrite existing phoneme with this key
        if ipa in self.phonemes:
            print(f"Phonemes add failed - phoneme already exists for {ipa}")
            return

        # expect a phoneme object
        phoneme = {
            'ipa': ipa,
            'letters': set(letters),
            'weight': weight
        }

        # create entry
        self.phonemes[ipa] = phoneme
        return phoneme
    
    # TODO: ability to manage (crud) individual letters
    def update(self, ipa, letters=None, weight=None, new_ipa=None):
        """Update the phoneme object for an existing ipa phoneme"""
        # fetch and check for existing phoneme
        phoneme = self.phonemes.get(ipa)
        if not phoneme:
            print(f"Phonemes failed to update unrecognized phoneme {ipa}")
            return
        # update individual properties in the phoneme
        phoneme['letters'] = set(letters) if letters else phoneme['letters']
        phoneme['weight'] = weight if weight else phoneme['weight']
        # also update the ipa and return the new object
        if new_ipa:
            return self.update_ipa(ipa, new_ipa)
        # return the updated phoneme object
        return phoneme
    
    # TODO: check that new ipa is featureful symbol
    def update_ipa(self, ipa, new_ipa):
        """Update the ipa symbol for an existing phoneme"""
        # try to remove the existing phoneme
        phoneme = self.remove(ipa)
        # check that phoneme object exists
        if not phoneme:
            print(f"Phonemes update_ipa failed to find phoneme for {ipa}")
            return
        # modify and store the phoneme object
        phoneme['ipa'] = new_ipa
        self.phonemes[new_ipa] = phoneme
        return phoneme

    def remove(self, ipa):
        """Delete phoneme associated with one symbol from the phonemes"""
        return self.phonemes.pop(ipa, None)

    def symbols(self):
        """Read all symbols stored as keys in the phonemes map"""
        return self.phonemes.keys()

    def get_symbol(self, ipa):
        """Read one phonetic symbol from one stored phoneme"""
        phoneme = self.get(ipa)
        if not phoneme:
            print("Phonemes get_symbol failed - unknown phoneme {0}".format(phoneme))
            return
        return phoneme.get_symbol()

    def get_letters(self, ipa):
        """Read all letters from one stored phoneme"""
        return self.phonemes.get(ipa, {}).get('letters')

    def get_weight(self, ipa):
        """Read the weight for one stored phoneme"""
        return self.phonemes.get(ipa, {}).get('weight')
