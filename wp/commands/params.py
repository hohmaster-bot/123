"""Declared parameter types of the character commands (package 27 B, review 5 F4 F5 F13 F14 F20 F21, D29).

dispatch calls check() BEFORE the command runs. The kind of a parameter comes from the data table
wp/commands/data/params.json ("commands": {command: {parameter: kind}}), else from the default in the signature:
"" -> str, an int -> int, True / False -> bool, () -> list, a rule reference -> int; None without a table entry -> any.
Kinds: str, int (a whole number: a float or a bool is refused, never truncated), number (finite int or float),
bool, list (list or tuple), map (dict), any; "?" at the end allows None; "id:<set>" is a str from a known set
(abilities, damage_types, sides, hand_sides, slots, saves; *_opt also allows ""); "list:<kind>" is a list of
that kind; "record:<Class>" is a record of that class whose fields fit their types (typecheck), "record" any record;
"intstr" a whole number or a formula text.
Counts: a parameter named in "nonneg" (n, amount, extra_bp ...) must be >= 0, except the commands listed under
"signed" (add_experience amount ...). Free fields (**fields) are checked by the command and by the type check of
the result (wp/storage/typecheck.py). Refusals: wrong_type, invalid_value (NaN / inf), out_of_range, unknown_parameter,
unknown_damage_type, not_allowed (an id outside its set); params: parameter, expected, allowed.
"""
import inspect
import io
import json
import math
import os

from wp.commands.base import CommandError

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "params.json")


def _load():
    with io.open(PATH, encoding="utf-8") as f:
        return json.load(f)


TABLE = _load()
_SPECS = {}


def _sets():
    from wp.model import character as mc
    from wp.model import defense_view as dfv
    from wp.model import doll_layout as dl
    from wp.model import hands
    from wp.model.class_types import SAVES
    from wp.core import damage as dm
    return {"abilities": mc.ABILITIES, "abilities_opt": ("",) + mc.ABILITIES,
            "damage_types": (dm.PHYSICAL,) + tuple(dfv.TYPES), "sides": hands.SIDES, "sides_opt": ("",) + hands.SIDES,
            "hand_sides": hands.SIDES + (hands.BOTH,), "slots": dl.ENTRY_IDS, "saves": SAVES}


_SET_CACHE = {}


def known(name):
    if not _SET_CACHE:
        _SET_CACHE.update(_sets())
    return _SET_CACHE[name]


def _from_default(d):
    if isinstance(d, bool):
        return "bool"
    if isinstance(d, int):
        return "int"
    if isinstance(d, float):
        return "number"
    if isinstance(d, str):
        return "str"
    if isinstance(d, (tuple, list)):
        return "list"
    if d is None:
        return "any"
    return "int"                       # a rule reference (rd.ref) stands for a number


def spec(cmd, fn):
    """{parameter: kind} and whether free fields are accepted."""
    if cmd not in _SPECS:
        sig = inspect.signature(fn)
        out, free = {}, False
        table = TABLE["commands"].get(cmd, {})
        for p in list(sig.parameters.values())[1:]:
            if p.kind == p.VAR_KEYWORD:
                free = True
                continue
            out[p.name] = table.get(p.name) or _from_default(None if p.default is p.empty else p.default)
        _SPECS[cmd] = (out, free)
    return _SPECS[cmd]


def _refuse(reason, name, text, **params):
    raise CommandError("parameter %s: %s" % (name, text), reason, values=(name,), parameter=name, **params)


def check_kind(name, kind, v):
    if kind.endswith("?"):
        if v is None:
            return
        kind = kind[:-1]
    if kind == "any":
        return
    if kind == "record" or kind.startswith("record:"):
        from wp.storage import character_io as cio
        from wp.storage import typecheck
        cls = cio._TYPES.get(kind[len("record:"):]) if ":" in kind else None
        if type(v).__name__ not in cio._TYPES or (cls is not None and type(v) is not cls):
            _refuse("wrong_type", name, "a %s record is expected" % (kind[len("record:"):] or "known"), expected=kind)
        bad = typecheck.record_problem(v, name)
        if bad:
            _refuse("wrong_type", name, bad, expected=kind)
        return
    if kind.startswith("list:"):
        if not isinstance(v, (list, tuple)):
            _refuse("wrong_type", name, "a list is expected", expected="list")
        for x in v:
            check_kind(name, kind[len("list:"):], x)
        return
    if kind.startswith("id:"):
        if not isinstance(v, str):
            _refuse("wrong_type", name, "a text is expected", expected="str")
        allowed = known(kind[len("id:"):])
        if v not in allowed:
            reason = "unknown_damage_type" if kind == "id:damage_types" else "not_allowed"
            _refuse(reason, name, "%r is not one of %s" % (v, ", ".join(allowed)), allowed=tuple(allowed))
        return
    if kind == "str" and not isinstance(v, str):
        _refuse("wrong_type", name, "a text is expected", expected="str")
    if kind == "bool" and not isinstance(v, bool):
        _refuse("wrong_type", name, "true or false is expected", expected="bool")
    if kind == "int" and (isinstance(v, bool) or not isinstance(v, int)):
        _refuse("wrong_type", name, "a whole number is expected", expected="int")
    if kind == "number":
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            _refuse("wrong_type", name, "a number is expected", expected="number")
        if isinstance(v, float) and not math.isfinite(v):
            _refuse("invalid_value", name, "not a finite number")
    if kind == "list" and not isinstance(v, (list, tuple)):
        _refuse("wrong_type", name, "a list is expected", expected="list")
    if kind == "map" and not isinstance(v, dict):
        _refuse("wrong_type", name, "a table is expected", expected="map")
    if kind == "intstr" and (isinstance(v, bool) or not isinstance(v, (int, str))):
        _refuse("wrong_type", name, "a whole number or a formula is expected", expected="intstr")


def _finite_deep(name, v, depth=0):
    """No NaN / inf anywhere inside a value (review 5 F13); a nesting deeper than the table's max_depth is refused."""
    if depth > TABLE["max_depth"]:
        _refuse("invalid_value", name, "nested too deep")
    if isinstance(v, float) and not math.isfinite(v):
        _refuse("invalid_value", name, "not a finite number")
    if isinstance(v, (list, tuple)):
        for x in v:
            _finite_deep(name, x, depth + 1)
    elif isinstance(v, dict):
        for x in v.values():
            _finite_deep(name, x, depth + 1)


def check(cmd, fn, params, ch=None):
    kinds, free = spec(cmd, fn)
    nonneg = set(TABLE["nonneg"]) - set(TABLE["signed"].get(cmd, ()))
    for name, v in params.items():
        _finite_deep(name, v)
        if name not in kinds:
            if free:
                continue
            _refuse("unknown_parameter", name, "%s has no such parameter" % cmd, allowed=tuple(kinds))
        check_kind(name, kinds[name], v)
        if name in nonneg and isinstance(v, (int, float)) and not isinstance(v, bool) and v < 0:
            _refuse("out_of_range", name, "must be >= 0", min=0, max=None)
