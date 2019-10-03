from ..tools import redacc

# TODO: optional/dependent sonority (see sonority scale list and associated methods below)
# - add_sonority_dependency()
# - e.g. CCV: if s -> {p,t,k,l,w}, then if st -> {r}
class Phonotactics:
    def __init__(self, phonology):
        # check that features exist
        self.phonology = phonology
        
        # feature dependencies - if outer feature is X, inner should be Y
        self.dependencies = {
            # each left feature defines its right followers and non-followers
            # feature: {'included': [features], 'excluded':True}
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

    # TODO: update to use sonority plus custom dependencies to build out possible chains
    def follow_dependencies(self, chain_branch):
        """Keep chaining the next feature based on the rightmost feature in the list
        until the chain ends"""
        # no latest feature to check
        if not chain_branch:
            return chain_branch
        # continue branch or end branch based on latest feature
        left_feature = chain_branch[-1]
        right_feature = self.dependencies.get(left_feature)
        if right_feature:
            return self.follow_dependencies(chain_branch + [right_feature])
        return chain_branch
    #
    def _remove_overlaps(self, chains):
        """Filter chains list for elements whose features do not recur in another chain"""
        no_subchain_chains = []
        for chain in chains:
            is_subchain = False
            for chain_check in chains:
                if set(chain).issubset(set(chain_check)):
                    is_subchain = True
                    break
            if not is_subchain:
                no_subchain_chains.append(chain)
        return no_subchain_chains
    #
    def get_chains(self, subchain=True):
        """Format dependencies into a list of all feature scales formable from
        walking all options in the chains map. Chains include subchains starting
        with the same feature key if it was added to at least one other chain being
        formed. Switching subchaining off performs a more expensive traversal."""
        # recursively build out all branches in dependency chains from chain map keys
        chains = [self.follow_chain_branch(feature) for feature in self.chain_map]
        # vet for overlapping subchains
        chains = self._remove_overlaps(chains) if not subchain else chains
        return chains
    # 
    def count_chains(self, chains):
        """Return a map of lists of chains keyed by chain length"""
        chains_count_map = redacc.redacc(
            chains,
            lambda chain, chains_map_acc: chains_map_acc.setdefault(len(chain), []).append(chain),
            {}
        )
        return chains_count_map

    def chain(self, *features):
        """Order one feature below another in the features chain map. Features will be
        applied hierarchically in a dependency chain until a sound with no dependency
        is found, then any new sound will be chosen."""
        if not self.is_features_list(features):
            raise ValueError(f"Cannot create chain using nonexisting feature")
        
        # traverse adding each left feature to keys and right to values
        for i in enumerate(features):
            # stop looping when run out of right (next) features
            if i >= len(features) - 1:
                break
            left_feature = features[i]
            right_feature = features[i + 1]
            self.chain_map.setdefault(left_feature, set()).add(right_feature)
        
        return self.chain

    def unchain(self, left_feature, right_feature):
        """Remove existing feature dependency from the chain map"""
        self.chain_map.get(left_feature, set()).discard(right_feature)
        if not self.chain_map.get(left_feature):
            self.chain_map.pop(left_feature)
        return self.chain_map

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

    def shape(self, syllable_features):
        """Fill out a syllable with all defined phonotactics including
        dependencies and sonority"""

        # break up and check syllables
        syllable_pieces = self.partition_syllable(syllable_features)

        if not syllable_pieces:
            return

        # build syllable features options from dependencies
        # TODO: test, and what if no same-length member in chains? go higher? random?
        chains_count_map = self.count_chains(self.get_chains())
        coda_features = chains_count_map[len(syllable_pieces['coda'])]
        onset_features = chains_count_map[len(syllable_pieces['onset'])]
        nucleus_features = syllable_pieces['nucleus']

        # add initial seed features back into chains
        for i in len(range(onset_features)):
            onset_features[i] += syllable_pieces['onset'][i]
        onset_features = list(set(onset_features))
        for i in len(range(coda_features)):
            coda_features[i] += syllable_pieces['coda'][i]
        coda_features = list(set(coda_features))

        # Build Syllable and Sonority Shape
        # Syllable Shape: split syllable into onset, nucleus, coda
        # Sonority Shape: fill out syllable shape following sonority scale
        
        return onset_features + nucleus_features + coda_features
