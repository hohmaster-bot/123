"""Game-rule constants as DATA (package 20, D23, review 4 F15): wp/rules_data/constants.json.

Every game-rule number lives in the table (id, value, type, group, unit, description, label). A character may override
any of them: Character.rules_settings.constants {id: value} (set_rule_setting / reset_rule_setting, the settings schema
of package 19). Defaults = the values the code had before, so no game result changes.

The code reads a constant ONLY through this module:
- const(cid, ch=None): the value for a character (its override, else the table). Without ch: the current scope.
- ref(cid): a lazy reference kept at module level (NAME = rules.ref("training.ability_step")); every use (arithmetic,
  comparison, indexing, int()) reads the value of the CURRENT scope at that moment.
- using(ch): the scope of one character. dispatch() runs every command inside using(ch); a UI that reads views of a
  character outside a command wraps the reads in `with rules.using(ch):` (otherwise the table defaults are used).
Package 37 (owner decision 1): every numeric constant is also an effect target const:<id>: a source adds to it or
replaces it (Effect note "replace"). The model layer installs EFFECTS = fn(ch) -> {id: ("add" | "replace", number)}
(wp/model/const_effects.py); const() applies it to the character's value (the override or the table value).
"""
import contextlib
import contextvars
import io
import json
import os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "constants.json")
_SCOPE = contextvars.ContextVar("wp_rule_constants", default=None)
_SCOPE_CH = contextvars.ContextVar("wp_rule_character", default=None)
EFFECTS = None                         # fn(ch) -> {id: (mode, number)}: the const:<id> effects (package 37)
PREFIX = "const:"


def _load(path=PATH):
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    table = {}
    for c in d["constants"]:
        if c["id"] in table:
            raise ValueError("duplicate rule constant %r" % c["id"])
        table[c["id"]] = dict(c)
    return table, d.get("allowlist", {})


TABLE, ALLOWLIST = _load()


def _plain(v):
    if isinstance(v, list):
        return tuple(_plain(x) for x in v)
    if isinstance(v, dict):
        return {k: _plain(x) for k, x in v.items()}
    return v


DEFAULTS = {cid: _plain(c["value"]) for cid, c in TABLE.items()}


def default(cid):
    return DEFAULTS[cid]


def overrides_of(ch):
    rs = getattr(ch, "rules_settings", None)
    return getattr(rs, "constants", None) or {}


def stored(cid, ch=None):
    """The character's value without the const:<id> effects (its override, else the table)."""
    if cid not in DEFAULTS:
        raise KeyError("no rule constant %r" % (cid,))
    over = overrides_of(ch) if ch is not None else (_SCOPE.get() or {})
    return _plain(over[cid]) if cid in over else DEFAULTS[cid]


def numeric(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def const(cid, ch=None):
    v = stored(cid, ch)
    who = ch if ch is not None else _SCOPE_CH.get()
    if EFFECTS is None or who is None or not numeric(v):
        return v
    change = EFFECTS(who).get(cid)
    if change is None:
        return v
    mode, n = change
    return type(v)(n) if mode == "replace" else type(v)(v + n)


@contextlib.contextmanager
def using(ch):
    token = _SCOPE.set(dict(overrides_of(ch)))
    token_ch = _SCOPE_CH.set(ch)
    try:
        yield
    finally:
        _SCOPE_CH.reset(token_ch)
        _SCOPE.reset(token)


def numeric_ids():
    """The ids of the numeric constants: every one is an effect target const:<id> (package 37)."""
    return tuple(cid for cid, v in DEFAULTS.items() if numeric(v))


def _v(x):
    return x.value if isinstance(x, Ref) else x


class Ref(object):
    """A lazy rule constant: behaves like its current value (number, tuple or mapping) in every expression."""
    __slots__ = ("cid",)

    def __init__(self, cid):
        if cid not in DEFAULTS:
            raise KeyError("no rule constant %r" % (cid,))
        self.cid = cid

    @property
    def value(self):
        return const(self.cid)

    def __repr__(self):
        return "Ref(%r=%r)" % (self.cid, self.value)

    # numbers
    def __int__(self): return int(self.value)
    def __float__(self): return float(self.value)
    def __index__(self): return int(self.value)
    def __bool__(self): return bool(self.value)
    def __neg__(self): return -self.value
    def __pos__(self): return +self.value
    def __abs__(self): return abs(self.value)
    def __add__(self, o): return self.value + _v(o)
    def __radd__(self, o): return _v(o) + self.value
    def __sub__(self, o): return self.value - _v(o)
    def __rsub__(self, o): return _v(o) - self.value
    def __mul__(self, o): return self.value * _v(o)
    def __rmul__(self, o): return _v(o) * self.value
    def __truediv__(self, o): return self.value / _v(o)
    def __rtruediv__(self, o): return _v(o) / self.value
    def __floordiv__(self, o): return self.value // _v(o)
    def __rfloordiv__(self, o): return _v(o) // self.value
    def __mod__(self, o): return self.value % _v(o)
    def __rmod__(self, o): return _v(o) % self.value
    def __pow__(self, o): return self.value ** _v(o)
    def __eq__(self, o): return self.value == _v(o)
    def __ne__(self, o): return self.value != _v(o)
    def __lt__(self, o): return self.value < _v(o)
    def __le__(self, o): return self.value <= _v(o)
    def __gt__(self, o): return self.value > _v(o)
    def __ge__(self, o): return self.value >= _v(o)
    def __hash__(self): return hash(self.value)
    # sequences and mappings
    def __len__(self): return len(self.value)
    def __iter__(self): return iter(self.value)
    def __contains__(self, x): return x in self.value
    def __getitem__(self, k): return self.value[k]

    def get(self, k, d=None):
        return self.value.get(k, d)

    def items(self):
        return self.value.items()

    def keys(self):
        return self.value.keys()

    def values(self):
        return self.value.values()


def ref(cid):
    return Ref(cid)


def value(x):
    """A plain value from a Ref (or the value itself): use it before storing a constant in a record."""
    return _v(x)
