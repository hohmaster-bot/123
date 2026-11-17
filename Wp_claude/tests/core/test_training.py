"""Core training vs RULES/training.md etc. Run: python Wp_claude/tests/core/test_training.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core import training as t  # noqa: E402

S = Suite("test_training")

# training.md Ability score cost Example: base 13 + race 2 = 15.
S.case("ability-15-16", "training.md Example: 15->16 = 150*3", 450)(lambda: t.ability_step_cost(13, 2))
S.case("ability-16-17", "training.md Example: 16->17 = 450", 450)(lambda: t.ability_step_cost(14, 2))
S.case("ability-17-18", "training.md Example: 17->18 = 150*4", 600)(lambda: t.ability_step_cost(15, 2))
S.case("ability-run", "training.md Example: 15 -> 18 total", 1500)(lambda: t.ability_cost(13, 2, 3))
S.case("ability-low", "training.md: max(1, new mod) -> 10->11 = 150", 150)(lambda: t.ability_step_cost(10))
S.case("ability-race-lost", "training.md: race bonus lost -> price follows new score (13->14 = 300)", 300)(
    lambda: t.ability_step_cost(13, 0))

# training.md Languages Tests [OWNER confirmed].
S.case("lang-first-free", "training.md: first native language free", 0)(
    lambda: t.native_language_cost(0, 0))
for _mod, _nat, _exp in [(2, 1, 50), (2, 2, 100), (3, 2, 50), (3, 3, 100), (1, 1, 100)]:
    S.case("lang-int%+d-nat%d" % (_mod, _nat), "training.md Languages Tests [OWNER]", _exp)(
        lambda m=_mod, n=_nat: t.native_language_cost(n, m))
S.case("lang-non-native", "training.md: non-native 30", 30)(lambda: t.language_cost(False))

# training.md Armor / shield grades.
S.case("shield-grades", "training.md: shield 100 per grade", (100, 100, 100))(
    lambda: tuple(t.shield_grade_cost(g) for g in ("none", "light", "heavy")))
S.case("armor-grades", "training.md: armor 250 per grade", (250, 250, 250))(
    lambda: tuple(t.armor_grade_cost(g) for g in ("none", "light", "medium")))


@S.case("shield-max", "training.md: tower is the last shield grade", "rejected")
def _shield_max():
    try:
        t.shield_grade_cost("tower")
    except ValueError:
        return "rejected"
    return "allowed"


# gear.md Base.
S.case("base-start", "gear.md Base: start 5 slots", 5)(lambda: t.BASE_START)
S.case("base-cost", "gear.md / training.md: base slot 100", 100)(lambda: t.base_slot_cost(5, 1))


@S.case("base-cap", "gear.md Base: max 10*level (level 2 -> 20)", "rejected")
def _base_cap():
    try:
        t.base_slot_cost(20, 2)
    except ValueError:
        return "rejected"
    return "allowed"


# progression.md.
S.case("start-training", "progression.md [OWNER]: creation 1000", 1000)(lambda: t.START_TRAINING)
S.case("level-up", "progression.md: level-up = 100 * new level", (200, 300))(
    lambda: (t.level_up_training(2), t.level_up_training(3)))

# resources.md Comfort.
S.case("comfort-max", "resources.md: comfort max 5 + 5*level (level 3 -> 20)", 20)(lambda: t.comfort_max(3))

# training.md Modes: only source = training spends points.
S.case("source-free", "training.md: race/class/loot/quirk never spend training", (1000, 1000, 1000, 1000))(
    lambda: tuple(t.pay(1000, 200, s) for s in ("race", "class", "loot", "quirk")))
S.case("source-training", "training.md: training source spends", 800)(lambda: t.pay(1000, 200))


@S.case("not-enough", "training.md Training mode needs resources", "rejected")
def _not_enough():
    try:
        t.pay(100, 200)
    except ValueError:
        return "rejected"
    return "allowed"


# training.md Attention course.
S.case("attention-comfort", "training.md option 2: Dex 3 -> 1.5 comfort; min 1", (1.5, 1.0))(
    lambda: (t.attention_comfort_equivalent(3), t.attention_comfort_equivalent(1)))
S.case("attention-base", "training.md option 4 Example: 5 attention at minimum = 2.0", 2.0)(
    lambda: t.attention_base_points(5, 1))
S.case("professionalism-cap", "training.md: professionalism <= character level", (True, False))(
    lambda: (t.professionalism_ok(3, 3), t.professionalism_ok(4, 3)))

if __name__ == "__main__":
    sys.exit(S.run())
