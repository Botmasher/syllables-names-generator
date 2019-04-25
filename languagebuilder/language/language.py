from ..grammar.grammar import Grammar
from ..phonetics.phonetics import Phonetics
from ..phonology.phonology import Phonology
from ..lexicon.dictionary import Dictionary
from ..lexicon.corpus import Corpus
import random

# TODO: Accentuation, suprasegmentals

# TODO: consider also storing bound flag for bases

# NOTE: throughout the code "ipa" (usu uncaps) denotes any stored phonetic symbols
# associated with a set of features in a language

# TODO: consider layering spelling & sound change before storing vs when requested
#   NOTE:   similar update problems when syllables or phonemes change anyhow; how
#           consistent do you want updates/stores to be compared to structures?
#   - fast access when computed then stored
#   - computing on request avoids updated letters/rules leaving legacy sounds/spellings
#   - similar consideration to storing exponents though!
#   - instead could have update functions through language
#       - these manage both storage and manipulation

# Shape of stored language data
# NOTE: look up using ('word', entry_index)
# dictionary : {
#   'word': [
#       {
#           'phones': "",       # phonemes generated for the word
#           'change': "",       # phones after sound change rules applied
#           'spelling': "",     # letters after spelling applied
#           'rules': [],        # list of ids for sound change rules applied
#           'word_class': "",   # part of speech used for word grammar
#           'definition': "",   # user-inputted string defining the word (built automatically for exponents)
#           'tags': []          # semantic tags for searching for the word
#           'exponent': ""      # id pointing to attributes if grammatical piece
#       },
#   ]
#   ...
# }
# 
# units / corpus : {
#   'example_id': {
#       'phones': ""            # string containing the built unit example phones
#       'change': ""            # string after sound changes applied
#       'boundaries': True      # whether sound change applied across boundaries
#       'spelling': ""          # string after spelling applied
#       'spell_change': True    # whether spelling applied after sound changes
#       'exponents': []         # exponents attached to this unit
#   },
#   ...
# }
#
# TODO: lay out patterns for exponents around base
# paradigms : {
# }

# TODO: language-level methods atop various components to check then pass through
# - handle feature checks in language instead of shared Features dependency
#   - check before passing non C xor V to syll
#   - check before adding consonant or vowel to inventory
#   - check before adding features to phone
# - language dictionary storing created words and definitions
# - set up default letters and symbols
# - have language check inventory, environment, rules
#   - e.g. avoid ['smiles', '_', 'sauce'] allow ['vowel', '_', 'vowel']
#   - '0', '#' when applying rules
# - see tasks within other class files

