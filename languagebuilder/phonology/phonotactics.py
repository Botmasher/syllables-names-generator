from .hierarchy import Hierarchy
from ..tools import redacc
import random
from uuid import uuid4

# NOTE: Phonotactics esp scale & dep build left-to-right. "Progressive" constraints are
# unideally handled either during syllable definition, e.g. in specific syllable types,
# or after syllable build, e.g. through sound changes
#
# NOTE: history, thoughts and issues leading to current solution
#   Recall that features passed can be any at the syllable type level, and any
#   at the syllable shape level (phonotactics)
#   OLD: scale or dependencies, then expanded to scale + dependencies
#       - both defined right options/filters given left sounds
#       - dependencies stored excluded or included right features/sounds for a left
#       - dependencies allowed looping back to scale if chain ended but feature in scale
#       - scale not only sonority, any feature pluggable (could do based on places, ...)
#       - loops, repetitions, ends, skips, and count were tricky to manage and generate
#       - e.g. CCCV: if s -> {p,t,k,l,w}, t -> {r}, no dependencies key r -> scale for say strj-
#       - e.g. CCCV: if s -> {p,t,k,l,w}, t -> None, end shape at st- (note it's CV!)
#  NEW: simplify to whole shapes - Types define syllables. Shapes refine types.
#       - keep scales and excludes in separate maps (each is a list of featuresets)
#           - dos are whole sequential shapes
#           - dos can be set to be gappable (have skippable sound slots)
#           - donts are feature or sound sequences that should not be built
#           - use donts to avoid building specific sequences
#       - flexibility: each set in a list is either features or ipa (but not mixed)
#       - if no dos or donts available, choose any sounds matching typeslots while shaping
#       - multiple ways to do options:
#           - skippable syntax: [featureset, [skippable featureset]]
#           - multiples: scale 1 [featureset, optional_featureset], scale 2 just [featureset]
#       - one scale can be marked as the hierarchy (id stored) and so used as the goto
#           - in this case prefer while shaping?
#           - choose maybe 50% of the time?
#           - or default to it and only use other scales when combinations chosen?
#       - repeatables/geminates are meant to be explicit like [nasal, nasal]
#       - storing the entire shape allows straightforward adding for users

# TODO: features across syllable boundaries

