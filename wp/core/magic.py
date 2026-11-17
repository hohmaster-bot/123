"""Spell cost (RULES/classes_magic.md "Spell cost", resources.md "Spirit, mana, overload").

Mage (mana user), circle 1-9: mana = spell mana cost, balance = same, overload = X.
Non-mage (slots), circle 1-9: one slot of that circle, no balance, overload = 2X.
Cantrip (circle 0): a circle-0 slot if the character has any (even mana users),
otherwise unlimited; overload 2X for everyone.
X = spell duration in rounds; instant cast = 0, so overload 0.
Overload > 0 forbids balance regen.
"""
from dataclasses import dataclass, replace
from typing import Dict, Optional

from wp.core.damage import Pool

MAGE = "mana"
SLOTS = "slots"


@dataclass(frozen=True)
class CastCost:
    mana: int
    balance: int
    slot_circle: Optional[int]    # None = no slot spent
    overload: int


@dataclass(frozen=True)
class CasterState:
    mana: Pool
    balance: Pool
    slots: Dict[int, Pool]
    overload: int = 0


def cast_cost(caster, circle, duration_rounds, mana_cost=0, circle0_slots=0):
    """Cost of one cast. caster: MAGE or SLOTS. circle0_slots: max circle-0 slots."""
    circle = int(circle)
    x = int(duration_rounds)
    if not 0 <= circle <= 9:
        raise ValueError("circle must be 0..9")
    if x < 0:
        raise ValueError("duration must be >= 0")
    if circle == 0:
        slot = 0 if circle0_slots > 0 else None
        return CastCost(mana=0, balance=0, slot_circle=slot, overload=2 * x)
    if caster == MAGE:
        m = int(mana_cost)
        return CastCost(mana=m, balance=m, slot_circle=None, overload=x)
    if caster == SLOTS:
        return CastCost(mana=0, balance=0, slot_circle=circle, overload=2 * x)
    raise ValueError("unknown caster type: %r" % (caster,))


def can_pay(state, cost):
    if state.mana.current < cost.mana:
        return False
    if cost.slot_circle is not None:
        p = state.slots.get(cost.slot_circle)
        if p is None or p.current < 1:
            return False
    return True


def pay_cast(state, cost):
    """Apply a cast cost. Balance floors at 0 (no OT from casting: RULES give none)."""
    if not can_pay(state, cost):
        raise ValueError("not enough mana or slots")
    slots = dict(state.slots)
    if cost.slot_circle is not None:
        p = slots[cost.slot_circle]
        slots[cost.slot_circle] = replace(p, current=p.current - 1)
    bal = state.balance
    return replace(
        state,
        mana=replace(state.mana, current=state.mana.current - cost.mana),
        balance=replace(bal, current=max(0, bal.current - cost.balance)),
        slots=slots,
        overload=state.overload + cost.overload,
    )


def balance_regen_blocked(overload):
    """Overload > 0 forbids balance regen."""
    return int(overload) > 0
