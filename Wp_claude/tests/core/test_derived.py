"""Core derived values vs numbers in RULES/. Run: python Wp_claude/tests/core/test_derived.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core import derived as d  # noqa: E402

S = Suite("test_derived")

# rest.md: BP cap = ceil(max HP / 4). Tests [OWNER] + Example (4 -> 1).
for _hp, _exp in [(11, 3), (15, 4), (19, 5), (20, 5), (21, 6), (4, 1)]:
    S.case("bp-cap-%d" % _hp, "rest.md BP cap Tests [OWNER]", _exp)(
        lambda hp=_hp: d.bp_cap(hp))

# rest.md Example [OWNER]: 4 max HP -> BP 1; leather armor 2; race +3 -> balance max 6.
S.case("balance-max-example", "rest.md BP and balance Example [OWNER]", 6)(
    lambda: d.balance_max(armor_bonus=2, bp_current=d.bp_cap(4), bonuses=3))

# rest.md Note: CURRENT BP is used, spending BP lowers balance max.
S.case("balance-max-current-bp", "rest.md BP and balance Note [confirmed]", 5)(
    lambda: d.balance_max(armor_bonus=2, bp_current=0, bonuses=3))

# rest.md: regen = level + Con mod + other, min 1 (formula, no owner numbers).
S.case("regen-formula", "rest.md balance regen (formula)", 5)(
    lambda: d.balance_regen(level=3, con_mod=1, other=1))
S.case("regen-min1", "rest.md balance regen min 1 (formula)", 1)(
    lambda: d.balance_regen(level=1, con_mod=-3))

# resources.md Pain Examples [OWNER].
for _hp, _exp in [(0, 0), (-2, 0), (-5, 1), (-7, 2), (-12, 4)]:
    S.case("pain-hp%d" % _hp, "resources.md Pain Examples [OWNER]", _exp)(
        lambda hp=_hp: d.pain_from_hp(hp))
S.case("pain-heal", "resources.md Pain Examples [OWNER]: -7 healed by 2", 1)(
    lambda: d.pain_from_hp(-7 + 2))

# defense.md Morale.
for _sc, _exp, _src in [(3, 1, "Examples"), (-4, -2, "Examples"), (1, 0, "Examples"),
                        (-10, -5, "formula text"), (10, 5, "formula text"),
                        (-3, -1, "trunc toward zero"), (-1, 0, "trunc toward zero")]:
    S.case("morale%+d" % _sc, "defense.md Morale %s" % _src, _exp)(
        lambda sc=_sc: d.morale_bonus(sc))
S.case("morale-no-combat", "defense.md Morale: only while combat is active", 0)(
    lambda: d.morale_bonus(6, combat_active=False))

# gear.md Weight, Examples [OWNER confirmed] (in L: 5.9 B = 59 L).
for _mod, _exp in [(0, (59, 109)), (2, (79, 129)), (-2, (39, 89)),
                   (3, (89, 139)), (-1, (49, 99))]:
    S.case("load%+d" % _mod, "gear.md Weight Examples [OWNER confirmed]", _exp)(
        lambda m=_mod: d.load_thresholds_l(m))
S.case("load-status", "gear.md Weight: light to 5.9, heavy to 10.9, above overload",
       ("light", "heavy", "heavy", "overload"))(
    lambda: tuple(d.load_status(w, 0) for w in (59, 60, 109, 110)))

S.case("ability-mod", "PF modifier floor((x-10)/2)", (-1, 0, 2, 4))(
    lambda: tuple(d.ability_mod(x) for x in (9, 10, 14, 18)))

if __name__ == "__main__":
    sys.exit(S.run())
