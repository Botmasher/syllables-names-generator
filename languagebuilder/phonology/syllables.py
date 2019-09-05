from uuid import uuid4
from ..tools import redacc, flat_list
import random

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
        
        # ordered sonority scale
        # applied in given order for onset and reverse for coda
        self.sonority = []

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

    # Syllabification

    def count(self, sounds, minimally=False):
        """Count the number of syllables in a sound sample"""
        syllables = self.syllabify_min(sounds) if minimally else self.syllabify(sounds)
        if not isinstance(syllables, list):
            raise ValueError(f"Could not count syllables - invalid syllables list {syllables}")
        return len(syllables)

    def _vet_sounds(self, sample):
        """Filter a list of known sounds from a sound sample list"""
        vetted_sounds = [
            sound for sound in sample
            if self.phonology.phonetics.has_ipa(sound)
        ]
        return vetted_sounds

    # Semioptimal syllabify method
    #   - build out every letter right to however many syllables it can be a part of
    #   - compare potential non-overlapping syllables
    #   - return one possible non-overlapping split for the whole sample
    def syllabify(self, sounds):
        """Separate sounds into a list of syllables, linearly closing out one syllable
        when another possible syllable follows."""
        
        # Verify sounds list input
        if not isinstance(sounds, list):
            raise TypeError(f"Syllables resyllabify expected list of strings not {sounds}")

        # Build word with syllables list of lists looking for syllables
        unknown_sounds = []
        vetted_sample = self._vet_sounds(sounds)
        if unknown_sounds:
            raise ValueError(f"Invalid unsyllabifiable sounds in sample: {unknown_sounds}")

        # Loop through building maximally valid syllables from the left
        syllabification = []
        start_i = 0
        while start_i < len(vetted_sample):
            sample_cut = vetted_sample[start_i:]
            syllable = self._syllabify_loop(sample_cut)
            if syllable:
                start_i += len(syllable)
                syllabification.append(syllable)
            else:
                # TODO: handle uncut or imperfectly cut samples
                raise ValueError(f"Could not find a valid syllable in {sample_cut}")
        
        # Check final syllable sounds were not leftovers (they are also a valid syllable)
        # TODO: include as semantic tests - may not be value errors for this method
        if not self.is_syllable(syllabification[-1]) or len(flat_list.flatten(syllabification)) != len(vetted_sample):
            raise ValueError(f"Syllables failed to syllabify all sounds: {syllabification}")
        
        return syllabification

    # Finalize left syllable when right leftover material also starts a syllable
    def _syllabify_loop(self, sample):
        """Split off the largest valid syllable from the left where the remaining
        right material also starts a single syllable"""
        # check sample for a single syllable shrinking window from right
        for i in reversed(range(len(sample) + 1)):
            sample_focus = sample[:i]
            sample_leftover = sample[i:]
            # check leftover right-side sounds for another syllable to ensure
            # that this syllable is valid without jeopardizing rightmore ones
            if self.is_syllable(sample_focus):
                if not sample_leftover:
                    return sample_focus
                for j in reversed(range(len(sample_leftover) + 1)):
                    if self.is_syllable(sample_leftover[:j]):
                        return sample_focus
        return

    def syllabify_min(self, sample):
        """Break sound sample into smallest possible syllables sequentially from
        left to right. This may leave stranded or leftover syllables"""
        vetted_sample = self._vet_sounds(sample)
        return redacc.redacc(            # reduce to a list of syllable lists
            vetted_sample,
            lambda sound, word: (
                word[:-1] + [word[-1] + [sound]],   # add sound to last syllable list
                word + [[sound]],                   # add sound to new syllable list
            )[self.is_syllable(word[-1])],          # if last list is a full syllable
            [[]]                                    # empty word with one empty syllable
        )

    # Sonority

    # Apply sonority when building syllables
    def build(self, restrictions=None, use_sonority=True, sonority_edge=False):
        """Use defined syllables, sonority and features and ipa from phonology to 
        generate the phonemes of one valid syllable.
        
        params:
            restrictions (list):    restrict options to specific syllable ids
            use_sonority (bool):    filter syllable sounds to fit sonority scale
            sonority_edge (bool):   maintain sonority when codas/onsets are longer than
                defined sonority scale, otherwise step back up and down the scale
        """
        
        # filter possible syllable options
        possible_syllables = [
            s for i, s in self.syllables.items()
            if not restrictions or i in restrictions
        ]

        # Syllable Shape: choose one syllable shape
        syllable_shape = random.choice(possible_syllables)

        # Sonority Shape: fill out the shape with sonority scale
        shape = {
            'onset': [],
            'nucleus': [],
            'coda': [],
            'unknown': []
        }
        # scaled features - anything past edge of extremes maintains vs rescales
        for featureset in syllable_shape:
            building_onset = True
            building_nucleus = False
            building_coda = False
            if building_onset:
                if 'vowel' in featureset:
                    building_onset = False
                    building_nucleus = True
                    shape['nucleus'].append(featureset)
                else:
                    shape['onset'].append(featureset)
            elif building_nucleus:
                if 'consonant' in featureset:
                    building_nucleus = False
                    building_coda = True
                    shape['coda'].append(featureset)
                else:
                    shape['nucleus'].append(featureset)
            elif building_coda:
                shape['coda'].append(featureset)
            else:
                shape['unknown'].append(featureset)
        if shape['unknown']:
            raise ValueError(f"Failed to build syllable - could not place features {shape['unknown']}")

        # Sound Shape: select sounds following each element in the shape so far
        syllable_sounds = [
            random.choice(self.phonology.phonetics.get_ipa(
                f,
                filter_phonemes=self.phonology.inventory()
            )) for f in shape['onset'] + shape['nucleus'] + shape['coda']
        ]

        return syllable_sounds

    # TODO: optional or dependent
    # - e.g. CCV: if s -> {p,t,k,l,w}, then if st -> {r}

    def get_sonority(self):
        """Read the sonority scale"""
        return self.sonority

    def set_sonority_scale(self, sonority_scale):
        """Replace the entire sonority scale with a new sequence of features"""
        # validate list of features
        if not isinstance(sonority_scale, list):
            raise ValueError(f"Failed to set sonority scale - expected list of features not {sonority_scale}")
        for feature in sonority_scale:
            if not self.phonology.phonetics.has_feature(feature):
                raise ValueError(f"Failed to set sonority scale - unknown feature {feature}")
        # update the scale
        self.sonority = sonority_scale
        return self.sonority        

    def add_sonority(self, feature, position):
        """Order one feature within the sonority scale"""
        if not self.phonology.phonetics.has_feature(feature):
            return
        if feature in self.sonority:
            return self.update_sonority(feature, position)
        self.sonority = self.sonority[:position] + [feature] + self.sonority[position:]
        return self.sonority

    def update_sonority(self, feature, position):
        """Reorder one existing feature within the sonority scale"""
        current_position = self.sonority.index(feature)
        if not current_position:
            return
        new_position = position - 1 if position > current_position else position
        self.sonority.pop(current_position)
        self.sonority = self.sonority[:new_position] + [feature] + self.sonority[new_position:]
        return self.sonority

    def remove_sonority(self, feature):
        """Remove one feature from the sonority scale"""
        position = self.sonority.index(feature)
        self.sonority.pop(position)
        return self.sonority
