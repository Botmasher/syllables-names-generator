# Hierarchy scale and dependencies for Phonotactics
# based around concept of sonority scale

class Hierarchy:
    def __init__(self):
        self.scale = []         # sequential featuresets options
        self.dependencies = {}  # featureset left-right dependencies

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
        self.scale = list(scale)

    def add(self, *features, position=0):
        """Add a featureset to a specific slot (-1 for innermost, 0 for outermost
        (default)) in the existing scale. Scale applies left to right for onsets
        and right to left for codas."""
        # check for valid feature
        #if not self.is_features_list([feature]):
        #    raise ValueError(f"Expected scale value to be a feature - instead found {feature}")
        
        # create set including all given features
        featureset = {feature for feature in features}

        # add to end of scale
        if position < 0:
            self.scale.append(featureset)
        # add to front or within scale
        else:
            self.scale = self.scale[:position] + [featureset] + self.scale[position:]
        
        return self.scale

    def remove(self, *features, position=None):
        """Remove features from the scale. If a feature occurs multiple times, all
        instances are deleted. If an index position is given, it is used instead."""
        # remove at given index
        if position is not None:
            self.scale = self.scale[:position] + self.scale[position+1:]
            return self.scale
        
        # find and remove occurrences of features
        for featureset in self.scale:
            for feature in features:
                featureset.discard(feature)
    
        return self.scale

    def chain(self, *features):
        """Order featuresets below each other in the dependency map from left to right.
        Params:
           *featuresets (list): sequence of sets to add as dependency key-values
        """
        #if False in [self.is_features_list(featureset) for featureset in featuresets]:
        #    raise ValueError(f"Cannot create chain using nonexisting feature")
        
        # NOTE: expecting array of sets vs strings. Note the complexity of dealing with
        # lists of lists of sets in both the scale and dependencies. Start with just
        # feature keys only? Inclusions/exclusions (dependency left 'exclude')?

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
