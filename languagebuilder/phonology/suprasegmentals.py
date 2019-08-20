from uuid import uuid4
import collections

# NOTE: what's called "suprasegmental" is actually meant to "mark" extra info around
# a single sound that can be configured, toggled or changed independently of that
# sound's internal value (see Phonetics for those features).

# NOTE: WAIT! let's think about the construction
#   - count morae, including turning strings into morae
#       - TODO: build moraics class
#   - count syllables, including turning strings into syllables
#       - TODO: build syllabics class
#   - TODO: revamp this class
#       - store seg marker names mapped to mark symbols
#       - store mark symbols mapped to marked sounds
#       - store marked sounds mapped to marked letters
#           - alternatively map marks to marked letters
#       - store marking or contour data telling how to apply marks
#           - index to specific syllable, mora or sound
#       - handle changes given any kind of environment
#           - features list, CV abbrev, sound, mark, mora, syllable
#           - TODO: here list an example of each kind of change to work towards

class Suprasegmentals:
    # MARKS data?
    # {
    #   mark: mark_id,              # use to look up marked letters/symbols
    #   prioritize: feature,        # attempt to mark this feature first
    #   mora: 0,                    # number of morae from fixed point
    #   relative: word/feature,     # from first/nearest occurrence, otherwise whole word
    #   syllable: 0,                # default to syll if given? 
    #   handedness: l/r,            # count sylls/morae either left or right
    #   direction: before/after     # search direction if markable not in mora/syll 
    # }
    def __init__(self, phonology):
        # renderable marks for sounds or whole syllables
        # NOTE: look up non-syll mark in diacritics (or separate out letters vs sounds?)
        self.marked_sounds = {}     # mark: { syllable: False, before: True, mark: "" }
        # marks assigning diacritics to letters
        self.diacritics = {}        # mark: { symbol: marked_symbol }

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
        self.syllabifications = {}
        self.default_contours = {}

    # TODO: rethink pitch/tone/accent alongside default and custom contours below
    def shift_accent(self, sounds, syllables=0):
        return
    def raise_pitch(self, sounds, octaves=0.0):
        return
    def reshape_pitch(self, sounds, shape):
        return
    
    # TODO: work through all possibilities: features list, CV abbrev, sound, mark, mora
    def detect_environment_including_marks(self, whole, parts):
        assert isinstance(parts, list), f"Expected detectable part in whole to be list not {parts}"
        assert isinstance(whole, (list, str)), f"Expected compared whole to be string or list not {whole}"
        matching_parts = []     # TODO: paired info about type of match?
        for i, symbol in enumerate(whole):
            if matching_parts == len(parts):
                return True     # or matching_parts list?
            did_match = True
            for j, part in enumerate(parts):
                if not did_match:
                    matching_parts = []
                    break
                compared_symbol = whole[i + j]
                # treat as features
                if set(compared_symbol).issubset(self.phonology.phonetics.features.keys()):
                    if set(part).issubset(set(compared_symbol)):
                        matching_parts.append(part)
                        continue
                # treat as single feature or abbreviation
                if isinstance(symbol, str) and part == symbol:
                    matching_parts.append(part)
                    continue
                # treat as single sound
                if self.phonology.has_sound(symbol):
                    matching_parts.append(part)
                    continue
                # treat as mark
                if self.marks.get(symbol) and part == symbol:
                    matching_parts.append(part)
                    continue
                did_match = False
        return False   # no match

    def get_mark(self, mark_id):
        return self.marks[mark_id]

    def add_syllabification(self, word_id, syllabification=None, do_syllabify=False):
        syllabification = self.syllabify(word_id[0]) if do_syllabify else syllabification
        if syllabification and word_id not in self.syllabifications:
            self.syllabifications[word_id] = syllabification
        return self.syllabifications[word_id]

    def update_syllabification(self, word_id, syllabification):
        if word_id not in self.syllabifications:
            return
        self.syllabifications[word_id] = syllabification
        return self.syllabifications[word_id]
    
    def remove_syllabification(self, word_id):
        return self.syllabifications.pop(word_id, None)

    def add_default_contour(self, name, mark="", conditioning_mark=None, offset=None, chain=None, overwrite=False):
        if not overwrite and name in self.default_contours:
            return
        
        # expect offset to be [syllable_index, symbol_index] pair
        if offset and (len(offset) != 2 or False in [isinstance(n, int) for n in offset]):
            return

        self.default_contours[name] = {
            'condition': conditioning_mark,     # assume word start/end if None
            'mark': mark,                       # mark applied to letter
            'offset': offset,                   # offset from compared mark/boundary
            'chain': chain                      # default contour name to apply next
        }
        return name
    
    def get_default_contour(self, name):
        return self.default_contours.get(name)

    def update_default_contour(self, name, mark=None, conditioning_mark=None, offset=None, chain=None):
        contour = self.remove_default_contour(name)
        if not contour:
            return
        return self.add_default_contour(
            name,
            mark = mark if mark else contour['mark'],
            conditioning_mark = conditioning_mark if conditioning_mark else contour['condition'],
            offset = offset if offset else contour['offset'],
            chain = chain if chain else contour['chain'],
            overwrite = True
        )

    def remove_default_contour(self, name):
        return self.default_contours.pop(name, None)

    def flat_count(self, nested_list, value=None, index=None, offset=1):
        """Count offset number of values in a list of lists disregarding depth, then
        return the nested index of that offset value. The offset is calculated from
        either the given index tuple positioning (outer_list_index, inner_list_index)
        or instead from the first instance of a value if one is supplied."""
        # expect a tuple with outer, inner list indexes
        if index and (len(index) != 2 or False in [isinstance(n, int) for n in index]):
            print(f"Failed to flat count nested list - expected index (int, int) not {index}")
            return
        # flat count up to offset
        count = 0
        identified_compared_value = False
        # build outer, inner list indexes from first occurrence of given value
        if value:
            first_list_with_value = next(l for l in nested_list if value in l)
            outer_i = nested_list.index(first_list_with_value)
            inner_i = first_list_with_value.index(value)
            index = (outer_i, inner_i)
        # if offset is negative, do reverse look
        outer_list = reversed(nested_list) if offset < 0 else nested_list
        for i, l in enumerate(outer_list, index[0]):
            inner_list = reversed(l) if offset < 0 else l
            for j, inner_value in enumerate(inner_list):
                if identified_compared_value:
                    if count == offset:
                        return (i, j)
                    count += 1
                elif (i, j) == index:
                    identified_compared_value = True
        return ()

    def apply_default_contour(self, syllables, name):
        contoured = [None for syllable in syllables for symbol in syllable]
        contour = self.default_contours[name]
        
        # TODO: interpet attributes and calc mark position(s)
        # - if offset is falsy and only mark is supplied, apply it everywhere
        # - mark from start or end
        # - mark from offset from conditioner
        # - if chain then apply next (or have plural apply do this)
        if not contour['offset']:   # TODO: no need to check for condition or start?
            contoured = [
                contour['mark']
                for syllable in contoured
                for mark in syllable
            ]
        # mark from another symbol
        elif contour['condition']:
            # grab indexes where conditioner appears
            compared_indexes = [
                (i, j)
                for i, syllable in enumerate(contoured)
                for j, compared_mark in enumerate(syllable)
                if compared_mark == contour['condition']
            ]
            # add mark forwards/backwards from conditioners
            for compared_index in compared_indexes:
                mark_index = self.flat_count(contoured, index=compared_index, offset=contour['offset'])
                contoured[mark_index[0]][mark_index[1]] = contour['mark']
        # mark from word start or end
        else:
            # count forwards/backwards from boundary and mark
            mark_index = self.flat_count(contoured, index=(0, 0), offset=contour['offset'])
            contoured[mark_index[0]][mark_index[1]] = contour['mark']
            
        # TODO: check for circular chain (do in plural method)
        next_contour = contour['chain']

        return (contoured, next_contour)

    # TODO: complete contours and compare to current hardcoded single-syll/char values
    #   - can be use to check environment marks or to apply changes
    #   - if useful enough structure the whole class around contours
    # EXs: Gk clitic tonoi, J pitch accent, Zh tone interactions, movable stress, ...
    # 
    # TODO: allow setting default patterns like always high-pitch final syllable 
    #
    def add_contour(self, word_id, syllabified_word=None, contour=None, do_syllabify=False, default_contour=False):
        # example_contour = [[], [], [None, 'high'], []]
        if not isinstance(word_id, (list, tuple)) or len(word_id) != 2 or not isinstance(word_id[0], str) or not isinstance(word_id[1], int):
            return
        if not contour or not isinstance(contour, (list, tuple)):
            return
        if not do_syllabify and (not syllabified_word or len(syllabified_word) != syllabified_word):
            return
        #
        # TODO: create a default contour
        # default_contour = []
        syllabified_word = self.phonology.syllables.syllabify(word_id[0]) if do_syllabify else syllabified_word
        # check contour
        if len(contour) > len(syllabified_word):
            return
        # TODO: format contour entry
        self.contours.setdefault(word_id, (syllabified_word, contour))
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
            syllabified_word = self.syllabify(vocabulary_item[0])
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

    