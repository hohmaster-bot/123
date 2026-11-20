"""Phase 3 part 2 commands and derived values vs RULES/.
Run: python Wp_claude/tests/model/test_commands2.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from dataclasses import replace  # noqa: E402

from wp.model.notebook import Drive
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


def rejected(ch, cmd, /, **params):
    try:
        dispatch(ch, cmd, **params)
    except CommandError:
        return "rejected"
    return "allowed"


# resources.md Spirit max [OWNER]: 5 + 5 * Cha mod, min 0, + bonuses. Tests.
S.case("spirit-max", "resources.md Tests [OWNER]: Cha mod +2 -> 15; -1 -> 0; -2 -> 0", (15, 0, 0))(
    lambda: tuple(dv.spirit_max(Character(abilities=ab(cha=c))) for c in (14, 8, 6)))
S.case("spirit-bonus", "resources.md Tests [OWNER]: +2 with bonus +3 -> 18", 18)(
    lambda: dv.spirit_max(Character(abilities=ab(cha=14), spirit_bonuses=(("ring", 3),))))
S.case("spirit-penalty-after-floor", "resources.md [OWNER, A7]: total never below 0 (Cha -1, penalty -2 -> 0)", 0)(
    lambda: dv.spirit_max(Character(abilities=ab(cha=8), spirit_bonuses=(("curse", -2),))))
S.case("spirit-long-rest", "rest.md: long rest restores all spirit (to the derived max)", 15)(
    lambda: run(Character(abilities=ab(cha=14)), ("long_rest", {})).spirit_current)

# narrative.md Attention [OWNER]: 1 + levels 3,6,9... + 1 per drive at 4+.
_CH7 = Character(level=7, hp_rolls=(8,) * 7, hp_current=8, drives=(Drive("growth", "g", 4), Drive("triumph", "t", 5), Drive("pleasure", "p", 3)),
                 attention=1)
S.case("attention-example", "narrative.md Example [OWNER]: level 7, two drives 4+ -> 5", 5)(
    lambda: dv.attention_per_cycle(_CH7))
S.case("attention-levels", "narrative.md: level 1 -> 1, 3 -> 2, 9 -> 4 (no drives)", (1, 2, 4))(
    lambda: tuple(dv.attention_per_cycle(Character(level=lv)) for lv in (1, 3, 9)))


@S.case("end-cycle", "narrative.md [OWNER]: end_cycle only adds attention, no maximum", (6, True))
def _cycle():
    new = run(_CH7, ("end_cycle", {}))
    same = replace(new, attention=_CH7.attention, log=_CH7.log, log_seq=_CH7.log_seq) == _CH7   # pkg 14 H: journal counter
    return (new.attention, same)


# skills.md [OWNER]: specialized ranks up to the level are free and follow the level.
# Level 5, bought ranks 0 -> effective rank 5. Target 6: one command, one paid rank: 10 * 6 = 60.
@S.case("spec-target-rank", "skills.md [OWNER]: level 5, target 6 -> one command, 60", (60, 6, 940))
def _spec():
    from wp.core import skills as sk
    ch = Character(level=5, skills=(sk.Skill("x", "int", sk.SPECIALIZED, 0),))
    r = dispatch(ch, "buy_skill_rank", name="x", target=6)
    return (r.info["cost"], r.state.skills[0].ranks, r.state.training)


# At level 6 rank 6 is free (level covers it): nothing to buy; next rank 7 costs 70.
@S.case("spec-level-up", "skills.md [OWNER]: at level 6 rank 6 is free; 7 costs 70", ("rejected", 6, 70))
def _spec_lvl():
    from wp.core import skills as sk
    ch = Character(level=6, skills=(sk.Skill("x", "int", sk.SPECIALIZED, 0),))
    eff = sk.effective_ranks(ch.skills[0], ch.level)
    return (rejected(ch, "buy_skill_rank", name="x", target=6), eff,
            dispatch(ch, "buy_skill_rank", name="x", target=7).info["cost"])


# Normal skill with a target: ranks 0 -> 3 at level 3 = 20 + 40 + 60 = 120.
@S.case("normal-target-rank", "skills.md: normal 0 -> 3 = 20 + 40 + 60", 120)
def _norm():
    from wp.core import skills as sk
    ch = Character(level=3, skills=(sk.Skill("y", "int"),))
    return dispatch(ch, "buy_skill_rank", name="y", target=3).info["cost"]


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

# gear.md [OWNER]: two activation kinds, each with its own spirit price on the card:
# "day" (until the end of the short rest) and "decade" (until the end of the long rest).
_SWORD = Item("sw", "sword", equipped=True, activation_day=1, effects_off=(Effect("attack", 1),),
              effects_on=(Effect("attack", 5, "enhancement"),))
_CLOAK = Item("cl", "cloak", equipped=True, activation_decade=5)
_BOTH = Item("bt", "staff", equipped=True, activation_day=1, activation_decade=5)
_NONE = Item("nn", "stone", equipped=True)
_BASE = Character(abilities=ab(cha=14), spirit_current=15, items=(_SWORD, _CLOAK, _BOTH, _NONE))


# Only the day price is set -> it works: spirit 15 - 1 = 14, active until short rest, attack tab +5.
@S.case("activate-day", "gear.md [OWNER]: one price set -> that one works (day, 1 spirit)", (14, True, "short", 5))
def _act1():
    ch = run(_BASE, ("activate_item", {"iid": "sw"}))
    return (ch.spirit_current, ch.item("sw").activated, ch.item("sw").active_until, dv.total(ch, "attack"))


S.case("activate-decade", "gear.md [OWNER]: only the decade price -> decade, 5 spirit", (10, "long"))(
    lambda: (lambda ch: (ch.spirit_current, ch.item("cl").active_until))(run(_BASE, ("activate_item", {"iid": "cl"}))))
S.case("both-prices-choose", "gear.md: both prices -> the player picks the kind", ((14, "short"), (10, "long")))(
    lambda: tuple((lambda ch: (ch.spirit_current, ch.item("bt").active_until))(
        run(_BASE, ("activate_item", {"iid": "bt", "kind": k}))) for k in ("day", "decade")))
S.case("both-prices-no-kind", "gear.md: both prices and no choice -> asks to choose", "rejected")(
    lambda: rejected(_BASE, "activate_item", iid="bt"))


# Owner: no price for day nor decade -> not activatable: soft refusal, sheet unchanged.
@S.case("no-price-soft-refusal", "gear.md [OWNER]: no price -> 'activation price not set', sheet unchanged",
        ("activation price not set", True, False))
def _none():
    r = dispatch(_BASE, "activate_item", iid="nn")
    return (r.info.get("refused"), r.state is _BASE, r.state.item("nn").activated)


S.case("kind-without-price", "gear.md: asking for a kind whose price is not set -> soft refusal", "activation price not set")(
    lambda: dispatch(_BASE, "activate_item", iid="sw", kind="decade").info.get("refused"))


@S.case("short-rest-off", "gear.md: short rest switches off day items, keeps decade ones", (False, True))
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


# End of combat.
@S.case("end-combat", "resources.md / buffs.md: button temp HP stay (pkg 4), end-of-combat statuses end "
        "(pkg 11 A: inactive, entry stays), overload 0 and morale scale 0 [OWNER]", (False, 5, ("curse",), 0, 0))
def _end():
    ch = Character(temp_hp=5, overload=3, morale_scale=6,
                   statuses=(Status("haste", sid="h", duration=ef.END_OF_COMBAT), Status("curse", sid="c")))
    ch = run(ch, ("start_combat", {}), ("end_combat", {}))
    return (ch.in_combat, ch.temp_hp, tuple(s.name for s in ch.statuses if s.active), ch.overload, ch.morale_scale)


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
