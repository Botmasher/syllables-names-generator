class Suprasegmentals:
    def __init__(self):
        # set of possible syllables (or read from phonology?)
        self.syllable_types = {}
        self.syllabifications = {
            # headword: [syllabification] pairs
        }
        self.accents = {
            # ipa: orthography pairs
            # TODO: determine how to add to a letter
        }
        self.intonation = {
            # pitch_range: character pairs
        }
        self.stress = {
            # character: feature pairs
        }
    
    def represent(self, headword):
        return

    def shift_accent(self, sounds, syllables=0):
        return
    
    def raise_pitch(self, sounds, octaves=0.0):
        return

    def contour_pitch(self, sounds, contour):
        return
    
    def resyllabify(self, sounds):
        syllabified_word = []
        current_syllable = []
        for sound in sounds:
            # TODO: determine if syllable built
            # - if so append to syllabified_word and clear current_syllable
            # - if not add and keep looking
            # - OR hold successful syllable and store on first fail
            continue
        return syllabified_word
    