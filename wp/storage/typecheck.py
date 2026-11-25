"""Type check of a stored character against the dataclass annotations (package 27, review 5 F5 F9 F13, D29).

problem(value, annotation) -> None or a short text "where: what" for the first value that does not fit:
- int: an int, never a bool; float: a finite int or float (no NaN / inf); str / bool: exactly that type;
- Optional[X]: None or X; Tuple[X, ...]: a tuple of X; Tuple[A, B]: a tuple of that shape; Dict[K, V]: a dict;
- a record class: an instance of it whose every field fits; Any: anything a JSON file can hold (finite numbers).
Collections of records keep unique ids (the first field of a record when it is a str named *id: Item.iid ...).
character_problem(ch, old=None): the whole character, or only the top-level fields that changed since `old`
(dispatch checks a command result this way; the loader checks the whole file).
"""
import dataclasses
import math
import typing

_HINTS = {}
NONE_TYPE = type(None)


def hints(cls):
    if cls not in _HINTS:
        _HINTS[cls] = typing.get_type_hints(cls)
    return _HINTS[cls]


def id_field(cls):
    """The id field of a record class (its first field, a str named *id), or None."""
    fs = dataclasses.fields(cls)
    if fs and fs[0].name.endswith("id") and hints(cls)[fs[0].name] is str:
        return fs[0].name
    return None


def _plain(v, where):
    """Any: JSON-able plain data with finite numbers."""
    if v is None or isinstance(v, (bool, str, int)):
        return None
    if isinstance(v, float):
        return None if math.isfinite(v) else "%s: not a finite number" % where
    if isinstance(v, (tuple, list)):
        for i, x in enumerate(v):
            bad = _plain(x, "%s[%d]" % (where, i))
            if bad:
                return bad
        return None
    if isinstance(v, dict):
        for k, x in v.items():
            if not isinstance(k, (str, int)) or isinstance(k, bool):
                return "%s: a key that is not a text" % where
            bad = _plain(x, "%s.%s" % (where, k))
            if bad:
                return bad
        return None
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        return record_problem(v, where)
    return "%s: a value of type %s" % (where, type(v).__name__)


def problem(v, t, where="value"):
    if t is typing.Any:
        return _plain(v, where)
    if t is int:
        return None if isinstance(v, int) and not isinstance(v, bool) else "%s: not a whole number" % where
    if t is float:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return "%s: not a number" % where
        return None if isinstance(v, int) or math.isfinite(v) else "%s: not a finite number" % where
    if t is str:
        return None if isinstance(v, str) else "%s: not a text" % where
    if t is bool:
        return None if isinstance(v, bool) else "%s: not true / false" % where
    if isinstance(t, type) and dataclasses.is_dataclass(t):
        if type(v) is not t:
            return "%s: not a %s record" % (where, t.__name__)
        return record_problem(v, where)
    origin, args = typing.get_origin(t), typing.get_args(t)
    if origin is typing.Union:
        if v is None and NONE_TYPE in args:
            return None
        rest = [a for a in args if a is not NONE_TYPE]
        bads = [problem(v, a, where) for a in rest]
        return None if any(b is None for b in bads) else bads[0]
    if origin is tuple:
        if not isinstance(v, tuple):
            return "%s: not a list" % where
        if not args:
            return _plain(v, where)
        if len(args) == 2 and args[1] is Ellipsis:
            for i, x in enumerate(v):
                bad = problem(x, args[0], "%s[%d]" % (where, i))
                if bad:
                    return bad
            return _unique(v, args[0], where)
        if len(v) != len(args):
            return "%s: %d values expected" % (where, len(args))
        for i, (x, a) in enumerate(zip(v, args)):
            bad = problem(x, a, "%s[%d]" % (where, i))
            if bad:
                return bad
        return None
    if origin is dict:
        if not isinstance(v, dict):
            return "%s: not a table" % where
        kt, vt = args or (typing.Any, typing.Any)
        for k, x in v.items():
            bad = problem(k, kt, "%s key" % where) or problem(x, vt, "%s.%s" % (where, k))
            if bad:
                return bad
        return None
    return _plain(v, where)


def _unique(v, t, where):
    if not (isinstance(t, type) and dataclasses.is_dataclass(t)):
        return None
    f = id_field(t)
    if f is None:
        return None
    seen = set()
    for x in v:
        i = getattr(x, f)
        if i and i in seen:
            return "%s: the id %r twice" % (where, i)
        seen.add(i)
    return None


def record_problem(rec, where="value"):
    h = hints(type(rec))
    for f in dataclasses.fields(rec):
        bad = problem(getattr(rec, f.name), h[f.name], "%s.%s" % (where, f.name))
        if bad:
            return bad
    return None


def character_problem(ch, old=None):
    h = hints(type(ch))
    for f in dataclasses.fields(ch):
        v = getattr(ch, f.name)
        if old is not None and v is getattr(old, f.name):
            continue
        bad = problem(v, h[f.name], f.name)
        if bad:
            return bad
    return None
