from ..tools.flat_list import tuplify, untuplify

class Morae:
    def __init__(self, phonology):
        self.phonology = phonology
        self.morae = {}     # map beat count ints to morae sets
    
    def set_mora(self, sounds_or_features, beats=1, overwrite=False):
        """Add a moraic structure and its associated beat count to the stored morae"""
        if not isinstance(beats, (int, float)):
            raise TypeError(f"Morae expected beat count to be a number not {beats}")

        # structure mora as list of lists
        mora_list = self.vet_mora(sounds_or_features)
        
        # optionally remove mora if it already exists
        existing_beats = self.get_beats(mora_list)
        if existing_beats:
            if overwrite:
                self.morae[existing_beats].remove(mora_list)
            else:
                raise ValueError(f"Mora already exists in Morae: {mora_list}")

        # map mora to associated beats
        self.morae.setdefault(beats, set()).add(mora_list)

        return self.morae[beats]

    def get_beats(self, mora):
        mora_list = self.vet_mora(mora)
        for beats in self.morae:
            if mora_list in self.morae[beats]:
                return beats
        return

    def is_mora(self, mora):
        mora_list = self.vet_mora(mora)
        beats = self.get_beats(mora_list)
        return beats in self.morae

    def beats_per_morae(self):
        """Remap morae data from morae sets per beatcount into beats per mora"""
        return {
            tuplify(mora): beats
            for beats, morae in self.morae.items()
            for mora in morae
        }
        
    # TODO: turn this into a more general phonology list of features list method
    #   - could be used to generate sylls, ...
    def vet_mora(self, sounds_or_features):
        """Turn a list of sounds or features lists or strings into a list of lists of
        features to be identified as a mora."""
        vetted_mora = []
        for features in sounds_or_features:
            # attempt to read as a single sound
            if self.phonology.phonetics.has_ipa(features):
                vetted_mora.append(self.phonology.phonetics.get_features(features))
            # attempt to read as a special feature character
            elif isinstance(features, str) and features in self.phonology.syllables.syllable_characters:
                feature = self.phonology.syllables.syllable_characters[features]
                vetted_feature = feature if self.phonology.phonetics.has_feature(feature) else None
                if vetted_feature:
                    vetted_mora.append([vetted_feature])
            # attempt to read as a feature string or features list
            elif self.phonology.phonetics.parse_features(features):
                vetted_features = self.phonology.phonetics.parse_features(features)
                vetted_mora.append(vetted_features)
            # back out if sound or features not found in this position
            else:
                return
        return vetted_mora

    # TODO: search morae (beats, features)
    
    # TODO: pretty print morae
    
    def count_morae(self, sounds):
        """Count the number of morae in a sound sample"""
        # convert sounds into a list of per-sound feature collections
        sample_features = [
            self.phonology.phonetics.parse_features(sound)
            for sound in sounds
        ]
        # flip beat map to traverse morae
        beats_per_morae = self.beats_per_morae()

        # traverse sounds (feature sets) in the sample
        current_mora = []
        count = 0
        for features in sample_features:
            current_mora.append(features)
            # identify moraic list-of-lists matches where stored morae
            # are a subset of current morae features
            for compared_mora, beats in beats_per_morae.items():
                if len(current_mora) != len(compared_mora):
                    continue
                feature_match = [
                    current_features.issuperset(compared_mora[i])
                    for i, current_features in enumerate(current_mora)
                    if i < len(compared_mora)
                ]
                if False not in feature_match:
                    count += beats
                    current_mora = []
                    break
        # check for leftover beats
        if current_mora:
            return
        return count
            