from ..tools.functional_maps import merge_maps

class Properties:
    def __init__(self, grammar):
        # reference to parent grammar where exponents provide these properties
        # used to update exponent details when categories or grammemes change
        self.grammar = grammar
        
        # store properties map containing {category: {grammemes: details}}
        self.properties = {}

    # Methods for properties CRUD

    def get(self, category=None, grammeme=None):
        """Read category:grammemes from the properties map"""
        # fetch all categories and grammemes
        if not category and not grammeme:
            return self.properties
        # fetch all grammemes in a single category
        elif not grammeme:
            return self.properties.get(category)
        # fetch a single grammeme
        else:
            return self.properties.get(category, {}).get(grammeme, None)
    
    def is_category(self, category):
        """Check if the category exists in the properties map"""
        return category in self.properties

    def add(self, category=None, grammeme=None, description=None):
        """Add one grammatical value to an existing category in the properties"""
        if not (category and grammeme and isinstance(category, str) and isinstance(grammeme, str)):
            print("Properties.add failed - expected category and grammeme to be non-empty strings")
            return

        # back out if property category:grammeme pair already exists
        if grammeme in self.properties.get(category, []):
            print("Properties.add failed - category {0} already contains grammeme {1} - did you mean to run update_property?".format(category, grammeme))
            return

        # create a new entry under the category for the grammeme
        self.properties.setdefault(category, {})[grammeme] = {
            'category': category,
            'grammeme': grammeme,
            'description': description
        }

        # read the created entry
        return self.properties[category][grammeme]

    def add_many(self, properties_details):
        """Add a map of grammatical values within categories to the properties"""
        if not isinstance(properties_details, dict):
            print("Properties.add_many failed - invalid properties map {0}".format(properties_details))
            return
        # store each new grammatical value added to the grammar
        # verify it has the expected details structure:
        # {
        #   # string representing the lookup category over the grammeme
        #   category: [
        #       # pass a map full of the new property's attributes
        #       {
        #           # optional repeated category name (unique top-level category name)
        #           'category': str,
        #           # required grammeme name (unique name within the category)
        #           'grammeme': str,
        #           # optional attributes
        #           'description': str
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
                print("Properties.add_many skipped category {0} - invalid grammemes collection {1}".format(category, grammemes))
                continue
            
            # TODO: flexible input including string - outline how to handle this and other types (incl dict)
            if isinstance(grammemes, str):
                self.add(category, grammemes)
                continue
            
            # go through category:grammemes and add each valid pair
            for grammeme in grammemes:
                # create a new grammeme passing along only its category name and grammeme name
                # NOTE: this bare-minimum method leaves all other attributes empty
                if isinstance(grammeme, str):
                    added_property = self.add(category=category, grammeme=grammeme)
                # expect any non-strings to be maps of grammeme details
                elif not isinstance(grammeme, dict) or 'grammeme' not in grammeme:
                    print("Properties.add_many skipped {0}:{1} - expected a map with a 'grammeme' key".format(category, grammeme))
                    continue
                # create a fuller grammeme entry from a map with supplied attributes
                else:
                    # create a bare entry with defaults to underlay missing details
                    default_details = {
                        'category': category,
                        'grammeme': grammeme,
                        'description': None
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
                        description=property_details['description']
                    )
                # collect successfully added properties
                added_property and added_properties.append(added_property)
        return added_properties

    def update(self, category, grammeme, description=None):
        """Modify text details for one grammatical property"""
        if not self.get(category, grammeme):
            print("Properties.update failed - invalid category value {0}:{1}".format(category, grammeme))
            return
        # create new property entry with modified details
        grammeme_details = merge_maps(self.properties[category][grammeme], {
            'description': description
        }, value_check=lambda x: type(x) is str)
        self.properties[category][grammeme] = grammeme_details
        # access and return the created details
        return self.get(category, grammeme)

    def remove(self, category, grammeme):
        """Delete the record for and exponent references to one property from the grammar"""
        if category not in self.properties or grammeme not in self.properties[category]:
            print("Properties.remove failed - unknown category value {0}:{1}".format(category, grammeme))
            return
        # reference deleted details
        removed_property = self.get(category, grammeme)
        # delete property key and details
        self.properties[category].pop(grammeme)
        # delete property from exponent properties category sets that have it
        for exponent_id, exponent_details in self.grammar.exponents.get_items():
            if category in exponent_details['properties'] and grammeme in exponent_details['properties'][category]:
                self.grammar.exponents.get(exponent_id)['properties'][category].remove(grammeme)
            # also delete the category from properties if it is left empty
            if self.grammar.exponents.get(exponent_id)['properties'][category] == set():
                self.grammar.exponents.get(exponent_id)['properties'].pop(category)
        # return the deleted details
        return removed_property
    
    # update grammeme name, grammeme categorization or category name

    def rename_category(self, category, new_category):
        """Update a category name in the properties map and for all grammemes and exponents that reference it"""
        # verify that category exists
        if category not in self.properties:
            print("Properties.rename_category failed - unknown property category {}".format(category))
            return
        # check for category rename conflict where target already exists
        if new_category in self.properties:
            print("Properties.rename_category failed - new category name already exists in properties: {}".format(new_category))
            return
        
        # retrieve property grammemes and clear out old category
        grammemes = self.properties.pop(category)
        
        # update the category attribute within each grammeme's details
        for grammeme_name in grammemes:
            grammemes[grammeme_name]['category'] = new_category

        # store grammemes under the new target category
        self.properties[new_category] = grammemes

        # update the property category reference in exponents that point to it
        for exponent_id, exponent_details in self.grammar.exponents.get_items():
            if category in exponent_details['properties']:
                self.grammar.exponents.get(exponent_id)['properties'][new_category] = self.grammar.exponents.get(exponent_id)['properties'].pop(category)

        # retrieve the new target category
        return self.properties[new_category]

    def recategorize(self, source_category, grammeme, target_category):
        """Recategorize an existing grammeme from below its source category to below a destination category"""
        # check existence of current property
        if not self.get(source_category, grammeme):
            print("Properties.recategorize failed - unrecognized property {}:{}".format(source_category, grammeme))
            return
        # check type of swap target category
        if not isinstance(target_category, str):
            print("Properties.recategorize failed - expected target category string not {}".format(target_category))
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
        for exponent_id, exponent_details in self.grammar.exponents.get_items():
            if grammeme in exponent_details['properties'].get(source_category, {}):
                # remove grammeme from exponent properties
                self.grammar.exponents.get(exponent_id)['properties'][source_category].remove(grammeme)
                # remove empty category from exponent properties
                not exponent_details['properties'][source_category] and self.grammar.exponents.get(exponent_id)['properties'].pop(source_category)
                # add grammeme to destination category under exponent properties
                self.grammar.exponents.get(exponent_id)['properties'].setdefault(target_category, set()).add(grammeme)

        # retrieve and send back the new grammeme details
        return self.properties[target_category][grammeme]

    def rename_grammeme(self, category, grammeme, new_grammeme):
        """Rename the grammeme for a single property and update exponents to reference the new name"""
        # check for updated grammeme string and existing property
        if not (new_grammeme and isinstance(new_grammeme, str)):
            print("Properties.rename_grammeme failed - invalid non-empty new grammeme string {0}".format(new_grammeme))
            return
        if not self.get(category, grammeme):
            print("Properties.rename_grammeme failed - unknown category:grammeme {0}:{1}".format(category, grammeme))
            return

        # remove old grammeme entry
        grammeme_details = self.properties[category].pop(grammeme)
        # store the new details with the new grammeme name
        grammeme_details['grammeme'] = new_grammeme
        self.properties[category][new_grammeme] = grammeme_details

        # swap out grammeme name within all exponents that reference the property
        for exponent_id, exponent_details in self.grammar.exponents.get_items():
            if grammeme in exponent_details['properties'].get(category, {}):
                self.grammar.exponents.get(exponent_id)['properties'][category].remove(grammeme)
                self.grammar.exponents.get(exponent_id)['properties'][category].add(new_grammeme)

        # return updated property details
        return self.properties[category][new_grammeme]

    def find(self, grammeme=None, category=None):
        """Return category:grammeme pairs naming properties with the matching details"""
        # check that at least one of the attributes is filled in
        if not (isinstance(grammeme, str) or isinstance(category, str)):
            print("Properties.find failed - expected at least one detail present")
            return
        # store category grammemes for propreties with matching details
        # check and return the explicit category:grammeme pair
        if grammeme and category:
            if self.get(category, {}).get(grammeme):
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
    

    # Methods for comparing maps and identifying requested properties

    def is_properties_map(self, properties=None):
        """Verify a well-structured map containing known categories and grammemes"""
        # expect a map to compare
        if not isinstance(properties, dict):
            print("Properties.is_properties_map check failed - invalid properties map {}".format(properties))
            return False
        
        # vet every single grammeme within every property category
        for category in properties:
            # verify category exists in the grammatical properties
            if category not in self.properties:
                return False
            # verify paralleled structure of nested grammemes under category
            for grammeme in self.properties[category]:
                # check against properties stored in the grammar
                if not self.get(category, grammeme):
                    return False
        
        # no properties or structures fell through during checks
        return True

    def filter_grammemes(self, category, grammemes):
        """Structure a set of category grammemes allowing for flexible input"""
        # handle a grammemes set or single string within a known category
        if category in self.properties:
            # return recognized grammeme collection members inside of a set
            if isinstance(grammemes, (list, set, tuple)):
                return set(grammemes).intersection(self.properties.get(category, set()))
            # recognized grammeme string inside of a set
            if isinstance(grammemes, str) and grammemes in self.properties.get(category, set()):
                # only one grammeme string given
                return {grammemes}
        # unrecognized category name or grammeme type input
        else:
            return

    def filter(self, properties=None):
        """Return a filtered properties copy containing only verified category keys and grammemes sets"""
        # verify that a map was provided
        if not isinstance(properties, dict):
            print("Properties.filter failed - expected properties dict not {0}".format(properties))
            return

        # map collections for all known categories
        filtered_map = {
            # collect only known grammemes under known categories
            category: self.filter_grammemes(category, grammemes)
            # iterate through categories - category existence handled in grammemes filter
            for category, grammemes in properties.items()
        }

        return filtered_map

    def map_uncategorized_properties(self, properties=None):
        """Build a map of properties using a list of grammeme names"""
        # typecheck for properties list
        if not isinstance(properties, list):
            print("Grammar map_uncategorized_properties failed - invalid properties list {0}".format(properties))
            return

        # collect recognizable/guessable properties and map them as category:grammemes
        properties_map = {}
        for category in properties:
            # read the first category:grammeme details where the grammeme matches this string
            properties_details = self.find(category=category)
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

    # subdict method used to determine whether requested properties
    def is_subproperties(self, compared_properties, base_properties=None):
        """Check whether all category:grammemes in a compared properties map exist in the base properties map"""
        # verify two comparable maps have been passed
        if not isinstance(compared_properties, dict) or not isinstance(base_properties, dict):
            print("Grammar is_subproperties failed - expected a comparison map and base map, got {0} and {1}".format(compared_properties, base_properties))
            return

        # default to entire properties tree
        if base_properties is None:
            base_properties = self.properties

        # check every compared category and grammeme for inclusion in the base map
        for category in compared_properties:
            # expect all compared categories to exist in the base map
            if category not in base_properties:
                return False

            # expect falsy category values to be shared by both
            if not compared_properties[category]:
                if base_properties[category]:
                    return False

            # expect iterable to turn into set of properties
            compared_grammemes = {grammeme for grammeme in compared_properties[category]}
            base_grammemes = {grammeme for grammeme in base_properties[category]}

            # expect all compared grammemes to exist in the base category
            if not compared_grammemes.issubset(base_grammemes):
                return False

        # no mismatch pitfalls - consider compared map as true subproperties
        return True
