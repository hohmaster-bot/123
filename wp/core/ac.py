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


def _dex(inp):
    d = inp.dex_mod
    if inp.max_dex is not None:
        d = min(d, inp.max_dex)
    return d


# Layer order of the defense ladder (RULES/defense_layers.md); "unlisted" = other AC types.
LAYER_TYPES = ("size", bo.DODGE, "insight", bo.MORALE, "competence", "luck", "circumstance",
               bo.DEFLECTION, bo.SHIELD, bo.ARMOR, bo.NATURAL)
UNLISTED = "unlisted"


def parts(inp, mode=FRONT, from_shield_side=False):
    """AC broken into layers: ((layer, value), ...) in LAYER_TYPES order, then (UNLISTED, value).
    dodge includes Dex (Dex gives dodge); armor holds max(armor, parry) in PARRY mode."""
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

    if mode == FLAT_FOOTED:
        dex_dodge = min(0, _dex(inp))      # low-Dex penalty stays; Dex bonus and dodge are lost
    else:
        dex_dodge = _dex(inp) + bo.stack([b for b in items if b.btype == bo.DODGE])
        if inp.overloaded:
            dex_dodge = min(dex_dodge, OVERLOAD_DODGE_CAP)

    out = []
    for t in LAYER_TYPES:
        if t == "size":
            v = inp.size_mod + bo.stack([b for b in items if b.btype == "size"])
        elif t == bo.DODGE:
            v = dex_dodge
        else:
            v = bo.stack([b for b in items if b.btype == t])
        out.append((t, v))
    out.append((UNLISTED, bo.stack([b for b in items if b.btype not in LAYER_TYPES])))
    return tuple(out)


def ac(inp, mode=FRONT, from_shield_side=False):
    """AC for one attack direction = 10 + the sum of its layers."""
    return BASE_AC + sum(v for _, v in parts(inp, mode, from_shield_side))


def all_modes(inp, from_shield_side=False):
    return {m: ac(inp, m, from_shield_side) for m in (FRONT, FLANK, FLAT_FOOTED, PARRY, TOUCH)}
