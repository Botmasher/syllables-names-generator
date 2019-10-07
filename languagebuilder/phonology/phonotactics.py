from ..tools import redacc
import random

# TODO: optional/dependent sonority (see sonority scale list and associated methods below)
# - add_sonority_dependency()
# - e.g. CCV: if s -> {p,t,k,l,w}, then if st -> {r}
class Phonotactics:
    def __init__(self, phonology):
        # check that features exist
        self.phonology = phonology
        
        # feature dependencies - if outer feature is X, inner should be Y
        self.dependencies = {
            # each left feature defines its right followers
            # feature: {features}
        }

        # TODO: allow doubles (like nmV or nnV)
        # - beyond just adding say "nasal", "nasal" to sonority
        self.sonority = []

       # configure syllable nucleus
        # TODO: consider defaulting to ['vowel'] if present
        self.nuclei = set()

        # first draw likelihoods
        # TODO: how likely each is to be chosen
        # OR just select from chains/sonority that are at onset/coda length?
        # self.lihelihoods = {
        #     'onset': {},
        #     'coda': {},
        #     'nucleus': {}
        # }

    # Syllable parts - nucleus

    def is_features_list(self, features):
        if not isinstance(features, (list, tuple)):
            return False
        elif False in [self.phonology.phonetics.has_feature(feature) for feature in features]:
            return False
        else:
            return True

    def add_nucleus(self, features):
        if not self.is_features_list(features):
            return
        self.nuclei.add(features)
        return self.nuclei

    def get_nuclei(self):
        return self.nuclei

    def remove_nucleus(self, features):
        if features in self.nuclei:
            self.nuclei.remove(features)
            return True
        return False

    def clear_nuclei(self):
        self.nuclei.clear()
        return self.nuclei

    # Syllable parts - onset and coda

    # TODO: when building C sound slots from dependency chains
    #   - get all dependency chains that are at least as long as cluster
    #   - apply for onset, reverse for coda
    # 
    # TODO: add and read as chains (allows adding sonority scale!)
    #   - each key is a single string feature or ipa, with ipa checked first
    def get_sonority(self):
        """Read the left-to-right sonority sequence scale"""
        return self.sonority
    
    def set_sonority(self, sonority):
        """Overwrite the existing sonority scale with a new sequence"""
        self.sonority = list(sonority)

    def add_sonority(self, feature, position=0):
        """Add a single feature to a specific (-1 for innermost, 0 for outermost
        (default)) slot in the existing sonority scale. Scale applies left to right
        for onsets and right to left for codas."""
        # check for valid feature
        if not self.is_features_list([feature]):
            raise ValueError(f"Expected sonority value to be a feature - instead found {feature}")
        # add to end of scale
        if position < 0:
            self.sonority.append(feature)
        # add to front or within scale
        else:
            self.sonority = self.sonority[:position] + [feature] + self.sonority[position:]
        return self.sonority

    def remove_sonority(self, position=None, feature=None):
        """Remove a single feature from the sonority. If a feature occurs multiple times,
        all instances are deleted. If an index position is given, it is used instead."""
        # remove at given index
        if position is not None:
            self.sonority = self.sonority[:position] + self.sonority[position+1:]
            return self.sonority
        # find and remove occurrences of feature
        self.sonority = list(filter(
            lambda sonority_value: sonority_value != feature,
            self.sonority
        ))
        return self.sonority

    def get_dependencies(self):
        """Read all of the features dependencies (if feature key selected for left sound
        slot, next right sound slot must be among the feature values included list and
        must not be among the feature values excluded list."""
        return self.dependencies

    def add_dependencies(self, *features):
        """Order features below each other in the dependency map from left to right.
        Params:
           *features (list): sequence of features to add as dependency key-values
        """
        if not self.is_features_list(features):
            raise ValueError(f"Cannot create chain using nonexisting feature")

        # traverse adding each left feature to keys and right to values
        for i in range(len(features)):
            # stop looping when run out of right (next) features
            if i >= len(features) - 1:
                break
            left_feature = features[i]
            right_feature = features[i + 1]
            self.dependencies.setdefault(left_feature, set()).add(right_feature)
        
        return self.dependencies

    def remove_dependencies(self, *features):
        """Remove existing feature dependencies from the map in a left-right chain."""
        # delete values from dependencies
        removable_keys = []
        for left_feature, right_features in self.dependencies.items():
            for feature in features:
                right_features.discard(feature)
            if not self.dependencies.get(left_feature):
                removable_keys.append(left_feature)
        
        # delete keys with empty values
        for k in removable_keys:
            self.dependencies.pop(k)
        
        # delete keys from dependencies
        for feature in features:
            self.dependencies.pop(feature, None)
        
        return self.dependencies

    # Split and shape syllable parts phonotactically

    def is_features_list_overlap(self, featureslist_a, featureslist_b, all_a_in_b=True):
        """Compare two lists of featuresets to determine if they are same-length
        overlapping features collections."""
        if len(featureslist_a) != len(featureslist_b):
            return False
        for i in range(len(featureslist_a)):
            feature_overlap = set(featureslist_a[i]) & set(featureslist_b[i])
            if not feature_overlap or (all_a_in_b and len(feature_overlap) != len(featureslist_a)):
                return False
        return True

    def partition_syllable(self, syllable_features):
        """Split syllable list of featureslists into onset, nucleus, coda"""
        nucleus_indexes = []
        for i, features in enumerate(syllable_features):
            for nucleus in self.nuclei:
                if self.is_features_list_overlap(features[i:i+len(nucleus)], nucleus):
                    nucleus_indexes += [i, i+len(nucleus)]
                    break
        
        if not nucleus_indexes:
            return

        syllable_parts = {
            'onset': syllable_features[:nucleus_indexes[0]],
            'coda': syllable_features[nucleus_indexes[0]:nucleus_indexes[1]],
            'nucleus': nucleus_indexes[1]
        }

        return syllable_parts

    
    # TODO: update to use sonority plus custom dependencies to build out possible chains
    
    # TODO: how to ensure gemination not just found down here in phonotactics?
    #   - also syllable interfaces, since san-nas yields gem
    #   - this brings up another q about restrictions along syllable bounds
    def shape(self, syllable_features, gaps=True, doubles=True, triples=False):
        """Fill out a syllable with all defined phonotactics including dependencies
        and sonority. Features walk hierarchically down the sonority scale (with gaps)
        until a dependency chain inclusion/exclusion is found, then the dependency
        chain is followed until a sound with no dependency is found, at which point
        vetting switches back to the sonority scale.      
        """

        # break up and check syllables
        syllable_pieces = self.partition_syllable(syllable_features)

        if not syllable_pieces:
            return

        # TODO: test, and what if no same-length member in chains? go higher? random?
        
        # build syllable features shape from sonority and dependencies
        
        syllable_shape = []

        # shape base featureset for each onset sound
        onset_shape = []
        for onset in syllable_pieces['onset']:
            # TODO: choose each onset shape
            # - if last feature has dependencies, follow one
            # - if not, follow sonority
            #   - skips
            #   - plateaux?
            #   - combine each onset seed and shape
            #   - track where in sonority and how much left to go (count at outset?)
            onset_shape.append()
            left_features = list(filter(
                lambda feature: feature in self.dependencies,
                onset_shape[-1]
            )) if onset_shape else []
            if left_features:
                onset_shape.append(random.choice(self.dependencies[left_features[0]]))
            else:
                pass
        syllable_shape.append(onset_shape)

        # shape nucleus
        nucleus_shape = [random.choice(self.nuclei)] + syllable_pieces['nucleus']
        syllable_shape.append(nucleus_shape)

        # shape coda
        coda_shape = []
        for coda in syllable_pieces['coda']:
            # TODO: choose in line with onset
            pass
        syllable_shape.append(coda_shape)

        # Build Syllable and Sonority Shape
        # Syllable Shape: split syllable into onset, nucleus, coda
        # Sonority Shape: fill out syllable shape following sonority scale
        
        return #onset_features + nucleus_features + coda_features
