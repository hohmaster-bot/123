"""Formula variables and effect conditions read from the REAL derived numbers (package 36, owner decisions 7, 12, 13).

Context(ch, base): the dict effects resolve against (Effect.resolve). Besides the base values (level, bab, overload,
the stat modifiers given by the caller) it computes on first use:
- the sheet numbers of formula.SHEET_VARIABLES (hp_max, mana_max, base_slots, pain, morale, balance_max, spirit_max,
  bp_max, comfort_max) and tagged_base_slots:<tag> (the base slots of the items with that tag lying at the base:
  trophies of 2 + 3 + 2 slots = 7);
- the stat modifiers when the caller left them lazy (stat_mod:<s> / <s>_mod);
- the conditions "cond:<id>" (decision 7): hp_full, bp_full, in_combat, pressure_eq:N, pressure_ge:N, pressure_le:N,
  pain_ge:N, charges_left:<kind>:<id>, status_tag:<tag> (automatic) and manual:<text> (a checkbox:
  Character.manual_conditions).
Cycles are NOT blocked (decision 12): a value that is being computed reads 0 while it is computed again (one pass, no
infinite loop); cycles(ch) finds the effect targets on a cycle so the Sources dialog can warn "cycle in formulas".
"""
from wp.core import effects as ef
from wp.core import formula as fm

COND = "cond:"
MANUAL = "manual:"
AND = "&"
TAGGED = fm.TAGGED + ":"
_BUSY = []                             # (id(ch), key) being computed: a second read inside is a cycle -> 0


def _morale(ch):
    from wp.model import sheet_targets as stg
    return ch.morale_scale + stg.value(ch, "morale_scale")


def _pool_max(name):
    def get(ch):
        from wp.model import derived_view as dv
        return getattr(dv, name + "_pool")(ch).max
    return get


def tagged_base_slots(ch, tag):
    """Base slots taken by the items with the tag lying at the base (Item.base_slot_cost; decision 13)."""
    from wp.model import sheet_numbers as sn
    return sum(int(it.base_slot_cost) for it in sn.at_base(ch) if tag in tuple(getattr(it, "tags", ())))


def _sheet(key):
    from wp.model import body_view as bv
    from wp.model import sheet_numbers as sn
    table = {"hp_max": _pool_max("hp"), "mana_max": _pool_max("mana"), "balance_max": _pool_max("balance"),
             "spirit_max": _pool_max("spirit"), "bp_max": _pool_max("bp"), "comfort_max": _pool_max("comfort"),
             "base_slots": sn.base_slots, "pain": bv.pain_total, "morale": _morale}
    return table.get(key)


def _number_after(cid, prefix):
    try:
        return int(cid[len(prefix):])
    except ValueError:
        return None


def condition(ch, cid):
    """True / False of one condition id (decision 7); an unknown id is False; "a&b" holds when both hold
    (package 36 P4: "in combat while the pressure is 0")."""
    from wp.model import derived_view as dv
    if AND in cid:
        return all(condition(ch, part) for part in cid.split(AND))
    if cid.startswith(MANUAL):
        return cid[len(MANUAL):] in tuple(getattr(ch, "manual_conditions", ()))
    if cid == "hp_full":
        p = dv.hp_pool(ch)
        return p.current >= p.max
    if cid == "bp_full":
        p = dv.bp_pool(ch)
        return p.current >= p.max
    if cid == "in_combat":
        return bool(ch.in_combat)
    for prefix, test in (("pressure_eq:", lambda a, b: a == b), ("pressure_ge:", lambda a, b: a >= b),
                         ("pressure_le:", lambda a, b: a <= b)):
        if cid.startswith(prefix):
            n = _number_after(cid, prefix)
            return n is not None and test(guarded(ch, "morale", _morale), n)
    if cid.startswith("pain_ge:"):
        n = _number_after(cid, "pain_ge:")
        return n is not None and guarded(ch, "pain", _sheet("pain")) >= n
    if cid.startswith(CHARGES_LEFT):       # package 37: "charges_left:feat:<id>" (the Mordon -4 counter)
        return _charges_left(ch, cid[len(CHARGES_LEFT):])
    if cid.startswith(STATUS_TAG):         # package 38: an active status with this tag (bleeding -> the x2 reminder)
        tag = cid[len(STATUS_TAG):]
        return any(tag in tuple(s.tags) for s in ch.statuses if ef.is_effective(s))
    return False