class Language:
    def __init__(self, name="", display_name=""):
        self.name = name
        self.display_name = display_name
        # ipa (sound symbols) and features
        self.phonetics = Phonetics()
        # word classes, properties, exponents
        self.grammar = Grammar()
        # phonemes and syllables atop phonetics
        self.phonology = Phonology(self.phonetics)
        # words with ipa, morphology, definition
        self.dictionary = Dictionary()
        # built units with grammar attached
        self.corpus = Corpus()

    def rename(self, name="", display_name=""):
        """Set the id name or display name for the language"""
        self.name = name if name else self.name
        self.display_name = display_name if display_name else self.display_name
        return {
            'name': self.name,
            'display_name': self.display_name
        }

    # TODO: send built sounds back up here to store them in dictionary
    #   - otherwise must pass language/dictionary down to phonology to store

    # TODO: send built grammar back up here to cache in a history
    def generate(self, length=1, definition="", spell_after_change=True, pre=False, post=False, bound=False, properties=None, word_class=None):
        # choose a random number of syllables if no syllable count supplied
        if not length:
            length = random.randrange(1, 5)
        # verify that syllable count is a whole number
        if not isinstance(length, int):
            print(f"Language failed to generate word - invalid number of syllables {length}")
            return
        
        # expect a single string for one part of speech
        if word_class and not isinstance(word_class, str):
            print(f"Language generate failed - expected one part of speech in a word_class string")
            return

        # generate the created phonemes in syllables
        word = self.phonology.build_word(length=length, spell_after_change=spell_after_change)
        
        # add as grammatical word
        if pre or post:
            empty_entry = {'spelling': "", 'sound': "", 'change': ""}
            # determine word to attach before or after
            pre_word = word if pre else empty_entry
            post_word = word if post else empty_entry
            # generate a second word piece for circum material
            if pre and post:
                post_word = self.phonology.build_word(length=length, spell_after_change=spell_after_change)
            # create the exponent
            exponent_id = self.grammar.exponents.add(
                pre=pre_word['sound'],
                post=post_word['sound'],
                properties=properties,
                bound=bound,
                pos=word_class
            )
            # store sound changes and spelling for both grammatical pieces
            pre_change = pre_word['change']
            post_change = post_word['change']
            pre_spelling = pre_word['spelling']
            post_spelling = post_word['spelling']
            # determine text linkers for formatted dictionary storage
            grammatical_forms = {
                (True, True, True): ("circumfix", "- -"),
                (True, False, True): ("prefix", "-"),
                (True, False, False): ("suffix", "-"),
                (False, True, True): ("circumposition", " ... "),
                (False, False, True): ("preposition", ""),
                (False, False, False): ("postposition", "")
            }
            # basic term to define forms
            grammatical_form = grammatical_forms[(bound, pre and post, pre)][0]
            # concatenator to place before, between or after forms
            spacing = grammatical_forms[(bound, pre and post, pre)][1]
            
            # TODO: use exponents to create a formatted properties and word class string

            # format forms with spacing
            formatted_word = f"{pre_word}{spacing}{post_word}"
            formatted_change = f"{pre_change}{spacing}{post_change}"
            # format definition
            formatted_definition = f"{grammatical_form} for {self.grammar.pretty_properties(properties)}{(f' {word_class}s', f'')[not word_class]}"
            # format the word spelling (before/after sound changes)
            formatted_spelling = f"{pre_spelling}{spacing}{post_spelling}"
            
            # store and return a grammatical word entry
            return self.store(
                formatted_word,
                formatted_definition,
                formatted_change,
                formatted_spelling,
                exponent_id
            )
        
        # Store and return a base word entry
        # store created word or word piece and return lookup info
        return self.store(
            word=word['sound'],
            change=word['change'],
            definition=definition.strip(),
            spelling=word['spelling']
        )

    def add_grammar(self, entry_headword, entry_index, pre=False, post=False, bound=False, properties="", word_classes=""):
        """Add grammatical data to an existing stored entry"""
        if not self.dictionary.lookup(entry_headword, entry_index):
            print(f"Language add_grammar could not grammaticalize invalid entry {entry_headword}({entry_index})")
            return
        vetted_properties = self.grammar.parse_properties(properties)
        vetted_word_classes = self.grammar.parse_word_classes(word_classes)
        
        exponent_id = self.grammar.exponents.add(
            pre=pre,
            post=post,
            bound=bound,
            properties=vetted_properties,
            pos=vetted_word_classes
        )

        # TODO: abstract grammar definition creation from .generate 
        self.dictionary.update(
            #definition=self.dictionary.define(),
            exponent=exponent_id
        )
        return self.dictionary.lookup(entry_headword, entry_index)

    def translate(self, definition, properties="", word_class=""):
        """Attempt to render a single base plus grammatical properties
        in the target language"""
        words = self.dictionary.search(definition)
        if not words:
            print(f"Language failed to translate - no word for {definition}")
            return
        return self.attach(
            base=words[0][0],
            entry_index=words[0][1],
            properties=properties,
            word_classes=word_class
        )

    def attach(self, base="", entry_index=0, properties=None, word_classes=None, lookup=True, spell_after_change=True):
        """Attach grammatical pieces around a base headword. Look up the base in the
        language's dictionary and use added exponents from the language's grammar."""
        # - iterate through grammar for that part of speech
        # - produce a unit
        # - or produce a table of all possible forms
        # - store the unit in the corpus
    
        if lookup and not self.dictionary.is_word(base):
            print(f"Language attach failed - unrecognized base word {base}")
            return

        # TODO: store word classes in dictionary
        
        # locate headword entry for base
        if lookup:
            base_entry = self.dictionary.lookup(headword=base, entry_index=entry_index)
            base_sounds = base_entry['sound']
            base_definition = base_entry['definition']
        # use given one-off base
        # TODO: consider definitions
        else:
            base_sounds = base
            base_definition = "(ad hoc base)"

        # compute spelling, underlying sounds and changed sounds
        unit_sounds = self.grammar.build_unit(
            base_sounds,
            properties=properties,
            word_classes=word_classes
        )
        unit_change = self.phonology.apply_rules(unit_sounds)
        if spell_after_change:
            unit_spelling = self.phonology.spell(unit_change, unit_sounds)
        else:
            unit_spelling = self.phonology.spell(unit_sounds)
        
        # unable to spell unit
        if not unit_spelling:
            raise ValueError(f"Language attach failed to spell unit - missing letters for built sounds {unit_sounds}")

        # TODO: get out the exponents used to build the unit
        #       - this way corpus can store then and their properties can be read later
        #       - alternatively store semantics with base definition, properties, word_classes
        exponents = []

        # format and store entry for built grammatical unit
        # TODO: vet properties and pos
        return self.corpus.add(
            sound=unit_sounds,
            change="".join(unit_change),
            spelling="".join(unit_spelling),
            definition=base_definition,
            exponents=exponents
        )

    # TODO: generate and store examples in either dictionary or corpus
    #   - take in a definition
    #   - take in a word class
    #   - for grammar, send to corpus 
    #   - also store grammar in dictionary but with exponent id
    #   - should results of sound changes really be stored? or refs to the rules?
    #   - should separate spellings be stored for changes? or flag for spelling before/after change?
    #   - core idea is to store important data for display but only 
    def store(self, word="", definition="", spelling="", change="", exponent_id=None):
        """Pass word entry components through to the dictionary for storage"""
        return self.dictionary.add(
            sound=word,
            spelling=spelling,
            change=change,
            definition=definition,
            exponent=exponent_id
        )
    
