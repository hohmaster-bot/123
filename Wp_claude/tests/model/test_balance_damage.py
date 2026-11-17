"""Group D: damage straight to the balance (empty-hand parry, owner).
Run: python Wp_claude/tests/model/test_balance_damage.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import dispatch  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import Character  # noqa: E402

S = Suite("test_balance_damage")


def fighter(balance=6, **kw):
    """HP 30/30, BP 6 -> balance max 6."""
    base = dict(hp_rolls=(30,), hp_current=30, bp_current=6, balance_current=balance)
    base.update(kw)
    return Character(**base)


def hit(ch, n):
    return dispatch(ch, "damage_to_balance", amount=n).state


# Balance 6, damage 4 -> balance 2, HP unchanged (30), no OT, no pain.
S.case("d-basic", "owner: damage to balance, HP untouched", (2, 30, 0, 0))(
    lambda: (lambda c: (c.balance_current, c.hp_current, c.trauma, dv.pain_total(c)))(hit(fighter(), 4)))
# Balance 2, damage 5 -> balance 0, overflow 3 -> OT +3, pain +1, HP unchanged.
S.case("d-overflow", "owner: overflow -> OT and +1 pain, HP untouched", (0, 3, 1, 30))(
    lambda: (lambda c: (c.balance_current, c.trauma, dv.pain_total(c), c.hp_current))(hit(fighter(2), 5)))
# In combat the cap drops by 1 when the balance really lost points: max 6 -> 5.
S.case("d-cap", "owner: in combat the balance cap drops by 1", (2, 5))(
    lambda: (lambda c: (c.balance_current, dv.balance_max(c)))(hit(dispatch(fighter(), "start_combat").state, 4)))
# Balance already 0, damage 3: the balance lost nothing -> the cap does not drop (6); overflow still -> OT 3.
S.case("d-cap-no-loss", "owner: cap drops only if the balance really lost points", (6, 3))(
    lambda: (lambda c: (dv.balance_max(c), c.trauma))(hit(dispatch(fighter(0), "start_combat").state, 3)))
# Damage 0 changes nothing.
S.case("d-zero", "owner: damage 0 changes nothing", (6, 30, 0, 0, 6))(
    lambda: (lambda c: (c.balance_current, c.hp_current, c.trauma, dv.pain_total(c), dv.balance_max(c)))(
        hit(dispatch(fighter(), "start_combat").state, 0)))
# No percent / DR: the player types the number; temp HP are not used either.
S.case("d-no-temp-hp", "owner: straight to the balance, temp HP not used", (2, 5))(
    lambda: (lambda c: (c.balance_current, c.temp_hp))(hit(fighter(temp_hp=5), 4)))

if __name__ == "__main__":
    sys.exit(S.run())
