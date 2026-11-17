"""Package 4: temp HP kinds (resources.md), the flat layer (defense_layers.md), parry and languages (training.md).
Run: python Wp_claude/tests/model/test_pkg4.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import ac as acm  # noqa: E402
from wp.core import ac_layers as L  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core.effects import OneShot, Status  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import Character  # noqa: E402

S = Suite("test_pkg4")


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def hero(**kw):
    base = dict(hp_rolls=(20,), hp_current=20, bp_current=5, balance_current=5)
    base.update(kw)
    return Character(**base)


def buff(n=5):
    return Status("aid", sid="aid", one_shot=(OneShot(ef.TEMP_HP, n),), duration=ef.TICKS, temp_hp_stacks=True)


# ---- A1 temp HP ----
S.case("button-survives-combat", "resources.md [OWNER pkg 4]: button temp HP survive the end of combat", 6)(
    lambda: run(hero(), ("start_combat", {}), ("set_temp_hp", {"value": 6}), ("end_combat", {})).temp_hp)
S.case("button-short-rest", "resources.md / rest.md: the short rest clears button temp HP", 0)(
    lambda: dv.temp_hp_total(run(hero(), ("set_temp_hp", {"value": 6}), ("short_rest", {}))))


@S.case("button-negative", "set_temp_hp refuses a negative value", "rejected")
def _neg():
    try:
        dispatch(hero(), "set_temp_hp", value=-1)
    except CommandError:
        return "rejected"
    return "accepted"


# Buff for 3 rounds: after 2 ticks still 5, after the 3rd tick 0.
S.case("buff-n-rounds", "resources.md [OWNER pkg 4]: buff temp HP live N rounds (N = 3)", (5, 5, 0))(
    lambda: (lambda c1: (dv.temp_hp_total(c1), dv.temp_hp_total(run(c1, ("tick", {}))),
                         dv.temp_hp_total(run(c1, ("tick", {}), ("tick", {}), ("tick", {})))))(
        run(hero(), ("add_status", {"status": buff(), "ticks": 3}))))
# Q23 assumption: button first. Button 4 + buff 5, hit 6 -> button 0, buff 3.
S.case("order-button-first", "OPEN_QUESTIONS Q23 assumption: button temp HP spent first", (0, 3))(
    lambda: (lambda c: (c.temp_hp, c.statuses[0].temp_hp_left))(
        run(hero(), ("set_temp_hp", {"value": 4}), ("add_status", {"status": buff(), "ticks": 3}),
            ("take_damage", {"amount": 6}))))


# ---- A3 flat layer ----
def layers(**kw):
    mode = kw.pop("mode", acm.FRONT)
    return dict(acm.parts(acm.AcInput(**kw), mode))


def untyped(v):
    return (bo.Bonus(v, bo.FLAT, bo.AC),)


# Armor 4, natural 2, untyped +2: 10-13 armor, 14-15 flat, 16-17 natural (natural moved up by 2), 18 exact.
S.case("flat-after-armor", "defense_layers.md [OWNER pkg 4]: untyped +2 after armor moves natural armor",
       (("armor", 10, 13), ("flat", 14, 15), ("natural", 16, 17), ("exact", 18, 18)))(
    lambda: tuple((r.layer, r.lo, r.hi) for r in L.ladder(acm.parts(acm.AcInput(armor=4, natural=2, bonuses=untyped(2))))
                  if r.layer in ("armor", "flat", "natural", "exact")))
S.case("sum-equals-ac", "defense_layers.md: sum of layers = AC in every mode (mixed input)", True)(
    lambda: all(L.ac_total(acm.parts(inp, m)) == acm.ac(inp, m)
                for inp in (acm.AcInput(dex_mod=-2, armor=4, natural=1, shield=2, size_mod=-1, parry=6,
                                        bonuses=(bo.Bonus(-3, "luck", bo.AC), bo.Bonus(2, "sacred", bo.AC),
                                                 bo.Bonus(1, bo.FLAT, bo.AC), bo.Bonus(2, bo.DODGE, bo.AC))),
                            acm.AcInput(dex_mod=3, armor=2, overloaded=True))
                for m in (acm.FRONT, acm.FLANK, acm.FLAT_FOOTED, acm.PARRY, acm.TOUCH)))
S.case("dex-minus2-flat", "defense_layers.md [OWNER pkg 4]: Dex -2 -> flat -2, dodge 0, AC 8", (-2, 0, 8))(
    lambda: (lambda p: (p["flat"], p["dodge"], 10 + sum(p.values())))(layers(dex_mod=-2)))
S.case("flat-footed-dex-minus2", "defense_layers.md: flat-footed Dex -2 -> flat still -2, dodge bonus blocked",
       (-2, 0, 8))(
    lambda: (lambda p: (p["flat"], p["dodge"], 10 + sum(p.values())))(
        layers(dex_mod=-2, bonuses=(bo.Bonus(3, bo.DODGE, bo.AC),), mode=acm.FLAT_FOOTED)))
S.case("no-negative-layers", "defense_layers.md: typed layers never below 0, penalties in flat (luck -3, size -1)",
       (True, -4))(
    lambda: (lambda p: (all(v >= 0 for t, v in p.items() if t != "flat"), p["flat"]))(
        layers(size_mod=-1, armor=3, bonuses=(bo.Bonus(-3, "luck", bo.AC),))))
S.case("other-type-in-flat", "OPEN_QUESTIONS Q26 assumption: sacred +2 goes to flat", 2)(
    lambda: layers(bonuses=(bo.Bonus(2, "sacred", bo.AC),))["flat"])
# AC below 10 (Dex -2 only): AC 8. Roll 9 is a hit, 8 exact, 7 position.
S.case("below-10-rolls", "defense_layers.md: AC 8 -> 9 hit, 8 exact, 7 position", ("hit", "exact", "position"))(
    lambda: tuple(L.layer_for_roll(acm.parts(acm.AcInput(dex_mod=-2)), r)[0] for r in (9, 8, 7)))
S.case("deflection-text", "defense_layers.md [OWNER pkg 4]: deflection text",
       "".join(chr(c) for c in (1072, 1090, 1072, 1082, 1072)))(
    lambda: L.texts()["deflection"][:5])

# ---- B: parry by armor proficiency and odd levels (training.md [OWNER pkg 4, Q27: from level 3]) ----
S.case("parry-odd-levels", "training.md Q27: +1 per odd level from 3 (1->0, 2->0, 3->1, 5->2, 6->2, 7->3)", (0, 0, 1, 2, 2, 3))(
    lambda: tuple(acm.odd_level_parry(lv) for lv in (1, 2, 3, 5, 6, 7)))
S.case("parry-armor-grades", "training.md: none 0, light 2, medium 4, heavy 6 (level 3: +1)", (1, 3, 5, 7))(
    lambda: tuple(acm.base_parry(g, 3) for g in ("none", "light", "medium", "heavy")))
S.case("parry-heavy-l5-in-ac", "training.md: heavy at level 5 -> parry 6 + 2 = 8 -> AC in parry mode 18, front 10", (10, 18))(
    lambda: (lambda c: (dv.ac(c), dv.ac(c, acm.PARRY)))(Character(level=5, armor_grade="heavy")))


# ---- B: language 30 * projects from the nearest native (training.md [OWNER pkg 4]) ----
def _lang(projects):
    return dispatch(Character(training=500), "buy_language", lid="elf", projects=projects).info["cost"]


S.case("lang-projects", "training.md: 30 * projects (1 -> 30, 3 -> 90)", (30, 90))(lambda: (_lang(1), _lang(3)))


@S.case("lang-projects-zero", "training.md: projects must be >= 1", "rejected")
def _lang0():
    try:
        _lang(0)
    except CommandError:
        return "rejected"
    return "accepted"


if __name__ == "__main__":
    sys.exit(S.run())
