"""Core weapon mastery vs RULES/weapons.md, combat.md. Run: python Wp_claude/tests/core/test_weapons.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core import weapons as w  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402

S = Suite("test_weapons")

S.case("level-names", "weapons.md Levels 0-12", ("none", "Skilled", "Specialist I", "Expert IV", "Master"))(
    lambda: tuple(w.level_name(x) for x in (0, 4, 5, 11, 12)))

# weapons.md Cost of +1 grade, Examples.
S.case("cost-60", "weapons.md Example: X=0, difficulty 1, scale 2 -> 60", 60)(
    lambda: w.grade_cost({"ls": Weapon("ls", 2, 1)}, "ls"))
S.case("cost-240", "weapons.md Example: X=2, difficulty 2, scale 3 -> 240", 240)(
    lambda: w.grade_cost({"g": Weapon("g", 3, 2, grades=3), "e1": Weapon("e1", grades=8),
                          "e2": Weapon("e2", grades=9)}, "g"))
S.case("cost-x-excludes-self", "weapons.md: X counts only OTHER groups at 8+", 30)(
    lambda: w.grade_cost({"a": Weapon("a", grades=9)}, "a"))

# Combat basics.
S.case("basics-cost", "weapons.md: basics 50/100/150 for scale 1/2/3", (50, 100, 150))(
    lambda: tuple(w.basics_cost(s) for s in (1, 2, 3)))
S.case("basics-bump", "weapons.md: +(5 - difficulty), difficulty 1 -> +4", (4, 3))(
    lambda: (w.basics_bump(1), w.basics_bump(2)))


def _family():
    return {
        "heavy blades": Weapon("heavy blades", 3, 1, basics=True),
        "eastern style": Weapon("eastern style", 3, 2, basics=True),
        "long swords": Weapon("long swords", 2, 1, basics=True, parents=("heavy blades", "eastern style")),
        "grandpa": Weapon("grandpa", 1, 1, basics=True, parents=("long swords",)),
    }


S.case("basics-no-stack", "weapons.md Example [OWNER]: basics on sword + variety + group -> 4, not 12", 4)(
    lambda: w.level(_family(), "grandpa"))
S.case("ancestors-multi", "weapons.md: a variety may sit in several groups",
       ("long swords", "heavy blades", "eastern style"))(lambda: w.ancestors(_family(), "grandpa"))
S.case("basics-from-ancestor", "weapons.md: basics only on the group still lifts the sword", 4)(
    lambda: w.level({"g": Weapon("g", 3, 1, basics=True), "s": Weapon("s", parents=("g",))}, "s"))
S.case("basics-plus-grades", "weapons.md: bought grades + basics bump, cap 12", (6, 12))(
    lambda: (w.level({"s": Weapon("s", grades=2, basics=True)}, "s"),
             w.level({"s": Weapon("s", grades=10, basics=True)}, "s")))

# Qualification.
S.case("qualification", "weapons.md: -4 not qualified, -2 one level below, 0 qualified", (0, -2, -4))(
    lambda: (w.qualification_penalty(5, 5), w.qualification_penalty(4, 5), w.qualification_penalty(2, 5)))


def _check(level, picks):
    try:
        w.validate_picks(level, [Pick(s, b) for s, b in picks])
        return "allowed"
    except ValueError:
        return "rejected"


_SPEC3 = [(5, "attack_1"), (6, "crit_1"), (7, "parry_1")]

# weapons.md Bonuses by tier, Tests.
S.case("expert-open", "weapons.md Test: after 3 different specialist picks, expert opens", "allowed")(
    lambda: _check(8, _SPEC3 + [(8, "damage_3")]))
S.case("expert-gate", "weapons.md: need 3 specialist picks before expert picks", "rejected")(
    lambda: _check(8, [(5, "attack_1"), (8, "damage_3")]))
S.case("crit-2nd-at-9", "weapons.md Test: at level 9, crit +1 a 2nd time is allowed", "allowed")(
    lambda: _check(9, _SPEC3 + [(8, "damage_3"), (9, "crit_1")]))
S.case("crit-3rd-before-12", "weapons.md Test: 3rd crit +1 not until 12", "rejected")(
    lambda: _check(11, _SPEC3 + [(8, "crit_1"), (9, "crit_1")]))
S.case("crit-3rd-at-12", "weapons.md: 3rd specialist pick at master", "allowed")(
    lambda: _check(12, _SPEC3 + [(8, "crit_1"), (12, "crit_1")]))
S.case("spec-repeat-in-spec", "weapons.md: specialist bonus 2nd time only from expert level", "rejected")(
    lambda: _check(7, [(5, "attack_1"), (6, "attack_1"), (7, "parry_1")]))
S.case("expert-2nd-at-master", "weapons.md: expert bonus 2nd time at master", ("rejected", "allowed"))(
    lambda: (_check(11, _SPEC3 + [(8, "damage_3"), (9, "damage_3")]),
             _check(12, _SPEC3 + [(8, "damage_3"), (12, "damage_3")])))
S.case("expert-in-spec-slot", "weapons.md: specialist slots take specialist bonuses only", "rejected")(
    lambda: _check(7, [(5, "damage_3")]))
S.case("slot-above-level", "weapons.md: slot opens at its level", "rejected")(
    lambda: _check(7, _SPEC3 + [(8, "damage_3")]))

# weapons.md Mastery bonuses in the final numbers [OWNER].
S.case("durability-100", "weapons.md [OWNER]: +30% and +70% -> +100% of base", 20)(
    lambda: w.final_durability(10, [Pick(5, "durability_30"), Pick(8, "durability_70")]))
S.case("durability-spec-only", "weapons.md: specialist +30%", 13)(
    lambda: w.final_durability(10, [Pick(5, "durability_30")]))
S.case("item-hp", "weapons.md [OWNER]: item HP +1 per expert pick", 7)(
    lambda: w.final_hp(5, [Pick(8, "hp_1"), Pick(12, "hp_1")]))
S.case("flat-bonuses", "weapons.md [OWNER]: picks add as flat to parry/attack/damage",
       {"parry": 1, "attack": 2, "damage": 3, "range_ft": 0, "balance_regen": 0})(
    lambda: w.mastery_flat([Pick(5, "attack_1"), Pick(6, "parry_1"), Pick(8, "damage_3"),
                            Pick(9, "attack_1")]))

# combat.md Crit.
S.case("crit-base", "combat.md: x2 alone = crit on 20", 20)(lambda: w.crit_threshold(20))
S.case("crit-mastery-2", "combat.md: mastery widens by 2 (20 -> 18) = two crit +1 picks", 18)(
    lambda: w.crit_threshold(20, picks=[Pick(5, "crit_1"), Pick(8, "crit_1")]))
S.case("crit-keen", "combat.md: keen doubles base range (19-20 -> 17-20)", 17)(
    lambda: w.crit_threshold(19, keen=True))
S.case("crit-keen-plus-mastery", "combat.md: keen doubles BASE only, picks add after", 16)(
    lambda: w.crit_threshold(19, keen=True, picks=[Pick(5, "crit_1")]))

# combat.md Lucky attack.
S.case("lucky-base", "combat.md: lucky attack base 20", 20)(lambda: w.lucky_threshold())
S.case("lucky-enchant", "combat.md + gear.md: +5 sword -> 15", 15)(lambda: w.lucky_threshold(enchant=5))
S.case("lucky-mastery-enchant-extra", "combat.md: mastery 1 + enchant 1 + feat 1", 17)(
    lambda: w.lucky_threshold([Pick(8, "lucky_1")], enchant=1, extra=1))

if __name__ == "__main__":
    sys.exit(S.run())
