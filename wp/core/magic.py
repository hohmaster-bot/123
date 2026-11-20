"""Spell cost (RULES/classes_magic.md "Spell cost", resources.md "Spirit, mana, overload").

Mage (mana user), circle 1-9: mana = spell mana cost, balance = same, overload = X.
Non-mage (slots), circle 1-9: one slot of that circle, no balance, overload = 2X.
Cantrip (circle 0): a circle-0 slot if the character has any (even mana users),
otherwise unlimited; overload 2X for everyone.
X = casting time in ACTIONS (standard action = 2, usually 2); spell duration does
not matter (owner change). The default comes from the formula; the player may
type another value at the cast. Overload > 0 forbids balance regen; it drops by 1
per zero-initiative tick (tick.py).
Mage with less balance than the cost: balance -> 0, +1 pain, OT = missing part,
concentration DC = 10 + 2 * OT (else the spell fails).
Spell from a magic item / consumable: no overload, no balance (item activation
costs spirit; that is a separate operation).
"""
from dataclasses import dataclass, replace
from typing import Dict, Optional

from wp.core.damage import Pool

MAGE = "mana"
SLOTS = "slots"
# Mana cost by circle 0..9 (spells.md [OWNER, package 10]); a spell may state its own cost instead.
CIRCLE_MANA = (0, 1, 3, 5, 7, 9, 11, 13, 15, 17)


CIRCLES = tuple(range(len(CIRCLE_MANA)))   # valid circles 0..9 (package 16 B: no circle 10 or above)


def valid_circle(circle):
    return isinstance(circle, int) and not isinstance(circle, bool) and circle in CIRCLES


def circle_mana(circle):
    return CIRCLE_MANA[int(circle)]


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
    pain: int = 0
    trauma: int = 0


@dataclass(frozen=True)
class CastResult:
    ot_gained: int = 0
    pain_gained: int = 0
    concentration_dc: Optional[int] = None   # None = no check needed


CONCENTRATION_BASE = 10
CONCENTRATION_PER_OT = 2


def concentration_dc(ot_gained):
    """DC = 10 + 2 * OT gained from the cast; no check when no OT."""
    if ot_gained <= 0:
        return None
    return CONCENTRATION_BASE + CONCENTRATION_PER_OT * int(ot_gained)


STANDARD_ACTION = 2      # combat.md: shift 1, move 1, standard 2, full-round 3, complete 4


def default_overload(caster, circle, cast_actions=STANDARD_ACTION, from_item=False):
    """Formula default: mage X, non-mage (slot) 2X, cantrip 2X for everyone,
    item / consumable 0. X = casting time in actions."""
    x = int(cast_actions)
    if x < 0:
        raise ValueError("casting time must be >= 0")
    if from_item:
        return 0
    if int(circle) == 0 or caster == SLOTS:
        return 2 * x
    if caster == MAGE:
        return x
    raise ValueError("unknown caster type: %r" % (caster,))


def cast_cost(caster, circle, cast_actions=STANDARD_ACTION, mana_cost=0, circle0_slots=0,
              from_item=False, overload=None, extra_mana=0, extra_balance=0):
    """Cost of one cast. caster: MAGE or SLOTS. cast_actions: casting time in actions.
    circle0_slots: max circle-0 slots. overload: value typed in by hand (None = formula).
    from_item: spell from a magic item / consumable -> no overload, no balance,
    no mana, no slot (the item pays; its spirit activation is separate).
    extra_mana / extra_balance: armor spell penalty for a mage, split by the player (package 9 I)."""
    circle = int(circle)
    if not 0 <= circle <= 9:
        raise ValueError("circle must be 0..9")
    ov = default_overload(caster, circle, cast_actions, from_item)
    if overload is not None:
        if int(overload) < 0:
            raise ValueError("overload must be >= 0")
        ov = int(overload)
    if from_item:
        return CastCost(mana=0, balance=0, slot_circle=None, overload=ov)
    if circle == 0:
        slot = 0 if circle0_slots > 0 else None
        return CastCost(mana=0, balance=0, slot_circle=slot, overload=ov)
    if caster == MAGE:
        m = int(mana_cost)
        return CastCost(mana=m + max(0, int(extra_mana)), balance=m + max(0, int(extra_balance)),
                        slot_circle=None, overload=ov)
    return CastCost(mana=0, balance=0, slot_circle=circle, overload=ov)


def can_pay(state, cost):
    if state.mana.current < cost.mana:
        return False
    if cost.slot_circle is not None:
        p = state.slots.get(cost.slot_circle)
        if p is None or p.current < 1:
            return False
    return True


def cast(state, cost):
    """Apply a cast cost. Returns (new_state, CastResult).

    Balance short: balance -> 0, +1 pain, OT = missing part, concentration DC shown.
    """
    if not can_pay(state, cost):
        raise ValueError("not enough mana or slots")
    slots = dict(state.slots)
    if cost.slot_circle is not None:
        p = slots[cost.slot_circle]
        slots[cost.slot_circle] = replace(p, current=p.current - 1)
    bal = max(0, state.balance.current)
    missing = max(0, cost.balance - bal)
    pain = 1 if missing > 0 else 0
    new = replace(
        state,
        mana=replace(state.mana, current=state.mana.current - cost.mana),
        balance=replace(state.balance, current=max(0, bal - cost.balance)),
        slots=slots,
        overload=state.overload + cost.overload,
        pain=state.pain + pain,
        trauma=state.trauma + missing,
    )
    return new, CastResult(ot_gained=missing, pain_gained=pain,
                           concentration_dc=concentration_dc(missing))


def pay_cast(state, cost):
    """Like cast(), but returns only the new state."""
    return cast(state, cost)[0]


def balance_regen_blocked(overload):
    """Overload > 0 forbids balance regen."""
    return int(overload) > 0
