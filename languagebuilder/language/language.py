from ..grammar.grammar import Grammar
from ..phonetics.phonetics import Phonetics
from ..phonology.phonology import Phonology
from ..lexicon.dictionary import Dictionary
from ..lexicon.corpus import Corpus
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
        # min and max length of a randomly generated baseword
        self.syllables_min = 1
        self.syllables_max = 1
        # grammatical paradigms based on dictionary entries
        self.paradigms = Paradigms(self)

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

    # TODO: send built grammar back up here to cache in a history
    def generate(self, length=None, definition="", spell_after_change=True, mid_target=None, pre=False, mid=False, post=False, bound=False, properties=None, word_class=None):
        """Create a word or grammatical piece that follows language's phonology and grammar"""
        # choose a random number of syllables if no syllable count supplied
        if not length:
            length = random.randint(self.syllables_min, self.syllables_max)
        # verify that syllable count is a whole number
        if not isinstance(length, int):
            print(f"Language failed to generate word - invalid number of syllables {length}")
            return
        
        # generate and add grammatical word
        if pre or mid or post:
            # default for uncreated exponents
            empty_entry = {
                'spelling': [],
                'sound': [],
                'change': []
            }

            # generate grammatical pieces for before, inside, after
            pre_word = self.phonology.build_word(
                length=length,
                spell_after_change=spell_after_change
            ) if pre else empty_entry

            mid_word = self.phonology.build_word(
                length=length,
                spell_after_change=spell_after_change
            ) if mid else empty_entry

            post_word = self.phonology.build_word(
                length=length,
                spell_after_change=spell_after_change
            ) if post else empty_entry

            # create the exponent
            exponent_id = self.grammar.exponents.add(
                pre=pre_word['sound'],
                mid=mid_word['sound'],
                post=post_word['sound'],
                properties=properties,
                bound=bound,
                pos=word_class
            )

            # back out if exponent not created
            if not exponent_id:
                print(f"Language generate failed - unable to create grammatical exponent")
                return
            
            # store sound changes and spelling for grammatical pieces
            pre_change = pre_word['change']
            mid_change = mid_word['change']
            post_change = post_word['change']
            pre_spelling = pre_word['spelling']
            mid_spelling = mid_word['spelling']
            post_spelling = post_word['spelling']
            # determine text linkers for formatted dictionary storage
            grammatical_format = {
                'circumfix': "{}- -{}",
                'infix': "-{}-",
                'prefix': "{}-",
                'suffix': "-{}",
                'multifix': "{}-{}-{}",
                'circumposition': "{}...{}",
                'interposition': "...{}...",
                'preposition': "{}",
                'postposition': "{}",
                'multiposition': "{}...{}...{}"
            }
            # basic term to define forms
            grammatical_form = self.grammar.grammatical_form(pre, mid, post, bound)
            
            # Format sound, spelling, and change strings
            # TODO: use exponents to create a formatted properties and word class string
            #   - aren't the exponent pieces in lists though?
            #   - simplify spacing
            #   - really store this extra formatting in the dictionary?
            # 
            if mid and (pre or post):
                formatted_word = grammatical_format[grammatical_form].format(pre_word['sound'], mid_word['sound'], post_word['sound'])
                formatted_change = grammatical_format[grammatical_form].format(pre_change, mid_change, post_change)
                formatted_spelling = grammatical_format[grammatical_form].format(pre_spelling, mid_spelling, post_spelling)
            elif mid:
                formatted_word = grammatical_format[grammatical_form].format(mid_word['sound'])
                formatted_change = grammatical_format[grammatical_form].format(mid_change)
            elif pre and post:
                formatted_word = grammatical_format[grammatical_form].format(pre_word['sound'], post_word['sound'])
                formatted_change = grammatical_format[grammatical_form].format(pre_change, post_change)
            elif pre:
                formatted_word = grammatical_format[grammatical_form].format(pre_word['sound'])
                formatted_change = grammatical_format[grammatical_form].format(pre_change)
            else:
                formatted_word = grammatical_format[grammatical_form].format(post_word['sound'])
                formatted_change = grammatical_format[grammatical_form].format(post_change)

            # format definition
            formatted_definition = self.grammar.autodefine(exponent_id)
            
            # store and return a grammatical word entry
            return self.store(
                word=formatted_word,
                definition=formatted_definition,
                change=formatted_change,
                spelling=formatted_spelling,
                exponent_id=exponent_id
            )
        
        # Generate and store a base word entry
        word = self.phonology.build_word(
            length=length,
            spell_after_change=spell_after_change
        )
        # check supplied part of speech
        if word_class and not self.grammar.word_classes.get(word_class):
            print(f"Language generate failed - invalid word class {word_class}")
            return
        # store created word or word piece and return lookup info
        return self.store(
            word=word['sound'],
            change=word['change'],
            definition=definition.strip(),
            spelling=word['spelling'],
            word_class=word_class
        )

    def add_grammar(self, entry_headword, entry_index, pre=False, mid=False, post=False, bound=False, properties="", word_classes=""):
        """Add grammatical data to an existing stored entry"""
        if not self.dictionary.lookup(entry_headword, entry_index):
            print(f"Language add_grammar could not grammaticalize invalid entry {entry_headword}({entry_index})")
            return
        vetted_properties = self.grammar.parse_properties(properties)
        vetted_word_classes = self.grammar.parse_word_classes(word_classes)
        
        exponent_id = self.grammar.exponents.add(
            pre=pre,
            mid=mid,
            post=post,
            bound=bound,
            properties=vetted_properties,
            pos=vetted_word_classes
        )

        # NOTE: grammar treating as word with pos or as exponent
        #   - non-exponents can have a word class
        #   - exponents can be restricted to providing to certain word classs
        # TODO: abstract grammar definition creation from .generate 
        self.dictionary.update(
            entry_headword,
            entry_index,
            definition=self.grammar.autodefine(exponent_id),
            exponent=exponent_id
        )
        return self.dictionary.lookup(entry_headword, entry_index)

    # TODO: create sentences checking grammar 
    def create_sentence(self, name, structure):
        return
    # TODO: apply sentences looking up headwords
    def apply_sentence(self, name, headwords):
        bases = [
            self.dictionary.lookup(*headword)
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
            base_sounds = list(base)
            base_definition = "(undefined)"

        # build grammatical unit with underlying sounds
        unit_sounds = self.grammar.build_unit(
            base_sounds,
            properties=properties,
            word_classes=word_classes
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
    #   - for grammar, send to corpus 
    #   - also store grammar in dictionary but with exponent id
    #   - should results of sound changes really be stored? or refs to the rules?
    #   - should separate spellings be stored for changes? or flag for spelling before/after change?
    #   - core idea is to store important data for display but only 
    def store(self, word="", definition="", spelling="", change="", exponent_id=None, word_class=None):
        """Pass word entry components through to the dictionary for storage"""
        #word_class = self.grammar.exponents.get(exponent_id).get('pos')
        #examples = self.craft_paradigm(word_class)
        return self.dictionary.add(
            sound=word,
            spelling=spelling,
            change=change,
            definition=definition,
            exponent=exponent_id,
            pos=word_class
            # examples=examples
        )