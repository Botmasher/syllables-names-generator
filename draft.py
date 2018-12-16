class Features:
    def __init__(self):
        self.voicing = []
        self.manner = []
        self.place = []
        self.height = []
        self.backness = []
        self.rounding = []

    def add_feature(self, feature_type, feature_name):
        if not get_attr(self, feature_type):
            return
        setattr(self, feature_type, [*getattr(self, feature_type), feature_name])

class Inventory:
    def __init__(self):
        self.features = []
        self.letters = {'consonants': [], 'vowels': []}
        self.syllables = []
        self.letters_by_feature = {}
        self.features_by_letter = {}
        self.feature_namer = self.initialize_features()

    def initialize_features():
        feature_namer = Features()
        feature_namer.add_feature('voicing', 'voiced')
        # TODO test if adding works and add standard features
        return

    # TODO check for valid letter and feature
    def add_consonant(self, letter, place, manner, voicing):
        self.letters['consonants'].append(letter)
        if place not in self.letters_by_feature:
            self.letters_by_feature[place] = []
        if manner not in self.letters_by_feature:
            self.letters_by_feature[manner] = []
        if voicing not in self.letters_by_feature:
            self.letters_by_feature[voicing] = []
        self.letters_by_feature[place].append(letter)
        self.letters_by_feature[manner].append(letter)
        self.letters_by_feature[voicing].append(letter)
        # TODO - just reduce over features to allow variants (letters mapped to many features)
        self.features_by_letter[letter] = [voicing, place, manner]
        return {letter: self.features_by_letter[letter]}

    def add_vowel(self, letter, height, backness, rounding):
        self.letters['vowels'].append(letter)
        if height not in self.letters_by_feature:
            self.letters_by_feature[height] = []
        if backness not in self.letters_by_feature:
            self.letters_by_feature[backness] = []
        if rounding not in self.letters_by_feature:
            self.letters_by_feature[rounding] = []
        self.letters_by_feature[height].append(letter)
        self.letters_by_feature[backness].append(letter)
        self.letters_by_feature[rounding].append(letter)
        # TODO - see above; reduce over features to allow variants
        self.features_by_letter[letter] = [height, backness, rounding]
        return {letter: self.features_by_letter[letter]}

    def add_syllable(self, syllable):
        # TODO check if valid syllable notation
        self.syllables.append(syllable)
        return self.syllables

    # TODO remove or update letter
