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

def flatten(l, depth=None, map_expression=None, filter_expression=None):
    """"Take a nested sequence and return a flattened list with no subcollections.
    Supports mapping or filtering elements before they get added to the final flatlist."""
    # reached individual list item or recursion depth
    if is_primitive(l):
        filter_e = [] if filter_expression and not filter_expression(l) else l
        terminal_e = [
            map_expression(filter_e)
        ] if map_expression and filter_e != [] else [filter_e]
        return terminal_e

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

def is_primitive(l):
    """Check if the value is considered a flatlist primitive"""
    return not isinstance(l, (list, set, tuple, deque))

def flat_map(expression, l):
    """Flatten and run expression on all elements in all sublists"""
    return flatten(l, map_expression=expression)

def flat_filter(expression, l):
    """Flatten and filter all elements in all sublists"""
    return flatten(l, filter_expression=expression)
