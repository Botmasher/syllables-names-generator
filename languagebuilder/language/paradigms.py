import re

# morphological paradigms built using language's dictionary and grammar
#   - for syntactic patterns use language's grammar.morphosyntax
#   - or put paradigms together (like multiple noun construct states)
class Paradigms:
    def __init__(self, language):
        # reference to language for dictionary, grammar, phonology
        # dictionary: fetch and check headwords
        # grammar: build units
        # phonology: apply sound changes
        self.language = language

        # paradigm name:slots storage
        # where name is custom name
        # and slot is
        self.paradigms = {}
    
    # Paradigm creation - defining basic syntax
    #
    # TODO: structure syntax and morphology through grammar
    #   - think of this as building out unit options
    #   - run through exponent attachment orders
    #   - so really all you need here is list of exponents in slots
    #
    # NOTE: first attempt merely took a word class and
    #       attached every exponent individually to a base
    
    def print_paradigm(self, name):
        """Format and print a string displaying a paradigm's name and slots"""
        paradigm = self.paradigms.get(name)
        if not paradigm:
            print(f"Failed to print paradigm with invalid name {name}")
            return
        formatted_paradigm = f"Paradigm name:    {paradigm['name']}\n"
        formatted_paradigm += f"Fixed categories: {', '.join(paradigm['fixed_categories'])}\n"
        formatted_paradigm += f"Fixed categories: {', '.join(paradigm['filled_categories'])}\n"
        formatted_paradigm += f"Word classes:     {', '.join(paradigm['word_classes'])}"
        print(formatted_paradigm)
        return formatted_paradigm

    # NOTE: define grammatical and content word slots to be filled on apply
    #   - word classes are for filtering headword in dictionary
    #   - fixed categories limit to one grammeme on apply, like animate below
    #   - filled categories will use all grammemes on apply, like case below
    #   - exponents list can hold one specific grammeme or many for e.g. "declension"
    #       - if a language casemarks a noun: (class:animate)(case)-horse
    #   - categories can appear in any order; exponent ordering handled through grammar
    def create(self, name, fixed_categories=None, filled_categories=None, word_classes=None):
        """Create a paradigm with grammatical categories to take on apply and categories
        to fill automatically. Optionally restrict the paradigm to specific word classes."""
        # check for existing name
        if self.paradigms.get(name):
            print(f"Paradigm create failed - cannot overwrite existing paradigm {name}")
            return
        # check for valid categories lists
        filled_categories = [] if not filled_categories else filled_categories
        fixed_categories = [] if not fixed_categories else fixed_categories
        if not isinstance(filled_categories, list) and not isinstance(fixed_categories, list):
            print(f"Paradigm create failed - expected fixed or filled categories list")
            return
        for category in fixed_categories + filled_categories:
            if not self.language.grammar.properties.is_category(category):
                print(f"Paradigms create failed - invalid category {category}")
                return
        # check for valid word classes
        word_classes = self.language.grammar.word_classes.filter(word_classes) if word_classes else []
        # store paradigm
        self.paradigms[name] = {
            'fixed_categories': fixed_categories,
            'filled_categories': filled_categories,
            'word_classes': word_classes
        }
        return name

    # TODO: sentence and phrase (morphosyntax)
    #   - like article, adjective, noun
    #   - then within those can build out units
    # ? Merge this with sentences idea from Grammar morphosyntax
    #   - need to know which exponents go with which bases
    #   - then apply bases to build units
    #   - built units can be stored in relation to each other
    #   - really becomes coordinating units with each other

    # NOTE: think of this as defining/applying a word/phrase
    # with certain grammatical properties, then on apply
    # those properties are provided by exponents. You are not
    # selecting exponents via create, and not explicitly
    # attaching them on apply (the grammar handles that).

    # TODO: search by properties in grammar.exponents.find
    #   - is this even necessary here though?
    #   - originally this was to 
    #
    # sketch of apply flow:
    #   - set fixed grammemes (applied every iteration)
    #   - traverse filled grammemes for exponents
    #   - pass every grammemes set to grammar for build unit 
    def apply(self, name, headword=None, filled_grammemes=None):
        """Apply exponent paradigm, filling base word class slots with headwords,
        to store or showcase examples"""
        paradigm = self.paradigms.get(name)
        if not paradigm:
            print(f"Failed to apply paradigm - unrecognized paradigm name {name}")
            return
        
        base_entry = self.language.dictionary.lookup(*headword)
        base_word = base_entry['sound']
        base_word_classes = base_entry['pos']

        # check and format grammemes list
        grammemes = set([]) if not filled_grammemes else set(filled_grammemes)
        # separate grammemes listed in a string
        if isinstance(filled_grammemes, str):
            grammemes = set(re.split(r"[, .]", filled_grammemes))
        # back out if no list
        if not isinstance(grammemes, set):
            print(f"Paradigms apply failed - expected filled grammemes list not {filled_grammemes}")
            return

        # compile a properties map to send to build word
        paradigm_properties = {}
        # fit passed-in grammemes to every fixed category
        for category in paradigm['fixed_categories']:
            # fetch the property's grammemes
            category_grammemes = set(
                self.language.properties
                .get(category=category).values()
            )
            # expect a matching grammeme for each fixed category
            shared_grammemes = list(category_grammemes & grammemes)
            if not shared_grammemes:
                print(f"Failed to apply paradigm - missing grammeme for filled category {category}")
                return
            # fill the fixed category with passed-in grammeme
            fixed_grammeme = shared_grammemes[0]
            grammemes.remove(fixed_grammeme)
            paradigm_properties[category] = fixed_grammeme

        # fill filled categories with all property grammemes
        for category in paradigm['filled_categories']:
            category_grammemes = self.language.properties.get(category=category).values()
            paradigm_properties[category] = category_grammemes

        # Traverse categories building requested properties
        # - go through every combination listed category grammemes
        # - hold fixed category grammemes (strings) steady
        built_units = []
        fixed_grammemes = list(filter(
            lambda x: isinstance(x, str),
            paradigm_properties.values()
        ))
        filled_grammemes = list(filter(
            lambda x: isinstance(x, list),
            paradigm_properties.values()
        ))
        # TODO: combinations for provided properties, with
        # fixed grammemes held constant every time but
        # filled grammemes combined
        for grammeme_list in filled_grammemes:
            built_unit = self.language.grammar.build_unit(
                base_word,
                properties=paradigm_properties,
                word_classes=base_word_classes
            )
            built_units.append(built_unit)

        return built_units
