import uuid

# NOTE: abstracted class storing and managing a map of typed objects
#   - built based on Rules class
#   - label (like self.types=['Rule']) for types to check on create
#   - store id:object pairs in dict
#   - maybe expect a dict per key to store subattributes

## demo for creating Rules in Language
#rules = Collector(types=['Rule'])
#rules = Collector(types=Rule, read_types_from_classes=True) # assumes Rule class

class Collector():
    def __init__(self, accepted_types=[], read_types_from_classes=False):
        self.map = {}
        # leave blank to accept any
        if read_types_from_classes and accepted_types:
            self.accepted_types = [t for t in type(accepted_types).__name__]
        else:
            self.accepted_types = accepted_types

    def is_valid(self, object):
        """Check if the object is of one of the accepted types"""
        if self.accepted_types and type(object).__name__ in self.accepted_types:
            return True
        return False

    def has(self, object_id):
        """Check if the object exists in the map"""
        if object_id in self.map:
            return True
        return False

    def get(self, object_id=None):
        """Read the value for one stored object, or all if no id passed in"""
        # fetch all for zero-arg calls
        if not object_id:
            return self.map
        # object does not exist in map
        if not self.has(object_id):
            print("Collector get failed - unknown object {0}".format(object_id))
            return
        # found object in map
        return self.map[object_id]

    def get_one(self, object_id):
        """Alias for get method """
        return self.get(object_id)

    def get_all(self):
        """Read the entire collection"""
        return self.map

    def get_items(self):
        """Read all keys and values in the collection"""
        return self.map.items()

    def get_keys(self):
        """Read all keys in the collection"""
        return self.map.keys()

    def get_values(self):
        """Read all values in the collection"""
        return self.map.values()

    def add(self, object):
        """Add one object to the map"""
        if not self.is_valid(object):
            print("Collector add failed - invalid object {0}".format(object))
            return
        object_id = uuid.uuid4()
        self.map[object_id] = object
        return object_id

    def update(self, object_id, object):
        """Modify an existing object"""
        if not self.is_valid(object):
            print("Collector update failed - unknown object {0}".format(object_id))
            return
        # TODO destructure incoming object for partial update
        self.map[object_id] = object
        return object_id

    def remove(self, rule_id):
        """Remove one object from the map"""
        if rule_id in self.rules:
            self.rules.pop(rule_id)
            return True
        return False

    def clear(self):
        """Reset the map"""
        map_cache = self.map
        def read_cache():
            return map_cache
        self.map = {}
        return read_cache
