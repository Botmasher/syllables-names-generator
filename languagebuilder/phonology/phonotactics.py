# TODO: optional/dependent sonority (see sonority scale list and associated methods below)
# - add_sonority_dependency()
# - e.g. CCV: if s -> {p,t,k,l,w}, then if st -> {r}
class Phonotactics:
    def __init__(self, phonology, syllables):
        # 
        self.phonology = phonology
        self.syllables = syllables

        # syllable edges sonority scale
        # TODO: apply in given order for onset and reverse for coda
        self.sonority = []
        
        # feature dependencies - if outer feature is X, inner should be Y
        self.dependencies = {}

        # first draw likelihoods
        # TODO: how likely each is to be chosen
        # OR just select from chains/sonority that are at onset/coda length?
        self.lihelihoods = {
            'onset': {},
            'coda': {},
            'nucleus': {}
        }

        # configure syllable nucleus
        # TODO: consider defaulting to ['vowel'] if present
        self.nuclei = {}

    def is_features(self, features):
        if not isinstance(features, (list, tuple)):
            return False
        elif False in [self.phonology.phonetics.has_feature(feature) for feature in features]:
            return False
        else:
            return True

    def add_nucleus(self, features):
        if not self.is_features(features):
            return
        self.nuclei.add(features)

    def clear_nuclei(self):
        self.nuclei.clear()
        return self.nuclei

    # Sonority
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


    # Split and shape syllable parts phonotactically

    def is_featureslist_overlap(self, featureslist_a, featureslist_b, all_a_in_b=True):
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
                if self.is_featureslist_overlap(features[i:i+len(nucleus)], nucleus):
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

    def shape(self, syllable_features):
        """Fill out a syllable with all defined phonotactics including
        dependencies and sonority"""

        # break up and check syllables
        syllable_pieces = self.partition_syllable(syllable_features)

        if not syllable_pieces:
            return
   
        # TODO: use sonority and dependencies to fill out
        #   ? - go with dependency map instead
        #   ? - interject
        #   ? - build sonority out from nucleus

        # Build Syllable and Sonority Shape
        # Syllable Shape: split syllable into onset, nucleus, coda
        # Sonority Shape: fill out syllable shape following sonority scale
        
        final_features = syllable_shape['onset'] + syllable_shape['nucleus'] + syllable_shape['coda']

        return final_features
