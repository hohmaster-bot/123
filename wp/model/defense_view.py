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
import io
import json
import os
from dataclasses import dataclass
from typing import Dict, Tuple

from wp.core import damage as dm
from wp.model import sheet_targets as stg

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "catalog", "data", "damage_types.json")
DR = "dr"
SR = "spell_resistance"


def _load(path=PATH):
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    return tuple(d["types"]), frozenset(d["physical"])


TYPES, PHYSICAL = _load()


@dataclass(frozen=True)
class DefenseView:
    dr: int
    dr_entries: Tuple[Tuple[str, int, str], ...]       # (source id, value, bypass text)
    resist: Dict[str, int]                              # damage type -> value (only types with a value)
    resist_entries: Dict[str, Tuple[Tuple[str, int, str], ...]]
    spell_resistance: int
    sr_entries: Tuple[Tuple[str, int, str], ...]


def resist(ch, dtype):
    return max(0, stg.value(ch, stg.RESIST + dtype))


def dr(ch):
    return max(0, stg.value(ch, DR))


def spell_resistance(ch):
    return max(0, stg.value(ch, SR))


def defense_view(ch):
    res = {t: resist(ch, t) for t in TYPES}
    return DefenseView(dr=dr(ch), dr_entries=stg.entries(ch, DR),
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
    return dm.Reductions(percent=dict(given.percent), flat=flat)
