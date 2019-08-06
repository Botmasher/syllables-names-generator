class Morae:
    def __init__(self, phonology):
        self.phonology = phonology
        self.morae = {}     # map of morae sets per beats count
        
    def set_mora(self, sounds_or_features, beats=1, overwrite=False):
        """Add a moraic structure and its associated beat count to the stored morae"""
        if not isinstance(beats, (int, float)):
            raise TypeError(f"Morae expected beat count to be a number not {beats}")

        vetted_mora = self.vet_mora(sounds_or_features)
        
        # add mora to single-count set
        self.morae.setdefault(beats, set()).add(vetted_mora)
        return vetted_mora

    def vet_mora(self, sounds_or_features):
        """Turn a list of sounds or features lists or strings into a list of lists of
        features to be identified as a mora."""
        vetted_mora = []
        for features in sounds_or_features:
            # attempt to read as a single sound
            if self.phonology.phonetics.has_ipa(features):
                vetted_mora.append(self.phonology.phonetics.get_features(features))
            # attempt to read as a special feature character
            elif features in self.phonology.syllables.syllable_characters:
                feature = self.phonology.syllables.syllable_characters[features]
                vetted_feature = feature if self.phonology.phonetics.has_feature(feature) else None
                if vetted_feature:
                    vetted_mora.append(vetted_feature)
            # attempt to read as a feature string or features list
            elif self.phonology.phonetics.parse_features(features):
                vetted_features = self.phonology.phonetics.parse_features(features)
                vetted_mora.append(vetted_features)
            # back out if sound or features not found in this position
            else:
                return
        return vetted_mora

    def count_morae(self, sounds):
        """Count the number of morae in a sound sample"""
        morae_features = [
            self.phonology.phonetics.parse_features(sound)
            for sound in sounds
        ]
        current_mora = []
        count = 0
        for features in morae_features:
            current_mora.append(features)
            # TODO: check for existence of any subset of features in dict lists
            for mora_count in self.morae:
                if current_mora in self.morae[mora_count]:
                    count += mora_count
                    current_mora = []
        if current_mora:
            return
        return count
    