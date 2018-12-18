import random

# TODO stretch to flexible categorization
#   - allow storing retracted or ATR or any other dimension
#   - associate letters with feature name
#   - overlapping or scalar membership

class Features:
    def __init__(self):
        self.voicing = []
        self.manner = []
        self.place = []
        self.height = []
        self.backness = []
        self.rounding = []

    def add_feature(self, feature_type, feature_name):
        if not hasattr(self, str(feature_type)):
            return
        features_list = getattr(self, feature_type)
        features_list.append(feature_name)
        return features_list

    def get(self):
        return {
            'consonants': {
                'voicing': self.voicing,
                'manner': self.manner,
                'place': self.place,
            },
            'vowels': {
                'height': self.height,
                'backness': self.backness,
                'rounding': self.rounding
            }
        }

    def add_features(self, features_dict={}):
        if not features_dict:
            return
        for feature_type in features_dict:
            if not hasattr(self, feature_type):
                continue
            for feature in features_dict[feature_type]:
                self.add_feature(feature_type, feature)
        return self.get()

    def is_consonant(self, voicing, place, manner):
        if place not in self.features.place:
            return False
        elif voicing not in self.features.voicing:
            return False
        elif manner not in self.features.manner:
            return False
        else:
            return True

    def is_vowel(self, height, backness, rounding):
        if height not in self.features.height:
            return False
        elif backness not in self.features.backness:
            return False
        elif rounding not in self.features.rounding:
            return False
        else:
            return True

# TODO build phones and sylls
class Phoneme:
    def __init__(self, symbol):
        self.letters = []
        self.symbol = symbol
    def add_letter():
        return
    def remove_letter():
        return
    def add_feature():
        return
    def remove_feature():
        return

class Syllable:
    def __init__(self, structure=[]):
        self.structure = structure
        self.letters = ['C', 'V']
    def update_syllable():
        return

class Inventory:
    def __init__(self, features):
        self.features = features
        self.letters = {'consonants': [], 'vowels': []}
        self.syllables = []
        self.letters_by_feature = {}
        self.features_by_letter = {}    # each letter allows variants in feat subarrays

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
        print(self.letters)
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

# TODO handle feature checks in language instead of shared Features dependency
#   - check before passing non C xor V to syll
#   - check before adding consonant or vowel to inventory
#   - check before adding features to phone

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
