import uuid
import re
import random

# NOTE the grammar relates grammatical exponents <> grammatical properties
# - exponents are phones of affixes, adpositions, particles, pre or post a base
# - properties are categories, grammemes
# - word classes help filter or limit the application of exponents to built words
class Grammar:
    def __init__(self):
        # word classes used to include or exclude words for exponents
        self.word_classes = {}
        # map of category, grammatical value pairs with details for each value
        self.properties = {}
        # map of exponent details, including pointing to an exponent's property ids
        self.exponents = {}

        # TODO: resupport property and word class abbreviations
        # - unambiguous abbreviation:full_term map
        # - previous use of abbreviations: add/update (crud), parse_properties (identification - originally parse_terms)
        # - distinguish property from word_class abbreviations
        # - case: what about abbreviations for a category like tns?
        self.abbreviations = {}

    # TODO: nest properties data
    # - expected: requested properties clearly match one or more exponents
    # - issue: flattening everything as grammemes creates inconsistent judgments when requested properties vs stored exponent properties sets are not well matched
    #
    # - proposed solution A: create {category: {properties}}
    #   - requested properties must now be passed in a dict
    #   - OR requested properties may be a list of grammemes ONLY
    #   - perhaps store a list of word_classes
    #   - perhaps store word_classes per exponent that are included/excluded
    # - implementation: ongoing
    #   - give properties a category and grammeme in add, update, remove and read
    #   - requested properties now expect {'category': 'grammeme', ...} pairs
    #   - excluded properties can be set of categories or grammemes
    #   - give exponents a reference to their must include {'category': 'grammemes'} pairs
    #   - give exponents a list of excluded properties
    #
    # - proposed solution B: limit ONLY to grammemes (expect everything to be low level)
    #   - each grammeme has a unique name
    #   - exponents explicitly lay out include/exclude properties, allowing vetting of broader terms in requested
    # - implementation: none

    # Method group A: Functional map building and layering

    # TODO: break merge_maps out as a util instead of limiting it to this class
    # functional dict building to avoid direct mutations in word class, property and exponent update methods
    def merge_maps(self, base_map, overlay_map, key_check=lambda x: x, value_check=lambda x: x):
        """Overlay map pairs with filtered keys and values onto a base map and return the new map"""
        # expect both an old "base" and a new "overlay" dict
        if not(type(base_map) is dict and type(overlay_map) is dict):
            print("Grammar merge_maps failed - invalid base map or overlay map")
            return
        # expect a valid filter function to validate overlayed keys and values
        if type(key_check).__name__ != 'function' or type(vale_check).__name__ != 'function':
            print("Grammar merge_maps failed - invalid checker functions")
            return
        # unpack old and new maps filtering the new one for proper types
        new_map = {
            **base_map,
            **{k: v for k, v in overlay_map.items() if key_check(k) and value_check(v)}
        }
        return new_map

    # NOTE: idiosyncratic implementation for comparing structures in the Grammar
    #   - stored properties nests dicts down to leaf detail entries
    #   - requested properties associates its top-level keys with sets of strings
    #   - each string in a requested properties set represents nested keys in stored properties
    #   - requested properties are passed in by caller as well as stored by exponents
    def intersect_maps(self, base_map, overlay_map):
        """Deeply evaluate shared pairs within two maps and return a map copy of their intersections.
        Intersections are shared keys, shared leaf values and shared values within collections
        returned as intersected sets."""
        # recursively branch through map along shared keys
        if isinstance(base_map, dict) and isinstance(overlay_map, dict):
            # intersection representing shared keys
            common_keys = base_map.keys() & overlay_map.keys()
            # check the values under those keys
            return {
                k: self.intersect_maps(base_map[k], overlay_map[k])
                for k in common_keys
            }
        # both are flat containers - test for shared values
        elif type(base_map) in (list, set, tuple) and type(overlay_map) in (list, set, tuple):
            # intersect the two containers
            common_values = set(base_map) & set(overlay_map)
            return common_values
        # expect non-collection values to match
        elif base_map == overlay_map:
            return base_map
        # no shared material found under this key
        else:
            return {}


    # Method group B: Core CRUD for mapping properties, word classes and exponents

    def add_word_class(self, word_class, description=None):
        """Add one word class or part of speech to the grammar"""
        if word_class in self.word_classes:
            print("Grammar add_word_class skipped {0} - word class already exists".format(word_class))
            return
        # create a new entry for the part of speech
        self.word_classes[word_class] = {
            'name': word_class,
            'description': description
        }
        # read the created part of speech
        return self.word_classes[word_class]

    def update_word_class(self, word_class, name=None, description=None):
        """Modify the details of a single word class"""
        if word_class not in self.word_classes:
            print("Grammar update_word_class failed - unknown word class {0}".format(word_class))
            return
        # create new word class entry updating only changed details
        word_class_details = self.merge_maps(self.word_classes[word_class], {
            'name': name,
            'description': description
        }, value_check=lambda x: type(x) is str)
        # rename the word class by removing the old entry and adding a new one
        if name != word_class:
            self.remove_word_class(word_class)
            self.word_classes[name] = word_class_details
        # replace the details for an existing entry
        else:
            self.word_classes[word_class] = word_class_details
        # read the modified part of speech
        return self.word_classes[word_class]

    def remove_word_class(self, word_class):
        """Delete one word class from word classes map and exponents that reference it"""
        if word_class not in self.word_classes:
            print("Grammar remove_word_class failed - unrecognized word class {0}".format(word_class))
            return
        # delete part of speech from the word classes map
        removed_word_class = self.word_classes[word_class]
        self.word_classes[word_class].pop(word_class)
        # remove part of speech from all property grammeme entries that reference it
        for category in self.properties:
            for grammeme, grammeme_details in self.properties[category].items():
                if word_class in grammeme_details['exclude']:
                    self.properties[category][grammeme]['exclude'].remove(word_class)
                if word_class in grammeme_details['include']:
                    self.exponents[category][grammeme]['include'].remove(word_class)
        # return deleted details
        return removed_word_class

    def get_property(self, category=None, grammeme=None):
        """Read one grammatical value from one category in the grammar"""
        try:
            return self.properties[category][grammeme]
        except:
            return

    def add_property(self, category=None, grammeme=None, description=None, include=[], exclude=[]):
        """Add one grammatical value to an existing category in the grammar"""
        if not (category and grammeme and type(category) is str and type(grammeme) is str):
            print("Grammar add_property failed - expected category and grammeme to be non-empty strings")
            return

        # collect valid word classes to include or exclude when property is applied
        # TODO: also allow including or excluding other categories or grammemes
        included_word_classes = {
            word_class for word_class in exclude
            if word_class in self.word_classes
        }
        excluded_word_classes = {
            word_class for word_class in include
            if word_class in self.word_classes
        }

        # add new category under properties
        if category not in self.properties:
            self.properties[category] = {}

        # back out if property category:grammeme pair already exists
        if grammeme in self.properties[category]:
            print("Grammar add_property failed - category {0} already contains grammeme {1} - did you mean to run update_property?".format(category, grammeme))
            return

        # create a new entry under the category for the grammeme
        self.properties[category][grammeme] = {
            'category': category,
            'grammeme': grammeme,
            'description': description if type(description) is str else None,
            'include': included_word_classes,
            'exclude': excluded_word_classes
        }

        # read the created entry
        return self.get_property(category, grammeme)

    def add_properties(self, properties_details):
        """Add a map of grammatical values within categories to the grammar"""
        if type(properties_details) is not dict:
            print("Grammar add_properties failed - invalid properties map {0}".format(properties_details))
            return
        # store each new grammatical value added to the grammar
        # verify it has the expected details structure:
        # {
        #   # string representing the lookup category over the grammeme
        #   category: [
        #       # pass a map full of the new property's attributes
        #       {
        #           # required name (also doubles as its unique id)
        #           'grammeme': str,
        #           # optional attributes
        #           'description': str,
        #           'include': list,        # word classes the property applies to
        #           'exclude': list         # word classes the property does not apply to
        #       },
        #       # or pass only a string to turn into the property's grammeme name and id
        #       str,
        #       ...
        #   ],
        #   ...
        # }
        added_properties = []
        for category, grammemes in properties_details.items():
            # NOTE: do not skip unknown category or grammeme - both can be added
            # expect each category to contain a collection of entries
            if type(grammemes) not in (list, tuple, set):
                print("Grammar add_properties skipped category {0} - invalid grammemes collection {1}".format(category, grammemes))
                continue
            # go through category:grammemes and add each valid pair
            for grammeme in grammemes:
                # create a new grammeme passing along only its category name and grammeme name
                # NOTE: this bare-minimum method leaves all other attributes empty
                if type(grammeme) is str:
                    added_property = self.add_property(category=category, grammeme=grammeme)
                # expect any non-strings to be maps of grammeme details
                elif type(grammeme) is not dict or 'grammeme' not in grammeme:
                    print("Grammar add_properties skipped {0}:{1} - expected a map with a 'grammeme' key".format(category, grammeme))
                    continue
                # create a fuller grammeme entry from a map with supplied attributes
                else:
                    # create a bare entry with defaults to underlay missing details
                    default_details = {
                        'grammeme': grammeme,
                        'description': None,
                        'include': [],
                        'exclude': []
                    }
                    # pass grammeme to create along with optional attributes
                    # filter grammeme keys to restrict them to known properties attributes
                    property_details = self.merge_maps(
                        default_details,
                        grammeme,
                        key_check=lambda x: x in default_details
                    )
                    # create property reading merged custom details + defaults for missing details
                    added_property = self.add_property(
                        category=property_details['category'],
                        grammeme=property_details['grammeme'],
                        description=property_details['description'],
                        include=property_details['include'],
                        exclude=property_details['exclude']
                    )
                # collect successfully added properties
                added_property and added_properties.append(property)
        return added_properties

    def update_property(self, category, grammeme, description=None):
        """Modify text details for one grammatical property"""
        if not self.get_property(category, grammeme):
            print("Grammar update_property failed - invalid category value {0}:{1}".format(category, grammeme))
            return
        # create new property entry with modified details
        grammeme_details = self.merge_maps(self.properties[category][grammeme], {
            'description': description
        }, value_check=lambda x: type(x) is str)
        self.properties[category][grammeme] = grammeme_details
        # access and return the created details
        return self.get_property(category, grammeme)

    # Specific property attribute updates and removals

    def add_property_word_class(self, category, grammeme, include=None, exclude=None):
        """Add one included or excluded word class to the grammatical property"""
        # check that the property exists and that there is a part of speech to add
        if not self.get_property(category, grammeme):
            print("Grammar add_property_word_class failed - unknown category:grammeme {0}:{1}".format(category, grammeme))
            return
        if not (include or exclude) or not (type(include) is str or type(exclude) is str):
            print("Grammar add_property_word_class failed - expected at least one include or exclude string")
            return

        # add verified parts of speech to grammeme word class sets
        if exclude and exclude in self.word_classes:
            self.properties[category][grammeme]['exclude'].add(exclude)
        if include and include in self.word_classes:
            self.properties[category][grammeme]['include'].add(include)

        return self.get_property(category, grammeme)

    def remove_property_word_class(self, category, grammeme, include=None, exclude=None):
        """Remove one included or excluded word class from the grammatical property"""
        # check for the property
        if not self.get_property(category, grammeme):
            print("Grammar remove_property_word_class failed - unknown category:grammeme {0}:{1}".format(category, grammeme))
            return

        # remove part of speech from grammeme details excluded word classes
        try:
            include and self.properties[category][grammeme]['exclude'].remove(exclude)
        except ValueError:
            print("Grammar remove_property_word_class skipped removing unknown word class from excludes: {0}".format(exclude))

        # remove word class from includes
        try:
            exclude and self.properties[category][grammeme]['include'].remove(include)
        except ValueError:
            print("Grammar remove_property_word_class skipped removing unknown word class from includes: {0}".format(include))

        return self.get_property(category, grammeme)

    def change_property_word_classes(self, category, grammeme, include=[], exclude=[]):
        """Update the included or excluded word classes for a property"""
        # verify that the property exists
        if not self.get_property(category, grammeme):
            print("Grammar change_property_word_classes failed - unknown category:grammeme {0}:{1}".format(category, grammeme))
            return
        # check for valid include and exclude part of speech lists
        if not (include or exclude) or type(include) not in (list, tuple, set) or type(exclude) not in (list, tuple, set):
            print("Grammar change_property_word_classes failed - invalid include or exclude lists")
            return

        # collect only recognized parts of speech
        included_word_classes = {pos for pos in include if pos in self.word_classes}
        excluded_word_classes = {pos for pos in exclude if pos in self.word_classes}

        # store word classes
        self.merge_maps(
            self.properties[category][grammeme],
            {
                'include': included_word_classes,
                'exclude': excluded_word_classes
            },
            value_check=lambda x: x != set()
        )

        return self.get_property(category, grammeme)

    def change_property_category(self, category, grammeme, new_category):
        """Update a property's category name and the location of its details in the properties map"""
        # verify that the updated category is good and that the property exists
        if not (new_category and type(new_category) is str):
            print("Grammar change_property_category failed - invalid non-empty new category string {0}".format(new_category))
            return
        if not self.get_property(category, grammeme):
            print("Grammar change_property_category failed - unknown category:grammeme {0}:{1}".format(category, grammeme))
            return

        # create a new details entry
        grammeme_details = self.merge_maps(
            self.properties[category][grammeme],
            {'category': new_category}
        )

        # move updated details to the new category within properties
        self.propertes[new_category] = self.properties.get(new_category, {})
        self.properties[new_category][grammeme] = grammeme_details

        # remove the old grammeme and its details
        self.properties[category].pop(grammeme)
        # remove the old category if it is empty
        not self.properties[category] and self.properties.pop(category)

        # send back the newly created and stored entry
        return self.get_property(new_category, grammeme)

    def remove_property(self, category, grammeme):
        """Delete the record for and exponent references to one property from the grammar"""
        if category not in self.properties or grammeme not in self.properties[category]:
            print("Grammar remove_property failed - unknown category value {0}:{1}".format(category, grammeme))
            return
        # reference deleted details
        removed_property = self.get_property(category, grammeme)
        # delete property key and details
        self.properties[category].pop(grammeme)
        # delete property from exponent properties category sets that have it
        for exponent_id, exponent_details in self.exponents.items():
            if category in exponent_details['properties'] and grammeme in exponent_details['properties'][category]:
                self.exponents[exponent_id]['properties'][category].remove(grammeme)
                # also delete the category from properties if it is left empty
                if self.exponents[exponent_id]['properties'][category] == set():
                    self.exponents[exponent_id]['properties'].pop(category)
        # return the deleted details
        return removed_property

    # NOTE: added exponent['properties'] details now expect this structure:
    # {
    #   category: {grammeme, ...},     # grammemes set NOT dict of value:details pairs as in self.properties
    #   category: 'grammeme'           # a single string is also allowed
    #   ...
    # }
    def add_exponent(self, pre="", post="", bound=True, properties={}):
        """Add one grammatical exponent to the grammar"""
        if not ((pre or post) and (type(pre) is str and type(post) is str)):
            print("Grammar add_exponent failed - expected pre or post exponent string")
            return

        # structure the categories and values of included properties
        exponent_properties = {}
        for category, grammemes in properties.items():
            # avoid non-existing categories
            if category not in self.properties:
                print("Grammar add_exponent failed - invalid grammatical category {0}".format(category))
                return
            exponent_properties[category] = set()
            # format a set for a single grammeme in one category, like past tense
            if type(grammemes) is str:
                if not self.get_property(category, grammemes):
                    print("Grammar add_exponent failed - invalid grammatical value {0}".format(grammemes))
                    return
                grammemes = {grammemes}
            # add one or more grammemes in one category, like past and present tense
            for grammeme in grammemes:
                # check that property exists then build it into this exponent
                if not self.get_property(category, grammeme):
                    print("Grammar add_exponent failed - invalid grammatical value {0} in category {1}".format(grammeme, category))
                    return
                exponent_properties[category].add(grammeme)

        # store exponent details
        exponent_id = "grammatical-exponent-{0}".format(uuid.uuid4())
        self.exponents[exponent_id] = {
            'id': exponent_id,
            'pre': pre,
            'post': post,
            'bound': bound,
            'properties': exponent_properties
        }
        return exponent_id

    def add_exponents(self, exponents_details):
        """Add a list of grammatical exponents with properties"""
        if type(exponents_details) is not list:
            print("Grammar add_exponents failed - invalid list of exponents {0}".format(exponents_details))
            return
        # prepare to store ids of created exponents
        exponent_ids = []
        # shape and store details
        for exponent in exponents_details:
            # verify expected details for an exponent
            if type(exponent) is not dict or 'properties' not in exponent or not ('pre' in exponent or 'post' in exponent):
                print("Grammar add_exponents skipped invalid element - expected dict with 'properties' and 'pre' or 'post', got {0}".format(exponent))
                continue
            # shape new details layering default values over missing details
            new_exponent_details = self.merge_maps(exponent, {
                'pre': "",
                'post': "",
                'bound': True,
            }, key_check=lambda x: x not in exponent)
            # create an exponent entry using the new details
            exponent_id = self.add_exponent(
                pre=new_exponent_details['pre'],
                post=new_exponent_details['post'],
                bound=new_exponent_details['bound'],
                properties=new_exponent_details['properties']
            )
            # keep references to successful exponents
            exponent_id and exponent_ids.append(exponent_id)
        return exponent_ids

    def remove_exponent(self, exponent_id):
        """Delete the record for one exponent from the grammar"""
        # check that the exponent exists
        if exponent_id not in self.exponents:
            print("Grammar remove_exponent failed - unknown id {0}".format(exponent_id))
            return
        # keep a copy of the details to return
        removed_exponent = self.exponents[exponent_id]
        # delete exponent id and details
        self.exponents.pop(exponent_id)
        return removed_exponent

    def update_exponent(self, exponent_id, pre="", post="", properties={}, bound=None):
        """Modify the basic details of one grammatical exponent"""
        # check that the exponent exists
        if exponent_id not in self.exponents:
            print("Grammar update_exponent failed - unknown exponent id {0}".format(exponent_id))
            return
        # filter requested category, values sets through the existing properties
        # TODO: abstract this and use for checking updated properties maps elsewhere in the grammar
        updated_properties = {
            category: set(values) for category, values in properties.items()
            if category in self.properties
            and type(values) in (set, list, tuple)
            and [value for value in values if value in self.properties[category]]
        }
        # create new entry with non-empty details overlayed onto existing ones
        updated_exponent_details = self.merge_maps(
            self.exponents[exponent_id],
            {
                'pre': pre if pre and type(pre) is str else None,
                'post': post if post and type(post) is str else None,
                'bound': bound if type(bound) is bool else None,
                'properties': updated_properties if updated_properties else None
            },
            value_check=lambda x: x is not None
        )
        # assign the existing exponent to point to the new details
        self.exponents[exponent_id] = updated_exponent_details
        return exponent_id


    # Method group C: Search for properties and exponents with matching details

    def find_properties(self, grammeme=None, category=None, description=None, count=None):
        """List every property (or optionally the first only) with the matching details"""
        # check that at least one of the attributes is filled in
        if not (type(grammeme) is str or type(category) is str or type(description) is str):
            print("Grammar find_properties failed - expected at least one detail present")
            return
        # store category grammemes for propreties with matching details
        found_properties = []
        # current number of property matches for assessing if count is reached
        matches_count = 0
        # search through properties where details match query details
        for category in self.properties.items():
            for grammeme in self.properties[category]:
                details = self.properties[category][grammeme]
                # create comparison details with overlayed non-blank queried attributes
                query_details = self.merge_maps(details, {
                    'grammeme': grammeme,
                    'category': category,
                    'description': description
                }, value_check = lambda x: x is not None)
                # check for matches between comparison details and existing ones
                if details == query_details:
                    # store successful matches as category grammeme pairs
                    found_properties.append((category, grammeme))
                    # immediately stop searching at the requested number of matches
                    count += 1
                    if count and matches_count == count:
                        break
        return found_properties

    def find_exponents(self, pre=None, post=None, bound=None, count=None):
        """List exponent ids (all or up to a count limit) with the matching details"""
        if pre is None and post is None and bound is None:
            print("Grammar find_exponents failed - expected at least one detail")
            return
        # prepare to store exponents with matching details
        found_exponents = []
        # tally matching exponents to return at count limit if defined
        matches_count = 0
        # search for exponents where details match non-blank query details
        for exponent_id, exponent_details in self.exponents.items():
            # overlay a new details map switching in non-null query args
            query_details = self.merge_maps(exponent_details, {
                'pre': pre,
                'post': post,
                'bound': bound
            }, value_check=lambda x: x is not None)
            # check if the query exponent details match the current exponent
            if query_details == exponent_details:
                # collect ids of exponents matching the compared details
                found_exponents.append(exponent_id)
                # return the exponent immediately if only one is requested
                count += 1
                if count and count == matches_count:
                    break
        # return a list of exponents with matching details
        return found_exponents


    # Method group D: Helpers for comparing maps and identifying
    # requested properties and parts of speech

    def is_properties_map(self, properties={}):
        """Verify a well-structured map containing known categories and grammemes"""
        # expect a map to compare
        if not isinstance(properties, dict):
            return False
        # vet every single grammeme within every property category
        for category in properties:
            # verify paralleled structure of nested collections inside map
            for grammeme in category:
                # check against properties stored in the grammar
                if not self.is_property(category, grammeme):
                    return False
        # no properties or structures fell through during checks
        return True

    # TODO: instead consider new abstract way of intersecting of maps at top
    def filter_properties_map(self, properties={}):
        """Return a copy of a properties map filtered to hold only verified category:grammemes"""
        # verify that a map was provided
        if not isinstance(properties, dict):
            print("Grammar filter_properties_map failed - expected properties dict not {0}".format(properties))
            return

        # map collections for all known categories
        filtered_map = {
            # collect only known grammemes under known categories
            category: {
                grammeme for grammeme in properties[category]
                if grammeme in self.properties[category]
            }
            for category in properties if category in self.properties
        }

        return filtered_map

    def filter_word_classes_set(self, word_classes=[]):
        """Return a copy of a word classes collection filtered to hold only verified parts of speech"""
        # check word classes structure
        if type(word_classes) not in (list, set, tuple):
            print("Grammar filter_word_classes_set failed - invalid word classes collection {0}".format(word_classes))
            return

        # build and return a set containing recognized word classes
        return {
            word_class for word_class in word_classes
            if word_class in self.word_classes
        }

    def map_uncategorized_properties(self, properties=[]):
        """Build a map of properties using a list of grammeme names"""
        # typecheck for properties list
        if not isinstance(properties, list):
            print("Grammar map_uncategorized_properties failed - invalid properties list {0}".format(properties))
            return

        # collect recognizable/guessable properties and map them as category:grammemes
        properties_map = {}
        for property in properties:
            # read the first category:grammeme details where the grammeme matches this string
            properties_details = self.find_properties(property, count=1)
            # abandon mapping if a property is not found
            if not properties_details or 'grammeme' not in properties_details[0]:
                print("Grammar map_uncategorized_properties failed - unknown property {0}".format(property))
                return
            # retrieve the category and grammeme from the stored details
            property_entry = properties_details[0]
            category = property_entry['category']
            grammeme = property_entry['grammeme']
            # add grammeme beneath its category - to new set if needed
            properties_map[category] = properties_map.get(category, set()).add(grammeme)

        return properties_map

    def parse_properties(self, properties_text):
        """Turn a string of grammatical terms into a map of properties"""
        # check the properties data structure
        if type(properties_text) is not str:
            print("Grammar failed to parse properties - expected a string not {0}".format(properties_text))
            return

        # create an ordered collection of grammatical terms
        unidentified_terms = re.split(r"\W+", properties_text)

        # set up a map of matching properties and classes to fill out and return
        parsed_properties = {}

        # flexibly store latest confirmed member of category:grammeme pairs
        # allowing category to lead, follow or be dropped from beside grammeme
        current_category = None     # explicit category to be associated with a grammeme
        current_grammeme = None     # grammeme to be matched to implicit or explicit category
        stranded_grammeme = None    # uncategorized previous grammeme holder when new grammeme found

        # TODO: once a known grammeme name is reached, identify its category and store in properties
        #   - consider cases where categories are not explicit
        #   - once you hit another grammeme even if there is no known category yet, you have two properties to store

        # search through word classes and properties for recognizable matches
        for term in unidentified_terms:
            # check and store unidentified terms for properties
            # start by looking for a category
            if term in self.properties:
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
                if current_grammeme and not current_category:
                    stranded_grammeme = current_grammeme
                # reassign grammeme to whatever the current term is
                current_grammeme = term

            # guess previously identified grammeme left unassociated with any explicit category
            if stranded_grammeme:
                # find the property by its grammeme name only
                matching_properties = self.find_properties(grammeme=stranded_grammeme)
                # create an entry for the identified category and its grammeme
                if matching_properties:
                    current_category = parsed_properties[matching_properties[0][0]] = parsed_properties.get(matching_properties[0][0], set()).add(matching_properties[0][1])
                # reset for the next uncategorized grammeme
                stranded_grammeme = None

            # empty current category and grammeme into map if both are identified
            if current_category and current_grammeme:
                # check that suspected but unverified grammeme is valid
                # NOTE: check held off until here because grammeme term may be found before or after its parent category
                if current_grammeme not in self.properties[current_category]:
                    # toss the suspected grammeme and keep parsing
                    print("Grammar parse_properties skipped parsed but unrecognized property {0}:{1}".format(current_category, current_grammeme))
                    current_grammeme = None
                    continue
                # create an entry for the category and grammeme in the parsed map
                parsed_properties[current_category] = parsed_properties.get(current_category, set()).add(current_grammeme)
                # reset the category:grammeme for the next unidentified pairing
                current_category = None
                current_grammeme = None

        # NOTE: think about the incoming data and how well you will parse cases
        #
        # (1) Consider shapes of strings expected to be parsed above:
        #   "present tense indicative mood verb"
        #   "tense: present, mood: indicative, verb"
        #   "tense:pres mood:ind v"
        #   "pres ind v"
        #   "present tense indicative verb"
        #   "v, present, indicative"
        #   "pres-ind-v"
        #   ""
        #   "vpres"
        #
        # (2) Now resolve conflicts arising from flexibility:
        #   - dropped category name: perfective aspect past verb
        #   - two grammemes in a row: aspect:perfective past tense
        #   - a grammeme-category category-grammeme: present tense mood indicative
        #   - are these accounted for by the following heuristics?
        #       - "if I am a grammeme and the thing after me is a grammeme, I must have a category"
        #           - "if a category is before me, that is my category"
        #           - "if no category is before me, assume (find) my category"
        #       - "if I am a category, the thing to my right or my left must be a grammeme"
        #       - "if I am a word class, I can be treated in isolation "

        return parsed_properties

    def parse_word_classes(self, word_classes):
        """Turn a string of grammatical terms into a map of word classes"""
        # check for a string to parse
        if type(word_classes) is not str:
            print("Grammar failed to parse word classes - expected a string not {0}".format(word_classes))
            return

        # split the string into a collection of terms to check
        suspected_word_classes = re.split(r"\W+", word_classes)

        # prepare collection for parsing and adding known parts of speech
        parsed_word_classes = set()

        # collect recognized word class names into the returned set
        for term in suspected_word_classes:
            if term in self.word_classes:
                parsed_word_classes.add(term)
            # skip unrecognized word classes
            else:
                print("Grammar parse_word_classes skipped unknown word class {0}".format(term))
                continue

        return parsed_word_classes

    def is_exponent(self, pre="", post=""):
        """Check if the given sounds are an exponent in this grammar"""
        if not (pre or post):
            print("Grammar is_exponent failed - expected pre or post string")
            return
        # search details for pre/post matches
        for exponent_details in self.exponents.values():
            # circumfix or circumposition
            if exponent_details['pre'] and exponent_details['post'] and pre == exponent_details['pre'] and post == exponent_details['post']:
                return True
            # prefix or preposition
            if exponent_details['pre'] and pre == exponent_details['pre']:
                return True
            # suffix or postposition
            if exponent_details['post'] and post == exponent_details['post']:
                return True
        return False


    # Method Group E: Build methods

    # TODO: use modified .properties and .exponents structure to handle
    # requested properties smaller or larger than what's in the grammar
    #
    # - case 1: built word properties are less verbose than stored exponent properties
    #   - example: word is ['verb', 'past'] but past affix is ['verb', 'past', 'tense']
    #
    # - case 2: built word properties are more verbose than exponent
    #   - example: word is ['verb', 'past', 'tense'] but past affix is ['past']
    #
    # - case 3: built word properties are less verbose but cover multiple exponents
    #   - example: word is ['verb', 'past', 'tense'] but affixes are ['verb', 'finite'] and ['past', 'tense']
    #
    # - case 4: built word properties are empty
    #
    def vet_build_word_classes(self, word_classes):
        """Attempt to collect a set copying valid, known word classes from flexible input"""
        # collect word classes in a set
        if type(word_classes) in (list, tuple, set):
            return self.filter_word_classes_set(word_classes)  # NOTE: returns set or void
        # break down the string and analyze classes into a set
        if isinstance(word_classes, str):
            return self.parse_word_classes(word_classes)       # NOTE: returns set or void
        # unexpected word classes value supplied
        return

    def vet_build_word_properties(self, properties):
        """Attempt to map a copy of valid, known category grammemes from flexible property input"""
        # vet map for recognized categories and their grammemes
        if isinstance(properties, dict):
            return self.filter_properties_map(properties)
        # parse string of terms to collect known properties
        if isinstance(properties, str):
            return self.parse_properties(properties)
        # turn a list of grammemes into a map of guessed categories and grammemes
        if type(properties) in (list, tuple, set):
            return self.map_uncategorized_properties(properties)
        # unexpected properties value given
        return

    def build_word(self, root, properties=[], word_classes=[], avoid_redundant_exponents=False):
        """Build up relevant morphology using the given grammatical terms"""
        # verify that a root word is given
        if type(root) is not str:
            print("Grammar build_word failed - invalid root word string {0}".format(root))
            return

        # make usable word class set collecting valid and recognizable pos terms
        vetted_word_classes = self.vet_build_word_classes(word_classes)

        # dead end if did not turn up a set of known word classes (or empty set)
        if vetted_word_classes == None or not isinstance(word_classes, set):
            print("Grammar build_word failed for root {0} - invalid word classes {1}".format(root, vetted_word_classes))
            return

        # make usable properties map collecting valid and recognizable category:grammemes
        vetted_properties = self.vet_build_word_properties(properties)

        # dead end when did not turn up a good map of properties
        if not self.is_properties_map(vetted_properties):
            print("Grammar build_word failed {0} - invalid properties {1}".format(root, vetted_properties))
            return

        # TODO: exponent using vetted_properties and vetted_word_classes
        #   - use properties to find an exponent with matching category:grammemes
        #   - use word_classes to filter in and out exponent include-excludes
        #
        # /!\ everything local below is from old best-match implementation /!\

        # TODO: instead of traversing all exponents, grab them from stored grammemes
        #   - NOTE: this means rethinking store-read-update data
        #   - properties store associated exponents at the grammeme level
        #   - every property requested will be checked for its exponent
        #   - then just keep intersecting property exponent sets
        #   - case: does this work? what if an exponent has more properties than requested? (past, ind, active when just past given)

        # collect relevant exponents
        matching_exponents = set()
        # properties that apply to more than one exponent for finding the optimal exponents
        reviewed_properties = {}    # 'category:grammeme' keys paired with exponent id sets
        collided_exponents = set()  # exponent ids for exponents that have on current pass

        # find exponents that match one or more properties and word class includes/excludes
        for exponent_id, exponent_details in self.exponents.items():
            # - expect requested properties set to be smaller per requested exponent than the exponents
            # - expect requested properties set to be larger per requested exponent if requesting multiple exponents
            # - expect requested properties set not to duplicate properties possibly repeated in multiple exponents
            # - expect exponent properties set to contain all relevant properties possibly requested

            # retrieve all property names for this exponent
            exponent_properties = exponent_details['properties']

            for category in exponent_properties:
                matched_category_grammemes = set()
                for grammeme in exponent_properties[category]:
                    category_grammeme = "{0}:{1}".format(category, grammeme)
                    matched_category_grammemes.add(category_grammeme)
                    # WAIT! isn't it if you add other category-grammemes you are a useful one?
                    # - but you still need to delete the old one(s)
                    # - say you have a "tense:past" exponent and a "mood:indicative" one, then a third with both comes along

                    # note exponents that already have these properties
                    if category_grammeme in reviewed_properties:
                        collided_exponents.add(collided_exponent)
                    # point to this exponent for future checks
                    else:
                        # I think if you ever get here and you have collided exponents
                        # you are a superset of another
                        # WAIT! think about cases where properties are split between two exponents which may share a third

                        # new requested property beyond currently matched exponents
                        reviewed_properties[category_grammeme] = exponent_id
                # if there were any collided exponents, check for supersets
                # - here look to see if all category:grammemes can be added to future checks or if exponent should be tossed
                # - if the current exponent properties are a superset of one in grammemes, replace the old one (add all its category:grammemes)
                # - if the current exponent properties are a subset, toss it
                # - if the current exponent properties have no conflicts, add all its category:grammemes

                if collided_exponents:
                    for property_name in collided_exponents:
                        continue
                    # search through the collided exponent_id properties
                    # compare the two to see if one is a superset of the other

            # exponent: 'id', 'pre', 'post', 'bound', 'properties'

            # TODO: note if two exponents collided on same property, then check them below
            matching_exponents.add(exponent_id)

        print("matching exponents: ", matching_exponents)

        # PROBLEM: is {verb, tense, past, indicative, first, person, singular} a better match than {verb, tense, past}?

        # TODO: find supersets/subsets of exponent matches
        #   - this happens when multiple exponents share properties
        #   - answer: is one more vague than another? choose the more exact one for requested properties
        #
        # does the exponent's properties contain all the category:grammemes?
        # if so, does it contain other grammemes?
        # if so, does it contain other keys (category:grammemes)?
        for matching_exponent in matching_exponents:
            matching_exponent_details = self.exponents[matching_exponent]
            best_exponent_match = None # track the id that matches the most properties (biggest superset)

            for compared_exponent in matching_exponents:
                # comparing exponent to itself
                if compared_exponent == matching_exponent:
                    continue
                compared_exponent_details = self.exponents[matching_exponent]

        # list of either one exact exponent properties match or one or more guesses
        print(matching_exponents)

        # add exponents to build up the word
        word = root
        for exponent_id in matching_exponents:
            word = self.attach_exponent(word, exponent_id=exponent_id)
        return word

    def attach_exponent(self, stem, exponent_id=None):
        """Attach one grammatical exponent to a string of phones"""
        # check for a good stem and an exponent to attach to it
        if type(stem) is not str:
            print("Grammar attach_exponent failed - invalid word stem {0}".format(stem))
            return
        if exponent_id not in self.exponents:
            print("Grammar attach_exponent failed - unknown exponent id {0}".format(exponent_id))
            return

        # prepare the base and attachment data
        exponented_word = stem
        exponent = self.exponents[exponent_id]

        # add exponent as affix
        if exponent['bound']:
            exponented_word = "{}{}{}".format(exponent['pre'], exponented_word, exponent['post'])
        # add exponent as particle or adposition structure
        else:
            if exponent['pre']:
                exponented_word = "{0} {1}".format(exponent['pre'], exponented_word)
            if exponent['post']:
                exponented_word = "{0} {1}".format(exponented_word, exponent['post'])
        return exponented_word

