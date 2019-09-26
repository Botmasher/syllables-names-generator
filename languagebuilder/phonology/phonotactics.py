import random

# TODO: optional/dependent sonority (see sonority scale list and associated methods below)
# - add_sonority_dependency()
# - e.g. CCV: if s -> {p,t,k,l,w}, then if st -> {r}
class Phonotactics:
    def __init__(self, phonology, syllables):
        # 
        self.phonology = phonology
        self.syllables = syllables

        # sonority scale dependency map
        # applied in given order for onset and reverse for coda
        self.sonority = {}

        # store features that identify the syllable nucleus
        # NOTE: defaults to vowel if present in phonetics
        self.nucleus = {'vowel'} if self.phonology.phonetics.has_feature("vowel") else set()

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

