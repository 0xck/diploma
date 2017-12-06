import itertools


def combination_dicts(dct):
    """generator of dicts with different number combinations of keys"""

    return ({key: dct[key] for key in keys} for comb in (itertools.combinations(sorted(dct), i) for i, _ in enumerate(range(len(dct)), start=1)) for keys in comb)


def str_cutter(strg, slicer=None):
    if slicer is None:
        slicer = slice(1, None, None)

    new_str = strg[slicer]

    return new_str if new_str else strg
