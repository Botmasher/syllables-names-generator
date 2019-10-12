from .hierarchy import Hierarchy
from ..tools import redacc
import random

# TODO: optional/dependent sonority (see sonority scale list and associated methods below)
# - add_sonority_dependency()
# - e.g. CCV: if s -> {p,t,k,l,w}, then if st -> {r}
class Phonotactics:
    def __init__(self, phonology):
        # check that features exist
        self.phonology = phonology
        
        # feature scale and dependencies
        self.hierarchy = Hierarchy()

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
        """Split syllable liss into onset, nucleus, coda.
        Params:
            syllable_features (list): list of string lists, each string representing a feature
        """
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

    # TODO: how to ensure gemination not just found down here in phonotactics?
    #   - also syllable interfaces, since san-nas yields gem
    #   - this brings up another q about restrictions along syllable bounds
    #
    # TODO: for each slot use hierarchy to choose a sound
    #   - no hierarchy -> open choice
    #   - each key is a single string feature or ipa, with ipa checked first
    #   - search for minimum same-length hierarchy element for codas, onsets
    #   - restrictions on the next slot are based on actual sounds chosen
    #
    #   - example: voiced, sibilant then next select sibilant > stop, voiced > voiced
    #   - example: voicing only on certain left-selects (like (voiced, stop) > voiced)
    #
    # TODO: allow doubles (like nmV or nnV)
    #   - beyond just adding say "nasal", "nasal" to sonority
    #
    # TODO: when building C sound slots from dependency chains
    #   - get all dependency chains that are at least as long as cluster
    #   - apply for onset, reverse for coda

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
