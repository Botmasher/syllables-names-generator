from ..tools import flat_list

class Suprasegmentals:
    def __init__(self, phonology):
        # store phonology for checking syllable types
        self.phonology = phonology
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
        # read possible syllables from phonology
        syllables = self.phonology.syllables.get().values()
        
        # final list of lists to return
        syllabified_word = []
        # intermediate syllable evaluation while iterating
        current_syllable = []
        current_syllable_position = 0
        
        # traverse sounds fitting each one into a syllable
        for sound in sounds:
            # test for sound fits at least one syllable at current compared position
            working_on_syllable = False

            # does at least one syllable ?
            for syllable in syllables:
                # is current compared position beyond syllable bounds?
                if current_syllable_position >= len(syllable):
                    continue
                # do sound features contain current compared syllable features as subset?
                if set(self.phonology.get_sound_features(sound)) >= set(syllable[current_syllable_position]):
                    # build up single syllable and move to next sound
                    current_syllable.append(sound)
                    current_syllable_position += 1
                    working_on_syllable = True
                    break
                
            # conclude a single syllable
            if not working_on_syllable:
                syllabified_word.append(current_syllable)
                current_syllable = []
                current_syllable_position = 0
                working_on_syllable = True

        # ensure 
        if len(flat_list.flatten(syllabified_word)) != len(sounds):
            print(f"Suprasegmentals failed to resyllabify - not all sounds placeable within compared phonology syllables")
            return
        
        return syllabified_word
    