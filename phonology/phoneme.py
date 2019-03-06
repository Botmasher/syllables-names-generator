# letters to and from phonetic symbols
# TODO environments for symbol (? or save for rule)
class Phoneme:
    def __init__(self, symbol, letters=[], weight=0):
        self.letters = set(letters)
        self.symbol = symbol
        self.weight = weight

    def get(self):
        """Read the letters, features and unique symbol for this phoneme"""
        return {
            'letters': list(self.letters),
            'symbol': self.symbol,
            'weight': self.weight
        }

    def get_letters(self):
        """Read all letters associated with this phoneme"""
        return list(self.letters)

    def get_symbol(self):
        """Read the unique symbol representing this phoneme"""
        return self.symbol

    def get_weight(self):
        """Read the weight associated with this phoneme"""
        return self.weight

    def add_letter(self, letter):
        """Add a letter to the collection of graphemes for this phoneme"""
        self.letters.add(letter)
        return self.get_letters()

    def add_letters(self, letters):
        """Add multiple letters to the graphemes representing this phoneme"""
        if type(letters) is not list:
            return
        for letter in letters:
            self.add_letter(letter)
        return self.get_letters()

    def set_weight(self, weight):
        """Adjust the weight associated with this phoneme"""
        if type(weight) is int:
            self.weight = weight
        return self.weight

    def remove_letter(self, letter):
        """Remove a letter from the graphemes representing this phoneme"""
        letter in self.letters and self.letters.remove(letter)
        return self.get_letters()

    def replace_letter(self, letter, new_letter):
        """Replace one letter in the letters representing this phoneme"""
        self.remove_letter(letter)
        self.add_letter(new_letter)
        return self.get_letters()

    def replace_letters(self, letters=[]):
        """Replace the entire set of letters representing this phoneme"""
        if type(letters) is list:
            self.letters = set(letters)
        return self.get_letters()
