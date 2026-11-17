"""Typed bonuses and stacking (RULES/defense.md "Typed bonus pools", combat.md stances).

A bonus = value + type + target (+ optional weapon).
Stacking for one target:
  - flat: everything adds up (bonuses and penalties);
  - dodge: adds up;
  - weapon proficiency: adds up, only for attacks with that weapon;
  - any other type: bonus and penalty do NOT add up; the value with the larger
    absolute value wins (highest bonus vs largest penalty); equal -> 0.
    +3 and -4 -> -4; +3 and -1 -> +3; +2 and -2 -> 0.
Computed separately for each target.
AC-only types (armor/parry, natural, shield, dodge, deflection) count only for AC.
Morale is a bonus of type "morale" on all rolls (skills, saves, attacks, maneuvers,
CMB, damage), not on the lucky attack die, the crit die or AC.
Type names follow the legacy list (modifiers.py, read only).
"""
from dataclasses import dataclass
from typing import Optional

# types
FLAT = "flat"
DODGE = "dodge"
PROFICIENCY = "proficiency"     # weapon proficiency (mastery) bonus
ARMOR = "armor"                 # parry uses the same type as armor
NATURAL = "natural"
SHIELD = "shield"
DEFLECTION = "deflection"
MORALE = "morale"
ENHANCEMENT = "enhancement"

TYPES = {
    FLAT, "alchemical", ARMOR, "circumstance", "competence", DEFLECTION, DODGE,
    ENHANCEMENT, "inherent", "insight", "luck", MORALE, NATURAL, "profane",
    "racial", "resistance", "sacred", SHIELD, "size", "trait", PROFICIENCY,
}
AC_ONLY_TYPES = {ARMOR, NATURAL, SHIELD, DODGE, DEFLECTION}
ADDING_TYPES = {FLAT, DODGE, PROFICIENCY}

# targets
AC = "ac"
ATTACK = "attack"
DAMAGE = "damage"
SAVE = "save"
SKILL = "skill"
INITIATIVE = "initiative"
CMB = "cmb"
MANEUVER = "maneuver"
LUCKY = "lucky"                 # lucky attack die: no bonuses from ROLLS
CRIT = "crit"                   # crit confirmation die: no bonuses from ROLLS
ROLLS = "rolls"                 # all rolls: attack, damage, saves, skills, initiative, CMB, maneuvers
ROLL_TARGETS = {ATTACK, DAMAGE, SAVE, SKILL, INITIATIVE, CMB, MANEUVER}


@dataclass(frozen=True)
class Bonus:
    value: int
    btype: str = FLAT
    target: str = ROLLS
    weapon: Optional[str] = None   # set -> only for attacks with this weapon
    source: str = ""

    def __post_init__(self):
        if self.btype not in TYPES:
            raise ValueError("unknown bonus type: %r" % (self.btype,))


def morale(value):
    """Morale as a typed bonus on all rolls (value from derived.morale_bonus)."""
    return Bonus(int(value), MORALE, ROLLS, source="morale")


def applies(b, target, weapon=None):
    """Does bonus b count for this target (and weapon, for attacks)?"""
    if b.btype in AC_ONLY_TYPES:
        return target == AC        # AC-only types: AC and nothing else
    if b.weapon is not None:
        # weapon-scoped: attacks (and damage, except proficiency) with that weapon only
        allowed = (ATTACK,) if b.btype == PROFICIENCY else (ATTACK, DAMAGE)
        if target not in allowed or b.weapon != weapon:
            return False
    if b.btype == PROFICIENCY and b.weapon is None:
        return False            # proficiency is always tied to a weapon
    if b.target == target:
        return True
    return b.target == ROLLS and target in ROLL_TARGETS


def stack(bonuses):
    """Sum a list of bonuses that already apply to one target."""
    total = 0
    best = {}     # type -> highest bonus
    worst = {}    # type -> largest penalty (most negative)
    for b in bonuses:
        v = int(b.value)
        if b.btype in ADDING_TYPES:
            total += v
        elif v >= 0:
            best[b.btype] = max(best.get(b.btype, 0), v)
        else:
            worst[b.btype] = min(worst.get(b.btype, 0), v)
    for t in set(best) | set(worst):
        total += winner(best.get(t, 0), worst.get(t, 0))
    return total


def winner(bonus, penalty):
    """Same type: larger absolute value wins; equal -> 0 (owner, defense.md)."""
    if bonus > -penalty:
        return bonus
    if -penalty > bonus:
        return penalty
    return 0


def total(bonuses, target, weapon=None):
    """Total typed bonus for a target (e.g. ATTACK with weapon 'longsword')."""
    return stack([b for b in bonuses if applies(b, target, weapon)])


def by_type(bonuses, target, weapon=None):
    """{type: stacked value} for display / breakdown."""
    groups = {}
    for b in bonuses:
        if applies(b, target, weapon):
            groups.setdefault(b.btype, []).append(b)
    return {t: stack(bs) for t, bs in groups.items()}
