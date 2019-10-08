# Hierarchy scale and dependencies for Phonotactics
# based around concept of sonority scale

class Hierarchy:
    def __init__(self):
        self.scale = []         # sequential featuresets options
        self.dependencies = {}  # featureset left-right dependencies

    def get(self):
        """Read the left-to-right sequence scale"""
        return self.scale
    
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
    
