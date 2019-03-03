from functional_maps import merge_maps

# TODO: simplify to focus around set instead of hashmap

class WordClasses:
    def __init__(self):
        self.word_classes = {}

    def add(self, word_class, description=None):
        """Add one word class or part of speech"""
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

    def add_many(self, word_classes):
        """Add multiple parts of speech"""
        # check for a collection of word classes
        if not isinstance (word_classes, (list, tuple, set)):
            print("Grammar add_word_classes failed - expected collection not {}".format(word_classes))
            return
        # comprehensively create parts of speech and return successful entries
        results = [self.add(word_class) for word_class in word_classes]
        added_word_classes = list(filter(lambda x: x, results))
        return added_word_classes

    def update(self, word_class, name=None, description=None):
        """Modify the details of a single word class"""
        if word_class not in self.word_classes:
            print("Grammar update_word_class failed - unknown word class {0}".format(word_class))
            return
        # create new word class entry updating only changed details
        word_class_details = merge_maps(self.word_classes[word_class], {
            'name': name,
            'description': description
        }, value_check=lambda x: type(x) is str)
        
        # rename the word class by removing the old entry and adding a new one
        if name != word_class:
            self.remove(word_class)
            self.word_classes[name] = word_class_details
            # return the renamed word class details
            return self.word_classes[name]
        
        # replace the details for an existing entry
        else:
            self.word_classes[word_class] = word_class_details
            # read the modified part of speech
            return self.word_classes[word_class]

    def remove(self, word_class):
        """Delete one word class from word classes map and exponents that reference it"""
        if word_class not in self.word_classes:
            print("Grammar remove_word_class failed - unrecognized word class {0}".format(word_class))
            return
        # delete part of speech from the word classes map
        removed_word_class = self.word_classes[word_class]
        self.word_classes.pop(word_class)

        # TODO: handle decoupling properties from word classes
        # remove part of speech from all property grammeme entries that reference it
        # /!\
        # for category in self.properties:
        #     for grammeme, grammeme_details in self.properties[category].items():
        #         if word_class in grammeme_details['exclude']:
        #             self.properties[category][grammeme]['exclude'].remove(word_class)
        #         if word_class in grammeme_details['include']:
        #             self.exponents[category][grammeme]['include'].remove(word_class)
        # /!\

        # return deleted details
        return removed_word_class

    def filter(self, word_classes):
        """Create a set of valid word classes from a single string or collection of strings"""
        # no word classes or empty collection passed
        if not word_classes:
            return set()
        # wrap a single string in a list for filtering set
        if isinstance(word_classes, str):
            word_classes = [word_classes]
        # create recognized set of word classes from collection
        return set(filter(lambda x: x in self.word_classes, word_classes))