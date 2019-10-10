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

    def chain(self, *features):
        """Order featuresets below each other in the dependency map from left to right.
        Params:
           *featuresets (list): sequence of sets to add as dependency key-values
        """
        for feature in features:
            if not self.phonology.phonetics.has_feature(feature):
                raise ValueError(f"Hierarchy scale cannot add unidentified feature {feature}")
        
        if len(features) < 2:
            raise ValueError(f"Phonological hierarchy dependencies expected a multi-element chain, not {features}")

        # chain add each left feature as keys and right as associated values
        for left, right in zip(features[:-1], features[1:]):
            self.dependencies.setdefault(left, set()).add(right)
        
        return self.dependencies

    def undepend(self, *features, values_only=False):
        """Remove one or more features from all dependencies, or from just the right
        dependency sets if values_only is set."""
        # remove features from right sets
        for featureset in self.dependencies.values():
            for feature in features:
                featureset.discard(feature)
        # remove features from left keys
        if not values_only:
            for feature in features:
                self.dependencies.pop(feature, None)
        
        return self.dependencies

    def unchain(self, *features):
        """Remove existing feature dependencies from the map in a left-right chain."""
        
        # delete chained values from dependencies
        empty_lefts = []
        for left, right in zip(features[:-1], features[1:]):
            self.dependencies[left].discard(right)
            if not self.dependencies[left]:
                empty_lefts.append(left)
        
        # delete empty keys from dependencies
        for feature in empty_lefts:
            self.dependencies.pop(feature, None)
        
        return self.dependencies
