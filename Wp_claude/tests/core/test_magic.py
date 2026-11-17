"""Core spell cost vs RULES/classes_magic.md. Run: python Wp_claude/tests/core/test_magic.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core.damage import Pool  # noqa: E402
from wp.core import magic as m  # noqa: E402

S = Suite("test_magic")


def caster(slots=None):
    return m.CasterState(mana=Pool(10, 10), balance=Pool(10, 10),
                         slots=slots or {})


def delta(state, cost):
    s = m.pay_cast(state, cost)
    slot = None
    if cost.slot_circle is not None:
        slot = s.slots[cost.slot_circle].current - state.slots[cost.slot_circle].current
    return (s.mana.current - 10, s.balance.current - 10, slot, s.overload)


# classes_magic.md Examples [OWNER, changed]: overload X = casting time in actions (standard 2).
S.case("mage-standard", "classes_magic.md Example: mage circle 2, 3 mana, standard action",
       (-3, -3, None, 2))(lambda: delta(caster(), m.cast_cost(m.MAGE, 2, 2, mana_cost=3)))
S.case("mage-full-round", "classes_magic.md Example: full-round (3 actions) -> mage +3",
       (-3, -3, None, 3))(lambda: delta(caster(), m.cast_cost(m.MAGE, 2, 3, mana_cost=3)))
S.case("nonmage-standard", "classes_magic.md Example: non-mage circle 1, standard -> slot -1, +4",
       (0, 0, -1, 4))(lambda: delta(caster({1: Pool(2, 2)}), m.cast_cost(m.SLOTS, 1)))
S.case("nonmage-full-round", "classes_magic.md Example: full-round -> non-mage +6",
       (0, 0, -1, 6))(lambda: delta(caster({1: Pool(2, 2)}), m.cast_cost(m.SLOTS, 1, 3)))
S.case("resources-example", "resources.md Example: mage +2, non-mage +4 for the same spell", (2, 4))(
    lambda: (m.cast_cost(m.MAGE, 2, mana_cost=3).overload, m.cast_cost(m.SLOTS, 2).overload))
S.case("default-standard", "classes_magic.md: usually 2 actions by default", 2)(
    lambda: m.cast_cost(m.MAGE, 1, mana_cost=1).overload)
S.case("manual-overload", "classes_magic.md [OWNER]: value typed in by hand at the cast", 5)(
    lambda: m.cast_cost(m.MAGE, 1, mana_cost=1, overload=5).overload)
S.case("mage-0mana", "classes_magic.md: 0 mana -> 0 balance",
       (0, 0, None, 2))(lambda: delta(caster(), m.cast_cost(m.MAGE, 1, 2, mana_cost=0)))

# Cantrips (circle 0): overload 2X for everyone (X = casting time).
S.case("cantrip-slot-mage", "classes_magic.md: cantrip spends circle-0 slot, even mana users",
       (0, 0, -1, 4))(lambda: delta(caster({0: Pool(3, 3)}),
                                    m.cast_cost(m.MAGE, 0, 2, mana_cost=1, circle0_slots=3)))
S.case("cantrip-unlimited", "classes_magic.md: no circle-0 slot at all -> unlimited, overload 2X",
       m.CastCost(0, 0, None, 4))(lambda: m.cast_cost(m.SLOTS, 0, 2, circle0_slots=0))


@S.case("no-slot", "classes_magic.md: non-mage without a slot cannot cast", "rejected")
def _no_slot():
    try:
        m.pay_cast(caster({1: Pool(0, 2)}), m.cast_cost(m.SLOTS, 1, 1))
    except ValueError:
        return "rejected"
    return "allowed"


@S.case("overload-adds", "resources.md: new casts add overload", 10)
def _adds():
    s = caster()
    for _ in range(2):
        s = m.pay_cast(s, m.cast_cost(m.MAGE, 1, mana_cost=1, overload=5))
    return s.overload


# classes_magic.md [OWNER]: balance 2, cost 5 -> balance 0, OT 3, pain 1, DC 16.
@S.case("balance-short", "classes_magic.md Example [OWNER]: balance 2, cost 5",
        (0, 3, 1, 16, 3, 1))
def _short():
    s0 = m.CasterState(mana=Pool(10, 10), balance=Pool(2, 10), slots={})
    s, res = m.cast(s0, m.cast_cost(m.MAGE, 3, 1, mana_cost=5))
    return (s.balance.current, s.trauma, s.pain, res.concentration_dc,
            res.ot_gained, res.pain_gained)


@S.case("balance-enough-no-check", "classes_magic.md: enough balance -> no OT, no pain, no DC",
        (0, 0, None))
def _enough():
    s0 = m.CasterState(mana=Pool(10, 10), balance=Pool(5, 10), slots={})
    s, res = m.cast(s0, m.cast_cost(m.MAGE, 3, 1, mana_cost=5))
    return (s.trauma, s.pain, res.concentration_dc)


# classes_magic.md [OWNER]: spells from items/consumables: no overload, no balance.
@S.case("from-item", "classes_magic.md [OWNER]: item spell, no overload, no balance",
        (0, 0, None, 0))
def _item():
    return delta(caster(), m.cast_cost(m.MAGE, 3, 5, mana_cost=5, from_item=True))


S.case("regen-blocked", "resources.md: overload > 0 forbids balance regen", (True, False))(
    lambda: (m.balance_regen_blocked(1), m.balance_regen_blocked(0)))

if __name__ == "__main__":
    sys.exit(S.run())
