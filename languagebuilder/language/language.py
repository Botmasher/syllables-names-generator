from ..grammar.grammar import Grammar, Sentences
from ..phonetics.phonetics import Phonetics
from ..phonology.phonology import Phonology
from ..reference.vocabulary import Vocabulary
from ..reference.summary import Summary
from ..reference.corpus import Corpus
from .paradigms import Paradigms
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
# - language vocabulary storing created base words and definitions
# - set up default letters and symbols
# - have language check inventory, environment, rules
#   - e.g. avoid ['smiles', '_', 'sauce'] allow ['vowel', '_', 'vowel']
#   - '0', '#' when applying rules
# - see tasks within other class files

class Language:
    def __init__(self, name="", display_name="", boundary_symbol="#", source_symbol="_", affix_symbol="-", spacing_symbol=" "):
        self.name = name
        self.display_name = display_name
        # ipa (sound symbols) and features
        self.phonetics = Phonetics()
        # word classes, properties, exponents
        self.grammar = Grammar()
        # for building and applying sentences
        self.sentences = Sentences(self.grammar)
        # phonemes and syllables atop phonetics
        self.phonology = Phonology(self.phonetics)
        # words with ipa, morphology, definition
        self.vocabulary = Vocabulary()
        # grammar storage and display
        self.corpus = Corpus()
        self.summary = Summary(self)
        # min and max length of a randomly generated baseword
        self.syllables_min = 1
        self.syllables_max = 1
        # grammatical paradigms based on dictionary entries
        self.paradigms = Paradigms(self)

        # stored special symbols to avoid hardcoding
        # TODO: pass these down to Phonology, Grammar
        self.boundary_symbol = boundary_symbol
        self.source_symbol = source_symbol
        self.affix_symbol = affix_symbol
        self.spacing_symbol = spacing_symbol

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

    def syllables_min_max(self, min_count=None, max_count=None):
        """Set the min or max number of syllables for generated words"""
        if min_count and isinstance(min_count, int):
            self.syllables_min = min_count
        if max_count and isinstance(max_count, int):
            self.syllables_max = max_count
        return (self.syllables_min, self.syllables_max)

    def decide_length(self, length=None):
        """Check for valid length integer or choose a length if none supplied.
        Intended for generating words with length number of syllables."""
        # choose a random number of syllables if no syllable count supplied
        if not length:
            length = random.randint(self.syllables_min, self.syllables_max)
        # verify that syllable count is a whole number
        if not isinstance(length, int):
            print(f"Language failed to generate word - invalid number of syllables {length}")
            return
        return length

    # TODO: adjust midpoint for infixes like fi-n-dere
    def create_base(self, length=None, definition="", spell_after_change=True, midpoint=None, word_class=None):
        """Generate a base word in the language and store it in the vocabulary,
        returning the headword lookup pair for its vocabulary entry."""
        length = self.decide_length(length)
        
        # generate a base word entry
        word = self.phonology.build_word(
            length=length,
            spell_after_change=spell_after_change,
            # build_word calculates target infix break in base word
            # NOTE: reads input as syllables count, changes to sound count
            midpoint=midpoint
        )
        # check supplied part of speech
        if word_class and not self.grammar.word_classes.get(word_class):
            print(f"Language generate failed - invalid word class {word_class}")
            return
        
        # store created word or word piece and return lookup info
        return self.vocabulary.add(
            sound=word['sound'],
            change=word['change'],
            spelling=word['spelling'],
            definition=definition.strip(),
            midpoint=word['midpoint'],
            pos=word_class
        )

    def set_midpoint(self, headword, entry_index, midpoint=0):
        """Change the split/infix midpoint for an existing vocabulary word"""
        vocabulary_entry = self.vocabulary.lookup(headword, entry_index)
        vocabulary_entry['midpoint'] = midpoint
        self.vocabulary.vocabulary[headword][entry_index] = vocabulary_entry
        return vocabulary_entry

    # TODO: send built grammar back up here to cache in a history
    def create_grammar(self, length=None, definition="", pre=False, mid=False, post=False, bound=True, properties=None, word_class=None):
        """Generate a grammatical exponent, returning the grammatical summary of the
        created pieces and their attributes, including exponent id in the grammar."""
        # generate grammatical pieces for before, inside, after
        length = self.decide_length(length)
        pieces = {
            'pre': pre,
            'mid': mid,
            'post': post,
        }
        pieces = {
            k: self.phonology.build_word(length)['sound']
            for k, v in pieces.items() if v
        }

        # create the exponent
        exponent_id = self.grammar.exponents.add(
            pre=pieces.get('pre'),
            mid=pieces.get('mid'),
            post=pieces.get('post'),
            properties=properties,
            bound=bound,
            pos=word_class
        )

        # back out if exponent not created
        if not exponent_id:
            print(f"Language generate failed - unable to create grammatical exponent")
            return
        
        # return a grammatical exponent summary
        # NOTE: only base words stored in vocabulary; exponents can be summarized
        return self.summary.summarize_exponent(exponent_id)

    def generate(self, length=None, definition="", spell_after_change=True, midpoint=None, pre=False, mid=False, post=False, bound=True, properties=None, word_class=None):
        """Create a word or grammatical piece that follows the phonology and grammar"""        
        # generate grammatical word
        if pre or mid or post:
            return self.create_grammar(length, definition, pre, mid, post, bound, properties, word_class)
        # generate base word
        else:
            return self.create_base(length, definition, spell_after_change, midpoint, word_class)

    # TODO: link grammaticalized vocabulary items to associated grammatical exponent
    def grammaticalize(self, entry_headword, entry_index, pre=False, mid=False, post=False, bound=False, properties="", word_classes=""):
        """Grammaticalize a vocabulary item and add it to the language's summary"""
        # check for valid word 
        vocabulary_item = self.vocabulary.lookup(entry_headword, entry_index)
        if not vocabulary_item:
            print(f"Language could not grammaticalize invalid entry {entry_headword}({entry_index})")
            return
        
        # check for valid grammar
        vetted_properties = self.grammar.parse_properties(properties)
        vetted_word_classes = self.grammar.parse_word_classes(word_classes)
        # expect only one of pre, mid, post
        if (pre, mid, post).count(True) != 1:
            print(f"Language could not grammaticalize {entry_headword} - indicate only one of pre, mid, post")
            return

        # determine a single exponent positional value to add
        # NOTE: what happens if collides with existing exponent?
        vocabulary_sounds = vocabulary_item['sound']
        added_pre = vocabulary_sounds if pre else None
        added_mid = vocabulary_sounds if mid else None
        added_post = vocabulary_sounds if post else None

        # add element to the grammar and send back its id
        return self.grammar.exponents.add(
            pre=added_pre,
            mid=added_mid,
            post=added_post,
            bound=bound,
            properties=vetted_properties,
            pos=vetted_word_classes
        )

    # TODO: create sentences checking grammar 
    def create_sentence(self, name, structure):
        return
    # TODO: apply sentences looking up headwords
    def apply_sentence(self, name, headwords):
        bases = [
            self.vocabulary.lookup(*headword)
            for headword in headwords
        ]
        built_sentence = self.sentences.apply(name, bases)
        sentence = {
            'sound': built_sentence['sound'],
            'change': self.change_sounds(built_sentence),
            'definition': built_sentence['definition']
        }
        return sentence

    # TODO: three levels of spreading change / blocking changes
    #   - change within morphs only
    #       - currently needs to be done from within Sentences.apply
    #       - requires accessing 'change' value from within Grammar.build_unit
    #   - change within words
    #   - change within sentence
    def change_sounds(self, sounds, blocked_by_spacing=True, spacing=" "):
        """Run a sound change on a list of ipa symbols representing a string
        of sounds in the language. Originally built to change built sentences.
        Pass in spacing to recognize word boundaries. Have spacing block
        changes from spreading beyond words."""
        
        # break ipa list into sublists for each word
        grouped_words = [[],]
        for symbol in sounds:
            # split into a new list at spacing
            if symbol == spacing:
                grouped_words.append([])
            # add character to end of latest split list
            else:
                last_i = len(grouped_words) - 1
                grouped_words[last_i].append(symbol)
            
        # get rid of empty lists
        grouped_words = list(filter(lambda x: x, grouped_words))

        # Change sounds for each grouped word
        # spread sound change up to word boundary
        if blocked_by_spacing:
            # change each word
            changed_sounds = [self.phonology.apply_rules(word) for word in grouped_words]
            # flatten the list and add spacing between words
            changed_sounds = [
                sound for word in changed_sounds
                for sound in word + [spacing]
            ][:-1]  # trim final added spacing
        # spread sound change across entire structure
        else:
            # TODO: verify that length and order are left unchanged
            changed_sounds = grouped_words
            # flatten list, change, then restructure back following original list
            sounds_to_change = [sound for word in grouped_words for sound in word]
            unspaced_change = self.phonology.apply_rules(sounds_to_change)

            # separate changed sounds into words following the original words list
            changed_sounds = []
            for i, word in enumerate(grouped_words):
                # add spacer before words except the first word
                if changed_sounds:
                    changed_sounds.append(spacing)
                # find the start and end index of each word
                changed_start = len(grouped_words[i - 1]) if i > 0 else 0
                changed_end = len(word) + changed_start
                # add the changed sounds for this word
                changed_sounds += unspaced_change[changed_start:changed_end]
        
        # flat list of sound symbols with words separated by spacing
        return changed_sounds

    def translate(self, definition, properties="", word_class=""):
        """Attempt to render a single base plus grammatical properties
        in the target language"""
        words = self.vocabulary.search(definition)
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
        if lookup and not self.vocabulary.is_word(base):
            raise KeyError(f"Language attach failed - vocabulary does not have base word {base}")

        # locate headword entry for base
        if lookup:
            base_entry = self.vocabulary.lookup(headword=base, entry_index=entry_index)
            base_sounds = base_entry['sound']
            base_definition = base_entry['definition']
            midpoint = base_entry['midpoint']
        # use given one-off base
        # TODO: consider definitions
        else:
            base_sounds = list(base)
            base_definition = "(undefined)"
            midpoint = 0

        # build grammatical unit with underlying sounds
        unit_sounds = self.grammar.build_unit(
            base_sounds,
            properties=properties,
            word_classes=word_classes,
            spacing=self.spacing_symbol,
            midpoint=midpoint
        )
        # compute changed sounds
        unit_change = self.phonology.apply_rules(unit_sounds)
        
        # obtain and store spelling
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
        # TODO: sound changes across boundaries (units spacing character " ")
        return self.corpus.add(
            sound=unit_sounds,
            change=unit_change,
            spelling=unit_spelling,
            definition=base_definition,
            exponents=exponents
        )
    
    # TODO: generate and store examples in either dictionary or corpus
    # NOTE: use Paradigms
    #   - take in a definition
    #   - take in a word class
    #   - for grammar rely on Summary instead
    #   - should results of sound changes really be stored? or refs to the rules?
    #   - should separate spellings be stored for changes? or flag for spelling before/after change?
