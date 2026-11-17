"""Core pain vs RULES/resources.md. Run: python Wp_claude/tests/core/test_pain.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core import bonuses as bo  # noqa: E402
from wp.core import pain as p  # noqa: E402
from wp.core.pain import PainEntry as E, PainProfile  # noqa: E402

S = Suite("test_pain")

_LIST = (E(2, "balance overflow"), E(1, "ability cost"), E(1, "curse", permanent=True))

S.case("sum", "resources.md [OWNER]: total = sum of entries", 4)(lambda: p.entries_total(_LIST))
S.case("sum-plus-hp", "resources.md: + pain from HP below 0 (-7 -> 2)", 6)(lambda: p.total_pain(_LIST, -7))
S.case("death-8", "resources.md: death at 8 pain (default cap)", (False, True))(
    lambda: (p.is_dead(7), p.is_dead(8)))
S.case("cap-12", "resources.md [OWNER]: cap changed by race/template/feat (12)", (False, True))(
    lambda: (p.is_dead(11, PainProfile(cap=12)), p.is_dead(12, PainProfile(cap=12))))
S.case("penalty", "resources.md [OWNER]: -1 per pain", -3)(lambda: p.penalty(3))
S.case("penalty-all-rolls", "resources.md [OWNER]: all rolls except the lucky attack",
       (-3, -3, -3, -3, -3, -3, 0, 0))(
    lambda: tuple(bo.total([p.penalty_bonus(3)], t) for t in
                  (bo.ATTACK, bo.DAMAGE, bo.SAVE, bo.SKILL, bo.INITIATIVE, bo.CMB, bo.LUCKY, bo.AC)))
S.case("no-penalty", "resources.md [OWNER]: 'pain gives no penalties'", (0, True))(
    lambda: (p.penalty(5, PainProfile(no_penalty=True)), p.is_dead(8, PainProfile(no_penalty=True))))
S.case("ignores-pain", "resources.md [OWNER]: race ignores pain", (0, False))(
    lambda: (p.penalty(5, PainProfile(ignores_pain=True)), p.is_dead(9, PainProfile(ignores_pain=True))))
S.case("damage-per-pain", "resources.md [OWNER]: race damage bonus per pain", 3)(
    lambda: p.damage_bonus(3, PainProfile(damage_per_pain=1)))
S.case("price-pain", "resources.md [OWNER]: pain as activation price", 5)(
    lambda: p.entries_total(p.add(_LIST, 1, "rage activation")))
S.case("remove-temporary", "rest.md: remove 1 pain (temporary first, permanent stays)", 3)(
    lambda: p.entries_total(p.remove(_LIST, 1)))


@S.case("remove-not-permanent", "resources.md: permanent pain is not removed by rest", "rejected")
def _perm():
    try:
        p.remove((E(1, "curse", permanent=True),), 1)
    except ValueError:
        return "rejected"
    return "allowed"


S.case("long-rest", "rest.md Long rest: all pain except permanent", 1)(
    lambda: p.entries_total(p.clear_temporary(_LIST)))

if __name__ == "__main__":
    sys.exit(S.run())
