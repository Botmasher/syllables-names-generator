import re                       # for splitting strings and parsing them for properties
from collections import deque   # for building pre- and post-exponented word pieces lists

# breakout components managing Grammar collections
# - word classes represent broad parts of speech
# - properties represent specific grammatical categories and values
# - exponents provide properties and are optionally restricted to word classes
from .word_classes import WordClasses
from .exponents import Exponents
from .properties import Properties
from .morphosyntax import Morphosyntax

# ## Cases from Grammar instantiation and testing

# # TODO: ignore capitalization

# # TODO: implement more robust search incl description and pos
# #   - also use word classes to test building words with requested recognized/unrecognized/mixed word classes

# # TODO: Flexible Parsing
# # Consider shapes of strings expected to be parsed:
# #   "present tense indicative mood verb"
# #   "tense: present, mood: indicative, verb"
# #   "tense:pres mood:ind v"
# #   "pres ind v"
# #   "present tense indicative verb"
# #   "v, present, indicative"
# #   "pres-ind-v"
# #   ""
# #   "vpres"

# # LIMITS OF REQUESTED PROPERTIES
# #
# # NOTE: use modified .properties and .exponents structure to handle
# # requested properties smaller or larger than what's in the grammar
# #
# # - case 1: built word properties are less verbose than stored exponent properties
# #   - example: word is ['verb', 'past'] but past affix is ['verb', 'past', 'tense']
# #
# # - case 2: built word properties are more verbose than exponent
# #   - example: word is ['verb', 'past', 'tense'] but past affix is ['past']
# #
# # - case 3: built word properties are less verbose but cover multiple exponents
# #   - example: word is ['verb', 'past', 'tense'] but affixes are ['verb', 'finite'] and ['past', 'tense']
# #
# # - case 4: built word properties are empty

# NOTE: Grammar relates grammatical exponents <> properties, word_classes
# - exponents are phones of affixes, adpositions, particles, pre or post a base
# - properties are category:grammemes pairs
# - word classes help filter or limit the application of exponents to built words

# TODO: modularize grammar.exponents, grammar.properties, grammar.word_classes

# TODO: handle non-pre/post kinds of exponents like apophony

# TODO: default or citation form properties for a word class
#   - example: just request "noun" and grammar gives you nominative singular

# TODO: update word classes parsing
# - from parse properties vs word classes to parsing both in one string
#   - consider, though increases ambiguity allows parsing "plural noun"
# - parse entire string for adding an exponent
#   - example: add_exponent(post="s", properties="plural noun")

# TODO: consider creating morphosyntax slotting of properties
#   - example: aspect suffix precedes number suffix
#   - build out a Syntax for these?
#   - makes Grammar a bigger container for putting together any morphosyntax

