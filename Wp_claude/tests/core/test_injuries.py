"""Core OT, injuries, stat damage vs RULES/. Run: python Wp_claude/tests/core/test_injuries.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core.damage import Pool  # noqa: E402
from wp.core import injuries as inj  # noqa: E402

S = Suite("test_injuries")

# injuries.md: light / medium / heavy removes 2 / 5 / 12 OT; base RL 3 / 2 / 1.
for _sev, _ot, _rl in [(inj.LIGHT, 2, 3), (inj.MEDIUM, 5, 2), (inj.HEAVY, 12, 1)]:
    S.case("injury-%s" % _sev, "injuries.md Trauma points + Healing rating [OWNER]", (20 - _ot, _rl))(
        lambda sev=_sev: (lambda t, i: (t, i.heal_rating))(*inj.take_injury(20, sev)))


@S.case("injury-not-enough-ot", "injuries.md: injury is traded for OT", "rejected")
def _not_enough():
    try:
        inj.take_injury(4, inj.HEAVY)
    except ValueError:
        return "rejected"
    return "allowed"


S.case("comfort-ot", "injuries.md: 1 comfort removes 3 OT", (7, 0))(
    lambda: (lambda t, c: (t, c.current))(*inj.spend_comfort_for_ot(10, Pool(1, 10))))

S.case("comfort-ot-floor", "injuries.md: OT never below 0", 0)(
    lambda: inj.spend_comfort_for_ot(2, Pool(1, 10))[0])

for _mod, _exp in [(0, 2), (1, 2), (4, 4)]:
    S.case("attention-ot-mod%d" % _mod, "injuries.md: 1 attention removes max(2, Str mod) OT", 10 - _exp)(
        lambda md=_mod: inj.spend_attention_for_ot(10, Pool(1, 1), md)[0])

S.case("rl-attention", "injuries.md: 1 attention raises light RL 3 -> 5 at minimum", 5)(
    lambda: inj.raise_heal_rating(inj.take_injury(10, inj.LIGHT)[1], Pool(1, 1), 0)[0].heal_rating)


@S.case("remove-no-ot-back", "buffs.md Test: removing an injury must NOT bring OT back", (8, 0))
def _remove():
    trauma, i = inj.take_injury(10, inj.LIGHT)
    left = inj.remove_injury((i,), 0)
    return (trauma, len(left))


S.case("delete-ot", "injuries.md: manual delete of OT always allowed", 0)(
    lambda: inj.delete_ot(3, 5))

# stats.md Tests.
S.case("stat-drain", "stats.md Tests: Str 18/18, drain 1 -> 17/18", (17, 18))(
    lambda: (lambda p: (p.current, p.max))(inj.damage_stat(Pool(18, 18), 1)))

S.case("stat-restore", "stats.md Tests: 17/18 + 1 -> 18/18 (not above max)", (18, 18))(
    lambda: (lambda p: (p.current, p.max))(inj.restore_stat(Pool(17, 18), 3)))

S.case("stat-permanent", "stats.md Tests: permanent Con damage 1 -> max 17, current min(current, 17)",
       ((17, 17), (15, 17)))(
    lambda: tuple((p.current, p.max) for p in (inj.permanent_stat_damage(Pool(18, 18), 1),
                                                inj.permanent_stat_damage(Pool(15, 18), 1))))

if __name__ == "__main__":
    sys.exit(S.run())
