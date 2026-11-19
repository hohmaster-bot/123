"""End-to-end scenarios through commands (D5) on numbers from RULES/.
Run: python Wp_claude/tests/model/test_scenarios.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from dataclasses import replace  # noqa: E402

from wp.commands import CHANGED, CommandError, dispatch  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core import magic as mg  # noqa: E402
from wp.core import rest as rs  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Status  # noqa: E402
from wp.core.pain import PainEntry as PE, PainProfile  # noqa: E402
from wp.core.weapons import Weapon  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import Ability, Character, WeaponEntry  # noqa: E402

S = Suite("test_scenarios")


def hero(**kw):
    """Level 3, Con 10, HP max 20 (rolls 8+6+6), BP max 5."""
    base = dict(level=3, hp_rolls=(8, 6, 6), hp_current=20, bp_current=5, balance_current=5)
    base.update(kw)
    return Character(**base)


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


# resources.md Balance Example [OWNER]: balance 1, hits 10, 1, 1 -> HP -12, balance 0, OT 11, pain 3.
@S.case("balance-1-hits-10-1-1", "resources.md Balance Example [OWNER] via take_damage",
        (-12, 0, 11, 3, 3))
def _overflow():
    ch = hero(balance_current=1)
    ch = run(ch, ("take_damage", {"amount": 10}), ("take_damage", {"amount": 1}),
             ("take_damage", {"amount": 1}))
    return (ch.hp_current - 20, ch.balance_current, ch.trauma, dv.pain_total(ch), len(ch.pain))


@S.case("temp-hp-example", "resources.md Example: 3 temp HP, 7 damage -> temp 0, HP -4, balance -4",
        (0, -4, -4))
def _temp():
    ch = run(hero(temp_hp=3, balance_current=5), ("take_damage", {"amount": 7}))
    return (ch.temp_hp, ch.hp_current - 20, ch.balance_current - 5)


@S.case("mana-absorber", "classes_magic.md: MANA absorbs 3 (no balance), the 3 reaching HP hit balance",
        (0, 17, 2))
def _absorb():
    ch = run(hero(mana=Pool(3, 6), absorbers=("mana",)), ("take_damage", {"amount": 6}))
    return (ch.mana.current, ch.hp_current, ch.balance_current)


# rest.md Short rest Example: level 3, HP 1/20: free +5, second heal 1 BP; remove 1 pain for 1 BP.
@S.case("short-rest", "rest.md Short rest 7 Example [OWNER] + pain spend", (11, 1, 1))
def _short():
    ch = hero(hp_current=1, bp_current=2, pain=(PE(2, "overflow"),))
    ch = run(ch, ("short_rest", {"spends": [(rs.OPT_HEAL, {}), (rs.OPT_PAIN, {})]}))
    return (ch.hp_current, ch.bp_current, dv.pain_total(ch))


@S.case("short-rest-overcap-lost", "rest.md Short rest 6 [OWNER pkg 8]: excess BP lost on Apply", 5)
def _short_temp():
    return run(hero(), ("short_rest", {"extra_bp": 2})).bp_current


# rest.md Long rest [OWNER].
@S.case("long-rest", "rest.md Long rest [OWNER]: HP, BP, mana, stats; pain except permanent; OT and comfort kept",
        (20, 5, 6, 18, 1, 7, 4, 0))
def _long():
    ch = hero(hp_current=-3, bp_current=0, mana=Pool(0, 6), mana_enabled=True,
              pain=(PE(3, "overflow"), PE(1, "curse", permanent=True)), trauma=7, comfort_current=4,
              overload=3, abilities=dict(Character().abilities, str=Ability(18, damage=2)))
    ch = run(ch, ("long_rest", {}))
    return (ch.hp_current, ch.bp_current, ch.mana.current, dv.ability_current(ch, "str"),
            dv.pain_total(ch), ch.trauma, ch.comfort_current, ch.overload)


# resources.md Pain: death at total >= cap (8; 12 for some races).
@S.case("death-cap", "resources.md [OWNER]: death at pain cap 8 (entries + HP below 0)", (False, True, False))
def _death():
    alive = hero(pain=(PE(5),), hp_current=-5)                 # 5 + 1 = 6
    dead = run(hero(pain=(PE(6),), hp_current=-6), ("take_damage", {"amount": 0}))  # 6 + 2 = 8
    tough = replace(dead, pain_profile=PainProfile(cap=12))
    return (dv.is_dead(alive), dv.is_dead(dead), dv.is_dead(tough))


# resources.md Zero initiative + [OWNER]: bleed for 3 rounds hits exactly 3 times, balance before DoT.
@S.case("combat-dot", "resources.md [OWNER]: bleed 3 rounds = 3 hits; balance first", (14, (), 0))
def _dot():
    bleed = Status("bleed", sid="s1", per_tick_hp=-2, duration=ef.TICKS)
    ch = run(hero(balance_current=0), ("add_status", {"active": True, "status": bleed, "ticks": 3}),
             ("tick", {}), ("tick", {}), ("tick", {}), ("tick", {}))
    return (ch.hp_current, tuple(s for s in ch.statuses if s.active), ch.trauma)   # pkg 11 A: entry stays inactive


# classes_magic.md [OWNER, changed]: mage overload 2, non-mage 4; -1 per tick, regen blocked.
@S.case("mage-cast", "classes_magic.md: mage standard cast -> overload 2, then 1, 0", (2, -3, -3, (1, 0)))
def _mage():
    ch = hero(caster=mg.MAGE, mana=Pool(10, 10), mana_enabled=True, balance_current=5)
    ch = run(ch, ("cast_spell", {"circle": 2, "mana_cost": 3}))
    ov0, mana, bal = ch.overload, ch.mana.current - 10, ch.balance_current - 5
    seq = []
    for _ in range(2):
        ch = run(ch, ("tick", {}))
        seq.append(ch.overload)
    return (ov0, mana, bal, tuple(seq))


@S.case("mage-regen-blocked", "resources.md: balance regen forbidden while overload > 0", (2, 2, 5))
def _blocked():
    ch = hero(caster=mg.MAGE, mana=Pool(10, 10), mana_enabled=True, balance_current=5)
    ch = run(ch, ("cast_spell", {"circle": 2, "mana_cost": 3}))      # balance 2, overload 2
    a = ch.balance_current
    ch = run(ch, ("tick", {}))                                        # overload 2 -> blocked
    b = ch.balance_current
    ch = run(ch, ("tick", {}), ("tick", {}))                          # overload 1 blocked, then 0 -> regen
    return (a, b, ch.balance_current)


@S.case("nonmage-cast", "classes_magic.md: non-mage standard cast -> overload 4, falls to 0 in 4 ticks",
        (4, 1, (3, 2, 1, 0), 5))
def _nonmage():
    ch = hero(caster=mg.SLOTS, slots={1: Pool(2, 2)})
    ch = run(ch, ("cast_spell", {"circle": 1}))
    ov0, slots = ch.overload, ch.slots[1].current
    seq = []
    for _ in range(4):
        ch = run(ch, ("tick", {}))
        seq.append(ch.overload)
    return (ov0, slots, tuple(seq), ch.balance_current)


@S.case("mage-balance-short", "classes_magic.md [OWNER]: balance 2, cost 5 -> OT 3, pain 1, DC 16",
        (0, 3, 1, 16))
def _short_bal():
    # level 5: a 5-mana spell fits the mana level (= level, package 10 Q49)
    ch = hero(level=5, caster=mg.MAGE, mana=Pool(10, 10), mana_enabled=True, balance_current=2)
    r = dispatch(ch, "cast_spell", circle=3, mana_cost=5)
    s = r.state
    return (s.balance_current, s.trauma, dv.pain_total(s), r.info["result"].concentration_dc)


# D5 plumbing.
@S.case("no-mutation-log-event", "D5: new state returned, old untouched, log + 'changed' event",
        (20, 10, 1, (CHANGED,), 1))
def _plumbing():
    seen = []
    ch = hero()
    r = dispatch(ch, "take_damage", [seen.append], amount=10)
    return (ch.hp_current, r.state.hp_current, len(r.state.log), r.events, len(seen))


@S.case("invalid-unchanged", "D5: failed validation raises, no state change", ("rejected", 0))
def _invalid():
    ch = hero(trauma=1)
    try:
        dispatch(ch, "add_injury", severity="heavy")
    except CommandError:
        return ("rejected", len(ch.log))
    return ("allowed", len(ch.log))


@S.case("restore-and-set", "resources.md Over max: restore clamps, set does not", (20, 25, True))
def _over():
    ch = run(hero(hp_current=15), ("restore", {"resource": "hp", "amount": 9}))
    ch2 = run(ch, ("set_value", {"resource": "hp", "value": 25}))
    return (ch.hp_current, ch2.hp_current, dv.hp_pool(ch2).over_max)


@S.case("spend-bp", "rest.md [OWNER pkg 8]: BP spent by hand, BP above max is ordinary BP", 4)
def _bp():
    return run(hero(bp_current=6), ("spend_bp", {"n": 2})).bp_current


@S.case("add-injury", "injuries.md: light injury removes 2 OT, RL 3", (3, 3))
def _inj():
    ch = run(hero(trauma=5), ("add_injury", {"severity": "light"}))
    return (ch.trauma, ch.injuries[0].heal_rating)


@S.case("no-charges", "buffs.md: no charges left -> cannot activate", "rejected")
def _charges():
    try:
        dispatch(hero(), "add_status", active=True, status=Status("rage", sid="r", charges=Pool(0, 3)))
    except CommandError:
        return "rejected"
    return "allowed"


# training.md purchases.
@S.case("buy-ability", "training.md Example: base 13 + race 2: 15->16 = 450; race source free",
        (550, 14, 1000))
def _buy():
    ch = hero(abilities=dict(Character().abilities, str=Ability(13, race=2)))
    a = run(ch, ("buy_ability", {"name": "str"}))
    b = run(ch, ("buy_ability", {"name": "str", "source": "race"}))
    return (a.training, a.ability("str").base, b.training)


@S.case("buy-weapon-grade", "weapons.md Example: X=0, difficulty 1, scale 2 -> 60", (940, 1))
def _wg():
    ch = hero(weapons=(WeaponEntry(Weapon("w-ls", 2, 1), "long swords"),))
    ch = run(ch, ("buy_weapon_grade", {"wid": "w-ls"}))
    return (ch.training, ch.weapons[0].weapon.grades)


@S.case("buy-base-cap", "gear.md: base max 10*level (level 1: 5 -> 10, then rejected)", (10, 500, "rejected"))
def _base():
    ch = hero(level=1, hp_rolls=(8,), hp_current=8)
    for _ in range(5):
        ch = run(ch, ("buy_base_slot", {}))
    try:
        dispatch(ch, "buy_base_slot")
        r = "allowed"
    except CommandError:
        r = "rejected"
    return (ch.base_slots, ch.training, r)


if __name__ == "__main__":
    sys.exit(S.run())
