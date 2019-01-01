class Inventory:
    def __init__(self):
        self.letters = set()
        self.syllables = set()
        self.letters_by_feature = {}
        self.letter_length_limit = 4

    def get_letter(self, features=[]):
        """Find every letter that has the given features"""
        if type(features) is str:
            feature = features
            if feature in self.letters_by_feature:
                return list(self.letters_by_feature[feature])
            else:
                print("Inventory get_letter failed - unknown feature {0}".format(feature))
                return []

        # reduce to set of found letters
        matching_letters = set()
        for i in range(len(features)):
            feature = features[i]
            if feature not in self.letters_by_feature:
                print("Inventory get_letter failed - unknown feature {0}".format(feature))
                return []
            if i == 0:
                matching_letters = self.letters_by_feature[feature]
                continue
            matching_letters &= self.letters_by_feature[feature]

        return list(matching_letters)

    def get_features(self, letter):
        """Read all features associated with a single letter"""
        matching_features = []
        for feature in self.letters_by_feature:
            if letter in self.letters_by_feature[feature]:
                matching_features.append(feature)
        return matching_features

    def get_syllables(self):
        """Read all syllables listed in the inventory"""
        return list(self.syllables)

    def _add_unique(self, letter, feature):
        """Private add unique letter to map of letters by features"""
        if not (type(letter) is str and type(feature) is str):
            return
        if feature not in self.letters_by_feature:
            self.letters_by_feature[feature] = set()
        if letter not in self.letters_by_feature[feature]:
            self.letters_by_feature[feature].add(letter)
        return self.letters_by_feature[feature]

    def add_letter(self, letter="", features=[]):
        """Store a new letter with features"""
        if not letter or type(letter) is not str or len(letter) > self.letter_length_limit:
            print("Inventory add_letter failed - invalid letter {0}".format(letter))
            return
        for feature in features:
            if not self._add_unique(letter, feature):
                print("Inventory add_letter failed - unknown feature {0}".format(feature))
                # TODO wipe letter from letters data
                # self.remove_letter(letter) # also remove feature if no letters left
                return
        self.letters.add(letter)
        return {letter: self.get_features(letter)}

    def remove_letter(self, letter):
        """Remove a letter and its feature associations from the inventory"""
        if letter not in self.letters:
            print("Inventory remove_letter failed - letter {0} not found".format(letter))
            return
        for letters in self.letters_by_feature.values():
            letter in letters and letters.remove(letter)
        self.letters.remove(letter)
        return self.letters

    def reset_letter(self, letter, new_features):
        """Update all features associated with a single letter"""
        if letter not in self.letters:
            print("Inventory reset_letter failed - letter {0} not found".format(letter))
            return
        for feature, letters in self.letters_by_feature.items():
            letter in letters and letters.remove(letter)
            feature in new_features and letters.add(letter)
        return {letter: self.get_features(letter)}

    def add_syllable(self, syllable):
        """Add a syllable structure to the inventory syllables collection"""
        if type(syllable).__name__ == 'Syllable' and syllable not in self.syllables:
            self.syllables.add(syllable)
        return self.syllables

    def remove_syllable(self, syllable):
        """Remove a syllable structure from the inventory syllables collection"""
        if syllable in self.syllables:
            self.syllables.remove(syllable)
        return self.syllables
