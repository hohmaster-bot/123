"""Read-only dict for the frozen sheet data (package 16 A7, review 4 F16).

FrozenDict is a dict (json, isinstance(dict), iteration and lookups work as before) that refuses every
in-place change: code that wants another value builds a new dict and a new record (commands, D5).
freeze(d) returns a FrozenDict (nested plain dicts inside are frozen too); freeze_fields(obj, names) is called
from __post_init__ of the frozen dataclasses that hold dicts.
"""


class FrozenDict(dict):
    __slots__ = ()

    def _refuse(self, *args, **kwargs):
        raise TypeError("FrozenDict cannot be changed in place: build a new one (commands only, D5)")

    __setitem__ = __delitem__ = _refuse
    clear = pop = popitem = setdefault = update = _refuse
    __ior__ = _refuse

    def __hash__(self):
        return hash(frozenset(self.items()))

    def __reduce__(self):
        return (FrozenDict, (dict(self),))

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __repr__(self):
        return "FrozenDict(%s)" % dict.__repr__(self)


def freeze(d):
    if isinstance(d, FrozenDict):
        return d
    return FrozenDict((k, freeze(v) if isinstance(v, dict) else v) for k, v in dict(d).items())


def freeze_fields(obj, names):
    """Replace the dict fields of a frozen dataclass instance by FrozenDicts (inside __post_init__)."""
    for n in names:
        v = getattr(obj, n)
        if isinstance(v, dict) and not isinstance(v, FrozenDict):
            object.__setattr__(obj, n, freeze(v))
