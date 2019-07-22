from ..tools import flat_list
from uuid import uuid4

# NOTE: what's called "suprasegmental" is actually meant to "mark" extra info around
# a single sound that can be configured, toggled or changed independently of that
# sound's internal value (see Phonetics for those features).
class Suprasegmentals:
    def __init__(self, phonology):
        # store phonology for checking syllable types
        self.phonology = phonology
        self.marked_words = {
            # word_id: [mark_ids]
        }
        self.marks = {
            # mark_id: { data }     # see info below
            # headword: {
            #   'syllables': [],    # list of syllable-long string lists
            #   'syllable':  0,     # target syllable containing marked sound
            #   'sound':     0      # target sound this mark applies to
            #   'mark':      'id',  # pointer to the mark details
            # }
        # NOTE: code for allowing multiple marks per sound, multiple marks per syllable
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
    
    # TODO: allow setting pattern like always high-pitch final syllable 
    # def represent(self, headword, syllable_target=0, sound_target=0, is_syllabified=True):
    #     syllables = self.resyllabify(headword) if not is_syllabified else headword
    #     self.marked_syllable[headword] = {
    #         'syllables': syllables,
    #         'target': syllable_target,
    #         'sound_target': sound_target,
    #     }
    #     return self.marked_syllable[headword]

    def shift_accent(self, sounds, syllables=0):
        return
    
    def raise_pitch(self, sounds, octaves=0.0):
        return

    def contour_pitch(self, sounds, contour):
        return
    
    def get_mark(self, mark_id):
        return self.marks[mark_id]

    def add_mark(self, headword, syllabified_word, target_syllable=0, target_sound=None):
        # TODO: decide on headword structure
        #   - matches vocabulary entry (word, entry_n)?
        # TODO: allow targeted syllable without specific targeted sound
        if not isinstance(target_sound, int):
            target_sound = None
        mark_id = f"mark-{uuid4()}"
        added_mark = {
            'syllable': target_syllable,
            'sound': target_sound
        }
        self.marks[mark_id] = added_mark
        self.marked_words.setdefault(headword, {
            'syllabification': syllabified_word,
            'marks': set()
        })['marks'].add(mark_id)
        self.marked_words[syllabified_word]
        return self.get_mark(mark_id)
    
    def update_mark(self, mark_id):
        return
    def remove_mark(self, mark_id):
        return

    def move(self, word_id, mark_id, syllable_target):
        """Move the targeted mark to a new syllable"""
        return

    def _is_syllable(self, syllable_fragment):
        """Verify that the fragment is a subset of least one syllable in the phonology"""
        # read possible syllables from phonology
        syllables = self.phonology.syllables.get().values()
        # traverse syllables for at least one subset match
        for syllable in syllables:
            if syllable_fragment >= len(syllable):
                return True       
        return False

    def resyllabify(self, sounds):
        # verify sounds list input
        if not isinstance(sounds, (list, tuple)):
            raise TypeError(f"Suprasegmentals resyllabify expected list of strings not {sounds}")
        
        # final list of lists to return
        syllabified_word = []
        # intermediate syllable evaluation while iterating
        current_syllable = []
        
        # traverse sounds fitting each one into a syllable
        for sound in sounds:
            # test for sound fits at least one syllable at current compared position
            working_on_syllable = False

            # continue working on syllable if this sound makes it a valid syllable fragment
            is_syllable = self._is_syllable([*current_syllable, sound])
            if is_syllable:
                # build up single syllable and move to next sound
                current_syllable.append(sound)
                working_on_syllable = True
                break
                
            # conclude a finished syllable
            if not working_on_syllable:
                syllabified_word.append(current_syllable)
                current_syllable = []

        # move leftover sounds into final syllable
        if current_syllable and self._is_syllable(current_syllable):
            syllabified_word.append(current_syllable)

        # ensure all input sounds were syllabified
        if len(flat_list.flatten(syllabified_word)) != len(sounds):
            print(f"Suprasegmentals failed to resyllabify - not all sounds placeable within compared phonology syllables")
            return
        
        return syllabified_word
    