# 1 - build properties
grammar = Grammar()

# expect grammar to add individually
# TODO ignore caps
grammar.add_property("verb", description="word class: for verbs")
grammar.add_property("noun", description="word class: for nouns")
grammar.add_property("adjective", description="word class: for adjectives")
grammar.add_property("adverb", description="word class: for adverbs")
added_property = grammar.add_property("particle", description="word class: for particles")
print(added_property)

# expect grammar to add all
# TODO limit/filter which properties must be excluded or included with another?
# - example: cases can include only nouns, adjectives
added_properties = grammar.add_properties([
    {'name': "case", 'description': "category: nominal case"},
    {'name': "nominative", 'description': "grammeme: case mainly for subjects"},
    {'name': "accusative", 'description': "grammeme: case mainly for objects"},
    {'name': "number", 'description': "category: grammatical number"},
    {'name': "singular", 'description': "grammeme: singular number"},
    {'name': "plural", 'description': "grammeme: plural number"},
    {'name': "deixis", 'description': "category: distance indicators"},
    {'name': "proximal", 'description': "grammeme: near distance"},
    {'name': "distal", 'description': "grammeme: far distance"},
    {'name': "aspect", 'description': "category: verbal aspect"},
    {'name': "perfective", 'description': "grammeme: perfective aspect"},
    {'name': "imperfective", 'description': "grammeme: imperfective aspect"},
    {'name': "tense", 'description': "category: verbal tense"},
    {'name': "present", 'description': "grammeme: present tense"},
    {'name': "past", 'description': "grammeme: past tense"},
    {'name': "mood", 'description': "grammeme: verbal mood"},
    {'name': "indicative", 'description': "grammeme: indicative mood"},
    {'name': "voice", 'description': "category: voice"},
    {'name': "active", 'description': "grammeme: active voice"}
])
print(added_properties)
# expect grammar to detect issue, avoid adding and return None
grammar.add_properties([])
grammar.add_properties([{}])
grammar.add_properties(['chocolate'])
grammar.add_properties([{'name': "xyz", 'favorites': 0}])
grammar.add_properties([{'favorites': 0}])

print(grammar.is_property(name="mood"))
print(grammar.is_property(name="plural"))
print(grammar.is_property(name="verb"))

# 2 - build exponents
grammar.add_exponent(post="tele", bound=False, properties=["noun", "deixis", "proximal"])
added_exponent = grammar.add_exponent(post="talak", bound=False, properties=["noun", "deixis", "distal"])
added_exponents = grammar.add_exponents([
    {'post': "l", 'bound': True, 'properties': ["verb", "present", "tense", "perfective", "aspect", "indicative", "mood", "active", "voice"]},
    {'post': "hapa", 'bound': True, 'properties': ["verb", "past", "tense", "perfective", "aspect", "indicative", "mood", "active", "voice"]}
])
print(added_exponent)
print(added_exponents)
grammar.add_exponent(properties=["noun", "deixis", "proximal"])
grammar.add_exponent(pre=[], post=[], properties=[])
grammar.add_exponent(pre="", post="", properties=[])

# 3 - build demo words
word_1 = grammar.build_word("poiuyt", properties=["verb", "past"])
print(word_1)
word_2 = grammar.build_word("poiuyt", properties=["verb"])
print(word_2)