CHARGES_LEFT = "charges_left:"
STATUS_TAG = "status_tag:"


def _charges_left(ch, ref):
    """True while the owner ("kind:id": feat / item / status / attack / maneuver) has a charge left."""
    from wp.model import usage as us
    kind, _, oid = ref.partition(":")
    owner = us.find(ch, kind, oid) if kind in us.KINDS and oid else None
    c = us.charges(kind, owner) if owner is not None else None
    return c is not None and c[0] > 0


def guarded(ch, key, fn):
    k = (id(ch), key)
    if k in _BUSY:
        return 0
    _BUSY.append(k)
    try:
        return int(fn(ch))
    except Exception:                  # noqa: BLE001 - a view never raises on a broken number (GOTCHAS): 0
        return 0
    finally:
        _BUSY.pop()


class Context(dict):
    """The effect context with lazy sheet numbers, stat modifiers and conditions (see the module text)."""

    def __init__(self, ch, base=None, lazy_mods=False):
        super().__init__(base or {})
        self.ch, self.lazy_mods = ch, lazy_mods

    def _compute(self, key):
        ch = self.ch
        if key.startswith(COND):           # guarded: HP max reads effects that may depend on "HP is max"
            cid = key[len(COND):]
            return bool(guarded(ch, key, lambda c: condition(c, cid)))
        if key.startswith(TAGGED):
            return tagged_base_slots(ch, key[len(TAGGED):])
        fn = _sheet(key)
        if fn is not None:
            return guarded(ch, key, fn)
        if self.lazy_mods:
            stat = key[len(ef.STAT_MOD):] if key.startswith(ef.STAT_MOD) else (key[:-len("_mod")]
                                                                              if key.endswith("_mod") else "")
            if stat in ch.abilities:
                from wp.model import derived_view as dv
                return guarded(ch, "mod:" + stat, lambda c: dv.ability_mod(c, stat))
        return None

    def get(self, key, default=None):
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        v = self._compute(key)
        if v is None:
            return default
        if not key.startswith(COND):           # conditions are read fresh (they are cheap)
            dict.__setitem__(self, key, v)
        return v

    def __getitem__(self, key):
        v = self.get(key)
        if v is None:
            raise KeyError(key)
        return v

    def __contains__(self, key):
        return dict.__contains__(self, key) or self._compute(key) is not None


# ------------------------------------------------------------------ the cycle check (Sources dialog warning)
VAR_TARGETS = {"hp_max": ("hp_max", "extra_hit_dice", "stat:con"), "mana_max": ("mana_max",),
               "base_slots": ("base_slots",), "morale": ("morale_scale",), "balance_max": ("balance_max", "bp_max"),
               "spirit_max": ("spirit_max",), "bp_max": ("bp_max",), "comfort_max": ("comfort_max",)}


def _targets_of(var):
    if var.endswith("_mod"):
        return ("stat:" + var[:-len("_mod")],)
    return VAR_TARGETS.get(var, ())


def cycles(ch):
    """The effect targets that lie on a cycle of formulas (target -> the targets its formulas read)."""
    from wp.model import blocks as blk
    graph = {}
    for _src, e in blk.active_effects(ch):
        if isinstance(e.value, str) and e.value != ef.ALL:
            for v in fm.variables(e.value):
                graph.setdefault(e.target, set()).update(_targets_of(v))
    on_cycle = set()
    for start in graph:
        seen, todo = set(), list(graph[start])
        while todo:
            t = todo.pop()
            if t == start:
                on_cycle.add(start)
                break
            if t not in seen:
                seen.add(t)
                todo.extend(graph.get(t, ()))
    return on_cycle
