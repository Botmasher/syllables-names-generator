import random

# TODO stretch to flexible categorization
#   - allow storing retracted or ATR or any other dimension
#   - associate letters with feature name
#   - overlapping or scalar membership

# (Features : features <> (ipa) <> letter : Phoneme)
#   - "feature" is broad, including "consonant" or really any consistent string
#   - "ipa" is any phonetic symbol associated with features
#   - "letter" is generally a looser graphic representation in writing
# features <> syllables
#   - "syllable" is a sequence of feature collections when generating a syllable
#   - a list of features is used to pick each letter in a syllable
# features, letters, syllables < inventory
#   - each letter can be added as multiple phonemes ("th" may be two letters)
#   - OR just have inventory store map of {letter:[phonemes]}
#   - may need to generate not just words but underlying sounds, then letters
# inventory, rules < language
#   - rules contain sequences of lists like syllables
#   - rules couple two sequences, input and operation, for how sounds should change
#   - search for input matches then change specific features
#       - this means storing strings of features for each word, or phon symbs

# features to and from phonetic symbols
class Features:
    def __init__(self):
        self.features = {}

    def get(self):
        """Read the features collection"""
        return self.features

    def get_features(self, ipa):
        """Find all features associated with a phonetic symbol"""
        if type(ipa) is not str:
            return []
        found_features = set()
        for feature in self.features:
            ipa in self.features[feature] and found_features.add(feature)
        return list(found_features)

    def get_ipa(self, features):
        """Find phonetic symbols matching all given features"""
        if type(features) is not list or features[0] not in self.features:
            return []
        # intersect symbols for listed features
        found_ipa = self.features[features[0]]
        for feature in features[1:]:
            if feature in self.features:
                found_ipa &= self.features[features]
            else:
                return []
        return list(found_ipa)

    def add_ipa(self, ipa, features=[]):
        """Add phonetic symbols to feature symbol sets"""
        if type(ipa) is not str or type(features) is not list:
            print("Features add_ipa failed - unknown symbol or features list")
            return
        for feature in features:
            if feature not in self.features:
                print("Features add_ipa failed - unkown feature {0}".format(feature))
                return
        for feature in features:
            self.features[feature].add(ipa)
        return self.get_ipa(features)

    def add_feature(self, feature):
        """Add one feature to the features map"""
        if type(feature) is not str:
            print("Features add_feature failed - invalid feature {0}".format(feature))
            return
        self.features[feature] = set()
        return {feature: self.features[feature]}

    def add_features(self, features=[]):
        """Add multiple features to the map"""
        if not features or type(features) is not list:
            return
        added_features = {}
        for feature in features:
            added_feature = self.add_feature(feature)
            if added_feature:
                added_features[feature] = added_feature.values()[0]
        return added_features

    def distribute_sounds(self, ipa):
        """Populate selectable symbols following a Zipf distribution"""
        # construct a mock population that behaves Zipfianly
        # TODO unrandomize - allow for weighted rank input
        consonants = []
        vowels = []
        consonants_input = list(self.features['consonants'])[:]
        vowels_input = list(self.features['vowels'])[:]
        random.shuffle(consonants_input)
        random.shuffle(vowels_input)
        high_frequency = 1000
        for i in range(len(vowels_input)):
            vowel = vowels_input[i]
            symbol_count = (1 / i) * (most_common_frequency)
            vowels += [vowel] * symbol_count
        for i in range(len(consonants_input)):
            consonant = consonants_input[i]
            symbol_count = (1 / i) * (most_common_frequency)
            consonants += [consonant] * symbol_count
        return {'consonants': consonants, 'vowels': vowels}

    def has_ipa(self, ipa):
        """Check if the phonetic symbol exists in the features map"""
        for feature in self.features:
            if ipa in self.features[feature]:
                return True
        return False

    def has_feature(self, feature):
        """Check if the feature exists in the features map"""
        return feature in self.features

# letters to and from phonetic symbols
# TODO environments for symbol (? or save for rule)
class Phoneme:
    def __init__(self, symbol, letters=[], weight=0):
        self.letters = set(letters)
        self.symbol = symbol
        self.weight = weight

    def get(self):
        """Read the letters, features and unique symbol for this phoneme"""
        return {
            'letters': list(self.letters),
            'symbol': self.symbol,
            'weight': self.weight
        }

    def get_letters(self):
        """Read all letters associated with this phoneme"""
        return list(self.letters)

    def get_symbol(self):
        """Read the unique symbol representing this phoneme"""
        return self.symbol

    def get_weight(self):
        """Read the weight associated with this phoneme"""
        return self.weight

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

    def set_weight(self, weight):
        """Adjust the weight associated with this phoneme"""
        if type(weight) is int:
            self.weight = weight
        return self.weight

    def remove_letter(self, letter):
        """Remove a letter from the graphemes representing this phoneme"""
        letter in self.letters and self.letters.remove(letter)
        return self.get_letters()

    def replace_letter(self, letter, new_letter):
        """Replace one letter in the letters representing this phoneme"""
        self.remove_letter(letter)
        self.add_letter(new_letter)
        return self.get_letters()

    def replace_letters(self, letters=[]):
        """Replace the entire set of letters representing this phoneme"""
        if type(letters) is list:
            self.letters = set(letters)
        return self.get_letters()