class Grammar:
    def __init__(self):
        # object for providing and checking exponent parts of speech
        self.word_classes = WordClasses(self)
        
        # object handling map of category:grammemes
        # including updating exponent properties on changes
        self.properties = Properties(self)

        # object handling map of exponent details
        # including pointing to an exponent properties and word classes
        self.exponents = Exponents(self)

        # object ordering word pieces and words
        self.morphosyntax = Morphosyntax(self)

        # TODO: resupport property and word class abbreviations
        # - unambiguous abbreviation:full_term map
        # - previous use of abbreviations: add/update (crud), parse_properties (identification - originally parse_terms)
        # - distinguish property from word_class abbreviations
        # - case: what about abbreviations for a category like tns?
        self.abbreviations = {}

    def parse_properties(self, properties_text):
        """Turn a string of grammatical terms into a map of properties"""
        # check the properties data structure
        if not isinstance(properties_text, str):
            print("Grammar failed to parse properties - expected a string not {0}".format(properties_text))
            return

        # create an ordered collection of grammatical terms
        unidentified_terms = re.split(r"\W+", properties_text)
        
        # map of matching properties to fill out and return
        parsed_properties = {}

        # flexibly store latest confirmed member of category:grammeme pairs
        # allowing category to lead, follow or be dropped from beside grammeme
        current_category = None     # explicit category to be associated with a grammeme
        current_grammeme = None     # grammeme to be matched to implicit or explicit category
        stranded_grammeme = None    # uncategorized previous grammeme holder when new grammeme found

        # search through word classes and properties for recognizable matches
        for i, term in enumerate(unidentified_terms):
            # check and store unidentified terms for properties
            # start by looking for a category
            if self.properties.is_category(term):
                # replace the identified category and await a grammeme match
                # conflicting current categories mean stranded or unidentified grammeme
                current_category = term
            # assume non-category terms are to be considered as grammemes
            # to reach this branch:
            #   - the category is empty, the current term may be a grammeme
            #   - the last term was a category, the current term may be a grammeme
            #   - the last term was a grammeme, the current term may be a grammeme
            else:
                # hold over uncategorized grammeme to find it an explicit category
                # if two as-yet uncategorized grammemes collide
                if not current_category and current_grammeme:
                    # hold over an uncategorized grammeme in the middle
                    stranded_grammeme = current_grammeme 
                # reassign grammeme to whatever the current term is
                current_grammeme = term

            # guess previously identified grammeme left unassociated with any explicit category
            if stranded_grammeme:
                # find the property by its grammeme name only
                matching_properties = self.properties.find(grammeme=stranded_grammeme)
                # create an entry using the first identified category and its grammeme
                if matching_properties:
                    # found properties hold paired category, grammeme tuples
                    stranded_category = matching_properties[0][0]
                    stranded_grammeme = matching_properties[0][1]
                    parsed_properties.setdefault(stranded_category, set()).add(stranded_grammeme)
                # reset for the next uncategorized grammeme
                stranded_grammeme = None

            # empty current category and grammeme into map if both are identified
            # or if final term in list is an uncategorized grammeme
            if current_grammeme and (current_category or i >= len(unidentified_terms) - 1):
                # catch final uncategorized term - handled here instead of as a stranded grammeme
                # case: penultimate and final terms are both uncategorized grammemes
                if not current_category:
                    matching_properties = self.properties.find(grammeme=current_grammeme)
                    if not matching_properties:
                        break
                    current_category = matching_properties[0][0]

                # check that suspected but unverified grammeme is valid
                # NOTE: check held off until here because grammeme term may be found before or after its parent category
                if current_grammeme not in self.properties.get(current_category):
                    # toss the suspected grammeme and keep parsing
                    print("Grammar parse_properties skipped parsed but unrecognized property {0}:{1}".format(current_category, current_grammeme))
                    current_grammeme = None
                # add grammeme under current category and consider it parsed
                else:
                    # add the identified grammeme to the category grammemes set in the parsed map
                    parsed_properties.setdefault(current_category, set()).add(current_grammeme)
                    # reset the category:grammeme for the next unidentified pairing
                    current_category = None
                    current_grammeme = None

        # deliver requested properties map
        return parsed_properties

    def parse_word_classes(self, word_classes):
        """Turn a string of grammatical terms into a map of word classes"""
        # check for a string to parse
        if not isinstance(word_classes, str):
            print("Grammar failed to parse word classes - expected a string not {0}".format(word_classes))
            return

        # split the string into a collection of terms to check
        suspected_word_classes = re.split(r"\W+", word_classes)

        # prepare collection for parsing and adding known parts of speech
        parsed_word_classes = set()

        # collect recognized word class names into the returned set
        for term in suspected_word_classes:
            if self.word_classes.get(term):
                parsed_word_classes.add(term)
            # skip unrecognized word classes
            else:
                print("Grammar parse_word_classes skipped unknown word class {0}".format(term))
                continue

        return parsed_word_classes


    # Build methods

    def vet_build_word_classes(self, word_classes, return_unrecognized=False):
        """Attempt to collect a set copying known word classes from a collection or a parsable string"""
        # collect word classes in a set
        if isinstance(word_classes, (list, tuple, set)):
            return self.word_classes.filter(word_classes)   # NOTE: expect returned set
        # break down the string and analyze classes into a set
        if isinstance(word_classes, str):
            return self.parse_word_classes(word_classes)    # NOTE: expect set or None
        # unexpected word classes value supplied
        return

    def vet_build_word_properties(self, properties):
        """Attempt to map a copy of valid, known category grammemes from flexible property input"""
        # vet map for recognized categories and their grammemes
        if isinstance(properties, dict):
            return self.properties.filter(properties)
        # parse string of terms to collect known properties
        if isinstance(properties, str):
            return self.parse_properties(properties)
        # turn a list of grammemes into a map of guessed categories and grammemes
        if type(properties) in (list, tuple, set):
            return self.properties.map_uncategorized_properties(properties)
        # unexpected properties value given
        return

    # the main public method for making use of data stored in the grammar
    def build_unit(self, root, properties=None, word_classes=None, exact_pos=False, all_or_none=False):
        """Build up relevant morphosyntax around a base using the given grammatical terms"""
        # TODO: better docstring particularly for this method

        # verify that a root word is given
        if not isinstance(root, str):
            print("Grammar build_word failed - invalid root word string {0}".format(root))
            return

        # make usable word class set collecting valid and recognizable pos terms
        requested_word_classes = self.vet_build_word_classes(word_classes)

        # make usable properties map collecting valid and recognizable category:grammemes
        # TODO: include 'pos' within self.properties - no major gains from separating
        # or enhance method to search for pos? - (properties, word_classes != None)
        requested_properties = self.vet_build_word_properties(properties)
        
        # dead end when did not turn up a good map of vetted properties
        if not self.properties.is_properties_map(requested_properties):
            print("Grammar build_word failed for {0} - invalid properties {1}".format(root, requested_properties))
            return

        # Below map-reduce exponents using vetted_properties and vetted_word_classes
        # 1. Map traversal:
        #   - use properties to find an exponent with matching category:grammemes
        #   - use word_classes to filter for exponent includes/excludes
        # 2. Reduce traversal:
        #   - use resulting match set to find exponents providing the most properties
        #   - ditch subproperties
        # 3. Exponent word:
        #   - attach mapped-reduced exponents to root

        # 1. Map matching exponents

        # collect exponents that provide at least one property
        matching_exponents = set()      # exponent ids set for exponents that have matching properties

        # track found vs missing properties for failing if not all properties provided
        # create a tracker map of all properties and how many times each provided
        provided_properties = {
            (category, grammeme) : 0
            for category in requested_properties
            for grammeme in requested_properties[category]
        }

        # find exponents that match one or more properties and word class includes/excludes
        for exponent_id, exponent_details in self.exponents.get_items():
            
            # TODO: should requested_word_classes be provided in whole or part?
            #   - consider in conjunction with exact_pos added to force exponent to provide word_classes
            #   - whole (current): exponent must provide {noun, adjective}
            #   - part: one exponent provides {noun}, another provides {adjective}
            #
            # pass over exponent based on word classes expected to be matched
            # check that the exponent provides requested parts of speech
            if (exponent_details['pos'] or exact_pos) and requested_word_classes != exponent_details['pos']:
                continue

            # retrieve all property names for this exponent
            exponent_properties = exponent_details['properties']

            # hold exponents that provide one or more requested properties and none not requested
            if self.properties.is_subproperties(exponent_properties, requested_properties):
                # consider this a candidate exponent
                matching_exponents.add(exponent_id)

                # track the matched properties - check later if all requested properties matched
                # NOTE: expect exponent category-grammemes all match requested by now otherwise error above
                for intersected_category in exponent_properties:
                    for intersected_grammeme in exponent_properties[intersected_category]:
                        provided_properties[(intersected_category, intersected_grammeme)] += 1

        # check that all properties were matched before reducing to optimal exponents
        if all_or_none:
            for category_grammeme_pair in provided_properties:
                property_count = provided_properties[category_grammeme_pair]
                if not property_count:
                    print("Grammar build_word failed - no exponent found for property {}:{}".format(category_grammeme_pair[0], category_grammeme_pair[1]))
                    return

        # 2. Reduce subsets among exponent matches
        #   - this happens when multiple exponents share properties
        #   - shrink list while still providing all requested properties

        reduced_exponents = set()

        # reduce to find supersets among exponent matches
        # find the fewest exponents that provide the requested properties
        for matching_exponent in matching_exponents:
            # skip evaluating exponent if already among best matches
            ## TODO: check cases to see if this works better than removing matching exponents
            ## that aren't superproperties matches when adding the best exponent below
            if matching_exponent in reduced_exponents:
                continue

            # exponent providing largest properties superset including these same properties
            best_exponent_match = None  # track the id that matches the most properties

            # properties for the base (matched) exponent
            exponent_properties = self.exponents.get(matching_exponent)['properties']

            # traverse all exponent matches and look for properties
            for compared_exponent in matching_exponents:

                # skip comparing base exponent to itself
                if compared_exponent == matching_exponent:
                    continue

                # properties from other matched exponents
                compared_exponent_properties = self.exponents.get(compared_exponent)['properties']

                # run the comparison looking for an exponent with superproperties
                if self.properties.is_subproperties(exponent_properties, compared_exponent_properties):
                    best_exponent_match = compared_exponent

            # set the best match to the base matched exponent if no superproperties found
            best_exponent_match = matching_exponent if not best_exponent_match else best_exponent_match

            # save the best match
            reduced_exponents.add(best_exponent_match)

        # 3. Exponent word

        # add exponents to build up the word
        # attach the best matches from the mapped and reduced exponents
        built_word = self.attach_exponents(root, reduced_exponents, as_string=True)

        # return the grammatically augmented word
        return built_word

    def attach_exponents(self, root, exponent_ids, as_string=False, reorder=True):
        """Exponent a complex word to correctly position a root, prefixes, postfixes, prepositions, postpositions"""
        # expect a collection of exponent ids and a word-building map
        if not isinstance(exponent_ids, (list, set, tuple)):
            print(f"Grammar attach_exponents failed - invalid exponents collection {exponent_ids}")
            return

        # exponent attachment types in in sequential order
        attachment_sequence = (
            'preposition',
            'prefix',
            'root',
            'postfix',
            'postposition'
        )

        # keep word pieces accounting for possible positions and spacing
        exponented_word_map = {
            attachment: deque()
            for attachment in attachment_sequence
        }
        exponented_word_map['root'].append(root)
        
        # rearrange exponents using morphosyntax ordering
        if reorder:
            # get back innermost-to-outermost ordered ids list
            # NOTE: arranges a list of ids ordered from outermost to innermost
            #   - placement decided on outer vs inner
            #   - outermost ("last") post will be considered the first one in the list
            #   - outermost ("first") pre will be considered the first one in the list
            #   - both lists contain ids so traversing requires extra lookups
            sorted_ids = self.morphosyntax.arrange_exponents(exponent_ids)
            print("Unsorted: {}".format([self.exponents.get(eid)['post'] for eid in exponent_ids]))
            print("Sorted: {}".format([self.exponents.get(eid)['post'] for eid in sorted_ids]))
            # store ordered 'pre' and 'post' exponents, leaving circums in both
            #   - 'pre' appear later in list when they're more "inner" (less "pre") than another
            #   - 'post' appear later in list when they're less "inner" (more "post") than another
            ordered_exponents = {
                'pre': sorted_ids,
                'post': list(reversed(sorted_ids))
            }
        # use whatever order exponents found in
        else:
            ordered_exponents = {
                'pre': exponent_ids,
                'post': exponent_ids
            }

        # go through exponents and map them as prescribed in the exponent
        for position in ordered_exponents:
            # set up positional keys and checks
            attachment_keys = ('preposition', 'prefix') if position == 'pre' else ('postposition', 'postfix')
            is_pre = position == 'pre'
            is_post = position == 'post'

            # traverse and compile exponents destined for this position
            for exponent_id in ordered_exponents[position]:
                exponent_details = self.exponents.get(exponent_id)

                # check for valid exponent
                if not exponent_details:
                    print(f"Grammar attach_exponents skipped invalid exponent {exponent_id}")
                    continue
                
                # use binding to determine placement and spacing
                attachment_key = attachment_keys[exponent_details['bound']]
                # add spaces next to filled exponents that are unbound
                spacing = "" if exponent_details['bound'] or not exponent_details[position] else " "

                # reference the actual material being added
                exponent_material = exponent_details[position]

                # add both spacing and material to the relevant attachment list
                if is_post:
                    exponented_word_map[attachment_key].append(exponent_material)
                    exponented_word_map[attachment_key].append(spacing)
                elif is_pre:
                    exponented_word_map[attachment_key].append(exponent_material)
                    exponented_word_map[attachment_key].append(spacing)

        # turn the exponenting map into a flat sequence
        exponented_word = [
            piece for attachment in attachment_sequence
            for piece in exponented_word_map[attachment]
        ]

        print(exponented_word)

        # return the sequence as a list or string
        if as_string:
            return "".join(exponented_word)
        return list(exponented_word)
    
    def attach_exponent(self, base, exponent_id=None, as_string=False):
        """Attach one grammatical exponent around a root word"""
        # check for a good stem and an exponent to attach to it
        if type(base) is not str:
            print("Grammar attach_exponent failed - invalid word stem {0}".format(base))
            return
        if not self.exponents.get(exponent_id):
            print("Grammar attach_exponent failed - unknown exponent id {0}".format(exponent_id))
            return

        # prepare the base and attachment data
        exponent = self.exponents.get(exponent_id)
        pre = exponent['pre']
        post = exponent['post']

        # include spaces around the root for non-affixes
        spacing = " " if not exponent['bound'] else ""

        # sequentially collect exponented material around root including spacing
        exponented_word = [pre, spacing, base, spacing, post]

        # return the word plus exponent either as string or list
        if as_string:
            return "".join(exponented_word)
        else:
            return exponented_word
