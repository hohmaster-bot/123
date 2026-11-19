"""Armor class by attack direction (RULES/defense.md "Positioning", gear.md overload).

  FRONT        full AC.
  FLANK        shield side: the shield bonus is ignored (option flank_drops_shield, default on).
  FLAT_FOOTED  no Dex bonus and no dodge (a low-Dex penalty stays); shield only from the shield side.
  PARRY        front only: armor slot uses max(armor, parry).
  TOUCH        ignores natural armor, shield, parry and armor; only the armor's touch bonus counts.
Overload caps Dex + dodge at +2. The shield bonus can be switched off.
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple

from wp.core import bonuses as bo

BASE_AC = 10
OVERLOAD_DODGE_CAP = 2

FRONT = "front"
FLANK = "flank"
FLAT_FOOTED = "flat_footed"
PARRY = "parry"
TOUCH = "touch"


@dataclass(frozen=True)
class AcInput:
    dex_mod: int = 0
    armor: int = 0                 # worn armor bonus
    parry: int = 0                 # parry value (same type as armor)
    natural: int = 0
    shield: int = 0
    size_mod: int = 0
    max_dex: Optional[int] = None  # armor max Dex, None = no cap
    overloaded: bool = False
    shield_enabled: bool = True    # UI toggle (also off after an attack with the shield)
    flank_drops_shield: bool = True    # checkbox: in FLANK mode the shield is dropped (attacker "may")
    touch_armor: int = 0           # worn armor bonus to TOUCH AC only (armor layer in TOUCH mode)
    bonuses: Tuple[bo.Bonus, ...] = field(default_factory=tuple)  # effects on AC


# Parry from armor proficiency (training.md [OWNER pkg 4]): none 0, light 2, medium 4, heavy 6,
# plus 1 on every odd level from 3 (3, 5, 7, ...; level 1 does not count, owner Q27),
# plus 2 for the "tower shields" proficiency grade. Parry comes from PROFICIENCY, not from an item.
ARMOR_GRADE_PARRY = {"none": 0, "light": 2, "medium": 4, "heavy": 6}
TOWER_GRADE = "tower"
TOWER_GRADE_PARRY = 2


def odd_level_parry(level):
    return max(0, (int(level) - 1) // 2)


def base_parry(armor_grade, level, shield_grade="none"):
    tower = TOWER_GRADE_PARRY if shield_grade == TOWER_GRADE else 0
    return ARMOR_GRADE_PARRY[armor_grade] + odd_level_parry(level) + tower


def _dex(inp):
    d = inp.dex_mod
    if inp.max_dex is not None:
        d = min(d, inp.max_dex)
    return d


# Layer order of the defense ladder (RULES/defense_layers.md). Base = 10 + PENALTY (the sum of all
# negative parts, <= 0); the layers follow the base, never below 0. "flat" (after armor) holds only
# positive untyped bonuses and positive types without their own layer.
PENALTY = "penalty"
LAYER_TYPES = ("size", bo.DODGE, "insight", bo.MORALE, "competence", "luck", "circumstance",
               bo.DEFLECTION, bo.SHIELD, bo.ARMOR, bo.FLAT, bo.NATURAL)
TYPED_LAYERS = tuple(t for t in LAYER_TYPES if t != bo.FLAT)


def parts(inp, mode=FRONT, from_shield_side=False):
    """AC as ((PENALTY, p), (layer, value), ...): p <= 0 lowers the base (base = 10 + p), then the
    layers in LAYER_TYPES order, each >= 0. The sum of all entries = AC - 10.
    dodge = dodge bonuses + Dex mod (they add up); a negative sum goes to the penalty (defense_layers.md).
    Flat-footed: the POSITIVE parts (dodge bonuses, Dex bonus) are lost, penalties stay.
    armor holds max(armor, parry) in PARRY mode, plus enhancement bonuses to AC (owner, Q26)."""
    if mode not in (FRONT, FLANK, FLAT_FOOTED, PARRY, TOUCH):
        raise ValueError("unknown AC mode: %r" % (mode,))

    armor_value = max(inp.armor, inp.parry) if mode == PARRY else inp.armor
    use_shield = inp.shield_enabled
    if mode == FLANK and inp.flank_drops_shield:
        use_shield = False
    if mode == FLAT_FOOTED and not from_shield_side:
        use_shield = False
    drop = set()
    if mode == TOUCH:
        drop |= {bo.ARMOR, bo.NATURAL, bo.SHIELD, bo.ENHANCEMENT}
    if not use_shield:
        drop.add(bo.SHIELD)

    items = [bo.Bonus(armor_value, bo.ARMOR, bo.AC, source="armor/parry"),
             bo.Bonus(inp.natural, bo.NATURAL, bo.AC, source="natural"),
             bo.Bonus(inp.shield, bo.SHIELD, bo.AC, source="shield")]
    items += [b for b in inp.bonuses if bo.applies(b, bo.AC)]
    items = [b for b in items if b.btype not in drop]
    if mode == TOUCH and inp.touch_armor > 0:
        # armor "touch AC" column: the only armor part of the touch AC (package 9 H)
        items.append(bo.Bonus(inp.touch_armor, bo.ARMOR, bo.AC, source="armor touch"))

    if mode == FLAT_FOOTED:
        # only the positive parts go: low-Dex penalty and dodge penalties stay
        dex_dodge = min(0, _dex(inp)) + sum(min(0, int(b.value)) for b in items if b.btype == bo.DODGE)
    else:
        dex_dodge = _dex(inp) + bo.stack([b for b in items if b.btype == bo.DODGE])
        if inp.overloaded:
            dex_dodge = min(dex_dodge, OVERLOAD_DODGE_CAP)

    values = {}
    for t in TYPED_LAYERS:
        if t == "size":
            values[t] = inp.size_mod + bo.stack([b for b in items if b.btype == "size"])
        elif t == bo.DODGE:
            values[t] = dex_dodge
        elif t == bo.ARMOR:
            values[t] = (bo.stack([b for b in items if b.btype == bo.ARMOR])
                         + bo.stack([b for b in items if b.btype == bo.ENHANCEMENT]))
        else:
            values[t] = bo.stack([b for b in items if b.btype == t])
    # untyped: positives to "flat", negatives to the penalty; other types without a layer (sacred,
    # profane...): stacked per type, a positive result to "flat", a negative one to the penalty
    flat = sum(max(0, int(b.value)) for b in items if b.btype == bo.FLAT)
    penalty = sum(min(0, int(b.value)) for b in items if b.btype == bo.FLAT)
    for t in {b.btype for b in items} - set(TYPED_LAYERS) - {bo.FLAT, bo.ENHANCEMENT}:
        v = bo.stack([b for b in items if b.btype == t])
        flat, penalty = flat + max(0, v), penalty + min(0, v)
    penalty += sum(min(0, v) for v in values.values())
    return ((PENALTY, penalty),) + tuple((t, flat if t == bo.FLAT else max(0, values[t])) for t in LAYER_TYPES)


def ac(inp, mode=FRONT, from_shield_side=False):
    """AC for one attack direction = base (10 + penalty) + the sum of the layers."""
    return BASE_AC + sum(v for _, v in parts(inp, mode, from_shield_side))


def all_modes(inp, from_shield_side=False):
    return {m: ac(inp, m, from_shield_side) for m in (FRONT, FLANK, FLAT_FOOTED, PARRY, TOUCH)}
