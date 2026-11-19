"""Core zero-initiative phase vs RULES/resources.md. Run: python Wp_claude/tests/core/test_tick.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core import effects as ef  # noqa: E402
from wp.core import statuses as st  # noqa: E402
from wp.core.damage import Pool, Vitals  # noqa: E402
from wp.core.effects import Status  # noqa: E402
from wp.core.tick import TickState, zero_initiative  # noqa: E402

S = Suite("test_tick")

BLEED = Status("bleed", per_tick_hp=-2, duration=ef.TICKS, remaining=3)


def state(balance=0, overload=0, statuses=(BLEED,), hp=20, neg=None, traits=st.NegativeTraits()):
    return TickState(vitals=Vitals(hp=Pool(hp, 20), balance=Pool(balance, 10)),
                     statuses=tuple(statuses), overload=overload, balance_regen=3,
                     negative_state=neg, traits=traits)


# resources.md Zero initiative: balance FIRST, then DoT.
# Balance 0, regen 3, bleed 2 -> balance 3 -> 1, HP -2, no overflow (no OT, no pain).
@S.case("order-balance-then-dot", "resources.md Zero initiative [OWNER]: balance first, then DoT",
        (1, 18, 0, 0))
def _order():
    s, _ = zero_initiative(state())
    v = s.vitals
    return (v.balance.current, v.hp.current, v.trauma, v.pain)


S.case("steps", "resources.md: 1 durations, 2 balance, 3 DoT", ("durations", "balance", "dot"))(
    lambda: zero_initiative(state())[1].steps)
S.case("duration-down", "resources.md step 1: durations -1", 2)(
    lambda: zero_initiative(state())[0].statuses[0].remaining)


@S.case("expired-removed", "resources.md step 1: expired statuses end (pkg 11 A: inactive, entry stays; last bleed still hits)",
        ((False,), ("bleed",), 18))
def _expired():
    s, r = zero_initiative(state(statuses=(Status("bleed", per_tick_hp=-2, duration=ef.TICKS, remaining=1),)))
    return (tuple(x.active for x in s.statuses), r.expired, s.vitals.hp.current)


@S.case("bleed-3-rounds", "resources.md [OWNER]: bleed for 3 rounds hits exactly 3 times", (14, ()))
def _bleed3():
    s = state(hp=20, balance=10)
    hits = []
    for _ in range(4):
        before = s.vitals.hp.current
        s, _ = zero_initiative(s)
        hits.append(before - s.vitals.hp.current)
    return (s.vitals.hp.current, tuple(x for x in s.statuses if x.active)) if hits == [2, 2, 2, 0] else hits


@S.case("overload-falls", "resources.md [OWNER]: overload -1 per tick, gone at 0", (3, 2, 1, 0, 0))
def _ov_falls():
    s = state(overload=4, statuses=())
    out = []
    for _ in range(5):
        s, _ = zero_initiative(s)
        out.append(s.overload)
    return tuple(out)


@S.case("overload-blocks", "resources.md: overload > 0 forbids balance regen", (0, True, 1))
def _overload():
    s, r = zero_initiative(state(overload=2, statuses=()))
    return (s.vitals.balance.current, r.regen_blocked, s.overload)


@S.case("heal-per-tick", "buffs.md [OWNER]: heal per tick is an ordinary status, clamped at max", 20)
def _heal():
    s, _ = zero_initiative(state(hp=18, statuses=(Status("regen", per_tick_hp=5),)))
    return s.vitals.hp.current


@S.case("dying-loss", "resources.md: dying -2 HP per tick, hits balance as usual", (-4, 1))
def _dying():
    s, _ = zero_initiative(state(hp=-2, balance=0, statuses=(), neg=st.DYING))
    return (s.vitals.hp.current, s.vitals.balance.current)


@S.case("resting-loss", "resources.md: resting in negatives -1 HP per tick", -3)
def _resting():
    return zero_initiative(state(hp=-2, statuses=(), neg=st.RESTING))[0].vitals.hp.current


@S.case("stabilized-loss", "resources.md: stabilized, no HP loss", -2)
def _stab():
    return zero_initiative(state(hp=-2, statuses=(), neg=st.STABILIZED))[0].vitals.hp.current


@S.case("diehard-loss", "resources.md: Diehard HP loss per tick 0", -2)
def _diehard():
    return zero_initiative(state(hp=-2, statuses=(), neg=st.DYING,
                                 traits=st.NegativeTraits(diehard=True)))[0].vitals.hp.current


if __name__ == "__main__":
    sys.exit(S.run())
