# Method group A: Functional map building and layering

# TODO: abstract out and avoid idiosyncratic applications of merge_maps
# functional dict building to avoid direct mutations in word class, property and exponent update methods

def merge_maps(base_map, overlay_map, key_check=lambda x: x, value_check=lambda x: x):
    """Overlay map pairs with filtered keys and values onto a base map and return the new map"""
    # expect both an old "base" and a new "overlay" dict
    if not(isinstance(base_map, dict) and isinstance(overlay_map, dict)):
        print("Grammar merge_maps failed - invalid base map or overlay map")
        return
    # expect a valid filter function to validate overlayed keys and values
    if type(key_check).__name__ != 'function' or type(value_check).__name__ != 'function':
        print("Grammar merge_maps failed - invalid checker functions")
        return
    # unpack old and new maps vetting the new one using key and value filters
    new_map = {
        **base_map,
        **{k: v for k, v in overlay_map.items() if key_check(k) and value_check(v)}
    }
    return new_map

# NOTE: idiosyncratic implementation for comparing structures in the Grammar
#   - stored properties nests dicts down to leaf detail entries
#   - requested properties associates its top-level keys with sets of strings
#   - each string in a requested properties set represents nested keys in stored properties
#   - requested properties are passed in by caller as well as stored by exponents
def intersect_maps(base_map, overlay_map):
    """Deeply evaluate shared pairs within two maps and return a map copy of their intersections.
    Intersections are shared keys, shared leaf values and shared values within collections
    returned as intersected sets."""
    # recursively branch through map along shared keys
    if isinstance(base_map, dict) and isinstance(overlay_map, dict):
        # intersection representing shared keys
        common_keys = base_map.keys() & overlay_map.keys()
        # check the values under those keys
        return {
            k: intersect_maps(base_map[k], overlay_map[k])
            for k in common_keys
        }
    # both are flat containers - test for shared values
    elif isinstance(base_map, (list, set, tuple)) and isinstance(overlay_map, (list, set, tuple)):
        # intersect the two containers
        common_values = set(base_map) & set(overlay_map)
        return common_values
    # expect non-collection values to match
    elif base_map == overlay_map:
        return base_map
    # no shared material found under this key
    else:
        return {}