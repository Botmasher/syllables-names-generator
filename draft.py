import random

# TODO stretch to flexible categorization
#   - allow storing retracted or ATR or any other dimension
#   - associate letters with feature name
#   - overlapping or scalar membership

class Features:
    def __init__(self):
        self.features = []

    def get(self):
        """Read the features collection"""
        return self.features

    def add(self, feature):
        """Add one feature to the features collection"""
        if feature not in self.features:
            return
        self.features.append(feature_name)
        return self.get()

    def add_many(self, features=[]):
        """Add multiple features to the collection"""
        if not features:
            return
        for feature in features:
            if feature in self.features:
                continue
            self.add(feature)
        return self.get()

    def has(self, feature):
        """Check if the feature exists in the features collection"""
        if feature in self.features:
            return True
        return False

class Phoneme:
    def __init__(self, symbol):
        self.letters = set()
        self.features = set()
        self.symbol = symbol

    def get(self):
        """Read the letters, features and unique symbol for this phoneme"""
        return {
            'letters': list(self.letters),
            'features': list(self.features),
            'symbol': self.symbol
        }

    def get_letters(self):
        """Read all letters associated with this phoneme"""
        return list(self.letters)

    def get_features(self):
        """Read all features associated with this phoneme"""
        return list(self.features)

    def get_symbol(self):
        """Read the unique symbol representing this phoneme"""
        return self.symbol

    def add_letter(self, letter):
        """Add a letter to the collection of graphemes for this phoneme"""
        self.letters.add(letter)
        return self.get_letters()

    def add_letters(self, letters):
        """Add multiple letters to the graphemes representing this phoneme"""
        if type(letters) is not list:
            return
        for letter in letters:
            self.add_letter(letter)
        return self.get_letters()

    def remove_letter(self, letter):
        """Remove a letter from the graphemes representing this phoneme"""
        letter in self.letters and self.letters.remove(letter)
        return self.get_letters()

    def add_feature(self, feature):
        """Add a feature to the collection of features for this phoneme"""
        self.features.add(feature)
        return self.get_features()

    def remove_feature(self, feature):
        """Remove a feature to the collection of features for this phoneme"""
        feature in self.features and self.features.remove(feature)
        return self.get_features()

class Syllable:
    def __init__(self, structure):
        self.structure = structure

    def get(self):
        """Read the syllable structure"""
        return self.structure

    def update(self, structure):
        """Update the syllable structure"""
        if type(structure) is list:
            self.structure = structure
        return self.structure

class Inventory:
    def __init__(self):
        self.letters = set()
        self.syllables = set()
        self.letters_by_feature = {}
        self.letter_length_limit = 4

    def get_letter(self, features=[]):
        """Find every letter that has the given features"""
        if type(features) is str:
            if feature in self.letters_by_feature:
                return self.letters_by_feature[feature]
            else:
                return None

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
            matching letters &= self.letters_by_feature[feature]

        return list(matching_letters)

    def get_features(self, letter):
        """Read all features associated with a single letter"""
        matching_features = []
        for feature in self.letters_by_feature:
            if letter in self.letters_by_feature[feature]:
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
            self.letters_by_feature[feature] = set()
        if letter not in self.letters_by_feature[feature]:
            self.letters_by_feature[feature].add(letter)
        return self.letters_by_feature[feature]

    def add_letter(self, letter="", *features):
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
            self.syllables.append(syllable)
        return self.syllables

    def remove_syllable(self, syllable):
        """Remove a syllable structure from the inventory syllables collection"""
        if syllable in self.syllables:
            self.syllables.remove(syllable)
        return self.syllables

# TODO handle feature checks in language instead of shared Features dependency
#   - check before passing non C xor V to syll
#   - check before adding consonant or vowel to inventory
#   - check before adding features to phone

# TODO set up default letters and symbols

class Language:
    def __init__(self, name="", name_en="", features=None, inventory=None):
        self.name = name
        self.name_en = name_en
        self.features = feeatures
        self.inventory = inventory

    def set_inventory(self, inventory):
        """Set the inventory object for this language"""
        self.inventory = inventory

    def set_features(self, features):
        """Set the features object for this language"""
        self.features = features

    # TODO add phonemes (incl letters, symbols, features) through here
    # TODO check features here

    def build_word(self, length=1):
        """Form a word following the defined inventory and syllable structure"""
        if not self.inventory and self.inventory.get_syllables():
            return
        word = ""
        for i in range(length):
            syllable_structure = random.choice(self.inventory.get_syllables())
            print(syllable_structure)
            for syllable_letter_feature in syllable_structure:
                letters = self.inventory.get_letter(syllable_letter_feature)
                # TODO choose letters by weighted freq/uncommonness
                if letters:
                    word += random.choice(letters)
        print(word)
        return word

# demo
inventory = Inventory()
# TODO juggle adding unique symbols through Features + Inventory
#       - ? do this inside Language
#       - instead of listing every single feature with each inventory add
inventory.add_letter(letter="t", "consonant", "voiceless", "alveolar", "stop")
inventory.add_letter(letter="dz", "consonant", "voiced", "dental", "affricate")
inventory.add_letter(letter="dh", "consonant", "voiced", "dental", "fricative")
inventory.add_letter(letter="a", "vowel", "low", "back", "unrounded")
inventory.add_letter(letter="i", "vowel", "high", "front", "unrounded")
inventory.add_letter(letter="y", "vowel", "high", "front", "rounded")
inventory.add_letter(letter="u", "vowel", "high", "back", "rounded")
syllables = (Syllable(["consonant", "vowel"]), Syllable(["vowel"]), Syllable(["consonant", "vowel", "consonant"]))
[inventory.add_syllable(syllable) for syllable in syllables]
language = Language(name="Dgemoxahlaqr", name_en="Demoish", inventory=inventory, features=features)
