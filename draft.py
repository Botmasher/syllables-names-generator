import random

class Features:
    def __init__(self):
        self.voicing = []
        self.manner = []
        self.place = []
        self.height = []
        self.backness = []
        self.rounding = []

    def add_feature(self, feature_type, feature_name):
        if not getattr(self, feature_type):
            return
        features_list = getattr(self, feature_type)
        features_list.append(feature_name)
        return features_list

class Inventory:
    def __init__(self):
        self.features = []
        self.letters = {'consonants': [], 'vowels': []}
        self.syllables = []
        self.letters_by_feature = {}
        self.features_by_letter = {}    # each letter allows variants in feat subarrays
        self.feature_namer = self.initialize_features()

    def initialize_features(self):
        feature_namer = Features()
        # TODO test if adding works and add standard features
        feature_types = {
            'voicing': ["voiced", "voiceless"],
            'manner': ["stop", "fricative", "affricate", "approximant", "liquid", "nasal"],
            'place': ["dental", "alveolar", "palatal", "velar", "uvular", "pharyngeal"],
            'height': ["high", "mid", "low"],
            'backness': ["front", "central", "back"],
            'rounding': ["rounded", "unrounded"]
        }
        for feature_type in feature_types:
            for feature in feature_types[feature_type]:
                feature_namer.add_feature(feature_type, feature)
        return feature_namer

    def is_consonant_features(self, voicing, place, manner):
        if place not in self.feature_namer.place:
            return False
        elif voicing not in self.feature_namer.voicing:
            return False
        elif manner not in self.feature_namer.manner:
            return False
        else:
            return True

    def is_vowel_features(self, height, backness, rounding):
        if height not in self.feature_namer.height:
            return False
        elif backness not in self.feature_namer.backness:
            return False
        elif rounding not in self.feature_namer.rounding:
            return False
        else:
            return True

    # TODO check for valid letter and feature
    def add_consonant(self, letter, voicing, place, manner):
        if not self.is_consonant_features(voicing, place, manner):
            return

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
        if not self.is_vowel_features(height, backness, rounding):
            return

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

    def build_word(self, length=1):
        """Form a word following the defined inventory and syllable structure"""
        word = ""
        for i in range(length):
            syllable_structure = random.choice(self.syllables)
            for syllable_letter in syllable_structure:
                if syllable_letter == 'C':
                    new_letter = random.choice(self.letters['consonants'])
                elif syllable_letter == 'V':
                    new_letter = random.choice(self.letters['vowels'])
                else:
                    new_letter = ''
                word.join(new_letter)
        print(word)
        return word

# test
inventory = Inventory()
inventory.add_consonant("t", "voiceless", "alveolar", "stop")
inventory.add_consonant("dz", "voiced", "dental", "affricate")
inventory.add_consonant("dh", "voiced", "dental", "fricative")
inventory.add_vowel("a", "low", "back", "unrounded")
inventory.add_vowel("i", "high", "front", "unrounded")
inventory.add_vowel("y", "high", "front", "rounded")
inventory.add_vowel("u", "high", "back", "rounded")
inventory.add_syllable(["C", "V"])
inventory.add_syllable(["V"])
inventory.add_syllable(["C", "V", "C"])
inventory.build_word(length=1)
inventory.build_word(length=5)
inventory.build_word(length=3)
inventory.build_word(length=1)
inventory.build_word(length=3)
