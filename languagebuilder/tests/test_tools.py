import unittest

from ..tools import flat_list, string_list

def setUpModule():
    print("Setting up the Tools test module")

def tearDownModule():
    print("Shutting down the Tools test module")

class FlatList(unittest.TestCase):
    def test_flatten_deep(self):
        a = [[[1], [2], [3]], [[4], [5], [6]]]
        self.assertEqual(
            flat_list.flatten(a),
            [1, 2, 3, 4, 5, 6],
            "Failed to flatten nested lists to a one-layer list"
        )

    def test_flatten_depth_1(self):
        a = [[[1], [2], [3]], [[4], [5], [6]]]
        self.assertEqual(
            flat_list.flatten(a, 1),
            [[1], [2], [3], [4], [5], [6]],
            "Failed to stop flattening a list after one flatten"
        )

    def test_flatten_depth_0(self):
        a = [[[1], [2], [3]], [[4], [5], [6]]]
        self.assertEqual(
            flat_list.flatten(a, 0),
            [[[1], [2], [3]], [[4], [5], [6]]],
            "Failed to stop flattening a list immediately"
        )

    def test_flatten_leaving_inner_tuples(self):
        # NOTE: used in languagebuilder to store (headword, headword_index) lookups
        a = [
            [('a', 1), ('a', 2)],
            [('b', 1)],
            [('c', 1), ('c', 2), ('c', 3)]
        ]
        self.assertEqual(
            flat_list.flatten(a, 1),
            [('a', 1), ('a', 2), ('b', 1), ('c', 1), ('c', 2), ('c', 3)],
            "Failed to flatten up to inner string, index tuples"
        )

    # NOTE: Tuplify/Tuplify removed
    #
    # def test_tuplify(self):
    #     a = [[[1], [2], [3]], [[4], [5], [6]], 7]
    #     self.assertEqual(
    #         flat_list.tuplify(a),
    #         (((1), (2), (3)), ((4), (5), (6)), 7)
    #     )
    #
    # def test_untuplify(self):
    #     a =  (((1), (2), (3)), ((4), (5), (6)), 7)
    #     self.assertEqual(
    #         flat_list.untuplify(a),
    #          [[[1], [2], [3]], [[4], [5], [6]], 7]
    #     )

    def test_flat_map(self):
        a =  [[[1], [2], [3]], [[4], [5], [6]], 7, [8]]
        self.assertEqual(
            flat_list.flat_map(lambda n: n * 2, a),
             [2, 4, 6, 8, 10, 12, 14, 16]
        )

    def test_flat_filter(self):
        a =  [[[1], [2], [3]], [[4], [5], [6]], 7, [8]]
        self.assertEqual(
            flat_list.flat_filter(lambda n: n % 2, a),
            [1, 3, 5, 7]
        )

class StringList(unittest.TestCase):
    def test_string_listify_string(self):
        s = "string"
        self.assertEqual(
            string_list.string_listify(s),
            ["string"],
            "Failed to turn string into list"
        )
    
    def test_string_listify_segments(self):
        s = "string"
        self.assertEqual(
            string_list.string_listify(s, True),
            ["s", "t", "r", "i", "n", "g"],
            "Failed to turn string into list of characters"
        )

    def test_string_listify_string_list(self):
        l = ["a string", "another string", "third string"]
        self.assertEqual(
            string_list.string_listify(l),
            ["a string", "another string", "third string"],
            "Failed to treat string list as a list of strings"
        )
