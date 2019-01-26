class Affix:
    def __init__(self, prefix="", suffix="", category="", grammeme=""):
        self.properties = {}
        self.set(
            prefix=prefix,
            suffix=suffix,
            category=category,
            grammeme=grammeme
        )

    def get(self):
        """Read all attributes for this affix"""
        return self.properties

    def set(self, prefix="", suffix="", category="", grammeme=""):
        """Set one or more attributes for this affix"""
        self.properties = {
            'prefix': prefix if prefix else self.properties['prefix'],
            'suffix': suffix if suffix else self.properties['suffix'],
            'category': category if category else self.properties['category'],
            'grammeme': grammeme if grammeme else self.properties['grammeme']
        }
        return self.get()

    def prefix(self):
        """Read the prefix string for this affix"""
        return self.properties['prefix']

    def suffix(self):
        """Read the suffix string for this affix"""
        return self.properties['suffix']

    def circumfix(self):
        """Read the prefix and suffix strings for this affix"""
        return (self.properties['prefix'], self.properties['suffix'])

    def grammeme(self):
        """Read the grammatical feature value for this affix"""
        return self.properties['grammeme']

    def category(self):
        """Read the grammatical feature category for this affix"""
        return self.properties['category']

    def grammar(self):
        """Read the grammatical feature category and value for this affix"""
        return (self.properties['category'], self.properties['grammeme'])
