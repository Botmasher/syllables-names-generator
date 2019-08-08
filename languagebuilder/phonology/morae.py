class Morae:
    def __init__(self, phonology):
        self.phonology = phonology
        self.morae = {}     # map of beat counts per mora
    
    def set_mora(self, sounds_or_features, beats=1, overwrite=False):
        """Add a moraic structure and its associated beat count to the stored morae"""
        if not isinstance(beats, (int, float)):
            raise TypeError(f"Morae expected beat count to be a number not {beats}")

        # structure mora as list of lists
        mora_list = self.vet_mora(sounds_or_features)
        
        # map mora and associated beats
        mora_key = self.store_mora_from_list(mora_list, beats=beats, overwrite=overwrite)
        return mora_key

    # TODO: search morae (beats, features)
    # TODO: pretty print morae

    def get_beats(self, mora):
        if isinstance(mora, list):
            return self.retrieve_mora_using_list(mora)
        return self.morae.get(mora)

    def is_mora(self, mora):
        return mora in self.morae

    def red_acc(self, iterable, expression, starting_value):
        accumulator = starting_value
        for current_value in iterable:
            accumulator = expression(current_value, accumulator)
        return accumulator

    def reduce_beats(self):
        """Remap morae data from beats per moraic entry into sets of morae per beat"""
        return self.red_acc(
            self.morae.keys(),
            lambda mora, morae_per_beat: morae_per_beat.setdefault(self.morae[mora], set()).add(mora),
            {}
        )

    def store_mora_from_list(self, mora, beats=1, overwrite=False):
        if not isinstance(mora, list):
            raise ValueError(f"Morae expected to convert tuple key from list, not {mora}")
        # TODO: expect list of lists -> tuple of tuples
        #   - have already accidentally split string
        mora_key = tuple(map(lambda x: tuple(x), mora))
        if overwrite or not self.morae.get(mora_key):
            self.morae[mora_key] = beats
        return mora_key

    def retrieve_mora_from_list(self, mora):
        if not isinstance(mora, list):
            raise ValueError(f"Morae expected to convert tuple key from list, not {mora}")
        mora_key = tuple(map(lambda x: tuple(x), mora))
        return (mora_key, None)[mora_key not in self.morae]
        
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
    