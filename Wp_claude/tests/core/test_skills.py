"""Core skills vs RULES/skills.md. Run: python Wp_claude/tests/core/test_skills.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core import skills as sk  # noqa: E402
from wp.core.skills import Skill  # noqa: E402

S = Suite("test_skills")

# skills.md Training cost, Tests [OWNER].
for _tier, _new, _lvl, _exp in [(sk.NORMAL, 1, 1, 20), (sk.NORMAL, 3, 3, 60), (sk.NORMAL, 20, 20, 400),
                                (sk.ADVANCED, 1, 1, 15), (sk.SPECIALIZED, 6, 5, 60),
                                (sk.SPECIALIZED, 20, 19, 200)]:
    S.case("rank-%s-%d-lvl%d" % (_tier[:4], _new, _lvl), "skills.md Training cost Tests [OWNER]", _exp)(
        lambda t=_tier, n=_new, l=_lvl: sk.rank_step_cost(t, n, l))

S.case("spec-up-to-level-free", "skills.md: specialized ranks up to level are free", 0)(
    lambda: sk.ranks_cost(sk.SPECIALIZED, 0, 5, 5))
S.case("ranks-sum", "skills.md: normal 0->3 = 20+40+60", 120)(
    lambda: sk.ranks_cost(sk.NORMAL, 0, 3, 3))


@S.case("normal-cap", "skills.md: normal ranks cannot exceed level", "rejected")
def _cap():
    try:
        sk.rank_step_cost(sk.NORMAL, 4, 3)
    except ValueError:
        return "rejected"
    return "allowed"


@S.case("advanced-cap", "owner: advanced ranks cannot exceed level either", "rejected")
def _adv_cap():
    try:
        sk.rank_step_cost(sk.ADVANCED, 4, 3)
    except ValueError:
        return "rejected"
    return "allowed"


S.case("spec-no-cap", "skills.md: specialized has no rank cap (level 3 -> rank 10 = 100)", 100)(
    lambda: sk.rank_step_cost(sk.SPECIALIZED, 10, 3))

# skills.md Examples.
S.case("2nd-advanced", "skills.md Example: 2nd advanced skill = 40+20*1", 60)(
    lambda: sk.promote_cost([Skill("a", "int", sk.ADVANCED), Skill("b", "int")], "b"))
S.case("3rd-spec", "skills.md Example: 3rd specialization = 200+50*2", 300)(
    lambda: sk.specialize_cost([Skill("a", "int", sk.SPECIALIZED), Skill("b", "int", sk.SPECIALIZED),
                                Skill("c", "int", sk.ADVANCED)], "c"))
# skills.md Creation: free specialization still counts -> second costs 250.
S.case("free-spec-counts", "skills.md Creation Example [OWNER]", 250)(
    lambda: sk.specialize_cost([Skill("free", "int", sk.SPECIALIZED), Skill("b", "int", sk.ADVANCED)], "b"))
S.case("normal-to-spec", "skills.md: normal -> specialized = 40 + 200 (no others)", 240)(
    lambda: sk.tier_cost([Skill("a", "int")], "a", sk.SPECIALIZED))

# skills.md Roll bonus: ranks + stat mod + bonuses + armor penalty (+3 if advanced).
S.case("bonus-normal", "skills.md Roll bonus", 6)(
    lambda: sk.roll_bonus(Skill("climb", "str", ranks=3, armor_penalty_applies=True), 3, 2, 3, -2))
S.case("bonus-advanced", "skills.md Roll bonus: +3 if advanced", 9)(
    lambda: sk.roll_bonus(Skill("climb", "str", sk.ADVANCED, 3, True), 3, 2, 3, -2))
S.case("bonus-no-armor", "skills.md: armor penalty only if it applies", 8)(
    lambda: sk.roll_bonus(Skill("know", "int", sk.NORMAL, 3), 3, 2, 3, -2))
S.case("spec-ranks-floor-level", "skills.md: specialized ranks auto rise to level", (7, 9))(
    lambda: (sk.effective_ranks(Skill("a", "int", sk.SPECIALIZED, 2), 7),
             sk.effective_ranks(Skill("a", "int", sk.SPECIALIZED, 9), 7)))

if __name__ == "__main__":
    sys.exit(S.run())
