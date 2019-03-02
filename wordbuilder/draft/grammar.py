import uuid         # for indexing exponent keys
import re           # for splitting strings and parsing them for properties
import math         # for allowing finds to break at user-defined count or data limit
from collections import deque   # for building pre- and post-exponented word pieces lists
#from functools import reduce    # for finding uncategorized grammemes

# NOTE: Grammar relates grammatical exponents <> grammatical properties
# - exponents are phones of affixes, adpositions, particles, pre or post a base
# - properties are categories, grammemes
# - word classes help filter or limit the application of exponents to built words

# TODO: handle non-pre/post kinds of exponents like apophony

class Grammar:
    def __init__(self):
        # word classes used to include or exclude words for exponents
        self.word_classes = {}
        # map of category, grammatical value pairs with details for each value
        # solution A: (implemented) store properties map containing {category: {grammemes: details}}
        # solution B: flatten every term (including categories and word classes) into low-level terms
        self.properties = {}
        # map of exponent details, including pointing to an exponent's property ids
        self.exponents = {}

        # TODO: resupport property and word class abbreviations
        # - unambiguous abbreviation:full_term map
        # - previous use of abbreviations: add/update (crud), parse_properties (identification - originally parse_terms)
        # - distinguish property from word_class abbreviations
        # - case: what about abbreviations for a category like tns?
        self.abbreviations = {}

    # Method group A: Functional map building and layering

    # TODO: break merge_maps out as a util instead of limiting it to this class
    # functional dict building to avoid direct mutations in word class, property and exponent update methods
    def merge_maps(self, base_map, overlay_map, key_check=lambda x: x, value_check=lambda x: x):
        """Overlay map pairs with filtered keys and values onto a base map and return the new map"""
        # expect both an old "base" and a new "overlay" dict
        if not(isinstance(base_map, dict) and isinstance(overlay_map, dict)):
            print("Grammar merge_maps failed - invalid base map or overlay map")
            return
        # expect a valid filter function to validate overlayed keys and values
        if type(key_check).__name__ != 'function' or type(value_check).__name__ != 'function':
            print("Grammar merge_maps failed - invalid checker functions")
            return
        # unpack old and new maps vetting the new one using key and value filters
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
            print("Grammar add_word_class skipped already existing word class {}".format(word_class))
            return
        # create a new entry for the part of speech
        self.word_classes[word_class] = {
            'name': word_class,
            'description': description
        }
        # read the created part of speech
        return self.word_classes[word_class]

    def add_word_classes(self, word_classes):
        """Add multiple parts of speech to the grammar"""
        # check for a collection of word classes
        if not isinstance (word_classes, (list, tuple, set)):
            print("Grammar add_word_classes failed - expected collection not {}".format(word_classes))
            return
        # comprehensively create parts of speech and return successful entries
        results = [self.add_word_class(word_class) for word_class in word_classes]
        added_word_classes = list(filter(lambda x: x, results))
        return added_word_classes

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
            # return the renamed word class details
            return self.word_classes[name]
        
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
        self.word_classes.pop(word_class)
        # remove part of speech from all property grammeme entries that reference it
        for category in self.properties:
            for grammeme, grammeme_details in self.properties[category].items():
                if word_class in grammeme_details['exclude']:
                    self.properties[category][grammeme]['exclude'].remove(word_class)
                if word_class in grammeme_details['include']:
                    self.exponents[category][grammeme]['include'].remove(word_class)
        # return deleted details
        return removed_word_class

    def filter_word_classes_set(self, word_classes):
        """Create a set of valid word classes from a single string or collection of strings"""
        # no word classes or empty collection passed
        if not word_classes:
            return set()
        # wrap a single string in a list for filtering set
        if isinstance(word_classes, str):
            word_classes = [word_classes]
        # create recognized set of word classes from collection
        return set(filter(lambda x: x in self.word_classes, word_classes))

    def get_property(self, category=None, grammeme=None):
        """Read one grammatical value from one category in the grammar"""
        return self.properties.get(category, {}).get(grammeme, None)

    def add_property(self, category=None, grammeme=None, description=None, include=None, exclude=None):
        """Add one grammatical value to an existing category in the grammar"""
        if not (category and grammeme and isinstance(category, str) and isinstance(grammeme, str)):
            print("Grammar add_property failed - expected category and grammeme to be non-empty strings")
            return

        # collect valid word classes to include or exclude when property is applied
        # TODO: also allow including or excluding other categories or grammemes
        included_word_classes = self.filter_word_classes_set(include)
        excluded_word_classes = self.filter_word_classes_set(exclude)

        # back out if property category:grammeme pair already exists
        if grammeme in self.properties.get(category, []):
            print("Grammar add_property failed - category {0} already contains grammeme {1} - did you mean to run update_property?".format(category, grammeme))
            return

        # create a new entry under the category for the grammeme
        self.properties.setdefault(category, {})[grammeme] = {
            'category': category,
            'grammeme': grammeme,
            'description': description,
            'include': included_word_classes,
            'exclude': excluded_word_classes
        }

        # read the created entry
        return self.properties[category][grammeme]

    def add_properties(self, properties_details):
        """Add a map of grammatical values within categories to the grammar"""
        if not isinstance(properties_details, dict):
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
        #           'category': str,
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
            if not isinstance(grammemes, (str, list, tuple, dict, set)):
                print("Grammar add_properties skipped category {0} - invalid grammemes collection {1}".format(category, grammemes))
                continue
            
            # TODO: flexible input including string - outline how to handle this and other types (incl dict)
            if isinstance(grammemes, str):
                self.add_property(category, grammemes)
                continue
            
            # go through category:grammemes and add each valid pair
            for grammeme in grammemes:
                # create a new grammeme passing along only its category name and grammeme name
                # NOTE: this bare-minimum method leaves all other attributes empty
                if type(grammeme) is str:
                    added_property = self.add_property(category=category, grammeme=grammeme)
                # expect any non-strings to be maps of grammeme details
                elif not isinstance(grammeme, dict) or 'grammeme' not in grammeme:
                    print("Grammar add_properties skipped {0}:{1} - expected a map with a 'grammeme' key".format(category, grammeme))
                    continue
                # create a fuller grammeme entry from a map with supplied attributes
                else:
                    # create a bare entry with defaults to underlay missing details
                    default_details = {
                        'category': category,
                        'grammeme': grammeme,
                        'description': None,
                        'include': set(),
                        'exclude': set()
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
                added_property and added_properties.append(added_property)
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
        if not (include or exclude) or not (isinstance(include, str) or isinstance(exclude, str)):
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

    def rename_property_category(self, category, new_category):
        """Update a category name in the properties map and for all grammemes and exponents that reference it"""
        # verify that category exists
        if category not in self.properties:
            print("Grammar rename_property_category failed - unknown property category {}".format(category))
            return
        # check for category rename conflict where target already exists
        if new_category in self.properties:
            print("Grammar rename_property_category failed - new category name already exists in properties: {}".format(new_category))
            return
        
        # retrieve property grammemes and clear out old category
        grammemes = self.properties.pop(category)
        
        # update the category attribute within each grammeme's details
        for grammeme_name in grammemes:
            grammemes[grammeme_name]['category'] = new_category

        # store grammemes under the new target category
        self.properties[new_category] = grammemes

        # update the property category reference in exponents that point to it
        for exponent_id, exponent_details in self.exponents.items():
            if category in exponent_details['properties']:
                self.exponents[exponent_id]['properties'][new_category] = self.exponents[exponent_id]['properties'].pop(category)

        # retrieve the new target category
        return self.properties[new_category]

    def change_property_grammeme_category(self, source_category, grammeme, target_category):
        """Recategorize an existing grammeme from below its source category to below a destination category"""
        # check existence of current property
        if not self.get_property(source_category, grammeme):
            print("Grammar change_property_grammeme_category failed - unrecognized property {}:{}".format(source_category, grammeme))
            return
        # check type of swap target category
        if not isinstance(target_category, str):
            print("Grammar change_property_grammeme_category failed - expected target category string not {}".format(target_category))
            return

        # retrieve and modify the grammeme details
        grammeme_details = self.properties[source_category].pop(grammeme)
        # create a new details entry
        grammeme_details = self.merge_maps(
            grammeme_details,
            {'category': target_category}
        )
        # remove the original category if it is left empty
        not self.properties[source_category] and self.properties.pop(source_category)
        # add the grammeme under the destination category
        self.properties.setdefault(target_category, {})[grammeme] = grammeme_details

        # swap the grammeme's category within exponent properties that reference it
        for exponent_id, exponent_details in self.exponents.items():
            if grammeme in exponent_details['properties'].get(source_category, {}):
                # remove grammeme from exponent properties
                self.exponents[exponent_id]['properties'][source_category].remove(grammeme)
                # remove empty category from exponent properties
                not exponent_details['properties'][source_category] and self.exponents[exponent_id]['properties'].pop(source_category)
                # add grammeme to destination category under exponent properties
                self.exponents[exponent_id]['properties'].setdefault(target_category, set()).add(grammeme)

        # retrieve and send back the new grammeme details
        return self.properties[target_category][grammeme]

    def rename_property_grammeme(self, category, grammeme, new_grammeme):
        """Rename the grammeme for a single property and update exponents to reference the new name"""
        # check for updated grammeme string and existing property
        if not (new_grammeme and isinstance(new_grammeme, str)):
            print("Grammar change_property_grammeme failed - invalid non-empty new grammeme string {0}".format(new_grammeme))
            return
        if not self.get_property(category, grammeme):
            print("Grammar change_property_grammeme failed - unknown category:grammeme {0}:{1}".format(category, grammeme))
            return

        # remove old grammeme entry
        grammeme_details = self.properties[category].pop(grammeme)
        # store the new details with the new grammeme name
        grammeme_details['grammeme'] = new_grammeme
        self.properties[category][new_grammeme] = grammeme_details

        # swap out grammeme name within all exponents that reference the property
        for exponent_id, exponent_details in self.exponents.items():
            if grammeme in exponent_details['properties'].get(category, {}):
                self.exponents[exponent_id]['properties'][category].remove(grammeme)
                self.exponents[exponent_id]['properties'][category].add(new_grammeme)

        # return updated property details
        return self.properties[category][new_grammeme]

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
    def add_exponent(self, pre="", post="", bound=True, properties=None):
        """Add one grammatical exponent to the grammar"""
        if not ((pre or post) and (isinstance(pre, str) and isinstance(post, str))):
            print("Grammar add_exponent failed - expected pre or post exponent string")
            return

        if not isinstance(properties, dict):
            print("Grammar add_exponent failed - expected properties dict")
            return

        # structure the categories and values of included properties

        # TODO: use sets determining if category:grammemes in properties are subsets of self.properties
        # set(properties.keys()).issubset(self.properties.keys())
        # map-reduce the grammemes for shared categories

        exponent_properties = {}
        for category, grammemes in properties.items():
            # avoid non-existing categories
            if category not in self.properties:
                print("Grammar add_exponent failed - invalid grammatical category {0}".format(category))
                return
            # format a set for a single grammeme in one category, like past tense
            if isinstance(grammemes, str):
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
                exponent_properties.setdefault(category, set()).add(grammeme)

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
        if not isinstance(exponents_details, list):
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

    def find_properties(self, grammeme=None, category=None):
        """Return category:grammeme pairs naming properties with the matching details"""
        # check that at least one of the attributes is filled in
        if not (isinstance(grammeme, str) or isinstance(category, str)):
            print("Grammar find_properties failed - expected at least one detail present")
            return
        # store category grammemes for propreties with matching details
        # check and return the explicit category:grammeme pair
        if grammeme and category:
            if self.properties.get(category, {}).get(grammeme):
                return [(category, grammeme)]
            return
        # uncategorized grammeme - return all occurrences
        elif grammeme and not category:
            return [(found_category, grammeme) for found_category in filter(
                lambda filtered_category: grammeme in self.properties[filtered_category],
                self.properties.keys()
            )]
        # all grammemes in a single category
        elif category in self.properties:
            return [(category, stored_grammeme) for stored_grammeme in self.properties[category].keys()]
        # no valid category or grammeme supplied
        else:
            return

    # NOTE: consider attribues-per-exponent map for easy reverse lookups
    def find_exponents(self, pre=None, post=None, bound=None, count=math.inf):
        """List exponent ids (all or up to a count limit) with the matching details"""
        if pre is None and post is None and bound is None:
            print("Grammar find_exponents failed - expected at least one detail")
            return
        # prepare to store exponents with matching details
        found_exponents = []
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
                # return requested exponents if count tally reached
                count -= 1
                if count == 0:
                    break
        # return a list of exponents with matching details
        return found_exponents


    # Method group D: Helpers for comparing maps and identifying
    # requested properties and parts of speech

    def is_properties_map(self, properties=None):
        """Verify a well-structured map containing known categories and grammemes"""
        # expect a map to compare
        if not isinstance(properties, dict):
            print("Grammar is_properties_map check failed - invalid properties map {}".format(properties))
            return False
        
        # vet every single grammeme within every property category
        for category in properties:
            # verify category exists in the grammatical properties
            if category not in self.properties:
                return False
            # verify paralleled structure of nested grammemes under category
            for grammeme in self.properties[category]:
                # check against properties stored in the grammar
                if not self.get_property(category, grammeme):
                    return False
        
        # no properties or structures fell through during checks
        return True

    def filter_grammemes(self, category, grammemes):
        """Structure a set of category grammemes allowing for flexible input"""
        # handle a grammemes set or single string within a known category
        if category in self.properties:
            # return recognized grammeme collection members inside of a set
            if type(grammemes) in (list, set, tuple):
                return set(grammemes).intersection(self.properties.get(category, set()))
            # recognized grammeme string inside of a set
            if type(grammemes) is str and grammemes in self.properties.get(category, set()):
                # only one grammeme string given
                return {grammemes}
        # unrecognized category name or grammeme type input
        else:
            return

    # NOTE: also see newer abstraction of intersecting maps at top
    def filter_properties_map(self, properties=None):
        """Return a copy of a properties map filtered to hold only verified category:grammemes"""
        # verify that a map was provided
        if not isinstance(properties, dict):
            print("Grammar filter_properties_map failed - expected properties dict not {0}".format(properties))
            return

        # map collections for all known categories
        filtered_map = {
            # collect only known grammemes under known categories
            category: self.filter_grammemes(category, grammemes)
            # iterate through categories - category existence handled in grammemes filter
            for category, grammemes in properties.items()
        }

        return filtered_map

    def vet_word_classes(self, word_classes):
        """Return a copy of a word classes collection filtered to hold only verified parts of speech"""
        # check word classes structure
        if not isinstance(word_classes, (list, set, tuple)):
            print("Grammar vet_word_classes failed - invalid word classes collection {0}".format(word_classes))
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
        for category in properties:
            # read the first category:grammeme details where the grammeme matches this string
            properties_details = self.find_properties(category)
            # abandon mapping if a property is not found
            if not properties_details or 'grammeme' not in properties_details[0]:
                print("Grammar map_uncategorized_properties failed - unknown property {0}".format(category))
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
                print(current_category, i, len(unidentified_terms)-1)
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
                matching_properties = self.find_properties(grammeme=stranded_grammeme)
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
                    matching_properties = self.find_properties(grammeme=current_grammeme)
                    if not matching_properties:
                        break
                    current_category = matching_properties[0][0]

                # check that suspected but unverified grammeme is valid
                # NOTE: check held off until here because grammeme term may be found before or after its parent category
                if current_grammeme not in self.properties[current_category]:
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

    def vet_build_word_classes(self, word_classes, return_unrecognized=False):
        """Attempt to collect a set copying known word classes from a collection or a parsable string"""
        # collect word classes in a set
        if isinstance(word_classes, (list, tuple, set)):
            return self.vet_word_classes(word_classes)      # NOTE: expect returned set
        # break down the string and analyze classes into a set
        if isinstance(word_classes, str):
            return self.parse_word_classes(word_classes)    # NOTE: expect set or None
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

    # subdict method used to determine whether exponent properties provide requested properties in build_word
    def is_subproperties(self, compared_properties, base_properties):
        """Check whether all category:grammemes in a compared properties map exist in another properties map"""
        # verify two comparable maps have been passed
        if not isinstance(compared_properties, dict) or not isinstance(base_properties, dict):
            print("Grammar is_subproperties failed - expected a comparison map and base map, got {0} and {1}".format(compared_properties, base_properties))
            return

        # check every compared category and grammeme for inclusion in the base map
        for category in compared_properties:
            # expect all compared categories to exist in the base map
            if category not in base_properties:
                return False

            # expect iterable to turn into set of properties
            compared_grammemes = {grammeme for grammeme in compared_properties[category]}
            base_grammemes = {grammeme for grammeme in base_properties[category]}

            # expect all compared grammemes to exist in the base category
            if not compared_grammemes.issubset(base_grammemes):
                return False

        # no mismatch pitfalls - consider compared map as true subproperties
        return True

    # the main public method for making use of data stored in the grammar
    def build_unit(self, root, properties=None, word_classes=None, all_or_none=False):
        """Build up relevant morphosyntax around a base using the given grammatical terms"""
        # TODO: better docstring particularly for this method

        # verify that a root word is given
        if not isinstance(root, str):
            print("Grammar build_word failed - invalid root word string {0}".format(root))
            return

        # make usable word class set collecting valid and recognizable pos terms
        requested_word_classes = self.vet_build_word_classes(word_classes)

        # make usable properties map collecting valid and recognizable category:grammemes
        requested_properties = self.vet_build_word_properties(properties)

        # dead end when did not turn up a good map of vetted properties
        if not self.is_properties_map(requested_properties):
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
        for exponent_id, exponent_details in self.exponents.items():
            # retrieve all property names for this exponent
            exponent_properties = exponent_details['properties']

            # also check that the optional property word class includes or excludes are met
            mismatched_word_classes = False
            # go through included and excluded word classes among grammemes in exponent properties
            for category in exponent_properties:
                for grammeme in exponent_properties[category]:
                    grammeme_includes = self.properties[category][grammeme]['include']
                    grammeme_excludes = self.properties[category][grammeme]['exclude']
                    # pass over exponent based on word classes expected to be included
                    if grammeme_includes and not (requested_word_classes and requested_word_classes.issubset(grammeme_includes)):
                        mismatched_word_classes = True
                        break
                    # pass over exponent based on word classes expected to be excluded
                    if grammeme_excludes and requested_word_classes and requested_word_classes.issubset(grammeme_excludes):
                        mismatched_word_classes = True
                        break

                # stop searching grammemes if word classes mismatch property includes/excludes
                if mismatched_word_classes:
                    break

            # hold exponents that provide one or more requested properties and none not requested
            if not mismatched_word_classes and self.is_subproperties(exponent_properties, requested_properties):
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
            exponent_properties = self.exponents[matching_exponent]['properties']

            # traverse all exponent matches and look for properties
            for compared_exponent in matching_exponents:

                # skip comparing base exponent to itself
                if compared_exponent == matching_exponent:
                    continue

                # properties from other matched exponents
                compared_exponent_properties = self.exponents[compared_exponent]['properties']

                # run the comparison looking for an exponent with superproperties
                if self.is_subproperties(exponent_properties, compared_exponent_properties):
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

    def attach_exponents(self, root, exponent_ids, as_string=False):
        """Exponent a complex word to correctly position a root, prefixes, postfixes, prepositions, postpositions"""
        # expect a collection of exponent ids and a word-building map
        if type(exponent_ids) not in (list, set, tuple):
            print("Grammar attach_exponent_map failed - invalid list of exponents {}".format(exponent_ids))
            return

        # exponent attachment types in in sequential order
        attachment_sequence = ('preposition', 'prefix', 'root', 'postfix', 'postposition')

        # keep word pieces accounting for possible positions and spacing
        exponented_word_map = {attachment: deque() for attachment in attachment_sequence}
        exponented_word_map['root'].append(root)

        # go through exponents and map them as prescribed in the exponent
        for exponent_id in exponent_ids:
            exponent_details = self.exponents.get(exponent_id)
            # check for valid exponent
            if not exponent_details:
                print("Grammar attach_exponents skipped invalid exponent {}".format(exponent_id))
                continue

            # decide to store exponent as affixal or positional
            pre_key, post_key = ('prefix', 'postfix') if exponent_details['bound'] else ('preposition', 'postposition')
            # leave space between non-affixes and base
            spacing = "" if exponent_details['bound'] else " "
            # reference to the actual material being added
            pre = exponent_details['pre'] if exponent_details['pre'] else ""
            post = exponent_details['post'] if exponent_details['post'] else ""

            # add exponent as the next-affixed/apposed material
            # add to left of prefixes or prepositions collection
            pre and exponented_word_map[pre_key].appendleft(spacing)
            pre and exponented_word_map[pre_key].appendleft(pre)
            # add to right of suffixes or postpositions collection
            post and exponented_word_map[post_key].append(spacing)
            post and exponented_word_map[post_key].append(post)

        # TODO: here consider whether creating morphosyntax slotting of properties is necessary

        # turn the exponenting map into a flat sequence
        exponented_word = [
            piece for attachment in attachment_sequence for piece in exponented_word_map[attachment]
        ]

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
        if exponent_id not in self.exponents:
            print("Grammar attach_exponent failed - unknown exponent id {0}".format(exponent_id))
            return

        # prepare the base and attachment data
        exponent = self.exponents[exponent_id]
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


# DEMO - intuitive buildout of words
grammar = Grammar()
grammar.add_word_class("noun", "verb")
# add basic properties
grammar.add_properties({
    'tense': ["present", "past", "future"],
    'aspect': ["perfective", "imperfective"],
    'number': ["singular", "plural"],
    'case': ["nominative", "oblique"]
})
grammar.add_property_word_class("tense", "present", include="verb")
grammar.add_property_word_class("number", "singular")
# TODO: should word classing actually be handled by exponent (switch back)?
# - make the property available for multiple; it's the exponent that gets attached
# - case: EN -s for pl n, -s for 3p sing v

# add basic exponents
grammar.add_exponent(post="s", properties={"case": "nominative", "number": "plural"}, bound=True)

singular_noun = grammar.build_unit("house", properties="nominative singular")
plural_noun = grammar.build_unit("house", properties="nominative plural")
print(singular_noun, plural_noun)
