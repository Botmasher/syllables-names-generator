class Morae:
    def __init__(self, phonology):
        self.phonology = phonology
        self.morae = {}     # map of beat counts per mora
    
    def set_beats(self, sounds_or_features, beats=1, overwrite=False):
        """Add a moraic structure and its associated beat count to the stored morae"""
        if not isinstance(beats, (int, float)):
            raise TypeError(f"Morae expected beat count to be a number not {beats}")

        vetted_mora = self.vet_mora(sounds_or_features)
        
        # map mora and associated beats
        if overwrite or vetted_mora not in self.morae:
            self.morae[vetted_mora] = beats
        return vetted_mora

    def count_beats(self, mora):
        return self.morae.get(mora)

    def is_mora(self, mora):
        return mora in self.morae

    def reduce(self, iterable, expression, starting_value):
        accumulator = starting_value
        for current_value in iterable:
            accumulator = expression(current_value, accumulator)
        return accumulator

    def reduce_beats(self):
        """Remap morae data from beats per moraic entry into sets of morae per beat"""
        return self.reduce(
            self.morae.keys(),
            lambda mora, morae_per_beat: morae_per_beat.setdefault(self.morae[mora], set()).add(mora),
            {}
        )

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
        morae_per_beat = self.reduce_beats()
        for features in morae_features:
            current_mora.append(features)
            for beats in morae_per_beat:
                # TODO: check for existence of any subset of features
                if current_mora in morae_per_beat[beats]:
                    count += beats
                    current_mora = []
        if current_mora:
            return
        return count
    