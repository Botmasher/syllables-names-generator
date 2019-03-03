from functional_maps import merge_maps

# TODO: handle word classes intertwined here

# Method group B: Core CRUD for mapping properties, word classes and exponents
class Properties:
    def __init__(self):
        self.properties = {}

    def get(self, category=None, grammeme=None):
        """Read one grammatical value from one category in the grammar"""
        return self.properties.get(category, {}).get(grammeme, None)

    def add(self, category=None, grammeme=None, description=None, include=None, exclude=None):
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

    def add_many(self, properties_details):
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
                self.add(category, grammemes)
                continue
            
            # go through category:grammemes and add each valid pair
            for grammeme in grammemes:
                # create a new grammeme passing along only its category name and grammeme name
                # NOTE: this bare-minimum method leaves all other attributes empty
                if type(grammeme) is str:
                    added_property = self.add(category=category, grammeme=grammeme)
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
                    property_details = merge_maps(
                        default_details,
                        grammeme,
                        key_check=lambda x: x in default_details
                    )
                    # create property reading merged custom details + defaults for missing details
                    added_property = self.add(
                        category=property_details['category'],
                        grammeme=property_details['grammeme'],
                        description=property_details['description'],
                        include=property_details['include'],
                        exclude=property_details['exclude']
                    )
                # collect successfully added properties
                added_property and added_properties.append(added_property)
        return added_properties

    def update(self, category, grammeme, description=None):
        """Modify text details for one grammatical property"""
        if not self.get(category, grammeme):
            print("Grammar update_property failed - invalid category value {0}:{1}".format(category, grammeme))
            return
        # create new property entry with modified details
        grammeme_details = merge_maps(self.properties[category][grammeme], {
            'description': description
        }, value_check=lambda x: type(x) is str)
        self.properties[category][grammeme] = grammeme_details
        # access and return the created details
        return self.get(category, grammeme)


    def rename_category(self, category, new_category):
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

    def recategorize(self, source_category, grammeme, target_category):
        """Recategorize an existing grammeme from below its source category to below a destination category"""
        # check existence of current property
        if not self.get(source_category, grammeme):
            print("Grammar change_property_grammeme_category failed - unrecognized property {}:{}".format(source_category, grammeme))
            return
        # check type of swap target category
        if not isinstance(target_category, str):
            print("Grammar change_property_grammeme_category failed - expected target category string not {}".format(target_category))
            return

        # retrieve and modify the grammeme details
        grammeme_details = self.properties[source_category].pop(grammeme)
        # create a new details entry
        grammeme_details = merge_maps(
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

    def rename_grammeme(self, category, grammeme, new_grammeme):
        """Rename the grammeme for a single property and update exponents to reference the new name"""
        # check for updated grammeme string and existing property
        if not (new_grammeme and isinstance(new_grammeme, str)):
            print("Grammar change_property_grammeme failed - invalid non-empty new grammeme string {0}".format(new_grammeme))
            return
        if not self.get(category, grammeme):
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

    def remove(self, category, grammeme):
        """Delete the record for and exponent references to one property from the grammar"""
        if category not in self.properties or grammeme not in self.properties[category]:
            print("Grammar remove_property failed - unknown category value {0}:{1}".format(category, grammeme))
            return
        # reference deleted details
        removed_property = self.get(category, grammeme)
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
