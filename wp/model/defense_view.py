"""DR, resistances and spell resistance from the sheet's effects (package 16 D; RULES/resources.md "Damage").

Effect targets: "dr" (value; Effect.note = the bypass text such as "cold iron", narrative only: it never changes a
number), "resist:<damage type>" (value), "spell_resistance" (value). Sources: anything that carries effects (race /
template, feats, worn items, consumable statuses, statuses, injuries), active by the rules of that source.
Stacking: the normal typed-bonus rules per target (same type -> larger wins; flat adds), bonuses.stack.
Damage types are data (wp/catalog/data/damage_types.json). DR works on the physical types only.
reductions(ch, types, skip): the flat reduction per damage type for take_damage: the larger of DR (physical types)
and resist:<type> (one reduction per part, the rule "overlap is not modelled"; assumption Q119), minus the keys in
`skip` (the player's choice before the hit: "dr", "resist:fire"...).
"""
from dataclasses import dataclass
from typing import Dict, Tuple

from wp.core import bonuses as bo
from wp.core import damage as dm
from wp.model import blocks as blk
from wp.model import derived_view as dv
from wp.model import sheet_targets as stg

DR = "dr"
SR = "spell_resistance"


def _load():
    """Damage types from the catalog file of kind "damage_types" (package 18)."""
    from wp.catalog import store as cs
    cat = cs.load_shipped("damage_types")
    types = tuple(e["id"] for e in cat.entries)
    physical = {e["id"] for e in cat.entries if e.get("physical")} | set(cat.meta.get("also_physical", ()))
    return types, frozenset(physical)


TYPES, PHYSICAL = _load()


@dataclass(frozen=True)
class DefenseView:
    dr: int
    dr_entries: Tuple[Tuple[str, int, str, bool], ...]  # (source id, value, bypass text, stacks)
    resist: Dict[str, int]                              # damage type -> value (only types with a value)
    resist_entries: Dict[str, Tuple[Tuple[str, int, str], ...]]
    spell_resistance: int
    sr_entries: Tuple[Tuple[str, int, str], ...]
    percent: Tuple[Tuple[str, int], ...] = ()          # (damage type, signed %) for types with a value


PERCENT = "percent:"


def _values(ch, target):
    return [v for _, v, _ in stg.entries(ch, target)]


def resist(ch, dtype):
    """Resistances NEVER stack: the larger wins (package 17, Q115)."""
    return max([0] + _values(ch, stg.RESIST + dtype))


def dr_entries(ch):
    """(source, value, bypass text, stacks) of every DR effect."""
    ctx = dv.context(ch)
    return tuple((src, e.resolve(ctx), e.note, e.stacks) for src, e in blk.active_effects(ch) if e.target == DR)


def dr(ch):
    """Total DR = the largest NON-stacking entry + the sum of the stacking entries (package 17, Q115). The bypass
    text never changes the number."""
    es = dr_entries(ch)
    return max(0, max([0] + [v for _, v, _, s in es if not s]) + sum(v for _, v, _, s in es if s))


def modifier(ch, dtype):
    """Signed percent modifier of one damage type (effects "percent:<type>"): one value per type; with several
    sources the larger absolute value wins (equal + and - -> 0, like typed bonuses); never below -100."""
    vs = _values(ch, PERCENT + dtype)
    return max(-100, bo.winner(max([0] + vs), min([0] + vs)))


def spell_resistance(ch):
    return max(0, stg.value(ch, SR))


def defense_view(ch):
    res = {t: resist(ch, t) for t in TYPES}
    mods = {t: modifier(ch, t) for t in TYPES}
    return DefenseView(dr=dr(ch), dr_entries=dr_entries(ch), percent=tuple((t, v) for t, v in mods.items() if v),
                       resist={t: v for t, v in res.items() if v},
                       resist_entries={t: stg.entries(ch, stg.RESIST + t) for t in TYPES if stg.entries(ch, stg.RESIST + t)},
                       spell_resistance=spell_resistance(ch), sr_entries=stg.entries(ch, SR))


def reductions(ch, types, skip=(), given=None):
    """Reductions for one hit: per damage type the larger of DR (physical) / resist:<type> / the caller's flat value;
    the caller's percent values are kept."""
    given = given or dm.Reductions()
    flat = dict(given.flat)
    d = 0 if DR in skip else dr(ch)
    for t in set(types):
        own = 0 if (stg.RESIST + t) in skip else resist(ch, t)
        best = max(own, d if t in PHYSICAL else 0, int(flat.get(t, 0)))
        if best:
            flat[t] = best
    mods = dict(given.modifier)
    for t in set(types):
        m = 0 if (PERCENT + t) in skip else modifier(ch, t)
        if m:
            mods[t] = m
    return dm.Reductions(percent=dict(given.percent), flat=flat, modifier=mods,
                         order=tuple(ch.rules_settings.damage_order))
