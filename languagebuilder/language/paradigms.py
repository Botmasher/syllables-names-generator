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
        hyphenated_slots = " - ".join(paradigm)
        formatted_paradigm = f"Paradigm: {paradigm['name']}\nSlots: {hyphenated_slots}"
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
        filled_categories = [] if filled_categories is None else filled_categories
        fixed_categories = [] if fixed_categories is None else fixed_categories
        if not isinstance(filled_categories, list) or not isinstance(fixed_categories, list):
            print(f"Paradigm create failed - expected fixed or filled categories list")
            return
        for category in fixed_categories + filled_categories:
            if category not in self.language.grammar.properties.is_category(category):
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

    # TODO: search by properties in grammar.exponents.find
    #   - is this even necessary here though?
    #   - originally this was to 
    #
    # sketch of apply flow:
    #   - set fixed grammemes (applied every iteration)
    #   - traverse filled grammemes for exponents
    #   - pass every grammemes set to grammar for build unit 
    def apply(self, name, headword=None):
        """Apply exponent paradigm, filling base word class slots with headwords,
        to store or showcase examples"""
        paradigm = self.paradigms.get(name)
        if not paradigm:
            print(f"Failed to apply paradigm - unrecognized paradigm name {name}")
            return
        filled_paradigm = []
        # TODO: merge this with sentences idea from Grammar morphosyntax
        #   - need to know which exponents go with which bases
        #   - then apply bases to build units
        #   - built units can be stored in relation to each other
        #   - really then this becomes like unit coordination vs each other
        return filled_paradigm
