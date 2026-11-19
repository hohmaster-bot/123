"""Group A: fixes from REVIEW_REPORT_2.md (each with a test that fails when the formula breaks).
Run: python Wp_claude/tests/model/test_group_a.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from dataclasses import replace  # noqa: E402

from wp.catalog import feats_catalog as fc  # noqa: E402
from wp.catalog import skills_catalog as sc  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import ac as acm  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core import skills as sk  # noqa: E402
from wp.core import statuses as st  # noqa: E402
from wp.core import weapons as wpn  # noqa: E402
from wp.core.damage import PHYSICAL, DamagePart, Pool, Reductions, Vitals, take_hit  # noqa: E402
from wp.core.effects import Effect, OneShot, Status  # noqa: E402
from wp.core.weapons import Pick  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import Ability, Character, Item  # noqa: E402

S = Suite("test_group_a")


def abil(**scores):
    a = dict(Character().abilities)
    for k, v in scores.items():
        a[k] = Ability(v)
    return a


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def hero(**kw):
    base = dict(hp_rolls=(20,), hp_current=20, bp_current=5, balance_current=5)
    base.update(kw)
    return Character(**base)


# A1: rage 2/3 (charges on the status) -> long rest -> 3/3.
S.case("a1-status-charges", "buffs.md / rest.md: long rest restores status charges (rage 2/3 -> 3/3)", 3)(
    lambda: run(hero(statuses=(Status("rage", sid="r", charges=Pool(2, 3)),)), ("long_rest", {})).statuses[0].charges.current)

# A2: HP 10 with state "dying" -> tick -> no HP loss (HP >= 0), state cleared.
S.case("a2-dying-at-positive-hp", "resources.md: states only while HP < 0", (20, None))(
    lambda: (lambda c: (c.hp_current, c.negative_state))(run(hero(negative_state=st.DYING), ("tick", {}))))
# HP -3 dying, healed by 5 -> HP 2 -> state cleared.
S.case("a2-healed-clears", "resources.md: healing to 0+ clears the state", (2, None))(
    lambda: (lambda c: (c.hp_current, c.negative_state))(
        run(hero(hp_current=-3, negative_state=st.DYING), ("restore", {"resource": "hp", "amount": 5}))))
S.case("a2-long-rest-clears", "rest.md: long rest -> HP max -> state cleared", None)(
    lambda: run(hero(hp_current=-3, negative_state=st.RESTING), ("long_rest", {})).negative_state)
S.case("a2-negative-still-loses", "resources.md: at HP < 0 dying still loses 2 per tick", (-5, st.DYING))(
    lambda: (lambda c: (c.hp_current, c.negative_state))(run(hero(hp_current=-3, negative_state=st.DYING), ("tick", {}))))


# A3: +2 to Stealth only; "all skills" +1 for everything. Dex 10, Str 10, 0 ranks:
# stealth = 0 + 2 + 1 = 3; athletics = 0 + 1 = 1.
@S.case("a3-one-skill", "buffs.md: a bonus to one skill applies only to it", (3, 1))
def _a3():
    cat = sc.load_default()
    stt = (Status("cloak", effects=(Effect(bo.skill_target("stealth"), 2, "competence"),)),
           Status("bard song", effects=(Effect(bo.SKILL, 1, bo.MORALE),)))
    ch = Character(statuses=stt, skills=(sc.make_skill(cat, "stealth"), sc.make_skill(cat, "athletics")))
    return (dv.skill_bonus(ch, "stealth"), dv.skill_bonus(ch, "athletics"))


# A4 (package 4): neither buff temp HP nor button temp HP are cleared by the end of combat.
# Buff 5 temp HP (3 ticks) + button temp HP 4. End of combat -> 9 remain.
@S.case("a4-temp-hp-duration", "resources.md [OWNER pkg 4]: end of combat clears no temp HP", (9, 9))
def _a4():
    buff = Status("aid", sid="aid", one_shot=(OneShot(ef.TEMP_HP, 5),), duration=ef.TICKS, temp_hp_stacks=True)
    ch = run(hero(temp_hp=4), ("start_combat", {}), ("add_status", {"active": True, "status": buff, "ticks": 3}))
    before = dv.temp_hp_total(ch)
    return (before, dv.temp_hp_total(run(ch, ("end_combat", {}))))


# The buff's temp HP disappear when the buff expires: 1 tick left -> tick -> 0.
S.case("a4-temp-hp-expire", "owner: temp HP go away with the buff", 0)(
    lambda: dv.temp_hp_total(run(hero(), ("add_status", {"active": True, "status": Status("aid", sid="a", one_shot=(OneShot(ef.TEMP_HP, 5),),
                                                                           duration=ef.TICKS), "ticks": 1}), ("tick", {}))))
# Damage takes the combat pool first, then the buff: pool 4 + buff 5, hit 6 -> pool 0, buff 3.
S.case("a4-temp-hp-order", "resources.md Q23 assumption: button temp HP are used before buff temp HP", (0, 3))(
    lambda: (lambda c: (c.temp_hp, c.statuses[0].temp_hp_left))(
        run(hero(temp_hp=4), ("add_status", {"active": True, "status": Status("aid", sid="a", one_shot=(OneShot(ef.TEMP_HP, 5),),
                                                              duration=ef.TICKS, temp_hp_stacks=True), "ticks": 3}),
            ("take_damage", {"amount": 6}))))
# Short rest after the spends clears ALL temp HP.
S.case("a4-short-rest-clears", "rest.md [OWNER]: short rest clears all temp HP", 0)(
    lambda: dv.temp_hp_total(run(hero(temp_hp=4), ("add_status", {"active": True, "status": Status(
        "aid", sid="a", one_shot=(OneShot(ef.TEMP_HP, 5),), duration=ef.TICKS, temp_hp_stacks=True), "ticks": 3}),
        ("short_rest", {}))))

# A5: Dex 6 (-2): front AC 10 - 2 = 8; flat-footed keeps the penalty: 8. Dex 14 (+2): front 12, flat 10.
S.case("a5-flat-footed-negative-dex", "defense.md: low-Dex penalty stays when flat-footed", ((8, 8), (12, 10)))(
    lambda: tuple((dv.ac(c), dv.ac(c, acm.FLAT_FOOTED)) for c in (Character(abilities=abil(dex=6)),
                                                                   Character(abilities=abil(dex=14)))))
S.case("a5-dodge-lost", "defense.md: dodge bonus lost when flat-footed even with low Dex", 8)(
    lambda: dv.ac(Character(abilities=abil(dex=6), statuses=(Status("d", effects=(Effect(bo.AC, 2, bo.DODGE),)),)),
                  acm.FLAT_FOOTED))

# A6: balance max = armor 2 + current BP 5 (3 + 2 above max, overcap pkg 8 C) + bonus 1 = 8.
S.case("a6-overcap-in-balance", "rest.md [OWNER pkg 8]: balance max includes BP above max", 8)(
    lambda: dv.balance_max(hero(bp_current=5, balance_bonus=1,
                                items=(Item("l", "leather", equipped=True, armor=2),))))

# A7: Cha 8 (-1) -> base 0; penalty -2 -> total never below 0 -> 0.
S.case("a7-spirit-floor", "resources.md [OWNER]: spirit total never below 0", 0)(
    lambda: dv.spirit_max(Character(abilities=abil(cha=8), spirit_bonuses=(("curse", -2),))))


# ------------------------------------------------------------- A8 weak tests

# M1: flat reductions per part: 8 physical + 1 fire, DR 2, fire resist 3 -> 6 + 0 = 6 (summed would be 9 - 5 = 4).
S.case("m1-flat-per-part", "resources.md step 2: flat reduction per typed part", 6)(
    lambda: take_hit(Vitals(Pool(30, 30), Pool(10, 10)), [DamagePart(8, PHYSICAL), DamagePart(1, "fire")],
                     Reductions(flat={PHYSICAL: 2, "fire": 3}))[1].after_reduction)
# M5: model balance max uses CURRENT BP: HP 20 -> BP max 5, current 2, no armor -> balance max 2.
S.case("m5-current-bp", "rest.md: model balance max from CURRENT BP (2 of 5)", (5, 2))(
    lambda: (lambda c: (dv.bp_max(c), dv.balance_max(c)))(hero(bp_current=2)))
# M17/M46: several worn items: armor and natural armor take the MAXIMUM, not the sum.
S.case("m17-m46-max-not-sum", "defense.md: same type -> highest (armor 4 and 2 -> 4; natural 2 and 3 -> 3)", (4, 3, 17))(
    lambda: (lambda c: (dv.armor_bonus(c), dv.ac_input(c).natural, dv.ac(c)))(
        Character(items=(Item("a", "mail", equipped=True, armor=4), Item("b", "vest", equipped=True, armor=2),
                         Item("c", "hide", equipped=True, natural=2), Item("d", "bark", equipped=True, natural=3)))))
# M21: promote counts specialized skills as "other advanced": 40 + 20 * 1 = 60.
S.case("m21-specialized-counts", "skills.md: specialized counts as another advanced skill", 60)(
    lambda: sk.promote_cost([sk.Skill("a", "int", sk.SPECIALIZED), sk.Skill("b", "int")], "b"))


# M37: item with no price cannot be activated; an extra "cost" parameter cannot override the card.
@S.case("m37-no-cost-override", "gear.md: price 0 -> not activatable; no cost override", ("activation price not set", "rejected", 15))
def _m37():
    ch = Character(abilities=abil(cha=14), spirit_current=15, items=(Item("n", "stone", equipped=True),))
    soft = dispatch(ch, "activate_item", iid="n").info.get("refused")
    try:
        dispatch(ch, "activate_item", iid="n", cost=1)
        hard = "allowed"
    except (CommandError, TypeError):
        hard = "rejected"
    return (soft, hard, ch.spirit_current)


# M41: overload 1: regen blocked in this tick, then overload 0; next tick regen works.
# Balance 0/5, regen = level 1 + Con 0 = 1.
@S.case("m41-overload-1", "resources.md: overload 1 -> this tick blocked, overload 0, next tick +1", ((0, 0), (1, 0)))
def _m41():
    ch = hero(balance_current=0, overload=1)
    a = run(ch, ("tick", {}))
    b = run(a, ("tick", {}))
    return ((a.balance_current, a.overload), (b.balance_current, b.overload))


# M47: lucky cap 3: 4 lucky picks (impossible by the repeat limits, forced here) -> 20 - 3 = 17.
S.case("m47-lucky-cap", "combat.md: lucky from mastery at most 3", 17)(
    lambda: wpn.lucky_threshold([Pick(8, "lucky_1")] * 4))
# M48: long rest drops BP above max (overcap, pkg 8 C).
S.case("m48-long-rest-overcap", "rest.md [OWNER pkg 8]: long rest BP above max -> max", True)(
    lambda: (lambda c: c.bp_current == dv.bp_max(c))(run(hero(bp_current=dv.bp_max(hero()) + 2), ("long_rest", {}))))


# A9: feat price comes from the catalog; a cost parameter is not accepted.
@S.case("a9-feat-price", "training.md:14: feat price set by its author, not changed on purchase", (800, "rejected"))
def _a9():
    cat = fc.load_default()
    a = dispatch(Character(), "add_feat", catalog=cat, fid="finesse_training").state.training
    try:
        dispatch(Character(), "add_feat", catalog=cat, fid="finesse_training", cost=5)
        b = "allowed"
    except (CommandError, TypeError):
        b = "rejected"
    return (a, b)


if __name__ == "__main__":
    sys.exit(S.run())
