# store and manage word classes for a grammar
class WordClasses:
    def __init__(self):
        # set for collecting word class names
        self.word_classes = set()
    
    def get(self, word_class):
        """Read a single word class from the collection"""
        if word_class in self.word_classes:
            return word_class
        return

    def add(self, word_class):
        """Add one word class or part of speech"""
        # send collections to add_many in order to add each one
        if isinstance(word_class, (list, tuple, set)):
            return self.add_many(word_class)

        # catch repeated word classes
        if word_class in self.word_classes:
            print("WordClass.add skipped already existing word class {}".format(word_class))
            return
        
        # avoid adding non-strings
        if not isinstance(word_class, str):
            print("WordClass.add failed - expected a new string not {}".format(word_class))
            return

        # create a new entry for the part of speech
        self.word_classes.add(word_class)
        
        # read the created part of speech
        return self.word_classes

    def add_many(self, word_classes):
        """Add multiple parts of speech"""
        # check for a collection of word classes
        if not isinstance (word_classes, (list, tuple, set)):
            print("WordClass.add_many failed - expected collection not {}".format(word_classes))
            return
        # comprehensively create parts of speech and return successful entries
        results = [self.add(word_class) for word_class in word_classes]
        added_word_classes = list(filter(lambda x: x, results))
        return added_word_classes

    def rename(self, word_class, new_word_class):
        """Modify the details of a single word class"""
        if word_class not in self.word_classes:
            print("WordClass.update failed - unknown word class {0}".format(word_class))
            return
        # rename the word class by removing the old entry and adding a new one
        self.word_classes.remove(word_class)
        self.word_classes.add(new_word_class)
        # return the renamed word class details
        return self.word_classes
        
    def remove(self, word_class):
        """Delete one word class from word classes map and exponents that reference it"""
        if word_class not in self.word_classes:
            print("WordClass.remove failed - unrecognized word class {0}".format(word_class))
            return
        
        # delete part of speech from the word classes map
        self.word_classes.remove(word_class)

        # TODO: deal with exponents storing references to pos
        #   - two options: here or when exponents accessed
        #
        # remove part of speech from all exponents that reference it
        for exponent_details in self.exponents.values():
            word_class in exponent_details['pos'] and exponent_details['pos'].remove(word_class)
        
        # return deleted part of speech
        return word_class

    def filter(self, word_classes):
        """Create a set of valid word classes from a single string or collection of strings"""
        # no word classes or empty collection passed
        if not word_classes:
            return set()
        
        # wrap a single string in a set for filtering
        if isinstance(word_classes, str):
            word_classes = set(word_classes)
        
        # create set of recognized parts of speech
        return set(word_classes) & self.word_classes
