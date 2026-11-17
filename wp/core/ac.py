"""Armor class by attack direction (RULES/defense.md "Positioning", gear.md overload).

  FRONT        full AC.
  FLANK        shield side: the shield bonus is ignored.
  FLAT_FOOTED  no Dex bonus and no dodge (a low-Dex penalty stays); shield only from the shield side.
  PARRY        front only: armor slot uses max(armor, parry).
  TOUCH        ignores natural armor, shield, parry and armor.
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
    shield_enabled: bool = True    # UI toggle
    bonuses: Tuple[bo.Bonus, ...] = field(default_factory=tuple)  # effects on AC


# Parry from armor proficiency (training.md [OWNER pkg 4]): none 0, light 2, medium 4, heavy 6,
# plus 1 on every odd level from 3 (3, 5, 7, ...; level 1 does not count, owner Q27).
ARMOR_GRADE_PARRY = {"none": 0, "light": 2, "medium": 4, "heavy": 6}


def odd_level_parry(level):
    return max(0, (int(level) - 1) // 2)


def base_parry(armor_grade, level):
    return ARMOR_GRADE_PARRY[armor_grade] + odd_level_parry(level)


def _dex(inp):
    d = inp.dex_mod
    if inp.max_dex is not None:
        d = min(d, inp.max_dex)
    return d


# Layer order of the defense ladder (RULES/defense_layers.md). "flat" comes after armor:
# untyped bonuses, types without their own layer, and ALL penalties (low Dex too) go there.
LAYER_TYPES = ("size", bo.DODGE, "insight", bo.MORALE, "competence", "luck", "circumstance",
               bo.DEFLECTION, bo.SHIELD, bo.ARMOR, bo.FLAT, bo.NATURAL)
TYPED_LAYERS = tuple(t for t in LAYER_TYPES if t != bo.FLAT)


def parts(inp, mode=FRONT, from_shield_side=False):
    """AC broken into layers: ((layer, value), ...) in LAYER_TYPES order; sum = AC - 10.
    Typed layers are never below 0; their negative part and the low-Dex penalty go to "flat".
    dodge includes the Dex bonus; armor holds max(armor, parry) in PARRY mode."""
    if mode not in (FRONT, FLANK, FLAT_FOOTED, PARRY, TOUCH):
        raise ValueError("unknown AC mode: %r" % (mode,))

    armor_value = max(inp.armor, inp.parry) if mode == PARRY else inp.armor
    use_shield = inp.shield_enabled
    if mode == FLANK:
        use_shield = False
    if mode == FLAT_FOOTED and not from_shield_side:
        use_shield = False
    drop = set()
    if mode == TOUCH:
        drop |= {bo.ARMOR, bo.NATURAL, bo.SHIELD}
    if not use_shield:
        drop.add(bo.SHIELD)

    items = [bo.Bonus(armor_value, bo.ARMOR, bo.AC, source="armor/parry"),
             bo.Bonus(inp.natural, bo.NATURAL, bo.AC, source="natural"),
             bo.Bonus(inp.shield, bo.SHIELD, bo.AC, source="shield")]
    items += [b for b in inp.bonuses if bo.applies(b, bo.AC)]
    items = [b for b in items if b.btype not in drop]

    dex_penalty = min(0, _dex(inp))        # low-Dex penalty: always stays, goes to "flat"
    if mode == FLAT_FOOTED:
        dex_dodge = dex_penalty            # Dex bonus and dodge are lost
    else:
        dex_dodge = _dex(inp) + bo.stack([b for b in items if b.btype == bo.DODGE])
        if inp.overloaded:
            dex_dodge = min(dex_dodge, OVERLOAD_DODGE_CAP)

    values = {}
    for t in TYPED_LAYERS:
        if t == "size":
            values[t] = inp.size_mod + bo.stack([b for b in items if b.btype == "size"])
        elif t == bo.DODGE:
            values[t] = dex_dodge - dex_penalty
        else:
            values[t] = bo.stack([b for b in items if b.btype == t])
    flat = (dex_penalty + bo.stack([b for b in items if b.btype not in TYPED_LAYERS])
            + sum(min(0, v) for v in values.values()))
    return tuple((t, flat if t == bo.FLAT else max(0, values[t])) for t in LAYER_TYPES)


def ac(inp, mode=FRONT, from_shield_side=False):
    """AC for one attack direction = 10 + the sum of its layers."""
    return BASE_AC + sum(v for _, v in parts(inp, mode, from_shield_side))


def all_modes(inp, from_shield_side=False):
    return {m: ac(inp, m, from_shield_side) for m in (FRONT, FLANK, FLAT_FOOTED, PARRY, TOUCH)}
