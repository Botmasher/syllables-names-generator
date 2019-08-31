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
                #print(f"{''.join(syllable_fragment)} matches syllable {syllable}!")
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
        # look for the smallest or largest valid syllables
        syllabification = self.syllabify_min(vetted_sounds) if minimally else self.syllabify_max(vetted_sounds)
        
        # check final syllable sounds were not leftovers (they are also a valid syllable)
        # TODO: include as semantic tests - may not be value errors for this method
        if not self.is_syllable(syllabification[-1]) or len(flat_list.flatten(syllabification)) != len(vetted_sounds):
            raise ValueError(f"Syllables failed to syllabify all sounds: {syllabification}")
        
        return syllabification

    def syllabify_min(self, sample):
        """Break sound sample into smallest possible syllables sequentially from
        left to right. This may leave stranded or leftover syllables"""
        return redacc.redacc(            # reduce to a list of syllable lists
            sample,
            lambda sound, word: (
                word[:-1] + [word[-1] + [sound]],   # add sound to last syllable list
                word + [[sound]],                   # add sound to new syllable list
            )[self.is_syllable(word[-1])],          # if last list is a full syllable
            [[]]                                    # empty word with one empty syllable
        )

    # Finalize left syllable when right leftover material also starts a syllable
    def _syllabify_max_loop(self, sample):
        """Split off the largest valid syllable from the left where the remaining
        right material also starts a single syllable"""
        # check sample for a single syllable shrinking window from right
        for i in reversed(range(len(sample) + 1)):
            sample_focus = sample[:i]
            sample_leftover = sample[i:]
            # check leftover right-side sounds for another syllable to ensure
            # that this syllable is valid without jeopardizing rightmore ones
            if self.is_syllable(sample_focus):
                #raise Exception(f"HERE! syll: {sample_focus}, left: {sample_leftover}")
                if not sample_leftover:
                    return sample_focus
                for j in reversed(range(len(sample_leftover) + 1)):
                    if self.is_syllable(sample_leftover[:j]):
                        return sample_focus
        return
    #
    def syllabify_max(self, sounds):
        """Split a sound sample into a list of syllable lists, closing out longest 
        identified syllables as the sample sequence is being evaluated."""
        unknown_sounds = []
        vetted_sample = [
            s
            if self.phonology.phonetics.has_ipa(s)
            else unknown_sounds.append(s)
            for s in sounds
        ]
        if unknown_sounds:
            raise ValueError(f"Invalid unsyllabifiable sounds in sample: {unknown_sounds}")

        syllabification = []
        start_i = 0
        while start_i < len(vetted_sample):
            sample_cut = vetted_sample[start_i:]
            syllable = self._syllabify_max_loop(sample_cut)
            if syllable:
                start_i += len(syllable)
                syllabification.append(syllable)
            else:
                # TODO: handle uncut or imperfectly cut samples
                raise ValueError(f"Could not find a valid syllable in {sample_cut}")
        return syllabification

