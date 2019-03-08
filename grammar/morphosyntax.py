from collections import defaultdict

# order word and sentence elements relative to each other
class Morphosyntax:
    def __init__(self, grammar):
        # used to read and verify that ordered exponents exist
        self.grammar = grammar
        
        # relative "internal" exponent ordering word or phrase units
        self.exponent_order = defaultdict(lambda: {
            'pre': set(),
            'post': set()
        })
        
        # relative "external" part of speech ordering for multi-unit phrases or sentences
        self.word_class_order = {}

        # fixed left-to-right order of word classes and exponents in various types of sentences
        self.sentence_order = {}

    # TODO: conditional ordering
    #   - example [first_ending, [another, only_if_another] || [this_one], ...]

    # TODO: assuming exponents are included, subarrange exponent units
    #   - have exponents gravitate to nearest applicable base (how to know? word classes?)
    #   - subarrange exponents around that base
    
    # TODO: support varying syntax and flexible word order
    #   - "interrogative" vs "declarative" syntax in EN
    #   - word order in nonconfig langs

    def make_relative_exponents_set(self, exponent_id, exponents_collection, pre_post_key):
        """Add to and return a copy of a relative exponents pre or post set"""
        return self.exponent_order.get(
            exponent_id, {}
        ).get(
            pre_post_key, set()
        ) | {
            exponent for exponent in exponents_collection
            if self.grammar.exponents.get(exponent)
        }

    def add_relative_exponent_order(self, exponent_id, pre=None, post=None):
        """Store the position of other exponents before or after an exponent
        Take axis exponent id the other exponents will be relative to, then
        pass collections of exponent ids occuring before (pre) or after (post)
        the axis exponent
        """
        # back out if axis or relatives
        if not self.grammar.exponents.get(exponent_id) or not (pre or post):
            print("Grammar morphosyntax expected one existing exponent and at least one pre or post collection")
            return
        
        # initialize positional exponent collections
        # read: from args
        requested_exponents = {
            'pre': pre,
            'post': post
        }
        # write: vet and collect
        filtered_exponents = {}

        # filter requested exponents allowing for single string or collection input
        # store recognized ones and their position around the axis exponent
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
            existing_exponents = self.exponent_order.get(exponent_id, {}).get(position, set())
            # unite new exponent collection with existing set
            updated_exponents = added_exponents | existing_exponents
            # store updated relative positional exponent collection
            self.exponent_order.setdefault(exponent_id, {})[position] = updated_exponents

            # TODO: optimize searching and updating relative entries
            # reverse update relative entries with correct position of axis
            opposite_position = "pre" if position == "post" else "post"
            for added_exponent in added_exponents:
                # relative exponent pre and post sets
                added_exponent_details = self.exponent_order[added_exponent]
                # add axis exponent to the opposite position in its relative
                # (if they are pre or post, add axis to their post or pre)
                # example: -affix1-affix2 with affix2 relative post affix1 should add affix1 to the set in the 'pre' key of affix2
                added_exponent_details[opposite_position].add(exponent_id) 
                # self.exponent_order                         \
                #     .setdefault(added_exponent, {})         \
                #     .setdefault(opposite_position, set())   \
                #     .add(exponent_id)

                # delete axis from the non-opposite position in its relative
                # (if axis is in relative's pre/post and they're post/pre, remove axis)
                # example: -affix1-affix2 with affix2 relative post affix1 should not store affix1 in the 'post' key of affix2
                added_exponent_details[position].discard(exponent_id)
                # self.exponent_order                         \
                #     .setdefault(added_exponent, {})         \
                #     .setdefault(position, set())            \
                #     .discard(exponent_id)
        
        # TODO: ? enforce individual relatives must be either pre xor post axis

        return self.exponent_order.get(exponent_id)

    # TODO: ability to pass in a sequence for a type of sentence
    def add_sentence_type_sequence(self, sentence_sequence):
        """Add a word (pos and exponent) order sequence to the sentence types"""
        return

    def add_relative_word_class_order(self, word_class, pre=None, post=None):
        """Store the position of other word classes before or after a word class"""
        return

    # TODO: use stored data to reorder passed-in lists of word classes

    def arrange_word_classes(self, word_classes):
        """Take a collection of word classes and return a reordered copy applying relative word class ordering"""
        return

    def arrange_exponents(self, exponent_ids):
        """Take a list of exponents and return a reordered copy applying relative exponent ordering"""
        return

    def arrange_sentence(self, sentence, sentence_tags, sentence_type):
        """Take a collection of sentence items and return a reordered copy applying sentence type ordering"""
        # sentence type exists in collection
        assert sentence_type in self.sentence_order
        # one pos/exponent tag per token
        assert len(sentence) == len(sentence_tags)
        return
