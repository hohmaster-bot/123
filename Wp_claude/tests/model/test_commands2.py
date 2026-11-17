"""Phase 3 part 2 commands and derived values vs RULES/.
Run: python Wp_claude/tests/model/test_commands2.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from dataclasses import replace  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import Ability, Character, Item  # noqa: E402

S = Suite("test_commands2")


def ab(**scores):
    a = dict(Character().abilities)
    for k, v in scores.items():
        a[k] = Ability(v)
    return a


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def rejected(ch, name, **params):
    try:
        dispatch(ch, name, **params)
    except CommandError:
        return "rejected"
    return "allowed"


# resources.md Spirit max [OWNER]: 5 + 5 * Cha mod, min 0, + bonuses. Tests.
S.case("spirit-max", "resources.md Tests [OWNER]: Cha mod +2 -> 15; -1 -> 0; -2 -> 0", (15, 0, 0))(
    lambda: tuple(dv.spirit_max(Character(abilities=ab(cha=c))) for c in (14, 8, 6)))
S.case("spirit-bonus", "resources.md Tests [OWNER]: +2 with bonus +3 -> 18", 18)(
    lambda: dv.spirit_max(Character(abilities=ab(cha=14), spirit_bonuses=(("ring", 3),))))
S.case("spirit-penalty-after-floor", "resources.md: floor 0 first, then penalties (Cha -1, -2 -> -2)", -2)(
    lambda: dv.spirit_max(Character(abilities=ab(cha=8), spirit_bonuses=(("curse", -2),))))
S.case("spirit-long-rest", "rest.md: long rest restores all spirit (to the derived max)", 15)(
    lambda: run(Character(abilities=ab(cha=14)), ("long_rest", {})).spirit_current)

# narrative.md Attention [OWNER]: 1 + levels 3,6,9... + 1 per drive at 4+.
_CH7 = Character(level=7, hp_rolls=(8,) * 7, hp_current=8, drives={"growth": 4, "triumph": 5, "pleasure": 3},
                 attention=1)
S.case("attention-example", "narrative.md Example [OWNER]: level 7, two drives 4+ -> 5", 5)(
    lambda: dv.attention_per_cycle(_CH7))
S.case("attention-levels", "narrative.md: level 1 -> 1, 3 -> 2, 9 -> 4 (no drives)", (1, 2, 4))(
    lambda: tuple(dv.attention_per_cycle(Character(level=lv)) for lv in (1, 3, 9)))


@S.case("end-cycle", "narrative.md [OWNER]: end_cycle only adds attention, no maximum", (6, True))
def _cycle():
    new = run(_CH7, ("end_cycle", {}))
    same = replace(new, attention=_CH7.attention, log=_CH7.log) == _CH7
    return (new.attention, same)


# training.md Armor / shield grades.
@S.case("shield-grades", "training.md: shield 100 per grade, tower is max", (700, "tower", "rejected"))
def _shield():
    ch = run(Character(), ("buy_shield_grade", {}), ("buy_shield_grade", {}), ("buy_shield_grade", {}))
    return (ch.training, ch.shield_grade, rejected(ch, "buy_shield_grade"))


@S.case("armor-grades", "training.md: armor 250 per grade; race source free", (750, "light", 1000))
def _armor():
    a = run(Character(), ("buy_armor_grade", {}))
    b = run(Character(), ("buy_armor_grade", {"source": "race"}))
    return (a.training, a.armor_grade, b.training)


# training.md Languages Tests [OWNER confirmed].
@S.case("languages-int2", "training.md: Int +2: first native free, 2nd 50, 3rd 100; non-native 30",
        (0, 50, 100, 30))
def _lang2():
    ch = Character(abilities=ab(int=14))
    costs = []
    for i, native in enumerate((True, True, True, False)):
        r = dispatch(ch, "buy_language", lid="l%d" % i, native=native)
        costs.append(r.info["cost"])
        ch = r.state
    return tuple(costs)


S.case("languages-int1", "training.md Test: Int +1, natives 1 -> 100", 100)(
    lambda: dispatch(run(Character(abilities=ab(int=12)), ("buy_language", {"lid": "a", "native": True})),
                     "buy_language", lid="b", native=True).info["cost"])
S.case("languages-int3", "training.md Test: Int +3, natives 2 -> 50", 50)(
    lambda: dispatch(run(Character(abilities=ab(int=16)), ("buy_language", {"lid": "a", "native": True}),
                         ("buy_language", {"lid": "b", "native": True})),
                     "buy_language", lid="c", native=True).info["cost"])

# gear.md Enabled / disabled: 1 spirit until short rest, 5 until long rest.
_SWORD = Item("sw", "sword", equipped=True, activation_cost=1, effects_off=(Effect("attack", 1),),
              effects_on=(Effect("attack", 5, "enhancement"),))
_CLOAK = Item("cl", "cloak", equipped=True, activation_cost=5)
_BASE = Character(abilities=ab(cha=14), spirit_current=15, items=(_SWORD, _CLOAK))


@S.case("activate-1", "gear.md: 1 spirit -> active until the end of the short rest", (14, True, "short", 5))
def _act1():
    ch = run(_BASE, ("activate_item", {"iid": "sw"}))
    return (ch.spirit_current, ch.item("sw").activated, ch.item("sw").active_until, dv.total(ch, "attack"))


@S.case("short-rest-off", "gear.md: short rest switches off 1-spirit items, keeps 5-spirit ones",
        (False, True))
def _short():
    ch = run(_BASE, ("activate_item", {"iid": "sw"}), ("activate_item", {"iid": "cl"}), ("short_rest", {}))
    return (ch.item("sw").activated, ch.item("cl").activated)


@S.case("long-rest-off", "gear.md: long rest switches off all", (False, False))
def _long():
    ch = run(_BASE, ("activate_item", {"iid": "sw"}), ("activate_item", {"iid": "cl"}), ("long_rest", {}))
    return (ch.item("sw").activated, ch.item("cl").activated)


S.case("activate-no-spirit", "gear.md: activation needs spirit", "rejected")(
    lambda: rejected(replace(_BASE, spirit_current=4), "activate_item", iid="cl"))
S.case("deactivate", "gear.md: player switches it off", (False, 1))(
    lambda: (lambda ch: (ch.item("sw").activated, dv.total(ch, "attack")))(
        run(_BASE, ("activate_item", {"iid": "sw"}), ("deactivate_item", {"iid": "sw"}))))
S.case("activate-x", "gear.md X spirit -> until long rest (OPEN_QUESTIONS Q14)", (12, "long"))(
    lambda: (lambda ch: (ch.spirit_current, ch.item("sw").active_until))(
        run(_BASE, ("activate_item", {"iid": "sw", "cost": 3}))))


# End of combat.
@S.case("end-combat", "resources.md / buffs.md: temp HP gone, end-of-combat statuses removed, "
        "overload 0 and morale scale 0 [OWNER]", (False, 0, ("curse",), 0, 0))
def _end():
    ch = Character(temp_hp=5, overload=3, morale_scale=6,
                   statuses=(Status("haste", sid="h", duration=ef.END_OF_COMBAT), Status("curse", sid="c")))
    ch = run(ch, ("start_combat", {}), ("end_combat", {}))
    return (ch.in_combat, ch.temp_hp, tuple(s.name for s in ch.statuses), ch.overload, ch.morale_scale)


S.case("end-combat-not-active", "end_combat without combat is rejected", "rejected")(
    lambda: rejected(Character(), "end_combat"))


@S.case("long-rest-overload-balance", "rest.md [OWNER confirmed]: long rest overload 0, balance max",
        (0, 8))
def _lr():
    ch = Character(hp_rolls=(8,), hp_current=8, bp_current=2, overload=4,
                   items=(Item("a", "mail", equipped=True, armor=6),))
    ch = run(ch, ("long_rest", {}))
    return (ch.overload, ch.balance_current)


if __name__ == "__main__":
    sys.exit(S.run())