class Phonotactics:
    def __init__(self, phonology):
        # check that features exist
        self.phonology = phonology
        
        # feature scale and dependencies
        self.hierarchy = Hierarchy(phonology)
        self.scale = self.hierarchy.scale
        self.dependencies = self.hierarchy.dependencies
        self.recommend = self.hierarchy.recommend

       # syllable nuclei map
        # TODO: consider weighting and defaulting to ['vowel'] if present
        self.nuclei = {
            # 'id': [featuresets],
        }

        # first draw likelihoods
        # TODO: how likely each is to be chosen - see nuclei weight comment above
        # OR just select from chains/sonority that are at onset/coda length?
        # self.lihelihoods = {
        #     'onset': {},
        #     'coda': {},
        #     'nucleus': {}
        # }

    # Syllable parts - nucleus
    def is_features_list(self, features):
        """Check that input is a collection containing only valid features"""
        return all([self.phonology.phonetics.has_feature(f) for f in features])

    def add_nucleus(self, *features):
        """Vet, build and add one new nucleus. Each nucleus is a list of featuresets.
        Input may contain single feature strings or syllable abbreviations."""
        # vet features for valid elements
        vetted_features = self.phonology.syllables.structure(features)
        # build nucleus as a featuresets list
        nucleus = []
        for featurelist in vetted_features:
            if not self.is_features_list(featurelist):
                raise ValueError(f"Phonotactics failed to add nucleus with invalid features - {featurelist}")
            featureset = set(featurelist)
            nucleus.append(featureset)
        # add nucleus to nuclei
        nucleus_id = f"nucleus-{uuid4()}"
        self.nuclei[nucleus_id] = nucleus
        return self.nuclei

    def get_nuclei(self):
        """Read the entire nuclei map"""
        return self.nuclei

    def remove_nucleus(self, nucleus_id):
        """Delete one nucleus entry and key in the nuclei map"""
        return self.nuclei.pop(nucleus_id)
    
    def clear_nuclei(self, return_old=False):
        """Empty out the entire nuclei map"""
        nuclei_copy = dict(self.nuclei)
        self.nuclei.clear()
        if return_old:
            return nuclei_copy
        return self.nuclei

    # Split and shape syllable parts phonotactically

    def is_features_list_overlap(self, featureslist_a, featureslist_b, all_a_in_b=True):
        """Compare two lists of featuresets to determine if they are overlapping
        features collections."""
        if len(featureslist_a) != len(featureslist_b):
            return False
        for i in range(len(featureslist_a)):
            feature_overlap = set(featureslist_a[i]) & set(featureslist_b[i])
            if not feature_overlap or (all_a_in_b and len(feature_overlap) != len(featureslist_a[i])):
                return False
        return True

    def partition_syllable(self, syllable_features):
        """Split syllable liss into onset, nucleus, coda.
        Params:
            syllable_features (list): list of string lists, each string representing a feature
        """
        nucleus_indexes = []
        for i in range(len(syllable_features)):
            for nucleus in self.nuclei.values():
                if self.is_features_list_overlap(syllable_features[i:i+len(nucleus)], nucleus):
                    nucleus_indexes += [i, i+len(nucleus)]
                    break
        
        if not nucleus_indexes:
            raise ValueError(f"Phonotactics failed to partition syllable with unknown nucleus - {syllable_features} not in {self.nuclei}")

        return {
            'onset': syllable_features[:nucleus_indexes[0]],
            'nucleus': syllable_features[nucleus_indexes[0]:nucleus_indexes[1]],
            'coda': syllable_features[nucleus_indexes[1]:]
        }

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

    def shape(self, raw_syllable, gaps=True, doubles=True, triples=False):
        """Fill out a syllable with all defined phonotactics including dependencies
        and sonority. Features walk hierarchically down the sonority scale (with gaps)
        until a dependency chain inclusion/exclusion is found, then the dependency
        chain is followed until a sound with no dependency is found, at which point
        vetting switches back to the sonority scale.      
        """
        # vet syllable for valid features
        syllable_features = self.phonology.syllables.structure(raw_syllable)

        # break up and check syllables
        syllable_pieces = self.partition_syllable(syllable_features)
        if not syllable_pieces:
            raise ValueError(f"Phonotactics failed to shape syllable - unknown syllable {syllable_features}")

        # prepare to build syllable features shape from scale and dependencies
        syllable_shape = {piece: [] for piece in syllable_pieces}

        # shape base featureset for each onset sound

        # TODO: on no phonemes available recommend a different feature from scale
        #   - if scale look for anything on the right on scale
        #   - if dependencies look down the chain
        #   - but what if still sounds to fill but no good sound left?
        #   - do we need to check that features in phonol not just features in scale?
        for current_features in syllable_pieces['onset']:
            last_sound = syllable_shape['onset'][-1] if syllable_shape['onset'] else None
            syllable_shape['onset'].append(self.recommend(last_sound, current_features))

        # shape nucleus
        nucleus_id = random.choice(list(self.nuclei))
        nucleus_shape = self.nuclei[nucleus_id]
        # TODO: also recommend through Hierarchy (could recommend handle nuclei?)
        for featureset in nucleus_shape:
            if not self.phonology.get_phonemes(featureset):
                raise Exception(f"Phonotactics failed to shape nucleus - invalid features {featureset}")
            nucleus_sound = random.choice(self.phonology.get_phonemes(featureset))[0]
            syllable_shape['nucleus'].append(nucleus_sound)

        # shape coda
        for current_features in syllable_pieces['coda']:
            last_sound = syllable_shape['coda'][0] if syllable_shape['coda'] else None
            syllable_shape['coda'] = [self.recommend(last_sound, current_features)] + syllable_shape['coda']

        # NOTE: syllable_shape has turned to a full fill-in of sound symbols
        syllable_sounds = [
            sound for sound in 
            syllable_shape['onset'] + syllable_shape['nucleus'] + syllable_shape['coda']
        ]
        syllable_shape.clear()
        return syllable_sounds

