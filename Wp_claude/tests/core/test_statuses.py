"""Core negative-HP states vs RULES/resources.md. Run: python Wp_claude/tests/core/test_statuses.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core import statuses as st  # noqa: E402
from wp.core.statuses import NegativeTraits as T  # noqa: E402

S = Suite("test_statuses")

S.case("hp-loss", "resources.md: dying 2, resting 1, stabilized 0 per tick", (2, 1, 0))(
    lambda: tuple(st.hp_loss_per_tick(x) for x in (st.DYING, st.RESTING, st.STABILIZED)))
S.case("diehard-loss", "resources.md: Diehard 0 (custom possible)", (0, 1))(
    lambda: (st.hp_loss_per_tick(st.DYING, T(diehard=True)),
             st.hp_loss_per_tick(st.DYING, T(diehard=True, diehard_hp_loss=1))))

# resources.md Example [OWNER]: move (1, clean) + special attack (2 actions) in base dying -> 2 pain.
S.case("dying-example", "resources.md Example [OWNER]: move + 2-action attack -> 2 pain", 2)(
    lambda: st.action_pain(1 + 2, st.DYING))
S.case("diehard-example", "resources.md: Diehard 2 clean, 3rd painful -> 1 pain", 1)(
    lambda: st.action_pain(3, st.DYING, T(diehard=True)))
S.case("one-clean", "resources.md: 1 clean action -> no pain", 0)(lambda: st.action_pain(1, st.DYING))
S.case("concentration", "resources.md: DC 20 success clears one more slot", (1, 0))(
    lambda: (st.action_pain(3, st.DYING, concentration_successes=1),
             st.action_pain(3, st.DYING, concentration_successes=5)))
S.case("painful-slots", "resources.md: painful slots shown red", ((2, 3), (3,), ()))(
    lambda: (st.painful_slots(st.DYING), st.painful_slots(st.DYING, T(diehard=True)),
             st.painful_slots(st.DYING, concentration_successes=2)))
S.case("unconscious", "resources.md: resting and stabilized are unconscious", (True, False, False))(
    lambda: tuple(st.can_act(x) for x in (st.DYING, st.RESTING, st.STABILIZED)))


@S.case("unconscious-no-actions", "resources.md: unconscious cannot act", "rejected")
def _no_act():
    try:
        st.action_pain(1, st.RESTING)
    except ValueError:
        return "rejected"
    return "allowed"


S.case("no-state-at-0", "resources.md: states only while HP < 0", None)(
    lambda: st.choose_state(0, st.DYING))


@S.case("stabilize-needs", "resources.md: stabilize needs auto-stabilize or a d100 90+ roll",
        ("rejected", st.STABILIZED, st.STABILIZED))
def _stab():
    try:
        st.choose_state(-3, st.STABILIZED)
        a = "allowed"
    except ValueError:
        a = "rejected"
    return (a, st.choose_state(-3, st.STABILIZED, T(auto_stabilize=True)),
            st.choose_state(-3, st.STABILIZED, stabilize_roll_ok=True))


if __name__ == "__main__":
    sys.exit(S.run())