# TODO store environments in rules
class Environment:
    def __init__(self):
        return

    def update(self):
        return

class Rules:
    def __init__(self):
        return

    def add(self, source, target):
        return

    def remove(self, rule_id):
        return

# TODO manage suffixes and prefixes by grammatical feature
class Affixes:
    def __init__(self):
        self.prefixes = {}
        self.suffixes = {}
        return

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
                matching_features.append(letter)
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

# TODO handle feature checks in language instead of shared Features dependency
#   - check before passing non C xor V to syll
#   - check before adding consonant or vowel to inventory
#   - check before adding features to phone

# TODO set up default letters and symbols

class Language:
    def __init__(self, name="", name_en="", features=None, inventory=None):
        self.name = name
        self.name_en = name_en
        self.features = features
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
            syllable = random.choice(self.inventory.get_syllables())
            syllable_structure = syllable.get()
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
feature_checker = Features()

# TODO decide if need negative features like "unrounded"
#   pro: makes matching to sound changes "rounded" to "unrounded"
#   con: easily found by filtering for sounds that do not have this feature
feature_checker.add_many(features=[
    "consonant",
    "voiceless",
    "voiced",
    "stop",
    "nasal",
    "fricative",
    "affricate",
    "tap",
    "trill",
    "approximant",
    "liquid",
    "labial",
    "dental",
    "alveolar",
    "postalveolar",
    "palatal",
    "velar",
    "uvular",
    "pharyngeal",
    "glottal",
    "vowel",
    "front",
    "close",
    "mid",
    "open",
    "central",
    "raised",
    "retracted",
    "unrounded",
    "rounded",
    "short",
    "long"
])

# TODO juggle adding unique symbols through Features + Inventory
#   - ? already have default IPA associations availabe in fetures
#   - ? do this inside Language
#   - instead of listing every single feature with each inventory add

# TODO disallowed sequences in syllables
# TODO sound laws in environments

sounds = {
    'a': {
        'letters': ["a", "â"],
        'features': ["vowel", "front", "open", "unrounded", "short"]
    },
    'i': {
        'letters': ["i"],
        'features': ["vowel", "front", "close", "unrounded", "short"]
    },
    'u': {
        'letters': ["u"],
        'features': ["vowel", "raised", "rounded", "short"]
    },
    'p': {
        'letters': ["p", "b"],
        'features': ["consonant", "voiceless", "labial", "stop"]
    },
    't': {
        'letters': ["t", "d"],
        'features': ["consonant", "voiceless", "dental", "stop"]
    },
    'k': {
        'letters': ["k", "g"],
        'features': ["consonant", "voiceless", "velar", "stop"]
    },
    'tʃ': {
        'letters': ["tch", "tj"],
        'features': ["consonant", "voiceless", "postalveolar", "affricate"]
    },
    'f': {
        'letters': ["f", "ph"],
        'features': ["consonant", "voiceless", "labial", "fricative"]
    },
    "θ": {
        'letters': ["th"],
        'features': ["consonant", "voiceless", "dental", "fricative"]
    },
    "x": {
        'letters': ["h"],
        'features': ["consonant", "voiceless", "velar", "fricative"]
    }
}

phonemes = [
    Phoneme(
        ipa,
        letters=v['letters'],
        features=[f for f in v['features'] if feature_checker.has(f)]
    ) for ipa, v in sounds.items()
]

for phoneme in phonemes:
    phoneme_features = phoneme.get_features()
    for phoneme_letter in phoneme.get_letters():
        inventory.add_letter(letter=phoneme_letter, features=phoneme_features)

syllables = (Syllable(["consonant", "vowel"]), Syllable(["vowel"]), Syllable(["consonant", "vowel", "consonant"]))
[inventory.add_syllable(syllable) for syllable in syllables]
language = Language(name="Dgemoxahlaqr", name_en="Demoish", inventory=inventory, features=feature_checker)
language.build_word()
language.build_word(length=3)
language.build_word(length=5)
language.build_word(length=2)
