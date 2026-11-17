"""Core damage pipeline vs numbers in RULES/. Run: python Wp_claude/tests/core/test_damage.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core.damage import (Absorber, DamagePart, Pool, Reductions, Vitals,  # noqa: E402
                            PHYSICAL, apply_percent, restore, set_value,
                            take_damage, take_hit)

S = Suite("test_damage")


def vit(hp=30, balance=10, temp=0, absorbers=()):
    return Vitals(hp=Pool(hp, 30), balance=Pool(balance, 10), temp_hp=temp,
                  absorbers=tuple(absorbers))


# resources.md HP and temp HP, Example: 3 temp HP, 7 damage -> temp 0, HP -4, balance -4.
@S.case("temp-hp", "resources.md temp HP Example", (0, -4, -4))
def _temp():
    v, _ = take_damage(vit(temp=3), 7)
    return (v.temp_hp, v.hp.current - 30, v.balance.current - 10)


# resources.md Balance Example [OWNER]: balance 1, hit 10 -> HP -10, balance 0, trauma +9, pain +1.
@S.case("overflow-1", "resources.md Balance Example [OWNER]", (-10, 0, 9, 1))
def _over1():
    v, _ = take_damage(vit(balance=1), 10)
    return (v.hp.current - 30, v.balance.current, v.trauma, v.pain)


# ... then hits 1 and 1: totals HP -12, pain 3, trauma 11.
@S.case("overflow-3", "resources.md Balance Example [OWNER]", (-12, 0, 11, 3))
def _over3():
    v = vit(balance=1)
    for amount in (10, 1, 1):
        v, _ = take_damage(v, amount)
    return (v.hp.current - 30, v.balance.current, v.trauma, v.pain)


@S.case("no-overflow-no-pain", "resources.md Balance: pain only with overflow > 0", (0, 0))
def _no_over():
    v, _ = take_damage(vit(balance=10), 4)
    return (v.pain, v.trauma)


@S.case("hp-below-0", "resources.md: HP can go below 0", -5)
def _neg():
    v, _ = take_damage(vit(hp=5, balance=0), 10)
    return v.hp.current


# resources.md Damage pipeline, Rounding [OWNER]: 10 dmg, 25% -> 7.5 -> 8.
S.case("round-up", "resources.md Rounding [OWNER]", 8)(lambda: apply_percent(10, 25))


# resources.md Damage pipeline Example: 10 fire, 50% -> 5, flat 2 -> 3, temp 0 -> HP -3, balance -3.
@S.case("fire-example", "resources.md Damage pipeline Example [OWNER]", (-3, -3))
def _fire():
    red = Reductions(percent={"fire": 50}, flat={"fire": 2})
    v, _ = take_damage(vit(), 10, "fire", red)
    return (v.hp.current - 30, v.balance.current - 10)


# resources.md step 2: DR is flat vs PHYSICAL; does not work on fire.
@S.case("dr-not-fire", "resources.md Damage pipeline step 2 [OWNER]", (10, 8))
def _dr():
    red = Reductions(flat={PHYSICAL: 2})
    v1, r1 = take_damage(vit(), 10, "fire", red)
    v2, r2 = take_damage(vit(), 10, PHYSICAL, red)
    return (r1.after_reduction, r2.after_reduction)


# resources.md step 2 (numbers from owner task): 8 physical + 3 fire, DR 2, fire resist 1 -> 6 + 2 = 8.
@S.case("parts", "resources.md Damage pipeline step 2 (owner numbers)", (8, -8))
def _parts():
    red = Reductions(flat={PHYSICAL: 2, "fire": 1})
    v, r = take_hit(vit(), [DamagePart(8, PHYSICAL), DamagePart(3, "fire")], red)
    return (r.after_reduction, v.hp.current - 30)


@S.case("parts-one-pain", "resources.md: pain +1 per HIT (one hit, two parts)", 1)
def _parts_pain():
    v, _ = take_hit(vit(balance=0), [DamagePart(5, PHYSICAL), DamagePart(5, "fire")])
    return v.pain


# resources.md steps 3-5 (derived from rule text): temp HP 2, mana analog 3, 7 dmg.
@S.case("absorber-order", "resources.md steps 3-5 + classes_magic.md absorbers",
        (0, 0, -2, -2))
def _order():
    v, _ = take_damage(vit(temp=2, absorbers=[Absorber("mana", 3)]), 7)
    return (v.temp_hp, v.absorbers[0].current, v.hp.current - 30, v.balance.current - 10)


@S.case("absorber-no-balance", "classes_magic.md: absorbed part does not hit balance", (10, 30))
def _abs_bal():
    v, _ = take_damage(vit(absorbers=[Absorber("mana", 5)]), 5)
    return (v.balance.current, v.hp.current)


# resources.md Over max [OWNER, confirmed]: restore clamps, set does not.
S.case("restore-clamp", "resources.md Over max: restore clamps", 30)(
    lambda: restore(Pool(25, 30), 10).current)
S.case("restore-over-kept", "resources.md Over max: over-max not trimmed by restore", 35)(
    lambda: restore(Pool(35, 30), 5).current)


@S.case("set-over-max", "resources.md Over max: set without clamp, flagged", (40, True))
def _set():
    p = set_value(Pool(10, 30), 40)
    return (p.current, p.over_max)


S.case("set-in-range", "resources.md Over max: not flagged within max", False)(
    lambda: set_value(Pool(10, 30), 30).over_max)

if __name__ == "__main__":
    sys.exit(S.run())
