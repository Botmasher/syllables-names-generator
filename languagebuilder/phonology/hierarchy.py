import random

# Hierarchy scale and dependencies for Phonotactics
# Based around sonority hierarchy (scale) plus variant state paths (dependencies).
# See Phonotactics.shape for use in practice.

class Hierarchy:
    def __init__(self, phonology):
        self.phonology = phonology  # feature existence checks only
        self.scale = []             # sequential featuresets options
        self.dependencies = {       # featureset left-right dependencies
            # each left strings a feature/ipa key
            # each right maps {'include': {features/ipas}, 'exclude': {features/ipas}}
            # as usual, guess it's a sound first before going to more spec feature
        }

    def get_scale(self):
        """Read the left-to-right sequence scale"""
        return self.scale
    
    def get_dependencies(self):
        """Read all of the features dependencies. If feature key selected for left sound
        slot, next right sound slot must be among the feature values included list and
        must not be among the feature values excluded list."""
        return self.dependencies

    def clear(self):
        """Empty the existing scale"""
        self.scale = []

    def rewrite(self, scale):
        """Overwrite the scale with a new sequence"""
        # expect a string collection
        if isinstance(scale, str) or not all([isinstance(f, str) for f in scale]):
           raise TypeError(f"Hierarchy rewrite scale expected a string list not {scale}")
        self.scale = list(scale)

    def add(self, *features, position=0):
        """Add one or more features to a specific slot (including -1 for left/outermost,
        0 for right/innermost (default)) in the existing scale. Position counts up from
        the right. Scale applies left to right for onsets and right to left for codas.
        Params:
            features (str): strings matching existing phonological features
            position (int): insertion index from end of scale (1 <= n <= scale length; 0: append, -1: prepend)
        """
        # check for valid feature
        for feature in features:
            if not self.phonology.phonetics.has_feature(feature):
                raise ValueError(f"Hierarchy scale cannot add unidentified feature {feature}")
        
        # reindex scale position to flip front instead of end
        clamped_position = min(max(-1, position), len(self.scale))
        scale_i = len(self.scale) - clamped_position

        # add features to scale
        self.scale = self.scale[:scale_i] + list(features) + self.scale[scale_i:]
        
        return self.scale

    def remove(self, feature, position=None):
        """Remove a feature from the scale. If a feature occurs multiple times, all
        instances are deleted. If an index position is given, it is used instead."""
        # remove at given index
        if position is not None:
            self.scale = self.scale[:position] + self.scale[position+1:]
            return self.scale
        
        # find and remove occurrences of a feature
        self.scale = list(filter(
            lambda f: f != feature,
            self.scale
        ))
    
        return self.scale

    # TODO: just pairwise left-right depend/undepends, inclusive and exclusive strs/sets
    #
    # NOTE: expecting array of sets vs strings. Note the complexity of dealing with
    # lists of lists of sets in both the scale and dependencies. Start with just
    # feature keys only? Inclusions/exclusions (dependency left 'exclude')?

    def depend(self, left_feature, right_feature, include=True):
        """Add a left feature to the existing feature dependencies and set one included
        or excluded right feature."""
        if not self.phonology.phonetics.has_feature(left_feature):
            raise KeyError(f"Phonotactics hierarchy failed to set dependencies for unidentified feature {left_feature}")
        if right_feature is not None and not self.phonology.phonetics.has_feature(right_feature):
            raise ValueError(f"Phonotactics hierarchy dependencies did not recognize feature {right_feature}")
        clusives = ('include', 'exclude')
        include_exclude = clusives[include]
        dependencies_entry = {clusive: set() for clusive in clusives}
        self.dependencies.setdefault(left_feature, dependencies_entry)
        self.dependencies[left_feature][include_exclude].add(right_feature)
        return {left_feature: self.dependencies[left_feature]}

    def undepend(self, left_feature, right_feature=None):
        """Remove one left-right feature from dependencies, or just the left feature to
        remove a whole dependencies entry."""
        dependencies_entry = self.dependencies[left_feature]
        # delete entire left feature including entry value
        if right_feature is None and None not in dependencies_entry['inclusive'] ^ dependencies_entry['exclusive']:
            self.dependencies.pop(left_feature)
        # delete from right sets
        else:
            for featureset in dependencies_entry:
                featureset.discard(right_feature)
        
        # clear out empty entries
        if not self.dependencies[left_feature]['include'] and not self.dependencies[left_feature]['exclude']:
            self.dependencies.pop(left_feature)

        return self.dependencies

    def chain(self, *features, include=True):
        """Order featuresets below each other in the dependency map from left to right.
        Params:
           *featuresets (list): list of feature strings to add as dependency key-values
           include (bool): whether to add each right entry to include or exclude sets
        """
        # expect multiple 
        if len(features) < 2:
            raise ValueError(f"Phonological hierarchy dependencies expected a multi-element chain, not {features}")

        # chain add each left feature as keys and right as associated values
        for left, right in zip(features[:-1], features[1:]):
            self.depend(left, right, include=include)
        
        return self.dependencies

    def unchain(self, *features):
        """Remove existing feature dependencies from the map in a left-right chain."""
        # delete chained values from dependencies
        for left, right in zip(features[:-1], features[1:]):
            self.undepend(left, right)
        
        return self.dependencies

    def build_featureset(self, features):
        """Convert features or ipa string or collection into a formatted featureset"""
        if not features:
            return set()
        elif isinstance(features, str):
            ipa_features = self.phonology.phonetics.get_features(features)
            return set(ipa_features) if ipa_features else {features}
        else:
            return set(features)

    def recommend(self, left_features=None, right_features=None, random_start=True, jumps=True, length=1):
        """Pick the next (right) sound given selected (left) features and some filter
        (right) features. If no left features are given, pick a random starting position
        in the hierarchy given cluster length constraints (leave at least that many
        sounds to the right).
        Params:
            left_features (str, list): input features defining for previous sound
            right_features (str, list): input features constraining selected sound
            random_start (bool): start anywhere in hierarchy if no features given
            jumps (bool): skip some of the scale sometimes for realistic and varied output
            cluster_length (int): leave enough right features slots for remaining sounds
        """
        # structure given right features for conditioning recommendations
        recommended_features = self.build_featureset(right_features)

        # pick a starting feature since no left feature input
        if not left_features:
            # start at any available feature in cluster scope
            if random_start:
                scale_features = self.scale[:len(self.scale) - length]
                scale_feature = random.choice(scale_features)
            # start at the outermost feature
            else:
                scale_feature = self.scale[0]
            # combine features and suggest a sound
            recommended_features.add(scale_feature)
            
            # TODO: on empty features/phonemes, recommend a different feature/sound
            #   - see calling Phonotactics shape method
            recommended_ipa = random.choice(self.phonology.get_phonemes(recommended_features))[0]
            
            return recommended_ipa
        
        # create featureset from sound symbol, single-feature string or features list
        left_features = self.build_featureset(left_features)
        #raise ValueError(f"Left features: {left_features}")

        # look for next (right) features using left features dependencies
        has_dependencies = False
        recommended_features = set()
        for left_feature in left_features:
            dependencies_entry = self.dependencies.get(left_feature)
            if dependencies_entry:
                # apply dependencies includes unless input features are excluded
                if not left_features & dependencies_entry['exclude']:
                    if not dependencies_entry['include']:
                        continue
                    # choose one right feature to include
                    feature_choice = random.sample(dependencies_entry['include'], 1)
                    # expect one feature option
                    if not feature_choice:
                        continue
                    included_feature = feature_choice[0]
                    has_dependencies = True
                    # end the sound choice and the cluster
                    if included_feature is None:
                        return [None]
                    # choose one feature from includes
                    recommended_features.add(included_feature)

        # use base hierarchy instead of dependencies
        if not has_dependencies:
            for i, scale_feature in enumerate(self.scale):
                if {scale_feature} & left_features:
                    recommended_features.add(random.choice(self.scale[i+1:]))
                    break
        
        if not recommended_features:
            raise KeyError(f"Hierarchy cannot recommend a sound for features {right_features} following a sound {left_features}")

        # take in features and recommend a sound symbol
        return random.choice(self.phonology.get_phonemes(recommended_features))[0]
