from uuid import uuid4
from ..tools import redacc, flat_list
import random

# TODO: optional/dependent sonority (see sonority scale list and associated methods below)
# - add_sonority_dependency()
# - e.g. CCV: if s -> {p,t,k,l,w}, then if st -> {r}

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
        
        # sonority scale dependency map
        # applied in given order for onset and reverse for coda
        self.sonority = {}

        # store features that identify the syllable nucleus
        # NOTE: defaults to vowel if present in phonetics
        self.nucleus = {'vowel'} if self.phonology.phonetics.has_feature("vowel") else set()

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
        if not syllable_fragment:
            return False

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
    def _find_left_syllable(self, sounds):
        if not sounds:
            return []
        for i in reversed(range(len(sounds) + 1)):
            if self.is_syllable(sounds[:i]):
                syllabified_sounds = [sounds[:i]] + self._find_left_syllable(sounds[i:])
                if None in syllabified_sounds:
                    continue
                return syllabified_sounds
        return [None]

    def syllabify(self, sounds):
        """Separate sounds into a list of syllables, linearly closing out one syllable
        when another possible syllable follows."""
        
        # Verify sounds list input
        if not isinstance(sounds, list):
            raise TypeError(f"Syllables resyllabify expected list of strings not {sounds}")

        # Build word with syllables list of lists looking for syllables
        vetted_sample = self._vet_sounds(sounds)
        if not vetted_sample:
            raise ValueError(f"Invalid sounds in sample {sounds}")

        # Loop through building maximally valid syllables from the left
        syllabification = self._find_left_syllable(vetted_sample)

        # TODO: handle uncut or imperfectly cut samples
        if not syllabification or None in syllabification:
            print(f"Could not find valid syllable in {vetted_sample}")
            return

        return syllabification

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

    # Shape

    def add_nucleus(self, feature):
        if not self.phonology.phonetics.has_feature(feature):
            return
        self.nucleus.add(feature)

    def reset_nucleus(self):
        self.nucleus = set()

    # Sonority

    # TODO: apply sonority when building syllables
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

        # Syllable Shape: choose one syllable and break into components
        syllable_features = random.choice(possible_syllables)
        syllable_shape = {
            'onset': [],
            'nucleus': [],
            'coda': []
        }
   
        # TODO: consider if sonority scale too rigid for generating 
        #   ? - go with dependency map instead
        #   ? - interject

        # Determine nucleus start and end
        nucleic_indexes = []
        syllable_core_features = []
        for i, features in enumerate(syllable_features):
            if set(features) & self.nucleus:
                nucleic_indexes.append(i)
        # Build onset features up to the nucleus
        for i in range(len(syllable_features[:nucleic_indexes[0]])):
            if i < len(self.sonority):
                syllable_core_features.append(self.sonority[i])
            else:
                syllable_core_features.append(self.sonority[-1])
        # Build nucleus
        for i in nucleic_indexes:
            syllable_core_features.append(set(syllable_features[i]) | self.nucleus)
        # Build coda features after the nucleus
        for i in range(len(syllable_features[nucleic_indexes[-1]+1:])):
            if i < len(self.sonority):
                syllable_core_features.append(list(reversed(self.sonority))[i])
            else:
                syllable_core_features.append(self.sonority[1])

        # Build sonority out from nucleus

        # Build Syllable and Sonority Shape
        # Syllable Shape: split syllable into onset, nucleus, coda
        # Sonority Shape: fill out syllable shape following sonority scale
        
        final_features = syllable_shape['onset'] + syllable_shape['nucleus'] + syllable_shape['coda']

        # Sound Shape: select a sound for each features element in the syllable shape
        syllable_sounds = []
        for features in final_features:
            sounds = self.phonology.phonetics.get_ipa(
                features,
                filter_phonemes=self.phonology.inventory()
            )
            sounds and syllable_sounds.append(random.choice(sounds))

        return syllable_sounds
    
    def get_sonority(self):
        """Read all dependencies along the sonority scale"""
        return self.sonority       

    def add_sonority(self, feature, dependent_feature):
        """Order one feature below another in the sonority map. Features will be
        applied hierarchically in a dependency chain until a sound with no dependency
        is found, then any new sound will be chosen (see Syllables.build)."""
        if self.phonology.phonetics.has_feature(feature):
            raise KeyError(f"Cannot overwrite sonority for already existing feature {feature}")
        self.sonority[feature] = dependent_feature
        return self.sonority

    def update_sonority(self, feature, dependent_feature):
        """Update one feature's dependent feature in the sonority map"""
        if not self.phonology.phonetics.has_feature(feature):
            raise KeyError(f"Cannot update sonority for nonexisting feature {feature}")
        self.sonority[feature] = dependent_feature
        return self.sonority

    def remove_sonority(self, feature, err_if_absent=True):
        """Remove existing feature dependency from the sonority map"""
        self.sonority.pop(feature) if err_if_absent else self.sonority.pop(feature, None)
        return self.sonority

    # TODO: TEST! & consider scale + exclusivity + inclusivity
    def chain_sonority(self, sonority_scales=None):
        """Return a list of hierarchy feature chains formable from the sonority scale"""
        # make starter sonority features scales on first call
        sonority_scales = [
            [feature, dependent_feature]
            for feature, dependent_feature in self.sonority.items()
        ] if sonority_scales is None else sonority_scales
        # traverse features adding sonority dependencies
        did_reach_dependency = False
        for scale in sonority_scales:
            if self.sonority.get(scale[-1]):
                did_reach_dependency = True
                scale.append(self.sonority[scale[-1]])
        # stop recursing if reached terminal dependencies
        if not did_reach_dependency:
            return sonority_scales
        # keep branching through dependencies' dependencies
        return self.chain_sonority(sonority_scales)

