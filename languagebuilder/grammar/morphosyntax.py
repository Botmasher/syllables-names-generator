# order word and sentence elements relative to each other
class Morphosyntax:
    def __init__(self, grammar):
        # used to read and verify that ordered exponents exist
        self.grammar = grammar
        
        # relative exponent ordering word or phrase units
        self.exponent_order = {}
        
        # fixed left-to-right order of elements within a unit]
        #   - unit can be ordered by a mix of word classes and properties
        #   - built to be used within a named fixed sentence order
        #
        # structure of unit:sequence pairs:
        # {
        #   'unit_name': [
        #       {'property_1', 'property_2'...},    # possible properties in this piece
        #       {'word_class_1},                    # word class in this piece
        #       ...
        #   ]
        # }
        self.units = {}

        # fixed left-to-right order of units in various types of sentences
        #   - each discrete part is a unit or a word classes
        #   - see arrange method for the reordering process
        #
        # structure of sentence:sequence pairs:
        # {
        #   'sentence_name': [
        #       {'unit_name', 'word_class', ...},   # options
        #       {'unit_name_2'},
        #       {'word_class_2', word_class_3}
        #   ]
        # }
        self.sentences = {}

    # TODO: conditional ordering
    #   - example [first_ending, [another, only_if_another] || [this_one], ...]

    # TODO: assuming exponents are included, subarrange exponent units
    #   - have exponents gravitate to nearest applicable base (how to know? word classes?)
    #   - subarrange exponents around that base
    
    # TODO: support varying syntax and flexible word order
    #   - "interrogative" vs "declarative" syntax in EN
    #   - word order in nonconfig langs

    def get_unit(self, unit_name):
        """Read unit pieces sequence for one named unit"""
        return self.units.get(unit_name)

    def check_unit_piece(self, piece):
        """Check whether a unit piece is a property or a word class"""
        # unit piece is a property two-member list [category,grammeme]
        if isinstance(piece, (tuple, list)):
            # category, grammeme found in grammar properties
            if self.grammar.properties.get(piece[0], {}).get(piece[1]):
                return "properties"
            # unfound property
            return
        # unit piece is a single-entry map {category:grammeme}
        elif isinstance(piece, dict) and len(piece.keys()) == 1:
            # category:grammeme pair found in grammar properties
            category = list(piece.keys())[0]
            grammeme = piece[category]
            if self.grammar.properties.get(category, {}).get(grammeme):
                return "properties"
            # unfound property
            return
        # unit piece is a word class name
        elif piece in self.grammar.word_classes:
            return "word_classes"
        # unrecognized unit piece
        else:
            return

    def add_unit(self, unit_name, unit_sequence, overwrite=False):
        """Store a new fixed order for a unit (sequence of properties or word classes)"""
        # avoid updating an existing unit
        if not overwrite and unit_name in self.units:
            print("Morphosyntax failed to add new unit order - unit name already exists {}".format(unit_name))
            return

        # store left-to-right sequence of unit pieces
        # each piece many contain properties, word classes, exponents
        filtered_unit = []

        # go through unit linearly veting and assigning options for each spot
        for unit_piece in unit_sequence:
            # build set of options for current position in the unit
            unit_piece_options = set()
            # add a single property, word class or exponent at this spot
            if isinstance(unit_piece, str) and self.check_unit_piece(unit_piece):
                unit_piece_options.add(unit_piece)
            # add recognized properties, word classes or exponents to this spot
            elif isinstance(unit_piece, (tuple, set, list)):
                [unit_piece_options.add(piece) for piece in unit_piece if self.check_unit_piece(piece)]
            # unrecognized unit info in the current piece
            else:
                continue
            # build up sequence of properties, word classes, exponents
            filtered_unit.append(unit_piece_options)
        
        # add the named unit sequence to the units map
        self.units[unit_name] = filtered_unit

        return self.units[unit_name]

    def update_unit(self, unit_name, unit_sequence):
        """Update an order for a named unit sequence"""
        if unit_name not in self.units:
            print("Morphosyntax failed to update unrecognized unit name {}".format(unit_name))
            return
        return self.add_unit(unit_name, unit_sequence, overwrite=True)

    def remove_unit(self, unit_name):
        """Delete and return one unit sequence from the unit order map"""
        # check for unit existence
        if not self.get_unit(unit_name):
            return
        # remove and return the named unit
        removed_unit = self.units.pop(unit_name)
        return removed_unit
    
    def get_sentence(self, sentence_name):
        """Read one named sentence sequence"""
        return self.sentences.get(sentence_name)

    def add_sentence(self, sentence_name, sentence_sequence, overwrite=False, all_or_none=False):
        """Add a named sentence type with a sequence of units in the sentence"""
        # check for existing sentence type name and sequence of units
        if (overwrite or sentence_name in self.sentences) or not isinstance(sentence_sequence, (list, tuple)):
            print("Failed to add sentence to morphosyntax - expected valid sentence name and sequence")
            return
        
        # collect only known units
        filtered_units = [
            unit for unit in sentence_sequence
            if unit in self.units
        ]

        # back out if any non-units given
        if all_or_none and len(filtered_units) != len(sentence_sequence):
            return

        # add units sequence to sentences
        self.sentences[sentence_name] = filtered_units

        return self.sentences[sentence_name]

    def update_sentence(self, sentence_name, sentence_sequence, all_or_none=False):
        """Modify the unit sequence of a single named sentence type"""
        # check that the sentence type already exists
        if not self.get_sentence(sentence_name):
            return
        # run sentence add with overwrite
        return self.add_sentence(sentence_name, sentence_sequence, overwrite=True)
    
    def remove_sentence(self, sentence_name):
        """Delete and return one existing sentence sequence from the sentence order map, or None if not sentence found"""
        # check for existence of sentence
        if not self.get_sentence(sentence_name):
            return
        # remove and return the sentence sequence
        removed_sentence = self.sentences.pop(sentence_name)
        return removed_sentence


    ## Relative Exponent ordering

    # TODO: ordering of non-positional exponents for example multiple apophonies

    # relative inner OR outer exponents add method for one exponent
    def make_relative_exponents_set(self, exponent_id, exponents_collection, inner_outer_key):
        """Add to and return a copy of a relative exponents pre or post set"""
        return self.exponent_order.get(
            exponent_id, {}
        ).get(
            inner_outer_key, set()
        ) | {
            exponent for exponent in exponents_collection
            if self.grammar.exponents.get(exponent)
        }

    # abstracted relative order-key collection add method for one axis item
    def make_relative_set(self, ordering_map, order_id, added_collection, order_item_key):
        """Add to and return a copy of a relative  set"""
        return ordering_map.get(
            order_id, {}
        ).get(
            order_item_key, set()
        ) | {
            item for item in added_collection
            if ordering_map.get(item)
        }
    
    def add_exponent_order(self, exponent_id, inner=None, outer=None):
        """Store the position of other exponents compared to an exponent
        Take exponent id the other exponents will be relative to, then
        pass collections of exponent ids occuring closer to the base (inner)
        or away from it (outer) compared to the given exponent
        """
        # back out if no main exponent or relatives
        if not self.grammar.exponents.get(exponent_id) or not (inner or outer):
            print("Grammar morphosyntax expected one existing exponent and at least one pre or post collection")
            return
        
        # initialize positional exponent collections
        # read: from args
        requested_exponents = {
            'inner': inner,
            'outer': outer
        }
        # write: vet and collect
        filtered_exponents = {}

        # filter requested exponents allowing for single string or collection input
        # store recognized ones and their position compared to the main exponent
        for position, exponents in requested_exponents.items():
            # exponents collection is a single string - create a one-item set
            if isinstance(exponents, str) and self.grammar.exponents.get(exponents):
                filtered_exponents[position] = {exponents}
            # create set from requested exponents collection
            elif isinstance(exponents, (list, tuple, set)):
                filtered_exponents[position] = {
                    exponent for exponent in exponents
                    if self.grammar.exponents.get(exponent)
                }
            # empty set if unrecognized exponent args for this position
            else:
                filtered_exponents[position] = set()

        # merge new relative exponents into stored exponent orders
        for position, added_exponents in filtered_exponents.items():
            # get current exponents at this position (inner/outer)
            existing_exponents = self.exponent_order.setdefault(exponent_id, {})
            position_exponents = existing_exponents.get(position, set())
            
            # get exponents set for the complementary position
            opposite_position = "inner" if position == "outer" else "outer"
            opposite_position_exponents = existing_exponents.get(opposite_position, set())

            # unite new exponent collection with existing set
            updated_exponents = added_exponents | position_exponents
            # store updated relative positional exponent collection
            self.exponent_order[exponent_id][position] = updated_exponents
            self.exponent_order[exponent_id][opposite_position] = opposite_position_exponents

            print("this exponent is ", existing_exponents)
            print("the relative adds are ", added_exponents)

            # TODO: optimize searching and updating relative entries
            # reverse update relative entries with correct position of main exponent
            for added_exponent in added_exponents:
                # remove relative from the added exponent's opposite position
                # example: if adding "pre" inner relative to exponent, delete it from outer
                self.exponent_order[exponent_id][opposite_position].discard(added_exponent)
                
                # get the relative exponent inner and outer sets
                added_exponent_details = self.exponent_order.setdefault(added_exponent, {})
                
                # add main exponent to the opposite position in its relative
                # (if they are inner or outer, add main outer/inner)
                # example: -affix1-affix2 with affix2 relative inner affix1 should add affix1 to the set in the 'pre' key of affix2
                added_exponent_details.setdefault(opposite_position, set()).add(exponent_id) 
                # self.exponent_order                         \
                #     .setdefault(added_exponent, {})         \
                #     .setdefault(opposite_position, set())   \
                #     .add(exponent_id)

                # delete main from the non-opposite position in its relative
                # (if main in relative's inner/outer and they're outer/inner, remove main)
                # example: -affix1-affix2 with affix2 relative post affix1 should not store affix1 in the 'post' key of affix2
                added_exponent_details.setdefault(position, set()).discard(exponent_id)
                # self.exponent_order                         \
                #     .setdefault(added_exponent, {})         \
                #     .setdefault(position, set())            \
                #     .discard(exponent_id)

        # TODO: ? enforce individual relatives must be either inner xor outer compared to main

        return self.exponent_order.get(exponent_id)


    ## Use stored morphosyntax to arrange words in a given unit or sentence
    
    # TODO: rewrite it as taking a contiguous list (pre-exponents or post-exponents)
    #   - stick exponents on the end if they're "inner"/nearer-to-base than the main
    #   - otherwise back until finding one they're "outer" compared to the main
    #   - intended to keep exponents ordered vs each other, not to completely reorder all exponents
    # 
    # NOTE: what about circumfixes? They are more or less inner, but pre/post?
    def arrange_exponents(self, exponent_ids, filter_ordered_only=False):
        """Take a list of exponents to surround a base, then return a reordered
        list after applying relative exponent ordering. Exponents that were
        not added to the relative exponents map are not returned within the
        reordered sequence. Breaks in relative exponent chain may result in
        unpredictable order of single exponents or groups of ordered exponents.
        """

        # filter down to a collection of only explicitly ordered exponents
        if filter_ordered_only:
            filtered_exponents = list(filter(
                lambda x: x in self.exponent_order,
                exponent_ids
            ))
        # collect any known exponent
        else:
            filtered_exponents = list(filter(
                lambda x: self.grammar.exponents.get(x),
                exponent_ids
            ))

        # back out if no filtered exponents found
        if not filtered_exponents:
            #print("Morphosyntax failed to arrange exponents - no valid exponent ids given")
            return []

        # initialize sorted list of exponents with the first exponent to compare
        ordered_exponents = [filtered_exponents[0]]

        # compare and sort recognized exponents by inner/outerness
        # with inner terms closer to the base and outer further from it
        # 
        # NOTE: orders 'pre' and 'post' exponents, including circumfixes
        #   - 'pre' appear earlier in list when they're less "inner" (more "pre") than another
        #   - 'post' appear earlier in list when they're more "inner" (less "post") than another
        for exponent_id in filtered_exponents[1:]:
            # get reference to this exponent's details
            current_exponent = self.grammar.exponents.get(exponent_id)

            # whether or not an already-sorted exponent follows this one
            before_found = False

            # go through and see if exponent fits earlier than anywhere in list
            for i in range(len(filtered_exponents)):
                # the compared exponent details
                compared_exponent = self.grammar.exponents.get(filtered_exponents[i])

                print("comparing exponent ", current_exponent, " to ", compared_exponent)
                
                # check if this exponent fits earlier than current list element
                # compare "pre" for catching outer (earlier) pre and circum elements first
                if current_exponent['pre'] and compared_exponent['pre']:
                    if filtered_exponents[i] in self.exponent_order.get(exponent_id, {}).get('outer', []):
                        before_found = True
                # compare "post" for catching inner (earlier) post elements
                elif current_exponent['post'] and compared_exponent['post']:
                    if filtered_exponents[i] in self.exponent_order.get(exponent_id, {}).get('inner', []):
                        before_found = True
                
                # insert exponent into the list before its later compared exponent
                if before_found:
                    ordered_exponents = ordered_exponents[:i] + [exponent_id] + ordered_exponents[i:]
                    break

            # no exponents sort after this one - add it to the end
            if not before_found:
                ordered_exponents.append(exponent_id)

        # send back the sorted exponents list
        return ordered_exponents

    # TODO: rework Syntax side to manage sentences and sentence units well
    #
    def arrange_sentence(self, sentence, sentence_tags, sentence_type):
        """Take a collection of sentence items and return a reordered copy
        reordering units using on the named sentence type."""

        # check if sentence type exists in collection
        if sentence_type not in self.sentences:
            print(f"Morphosyntax failed to arrange unidentified sentence type {sentence_type}")
            return
        # expect all sentence elements to be tagged 
        if len(sentence) != len(sentence_tags):
            print(f"Morphosyntax failed to arrange sentence - tokens and tags counts do not match")
            return

        # TODO: arrange sentence units and each individual unit
        #   - expect one-to-one mapping of sentence elements and tags
        #   - expect tags to be properties or word classes (per-unit info)
        #   - expect groups of units
        #   - linearly identify which raw pieces belong to which units
        #   - assume properties in multiple units are nearer to their units

        # set up a sequence for catching all unit pieces in order
        sentence_units = [
            {
                'unit_piece': unit_piece,
                # data for elements from the passed-in sentence
                'token': None,
                'tag': None
            }
            for unit in self.sentences[sentence_type]
            for unit_piece in self.units[unit]
        ]

        # which indexes have already settled in order
        used_indexes = set()

        # fill in units
        for unit_piece in sentence_units:
            # find the next unused element fiting into this piece of this unit
            for i in range(len(sentence_tags)):
                if sentence_tags[i] in unit_piece and i not in used_indexes:
                    # remember the token/tag as used
                    used_indexes.add(i)
                    # store info for the token/tag
                    sentence_units[unit_piece]['token'] = sentence[i]
                    sentence_units[unit_piece]['tag'] = sentence_tags[i]
                    break
            continue
        
        # use the settled tokens to collect reordered sentence elements
        ordered_sentence = [sentence_units[unit]['token'] for unit in sentence_units]

        return ordered_sentence
