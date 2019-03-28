import random

# TODO: move to documentation - discusses components across a Language
# (features <> ipa < Phonetics | Phonology > phoneme <> letter)
#   - "feature" is broad, including "consonant" or really any consistent string
#   - "ipa" is any phonetic symbol associated with features
#   - "letter" is generally a looser graphic representation in writing
# features and syllables
#   - "syllable" is a sequence of feature collections when generating a syllable
#   - a list of features is used to pick each letter in a syllable
# features, letters, syllables, rules < inventory
#   - each letter can be added as multiple phonemes ("th" may be two letters)
#   - OR just have inventory store map of {letter:[phonemes]}
#   - may need to generate not just words but underlying sounds, then letters
# rules
#   - rules contain sequences of lists like syllables
#   - rules couple two sequences, input and operation, for how sounds should change
#   - search for input matches then change specific features
#       - this means storing strings of features for each word, or phon symbs

# features to and from phonetic symbols
class Features:
    def __init__(self):
        self.features = {}  # map feature:{ipa}
        self.ipa = {}       # map ipa:{features}

    def has_ipa(self, symbol):
        """Check if the symbol exists in the ipa map"""
        return isinstance(symbol, str) and symbol in self.ipa

    def has_feature(self, feature):
        """Check if the feature exists in the features map"""
        return isinstance(feature, str) and feature in self.features

    def map_by_features(self):
        """Read the ipa-per-features map"""
        return self.features

    def map_by_ipa(self):
        """Read the features-per-ipa map"""
        return self.ipa

    def get_features(self, symbol):
        """Find all features associated with a phonetic symbol"""
        if not self.has_ipa(symbol):
            print(f"Features get_features failed - invalid phonetic symbol {symbol}")
            return []
        return list(self.ipa[symbol])

    def get_ipa(self, features, filter_phonemes=[], exact=True):
        """Find phonetic symbols (optionally restricted to a filtered list) matching all given features"""
        if len(features) < 1:
            return []
        # optionally restrict phonetic symbols searched
        phonetic_symbols = filter_phonemes if filter_phonemes else self.ipa.keys()
        # compare test features to stored features for symbol matches
        found_symbols = set()
        for symbol in phonetic_symbols:
            if symbol not in self.ipa:
                print("Features get_ipa skipped unknown phonetic filter symbol {0}".format(symbol))
                continue
            # store exact or subset match
            match_features = self.ipa[symbol]
            if exact and not set(features) ^ match_features:
                found_symbols.add(symbol)
            elif match_features.issuperset(features):
                found_symbols.add(symbol)
        return list(found_symbols)

    def add_map(self, ipa_features_map):
        """Add phonetic symbols mapped to their associated features"""
        if type(ipa_features_map) is not dict:
            print("Features add_map failed - expected dict not {0}".format(type(ipa_features_map)))
            return
        # new symbols and new features - other methods do one or the other
        for symbol, features in ipa_features_map.items():
            self.add_entry(symbol, features)
        return True

    # NOTE: sync handling two-way mapping between features and symbols
    #
    # expected: every features key exists in the values set for eachof its listed symbols
    # expected: every ipa key exists in the values set for each of its listed features
    #
    # alternative: reduce inventory map from subset instead of duping all features data
    #   - here just store map of {symbol:{features}}
    #   - inventory creates two-way maps for quick lookups from language's chosen features/symbols
    #
    def add_entry(self, symbol, features):
        """Alias for Features.add method"""
        return self.add(symbol, features)

    def add(self, symbol, features):
        """Add one phonetic symbol and its associated features to the maps"""
        if not isinstance(symbol, str): #or len(symbol) > 2:
            print(f"Features add_entry failed to add invalid symbol {symbol}")
            return
        added_features = []
        for feature in features:
            if not isinstance(feature, str):
                print(f"Features add_entry skipped invalid feature {feature}")
            else:
                if feature not in self.features:
                    self.features[feature] = set()
                if symbol not in self.ipa:
                    self.ipa[symbol] = set()
                self.features[feature].add(symbol)
                self.ipa[symbol].add(feature)
                added_features.append(feature)
        return {symbol: added_features}

    # NOTE: maps crud still untested
    def update_symbol(self, symbol, new_symbol):
        """Update a symbol in ipa and features maps"""
        if not self.has_ipa(symbol):
            return
        features = self.ipa[symbol]
        self.ipa[new_symbol] = features
        self.remove_symbol(
            symbol,
            feature_callback=lambda f: self.features[f].add(new_symbol)
        )
        return {new_symbol: self.ipa[new_symbol]}

    def remove_symbol(self, symbol, feature_callback=None):
        """Remove a symbol from ipa and features maps"""
        if not self.has_ipa(symbol):
            return
        features = list(self.ipa[symbol])
        self.ipa.pop(symbol)
        for feature in features:
            self.features[feature].remove(symbol)
            feature_callback and feature_callback(feature)
        return features

    def update_feature(self, feature, new_feature):
        """Update a feature in ipa and features maps"""
        if not self.has_feature(feature):
            return
        self.remove_feature(
            feature,
            ipa_callback=lambda s: self.ipa[s].add(new_feature)
        )
        return {new_feature: self.features[new_feature]}

    def remove_feature(self, feature, ipa_callback=None):
        """Remove a feature from ipa and features maps"""
        if not self.has_feature(feature):
            return
        symbols = list(self.features[feature])
        for symbol in symbols:
            self.ipa[symbol].remove(feature)
            ipa_callback and ipa_callback(symbol)
        return symbols

    # TODO unrandomize - allow for weighted rank input
    def distribute_sounds(self, ipa):
        """Populate selectable symbols following a Zipf distribution"""
        # construct a mock population that behaves Zipfianly
        consonants = []
        vowels = []
        consonants_input = list(self.features['consonants'])[:]
        vowels_input = list(self.features['vowels'])[:]
        random.shuffle(consonants_input)
        random.shuffle(vowels_input)
        high_frequency = 1000
        for i in range(len(vowels_input)):
            vowel = vowels_input[i]
            symbol_count = (1 / i) * (high_frequency)
            vowels += [vowel] * symbol_count
        for i in range(len(consonants_input)):
            consonant = consonants_input[i]
            symbol_count = (1 / i) * (high_frequency)
            consonants += [consonant] * symbol_count
        return {'consonants': consonants, 'vowels': vowels}

    # OLD methods for managing one map or the other
    def _add_ipa(self, symbol, features, overwrite_symbol=False):
        """Add a phonetic symbol to existing feature symbol sets"""
        if type(symbol) != str or type(features) != list:
            print("Features add_ipa failed - invalid symbol or features")
            return False
        # add new symbol
        if not self.has_ipa(symbol) or overwrite_symbol:
            print("Features add_ipa - adding new symbol {0}".format(symbol))
            self.ipa[symbol] = set()
        # add features to symbol
        for feature in features:
            if not self.has_feature(feature):
                print("Features add_ipa skipped unknown feature {0} for symbol {1}".format(feature, symbol))
            else:
                self.ipa[symbol].add(feature)
        return True

    def _add_features(self, features, symbol=None):
        """Add features to the features map with an associated phonetic symbol"""
        if type(features) is not list:
            print("Features add_features failed - invalid features list {0}".format(features))
            return False
        for feature in features:
            # log unrecognized or new features
            if type(feature) is not str:
                print("Features add_feature skipped invalid feature {0}".format(feature))
            # add feature
            if not self.has_feature(feature):
                print("Adding new feature {0}".format(feature))
                self.features[feature] = set()
            # add symbol to feature
            symbol and self.features[feature].add(symbol)
        return True

    def _add_feature(self, feature, default_value=None):
        """Add one new feature to the features map"""
        if type(feature) is not str:
            print("Features add_feature failed - invalid feature {0}".format(feature))
            return
        if feature not in self.features:
            self.features[feature] = {default_value} if default_value else {}
            return feature
        print("Features add_feature ignored {0} - key already exists".format(feature))
        return
