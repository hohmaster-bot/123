"""Balance cap in combat (owner homerule) and end of cycle / OV (narrative.md, training.md).
Run: python Wp_claude/tests/model/test_cap_cycle.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.model.notebook import Drive
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core.damage import PHYSICAL, Reductions  # noqa: E402
from wp.core.effects import Status  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import Ability, Character  # noqa: E402

S = Suite("test_cap_cycle")


def fighter(**kw):
    """HP 30/30, BP 6 (current) + no armor + no bonus -> balance max 6; balance 6/6."""
    base = dict(hp_rolls=(30,), hp_current=30, bp_current=6, balance_current=6)
    base.update(kw)
    return Character(**base)


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def bal(ch):
    return (ch.balance_current, dv.balance_max(ch))


IN = ("start_combat", {})


# Owner example: balance 6/6, hit 5 -> balance 1/6, then the cap drops by 1 -> 1/5.
S.case("example-6-6", "owner homerule: 6/6, hit 5 -> 1/5", (1, 5))(
    lambda: bal(run(fighter(), IN, ("take_damage", {"amount": 5}))))

# Two hits (1 and 1): 6/6 -> 5/5 -> 4/4: cap 4.
S.case("two-hits", "owner: two hits -> cap 6 - 2 = 4", 4)(
    lambda: dv.balance_max(run(fighter(), IN, ("take_damage", {"amount": 1}), ("take_damage", {"amount": 1}))))

# A hit fully absorbed by temp HP (5 temp, hit 4): nothing reached HP -> cap stays 6, balance 6.
S.case("temp-hp-absorbs-all", "owner: a fully absorbed hit does not lower the cap", (6, 6))(
    lambda: bal(run(fighter(temp_hp=5), IN, ("take_damage", {"amount": 4}))))

# Hit 7 with temp HP 3: 4 reaches HP -> balance 6 - 4 = 2, cap 6 - 1 = 5.
S.case("temp-hp-partial", "owner: hit 7, temp HP 3 -> 4 reached HP, cap -1", (2, 5))(
    lambda: bal(run(fighter(temp_hp=3), IN, ("take_damage", {"amount": 7}))))

# A hit zeroed by DR (5 physical vs DR 5): nothing reaches HP -> cap stays 6.
S.case("dr-zeroes", "owner: a hit zeroed by DR does not lower the cap", (6, 6))(
    lambda: bal(run(fighter(), IN, ("take_damage", {"amount": 5, "reductions": Reductions(flat={PHYSICAL: 5})}))))

# DoT: bleed 2 per tick, no flag -> cap stays 6 (balance: 6 is max, regen nothing, bleed 2 -> 4).
S.case("dot-no-flag", "owner: DoT does not lower the cap by default", (4, 6))(
    lambda: bal(run(fighter(), IN,
                    ("add_status", {"active": True, "status": Status("bleed", sid="b", per_tick_hp=-2, duration=ef.TICKS), "ticks": 3}),
                    ("tick", {}))))

# DoT with the flag "lowers cap": cap 6 - 1 = 5.
S.case("dot-flag", "owner: DoT with the flag lowers the cap", (4, 5))(
    lambda: bal(run(fighter(), IN,
                    ("add_status", {"active": True, "status": Status("burn", sid="b", per_tick_hp=-2, duration=ef.TICKS,
                                                     lowers_balance_cap=True), "ticks": 3}),
                    ("tick", {}))))

# Out of combat a hit does not lower the cap: 6/6, hit 5 -> 1/6.
S.case("out-of-combat", "owner: counting only while combat is active", (1, 6))(
    lambda: bal(run(fighter(), ("take_damage", {"amount": 5}))))

# After end_combat the cap is back to normal: 6.
S.case("after-end-combat", "owner: end_combat resets the counter, cap 6 again", (6, 0))(
    lambda: (lambda ch: (dv.balance_max(ch), ch.balance_cap_hits))(
        run(fighter(), IN, ("take_damage", {"amount": 1}), ("take_damage", {"amount": 1}), ("end_combat", {}))))

# start_combat also resets a leftover counter.
S.case("start-resets", "owner: start_combat resets the counter", 0)(
    lambda: run(fighter(balance_cap_hits=3), IN).balance_cap_hits)

# The current balance is NOT lowered when the cap drops (only the hit itself lowers it): 6 - 5 = 1, not 0.
S.case("current-not-lowered", "owner: lowering the cap does not lower the current balance", 1)(
    lambda: run(fighter(), IN, ("take_damage", {"amount": 5})).balance_current)


# ------------------------------------------------------------- end of cycle, OV

# Attention 3, OV 4; gain = 1 + 7 // 3 + 2 drives at 4+ = 1 + 2 + 2 = 5 -> Attention 8, OV 0.
@S.case("end-cycle", "narrative.md [OWNER]: attention +5, OV burned", (8, 0, 5))
def _cycle():
    ch = Character(level=7, hp_rolls=(8,) * 7, attention=3, ov=4, drives=(Drive("a", "a", 4), Drive("b", "b", 5), Drive("c", "c", 1)))
    r = dispatch(ch, "end_cycle")
    return (r.state.attention, r.state.ov, r.info["gain"])


def con(score):
    a = dict(Character().abilities)
    a["con"] = Ability(score)
    return a


# convert_attention: 1 Attention -> max(2, Con mod) OV. Con 12 (+1) -> 2; Con 18 (+4) -> 4.
S.case("convert-attention", "training.md: Con mod +1 -> 2 OV, +4 -> 4 OV", ((2, 0), (4, 0)))(
    lambda: tuple((lambda c: (c.ov, c.attention))(dispatch(Character(abilities=con(s), attention=1),
                                                           "convert_attention").state) for s in (12, 18)))


def rejected(ch, cmd, /, **params):
    try:
        dispatch(ch, cmd, **params)
    except CommandError:
        return "rejected"
    return "allowed"


S.case("convert-needs-attention", "training.md: converting needs 1 attention", "rejected")(
    lambda: rejected(Character(attention=0), "convert_attention"))
S.case("spend-ov", "crafting.md / narrative: spend OV", (1, "rejected"))(
    lambda: (dispatch(Character(ov=4), "spend_ov", n=3).state.ov, rejected(Character(ov=2), "spend_ov", n=3)))
S.case("burn-ov", "narrative.md: burn unspent OV by hand", 0)(
    lambda: dispatch(Character(ov=7), "burn_ov").state.ov)

# end_cycle does not touch activations and does not run a long rest (separate buttons).
S.case("cycle-not-long-rest", "rest.md / narrative.md [OWNER]: end of cycle is not a long rest", (1, 0))(
    lambda: (lambda c: (c.hp_current, c.overload))(dispatch(Character(hp_current=1, overload=0), "end_cycle").state))

if __name__ == "__main__":
    sys.exit(S.run())
