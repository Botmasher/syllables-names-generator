from collections import deque

def flatten(l, depth=None):
    """"Take a nested sequence and return a flattened list with no subcollections"""
    # reached individual list item or recursion depth
    if not isinstance(l, (list, set, tuple, deque)):
        return [l]

    # 
    if isinstance(depth, int):
        if depth <= 0:
            return l
        depth -= 1

    # reached another list - flatten it
    flat_l = []
    # recurse through sublists
    for l_sub in l:
        flat_l += flatten(l_sub, depth)

    return flat_l
