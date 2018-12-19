import random

# TODO stretch to flexible categorization
#   - allow storing retracted or ATR or any other dimension
#   - associate letters with feature name
#   - overlapping or scalar membership

class Features:
    def __init__(self):
        self.features = []

    def get(self):
        return self.features

    def add(self, feature):
        if feature not in self.features:
            return
        self.features.append(feature_name)
        return self.get()

    def add_many(self, features=[]):
        if not features:
            return
        for feature in features:
            if feature in self.features:
                continue
            self.add(feature)
        return self.get()

    def has(self, feature):
        if feature in self.features:
            return True
        return False

class Phoneme:
    def __init__(self, symbol):
        self.letters = []
        self.features = []
        self.symbol = symbol

    def get(self):
        return {
            'letters': self.letters,
            'features': self.features,
            'symbol': self.symbol
        }

    def get_letters(self):
        return self.letters

    def get_features(self):
        return self.features

    def add_letter(self, letter):
        if letter not in self.letters:
            self.letters.append(letter)

    def remove_letter(self, letter):
        if letter in self.letters:
            self.letters.remove(letter)

    def add_feature(self, feature):
        if feature not in self.features:
            self.features.append(feature)

    def remove_feature(self, feature):
        if feature in self.features:
            self.features.remove(feature)

class Syllable:
    def __init__(self, structure=[]):
        self.structure = structure

    def get(self):
        return self.structure

    def update(self, structure=[]):
        if type(structure) is list:
            self.structure = structure
        return self.structure

class Inventory:
    def __init__(self):
        self.letters = []
        self.syllables = []
        self.letters_by_feature = {}

    def get_letter(self, features=[]):
        """Find every letter that has the given features"""
        if type(features) is str:
            if feature in self.letters_by_feature:
                return self.letters_by_feature[feature]
            else:
                return None

        # reduce to found letters
        matching_letters = set()
        for i in range(len(features)):
            feature = features[i]
            if feature not in self.letters_by_feature:
                print("Inventory get_letter failed - unknown feature {0}".format(feature))
                return []
            if i == 0:
                matching_letters = set(self.letters_by_feature[feature])
                continue
            matching letters &= self.letters_by_feature[feature]

        return list(matching_letters)

    def get_features(self, letter):
        """Read all features associated with a single letter"""
        matching_features = []
        for feature in self.features_by_letter:
            if letter in self.features_by_letter[feature]:
                matching_features.append(letter)
        return matching_features

    def get_syllables(self):
        """Read all syllables listed in the inventory"""
        return self.syllables

    def _add_unique(self, letter, feature):
        """Private add unique letter to map of letters by features"""
        if not (type(letter) is str and type(feature) is str):
            return
        if feature not in self.letters_by_feature:
            self.letters_by_feature[feature] = []
        if letter not in self.letters_by_feature[feature]:
            self.letters_by_feature[feature].append(letter)
        return self.letters_by_feature[feature]

    def add_letter(self, letter, *features):
        """Store a new letter with features"""
        for feature in features:
            if not self._add_unique(letter, feature):
                print("Inventory add_letter failed - unknown feature {0}".format(feature))
                # TODO wipe letter from letters data
                # self.remove_letter(letter) # also remove feature if no letters left
                return
        self.letters.append(letter)
        return {letter: self.features_by_letter[letter]}

    # TODO update
    def update_letter(self):
        return

    def add_syllable(self, syllable):
        if type(syllable).__name__ == 'Syllable' and syllable not in self.syllables:
            self.syllables.append(syllable)
        return self.syllables

# TODO handle feature checks in language instead of shared Features dependency
#   - check before passing non C xor V to syll
#   - check before adding consonant or vowel to inventory
#   - check before adding features to phone

# TODO set up default letters and symbols

class Language:
    def __init__(self, name):
        self.name = name

    def set_inventory(self, inventory):
        self.inventory = inventory

    def set_syllables(self, syllables):
        self.syllables = syllables

    def build_word(self, length=1):
        """Form a word following the defined inventory and syllable structure"""
        if not self.syllables:
            return
        word = ""
        for i in range(length):
            syllable_structure = random.choice(self.syllables)
            print(syllable_structure)
            for syllable_letter in syllable_structure:
                if syllable_letter == 'C' and self.letters['consonants']:
                    new_letter = random.choice(self.letters['consonants'])
                elif syllable_letter == 'V' and self.letters['vowels']:
                    new_letter = random.choice(self.letters['vowels'])
                else:
                    new_letter = ''
                word += new_letter
        print(word)
        return word

# TODO update demo
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
