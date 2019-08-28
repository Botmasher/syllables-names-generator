from uuid import uuid4
from ..tools import redacc, flat_list

class Syllables():
    def __init__(self, phonology):
        # map of syllable structures
        self.syllables = {}
        # special syllable character abbreviations
        self.syllable_characters = {
            '_': "_",
            '#': "#",
            ' ': " ",
            'C': "consonant",
            'V': "vowel"
        }
        # reference phonology into which injected
        self.phonology = phonology

    def has(self, syllable_id):
        """Check if an id exists in the syllables map"""
        return syllable_id in self.syllables

    # TODO: vet for syllable characters || features
    # def is_valid_structure(self, structure):
    #     if not isinstance(structure, list):
    #         return False
    #     return True

    def get(self, syllable_id=None):
        """Read one syllable or all if no id given"""
        # return all syllables if no id given
        if not syllable_id:
            return self.syllables
        # return a single syllable entry
        return self.syllables.get(syllable_id)

    # TODO: check how environment/rule formats readout
    def print_syllables(self):
        """Print out all syllables in a human-readable formatted string"""
        syllable_text = ""
        count = 0
        for syllable in self.syllables.values():
            count += 1
            syllable_text += f"Syllable {count}: "
            for syllable_item in syllable.get_structure():
                for feature in syllable_item:
                    syllable_text += f"{feature}, "
            syllable_text = syllable_text[:-2]
            syllable_text += "\n"
        print(syllable_text)
        return syllable_text

    def structure(self, raw_structure):
        """Clean up and format a list or string as a list of features and syllable characters"""
        if not isinstance(raw_structure, (list, tuple, str)):
            print(f"Failed to structure syllable - expected list or string not {raw_structure}")
            return
        
        # treat string as list of special syllable characters
        #
        # TODO: parse string into list containing features or syllable characters
        syllable_items = list(raw_structure) if isinstance(raw_structure, str) else raw_structure

        structure = []

        # TODO: use below checks for vetting 

        # build up sequence of valid features or syllable characters
        for syllable_item in syllable_items:
            # add from string containing a single feature or syllable character
            if isinstance(syllable_item, str):

                # split item string for parsing
                syllable_subitems = syllable_item.split()
                
                # add syllable character to final list
                # NOTE: consider how turning CV into 'consonant', 'vowel'
                # plays with added features, build_word and rules/environments
                if len(syllable_subitems) == 1 and syllable_subitems[0] in self.syllable_characters:
                    structure.append([self.syllable_characters[syllable_subitems[0]]])
                
                # add a good list of features
                else:
                    for syllable_subitem in syllable_subitems:
                        if not self.phonology.phonetics.has_feature(syllable_subitem):
                            print(f"Syllables add failed - invalid syllable item {syllable_item}")
                            return
                    structure.append(syllable_subitems)
                
            # catch and add syllable characters within a one-element list
            elif isinstance(syllable_item, list) and len(syllable_item) == 1 and syllable_item[0] in self.syllable_characters:
                structure.append(self.syllable_characters[syllable_item[0]])
            # add good list of features directly to new structure
            elif isinstance(syllable_item, list):
                for feature in syllable_item:
                    if not self.phonology.phonetics.has_feature(syllable_item):
                        print("Phonology add_syllable failed - invalid syllable feature {0}".format(feature))
                        return
                structure.append(syllable_item)
        
        return structure
    
    def add(self, structure):
        """Add a new syllable to the syllables map"""
        
        # store valid terms for added structure
        new_structure = self.structure(structure)

        # verify valid vetted structure
        if not new_structure:
            print(f"Syllables failed to add invalid structure {structure}")
            return
        
        # add created syllable to the map
        syllable_id = f"syllable-{uuid4()}"
        self.syllables[syllable_id] = new_structure
        return syllable_id

    def update(self, syllable_id, structure):
        """Modify an existing syllable"""
        # check if syllable exists
        if not self.get(syllable_id):
            print("Syllable update failed - unknown syllable_id")
            return
        
        # restructure into list of valid features and syllable characters
        new_structure = self.structure(structure)

        # check for valid updated structure
        if not new_structure:
            print(f"Syllable update failed - invalid syllable structure {structure}")
            return
        
        # store the updated structure
        self.syllables[syllable_id] = new_structure
        return syllable_id

    def remove(self, syllable_id):
        """Remove one syllable from the syllables map"""
        return self.syllables.pop(syllable_id, None)

    def clear(self):
        """Reset the syllables map and return a cache read method"""
        syllables_cache = self.syllables.copy()
        def read_cache():
            return syllables_cache
        self.syllables.clear()
        return read_cache

    def is_syllable(self, syllable_fragment):
        """Verify that the fragment matches one syllable in the phonology"""
        # vet features in syllable fragment
        features = [
            set(self.phonology.phonetics.get_features(sound))
            for sound in syllable_fragment
        ]
        # traverse possible syllables looking for featureset matches
        for syllable in self.get().values():
            if len(syllable) != len(features):
                continue
            # syllable applies to all featureset in features
            matches = [
                set(features[i]).issuperset(syllable[i])
                for i in range(len(features))
            ]
            if all(matches):
                print(f"{''.join(syllable_fragment)} matches syllable {syllable}!")
                return True
        return False

    def count(self, sounds, minimally=False):
        syllables = self.syllabify(sounds, minimally=minimally)
        if not isinstance(syllables, list):
            raise ValueError(f"Could not count syllables - invalid syllables list {syllables}")
        return len(syllables)

    # TODO: smart/adaptive syllabify method
    #   - (currently: add max or min syllable when one is possible)
    #   - look ahead/behind to determine syllable boundary
    #   - best fit across whole words
    # NOTE: ideas
    #   - build out every letter right to however many syllables it can be a part of
    #   - compare potential non-overlapping syllables
    #   - return one possible non-overlapping split for the whole sample
    def syllabify(self, sounds, minimally=False):
        """Separate sounds into a list of syllables using one of two very basic
        approaches, linearly searching for either the shortest or the longest possible
        syllable matches depending on the value of the minimally flag."""
        # verify sounds list input
        if not isinstance(sounds, list):
            raise TypeError(f"Syllables resyllabify expected list of strings not {sounds}")
        
        # create list of known sounds
        vetted_sounds = [
            sound for sound in sounds
            if self.phonology.phonetics.has_ipa(sound)
        ]

        # Build word with syllables list of lists

        # look for the smallest valid syllables
        if minimally:
            syllabification = redacc.redacc(            # reduce to a list of syllable lists
                vetted_sounds,
                lambda sound, word: (
                    word[:-1] + [word[-1] + [sound]],   # add sound to last syllable list
                    word + [[sound]],                   # add sound to new syllable list
                )[self.is_syllable(word[-1])],          # if last list is a full syllable
                [[]]                                    # empty word with one empty syllable
            )
        # look for maximal valid syllables
        else:
            syllabification = self.syllabify_max(sounds)

        # check final syllable sounds were not leftovers (they are also a valid syllable)
        # TODO: include as semantic tests - may not be value errors for this method
        if not self.is_syllable(syllabification[-1]) or len(flat_list.flatten(syllabification)) != len(sounds):
            raise ValueError(f"Syllables failed to syllabify all sounds: {syllabification}")
        
        return syllabification

    # TODO: less expensive look-ahead finalizing left syllable when right one is
    #   - worry about orphaned stuff
    #   - checking current syll, ensure remaining letters can form at least one more chunk
    #   - if you get to one possible syllable, and you have one behind it,
    #       is that previous one guaranteed to be good?
    #   - "kaan" in lang c CV, CVVn: you will close out CV, V before getting to CVVn
    #   - also recall dealing with: CV, CVC "tatata", "tat"
    def syllabify_suboptimally(self, sounds):
        """Split a sound sample into a list of syllable lists, closing out syllables
        as the sample sequence is being evaluated."""
        vetted_sample = [
            s for s in sounds
            if self.phonology.phonetics.has_ipa(s)
        ]
        if len(sounds) != vetted_sample:
            return
        syllabification = []
        #last_syllable = []
        #current_syllable = []
        for i in reversed(range(len(vetted_sample))):
            sample_cut = sounds[:i]
            if self.is_syllable(sample_cut):
                if i == len(sounds):
                    return sample_cut
                can_syllabify_here = False
                for j in reversed(range(len(vetted_sample[i:]))):
                    if self.is_syllable(vetted_sample[i:j]):
                        can_syllabify_here = True
                        break
                if can_syllabify_here:
                    syllabification.append(sample_cut)
            else:
                continue
        return syllabification

    def _build_out_syllables(self, syllable, tracking_index, syllable_tracker, sound_count):
        """Go through a tracked list of possible syllables starting at specific indexes
        in a sound sample and determine a syllable concatenation path that includes all
        sounds in the sample and each sound is only represented once."""
        return []

    def syllabify_optimally(self, sounds):
        """Syllabify sound sample into a list of syllable lists ensuring all sounds
        in the sample are included in final syllabification."""
        # list of possible syllable sounds per starting index
        tracking = {}
        # collect all possible sound sequences
        for i, s in enumerate(sounds):
            tracking.setdefault(i, []).append([])
            for t in tracking[i]:
                t.append(s)
        # filter down to valid syllables only
        tracking = {
            i: [seq for seq in t if self.is_syllable(seq)]
            for i, t in tracking.items()
        }
        # compare possible syllables for concatenated syllables covering all sounds
        total_count = len(sounds)
        for i in tracking:
            for syllable in t:
                syllables = self._build_out_syllables(syllable, i, tracking, total_count)
                if syllables:
                    return syllables
        return None

    def _syllabify_max_core_loop(self, sounds, start_i=0, end_i=None):
        """Inner recursive end-to-start search for longest possible syllable"""
        end_i = len(sounds) if end_i is None else end_i
        if start_i == end_i or end_i < 1:
            return []
        elif self.is_syllable(sounds[start_i:end_i]):
            return [sounds[start_i:end_i]] + self._syllabify_max_core_loop(
                sounds,
                start_i = end_i,
                end_i = len(sounds)
            )
        else:
            return self._syllabify_max_core_loop(
                sounds[start_i:-1],
                start_i = start_i,
                end_i = end_i-1
            )

    def syllabify_max(self, sounds):
        """Break a sound sample into a list of longest possible syllables lists"""
        syllabification = []
        end_i = len(sounds)
        start_i = 0
        while start_i is not None and start_i < end_i:
            syllable, start_i = self._syllabify_max_core_loop(sounds[start_i:], end_i)
            syllable and syllabification.append(syllable)
        if len(flat_list.flatten(syllabification)) != len(sounds):
            raise ValueError(f"Failed to syllabify all sounds in {''.join(sounds)}: {syllabification}")
        return syllabification

