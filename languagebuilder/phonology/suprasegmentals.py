from ..tools import flat_list
from uuid import uuid4
import collections

# NOTE: what's called "suprasegmental" is actually meant to "mark" extra info around
# a single sound that can be configured, toggled or changed independently of that
# sound's internal value (see Phonetics for those features).
class Suprasegmentals:
    def __init__(self, phonology):
        # map diacritical marks per letter to rendered letters 
        self.diacritic_sounds = {
            # mark: { symbol: { sound: "", spelling: "" }, ... },
            # ...
        }
        self.diacritic_spellings = {}

        # store phonology for checking syllable types
        self.phonology = phonology
        self.marked_words = {
            # word_id: [mark_ids]
        }

        # NOTE: code for allowing multiple marks per sound, multiple marks per syllable
        self.marks = {
            # mark_id: { data }     # see info below
            # headword: {
            #   'syllables': [],    # list of syllable-long string lists
            #   'syllable':  0,     # target syllable containing marked sound
            #   'sound':     0      # target sound this mark applies to
            #   'mark':      'id',  # pointer to the mark details
            # }
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

        # associate word lookups with contours
        # then use contours when applying changes or checking environments
        # TODO: support contours with one mark per unique contour key
        # TODO: support marks with one char per marked sound
        #   - when applying marks look for first syll char taking that mark
        #   - also allow for syllable mark (but store whether before/after)
        self.contours = {}
    
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

    # TODO: complete contours and compare to current hardcoded single-syll/char values
    #   - can be use to check environment marks or to apply changes
    #   - if useful enough structure the whole class around contours
    # EXs: Gk clitic tonoi, J pitch accent, Zh tone interactions, movable stress, ...
    def add_contour(self, word_id, syllabified_word=None, contour=None, do_syllabify=False, default_contour=False):
        # example_contour = [[], [], [None, 'high'], []]
        if not isinstance(word_id, (list, tuple)) or len(word_id) != 2 or not isinstance(word_id[0], str) or not isinstance(word_id[1], int):
            return
        if not contour:
            return
        if not do_syllabify and (not syllabified_word or len(syllabified_word) != syllabified_word):
            return
        #
        # TODO: create a default contour
        # default_contour = []
        syllabified_word = self.resyllabify(word_id[0]) if do_syllabify else syllabified_word
        self.contours.setdefault(word_id)
        return self.contours.get(word_id)
    # TODO: mark letters in syllables
    def apply_contour(self, word_id):
        syllabification = self.syllabifications[word_id][:]
        contour = self.contours[word_id]
        for syllable, i in enumerate(syllabification):
            syllable_marks = contour[i][:]
            current_marked = 0
            for c, j in enumerate(syllable):
                if c in self.diacritics:
                    syllabification[i][j] = self.diacritics[syllable_marks[current_marked]][c]
                    current_marked += 1
                # TODO: instead apply syllable-wide mark to beginning/end of syll
            if not current_marked >= len(syllable_marks):
                # FAILED to apply all marks to syllable; syllable doesn't match contour?
                return
        return syllabification
    # TODO: keep track of syllable added/removed
    def track_contour_changes(self, word_id):
        syllabification = self.syllabifications[word_id]
        syllable_ids = [i for i in range(len(syllabification))]
        def update_contour():
            # add/remove/adjust syllable ids
            return syllable_ids
        return update_contour

    def is_syllabified(self, word):
        """Check for a syllabified word containing a list of syllable lists each
        containing sound strings"""
        # is a list
        if not isinstance(word, (tuple, list)):
            return False
        # is a list of syllable lists
        for syllable in word:
            if not isinstance(syllable, (tuple, list)):
                return False
            # is a sound string
            for sound in syllable:
                if not isinstance(sound, str) or not self.phonology.has_sound(sound):
                    return False
        return True

    def map_diacritic(self, diacritic, symbol, modified_symbol, is_spelling=False):
        diacritics = self.diacritic_spellings if is_spelling else self.diacritic_sounds
        diacritics.setdefault(diacritic, {})
        diacritics[diacritic][symbol] = modified_symbol
        return diacritics[diacritic]
    def unmap_diacritic(self, diacritic, symbol, is_spelling=False):
        diacritics = self.diacritic_spellings if is_spelling else self.diacritic_sounds
        return diacritics[diacritic].pop(symbol, None)
    def remove_diacritic(self, diacritic, is_spelling=False):
        diacritics = self.diacritic_spellings if is_spelling else self.diacritic_sounds
        return diacritics.pop(diacritic, None)

    # TODO: sound changes, shifts?
    def apply_marks(self, word_id, as_string=False, is_spelling=False):
        """Build a representation of a word's sounds with diacritics and syllable marks"""
        word_details = self.marked_words.get(word_id)
        if not word_details:
            return
        syllabification = word_details['syllabification'][:]
        marked_syllables = {}
        marks = word_details['marks']
        for mark_id in marks:
            mark = self.marks.get(mark_id)
            if not mark:
                continue
            symbol = mark['symbol']
            if not mark['sound']:
                marked_syllables.setdefault(3, set()).add(symbol)
            # add/alter character marks
            diacritics = self.diacritic_spellings if is_spelling else self.diacritic_sounds
            modified_symbol = diacritics[symbol][syllabification[mark['syllable']][mark['sound']]]
            syllabification[mark['syllable']][mark['sound']] = modified_symbol
        # prepend syllable marks
        for syllable_n, syllable_mark in collections.OrderedDict(marked_syllables).items():
            syllabification[syllable_n] = [syllable_mark] + syllabification[syllable_n]
        # flatten into list of symbols
        resulting_symbols = [
            syllable_symbol for syllable_list in syllabification
            for syllable_symbol in syllable_list
        ]
        if as_string:
            return "".join(resulting_symbols)
        return resulting_symbols

    # TODO: split marking word from adding mark
    def add_mark(self, vocabulary_item, syllabified_word=None, symbol="", is_diacritic=True, pitch=None, stress=None, target_syllable=0, target_sound=None, do_syllabify=False):
        """Mark a single word on a specific syllable, optionally a specific sound
        within that syllable"""
        # expect headword structure to match vocabulary (word, index) pair
        if not len(vocabulary_item) == 2 and isinstance(vocabulary_item[0], str) and isinstance(vocabulary_item[1], int):
            print(f"Suprasegmentals failed to add mark - invalid vocabulary item {vocabulary_item}")
            return

        # allow targeted syllable without specific targeted sound
        if not isinstance(target_sound, int):
            target_sound = None

        # make or check useful syllabification
        if do_syllabify:
            syllabified_word = self.resyllabify(vocabulary_item[0])
        if not syllabified_word or not self.is_syllabified(syllabified_word):
            print(f"Suprasegmentals failed to add mark - unrecognized syllabified word {syllabified_word}")
            return

        if is_diacritic and not self.diacritics.get(symbol):
            print(f"Supgrasegmentals failed to mark {vocabulary_item} - unrecognized diacritic {symbol}")
            return
        # TODO: otherwise place where with respect to each syllable - above? before?

        # TODO: combining symbol mapping
        # TODO: vet characteristicts (symbol, pitch, stress)

        mark_id = f"mark-{uuid4()}"
        added_mark = {
            'symbol': symbol,
            'diacritic': is_diacritic,
            'pitch': pitch,
            'stress': stress,
            'syllable': target_syllable,
            'sound': target_sound
        }
        self.marks[mark_id] = added_mark
        self.marked_words.setdefault(vocabulary_item, {
            'syllabification': syllabified_word,
            'marks': set()
        })['marks'].add(mark_id)
        self.marked_words[syllabified_word]
        return self.get_mark(mark_id)
    
    def update_mark(self, mark_id):
        return
    def remove_mark(self, mark_id):
        return

    def render_marks(self, marked_word):
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
    