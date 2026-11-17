"""Core typed bonuses vs RULES/defense.md. Run: python Wp_claude/tests/core/test_bonuses.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core import bonuses as bo  # noqa: E402
from wp.core.bonuses import Bonus  # noqa: E402

S = Suite("test_bonuses")

# defense.md Example: +1 enchanted sword + "magic weapon" +1 enchant -> +1, not +2.
S.case("enchant-example", "defense.md Typed bonus pools Example", 1)(
    lambda: bo.total([Bonus(1, bo.ENHANCEMENT, bo.ATTACK), Bonus(1, bo.ENHANCEMENT, bo.ATTACK)],
                     bo.ATTACK))

S.case("same-type-highest", "defense.md: same type, only the highest", 4)(
    lambda: bo.total([Bonus(2, "luck", bo.SAVE), Bonus(4, "luck", bo.SAVE)], bo.SAVE))

S.case("flat-stacks", "defense.md: flat stacks with itself", 5)(
    lambda: bo.total([Bonus(2), Bonus(3)], bo.SKILL))

S.case("dodge-stacks", "defense.md: dodge stacks with itself", 3)(
    lambda: bo.total([Bonus(1, bo.DODGE, bo.AC), Bonus(2, bo.DODGE, bo.AC)], bo.AC))

S.case("penalty-largest", "defense.md: same-type penalties -> the largest penalty", -4)(
    lambda: bo.total([Bonus(-2, "luck", bo.ATTACK), Bonus(-4, "luck", bo.ATTACK)], bo.ATTACK))

# defense.md Stacking [OWNER decision] examples: larger absolute value wins, equal -> 0.
for _b, _p, _exp in [(3, -4, -4), (3, -1, 3), (2, -2, 0)]:
    S.case("same-type%+d%+d" % (_b, _p), "defense.md Stacking Examples [OWNER]", _exp)(
        lambda b=_b, p=_p: bo.total([Bonus(b, "luck", bo.SAVE), Bonus(p, "luck", bo.SAVE)], bo.SAVE))

S.case("flat-bonus-penalty-add", "defense.md: flat adds up (+3 and -4 -> -1)", -1)(
    lambda: bo.total([Bonus(3), Bonus(-4)], bo.SAVE))

# defense.md: per target. Morale +1 on everything, spell morale -2 on attacks.
_m1 = [bo.morale(1), Bonus(-2, bo.MORALE, bo.ATTACK)]
S.case("morale-per-target", "defense.md Example [OWNER]: attacks -2, rest +1", (-2, 1, 1, 1))(
    lambda: tuple(bo.total(_m1, t) for t in (bo.ATTACK, bo.SAVE, bo.SKILL, bo.DAMAGE)))
# Heroism +4 morale on attacks, morale -1 on everything.
_m2 = [bo.morale(-1), Bonus(4, bo.MORALE, bo.ATTACK)]
S.case("heroism", "defense.md Example [OWNER]: heroism +4 on attacks, morale -1", (4, -1, -1))(
    lambda: tuple(bo.total(_m2, t) for t in (bo.ATTACK, bo.SAVE, bo.CMB)))

S.case("different-types-add", "defense.md: different types add", 3)(
    lambda: bo.total([Bonus(1, bo.ENHANCEMENT, bo.ATTACK), Bonus(2, "luck", bo.ATTACK)], bo.ATTACK))

# defense.md: weapon proficiency stacks with itself, only on attacks with that weapon.
_prof = [Bonus(1, bo.PROFICIENCY, bo.ATTACK, weapon="longsword"),
         Bonus(1, bo.PROFICIENCY, bo.ATTACK, weapon="longsword")]
S.case("prof-stacks", "defense.md: proficiency stacks, that weapon", 2)(
    lambda: bo.total(_prof, bo.ATTACK, weapon="longsword"))
S.case("prof-other-weapon", "defense.md: proficiency only for that weapon", 0)(
    lambda: bo.total(_prof, bo.ATTACK, weapon="axe"))
S.case("prof-not-damage", "defense.md: proficiency only for attacks", 0)(
    lambda: bo.total([Bonus(1, bo.PROFICIENCY, bo.DAMAGE, weapon="longsword")], bo.DAMAGE,
                     weapon="longsword"))

# defense.md: AC-only types apply only to AC.
_ac_types = [Bonus(2, t, bo.ROLLS) for t in (bo.ARMOR, bo.NATURAL, bo.SHIELD, bo.DODGE, bo.DEFLECTION)]
S.case("ac-only-not-attack", "defense.md: AC-only types never on rolls", 0)(
    lambda: bo.total(_ac_types, bo.ATTACK))
S.case("ac-only-on-ac", "defense.md: AC-only types count on AC", 10)(
    lambda: bo.total(_ac_types, bo.AC))

# defense.md Morale: type morale on ALL rolls, not AC.
S.case("morale-all-rolls", "defense.md Morale: all rolls, not lucky/crit/AC",
       (2, 2, 2, 2, 2, 2, 2, 0, 0, 0))(
    lambda: tuple(bo.total([bo.morale(2)], t) for t in
                  (bo.ATTACK, bo.DAMAGE, bo.SAVE, bo.SKILL, bo.INITIATIVE, bo.CMB, bo.MANEUVER,
                   bo.LUCKY, bo.CRIT, bo.AC)))
S.case("morale-highest", "defense.md Morale: highest only, like any typed bonus", 3)(
    lambda: bo.total([bo.morale(1), bo.morale(3)], bo.ATTACK))

# combat.md Stances Example: "defensive" +2 dodge, -4 attack (flat).
_stance = [Bonus(2, bo.DODGE, bo.AC), Bonus(-4, bo.FLAT, bo.ATTACK)]
S.case("stance-defensive", "combat.md Stances Example", (2, -4))(
    lambda: (bo.total(_stance, bo.AC), bo.total(_stance, bo.ATTACK)))


@S.case("unknown-type", "bonus type must be known", "rejected")
def _unknown():
    try:
        Bonus(1, "magic")
    except ValueError:
        return "rejected"
    return "allowed"


if __name__ == "__main__":
    sys.exit(S.run())
