class Syllable:
    def __init__(self, structure):
        self.structure = structure

    def get_structure(self):
        """Read the syllable structure"""
        return self.structure

    def update(self, structure):
        """Update the syllable structure"""
        if isinstance(structure, list):
            self.structure = structure
        return self.structure
