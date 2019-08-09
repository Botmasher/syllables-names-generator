from collections import deque

def tuplify(l):
    """Convert deep lists into deep tuples"""
    if not isinstance(l, (list, set, tuple, deque)):
        return l
    t = tuple(tuplify(sub_l) for sub_l in l)
    return t

def untuplify(t):
    """Revert deep tuples back to deep lists"""
    if not isinstance(t, (tuple)):
        return t
    l = [untuplify(sub_t) for sub_t in t]
    return l

def flatten(l, depth=None):
    """"Take a nested sequence and return a flattened list with no subcollections"""
    # reached individual list item or recursion depth
    if not isinstance(l, (list, set, tuple, deque)):
        return [l]

    # optionally break at specific recursion depth
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
