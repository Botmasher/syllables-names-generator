# NOTE: abstracted class for storing and managing a set of typed objects
class SetCollector():
    def __init__(self, accepted_types=[]):
        self.collection = set()
        self.accepted_types = accepted_types

    def is_valid(self, value):
        """Check if the value is of one of the accepted types"""
        if not self.accepted_types or type(value).__name__ in self.accepted_types:
            return True
        return False

    def has(self, value):
        """Check if the value exists in the set"""
        return value in self.collection

    def get(self):
        """Read all values stored in the set"""
        return self.collection

    def add(self, value):
        """Add one value to the set"""
        if not self.is_valid(value):
            print("SetCollector add failed - invalid value {0}".format(value))
            return
        self.collection.add(value)
        return value

    def update(self, old_value, new_value):
        """Modify an existing value"""
        if not (self.has(old_value) and self.is_valid(new_value)):
            print("Collector update failed - unknown value")
            return
        self.collection.remove(old_value)
        self.collection.add(new_value)
        return new_value

    def remove(self, value):
        """Remove one value from the set"""
        if self.has(value):
            self.collection.remove(value)
            return True
        return False

    def clear(self):
        """Reset the set and return a cache read method"""
        set_cache = self.collection.copy()
        def read_cache():
            return set_cache
        self.collection.clear()
        return read_cache
