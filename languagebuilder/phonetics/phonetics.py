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
class Phonetics:
    def __init__(self):
        self.features = {}  # map feature:{ipa}
        self.ipa = {}       # map ipa:{features}

    def has_ipa(self, symbol):
        """Check if the symbol exists in the ipa map"""
        return isinstance(symbol, str) and symbol in self.ipa

    def has_feature(self, feature):
        """Check if the feature exists in the features map"""
        return isinstance(feature, str) and feature in self.features

    # Parse features input
    def parse_features(self, features_input):
        # turn features string into features sequence
        if isinstance(features_input, str):
            features_input = features_input.split()
        
        # verify raw feature input
        if not isinstance(features_input, (list, tuple)):
            print(f"Phonetics parse features failed - invalid raw feature sequence {features_input}")
            return

        # filter down to list of recognized phonetic features
        parsed_features = list(filter(
            lambda x: self.has_feature(x.lower().strip()),
            features_input
        ))
        return parsed_features

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

    def get_ipa(self, features, filter_phonemes=None, exact=False):
        """Find phonetic symbols (optionally restricted to a filtered list)
        matching all and only the given features"""
        # return no matches for empty or null features
        if not features:
            return []

        # optionally restrict phonetic symbols searched
        if filter_phonemes:
            phonetic_symbols = list(filter(
                lambda x: x in self.ipa,
                filter_phonemes
            ))
        else:
            phonetic_symbols = list(self.ipa)

        # find symbols matching requested features to stored features
        found_symbols = set()
        for symbol in phonetic_symbols:
            # store exact or subset match
            match_features = self.ipa[symbol]
            # add exact match if all symbol features are in requested
            is_exact = exact and set(features) == match_features
            # add partial match if all requested features are in symbol
            is_partial = not exact and match_features.issuperset(features)
            if is_exact or is_partial:
                found_symbols.add(symbol)
        
        return list(found_symbols)

    def add_map(self, ipa_features_map):
        """Add phonetic symbols mapped to their associated features"""
        if not isinstance(ipa_features_map, dict):
            print("Features add_map failed - expected dict mapping ipa:features")
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
        # check that the symbol is valid ipa
        if not isinstance(symbol, str):
            print(f"Features add_entry failed to add invalid symbol {symbol}")
            return
        # add each feature to both symbols and features maps
        for feature in features:
            # check that the feature is valid
            if not isinstance(feature, str):
                print(f"Features add_entry skipped invalid feature {feature}")
                continue
            # add features and symbols to their sets
            self.features.setdefault(feature, set()).add(symbol)
            self.ipa.setdefault(symbol, set()).add(feature)
        return {symbol: self.ipa[symbol]}

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
        """Update a feature name in ipa and features maps"""
        # verify that the feature exists
        if not self.has_feature(feature):
            return
        # move the old feature data to the new feature
        old_feature_symbols = self.features[feature]
        self.features[new_feature] = old_feature_symbols
        # remove the old feature from features and symbols maps
        self.remove_feature(
            feature,
            # add the new feature to all symbols that had the old one
            ipa_callback=lambda s: self.ipa[s].add(new_feature)
        )
        # return the updated feature name and data
        return {new_feature: self.features[new_feature]}

    def remove_feature(self, feature, ipa_callback=None):
        """Remove a feature from ipa and features maps"""
        # verify the feature exists
        if not self.has_feature(feature):
            return
        # remove the feature and grab its stored symbols
        symbols = list(self.features.pop(feature))
        # remove the feature from symbols
        for symbol in symbols:
            self.ipa[symbol].remove(feature)
            ipa_callback and ipa_callback(symbol)
        # send back the deleted data
        return {feature: symbols}

    # TODO: unrandomize - allow ordering/sorting
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
