"""Package 5: owner answers (dodge/Dex, enhancement layer, shields, ids, shield attacks, enchantment).
Run: python Wp_claude/tests/model/test_pkg5.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.core import ac as acm  # noqa: E402
from wp.core import ac_layers as L  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import ids  # noqa: E402
from wp.core.effects import Status  # noqa: E402
from wp.model.character import SHIELD, Character, Item  # noqa: E402

S = Suite("test_pkg5")


def layers(mode=acm.FRONT, **kw):
    return dict(acm.parts(acm.AcInput(**kw), mode))


def dodge(v):
    return bo.Bonus(v, bo.DODGE, bo.AC)


def pick(p, *keys):
    return tuple(p[k] for k in keys)


# ---- A: dodge layer = dodge bonuses + Dex mod ----
S.case("a-dex-2-dodge+1", "defense_layers.md [OWNER pkg 5]: Dex -2, dodge +1 -> sum -1: base 9, dodge 0, flat 0",
       (0, 0, 9))(
    lambda: (lambda p: (p["dodge"], p["flat"], L.base(tuple(p.items()))))(layers(dex_mod=-2, bonuses=(dodge(1),))))
S.case("a-dex-2-dodge+1-ff", "defense_layers.md: Dex -2, dodge +1, flat-footed -> base 8", (0, 8))(
    lambda: (lambda p: (p["dodge"], L.base(tuple(p.items()))))(
        layers(acm.FLAT_FOOTED, dex_mod=-2, bonuses=(dodge(1),))))
# Owner example: Dex -2, armor 8: base 8, position 1-7, armor 8-15, exact 16, hit 17+; flat-footed the same.
_EX = (("position", None, 7), ("armor", 8, 15), ("exact", 16, 16), ("hit", 17, None))
S.case("a-example-ladder", "defense_layers.md Example [OWNER pkg 5]: Dex -2, armor 8 (front and flat-footed)",
       (_EX, _EX))(
    lambda: tuple(tuple((r.layer, r.lo, r.hi) for r in L.ladder(acm.parts(acm.AcInput(dex_mod=-2, armor=8), m)))
                  for m in (acm.FRONT, acm.FLAT_FOOTED)))
S.case("a-example-rolls", "defense_layers.md: rolls 7 position, 8 armor, 16 exact, 17 hit", ("position", "armor", "exact", "hit"))(
    lambda: tuple(L.layer_for_roll(acm.parts(acm.AcInput(dex_mod=-2, armor=8)), r)[0] for r in (7, 8, 16, 17)))
S.case("a-untyped-split", "defense_layers.md: untyped +3 to flat, untyped -1 lowers the base", (3, -1))(
    lambda: pick(layers(bonuses=(bo.Bonus(3, bo.FLAT, bo.AC), bo.Bonus(-1, bo.FLAT, bo.AC))), "flat", "penalty"))
S.case("a-dex+2-dodge+1", "defense_layers.md: Dex +2, dodge +1 -> dodge 3", (3, 0))(
    lambda: pick(layers(dex_mod=2, bonuses=(dodge(1),)), "dodge", "flat"))
S.case("a-dex+2-dodge+1-ff", "defense_layers.md: Dex +2, dodge +1, flat-footed -> 0", (0, 0))(
    lambda: pick(layers(acm.FLAT_FOOTED, dex_mod=2, bonuses=(dodge(1),)), "dodge", "flat"))
S.case("a-real-ac", "defense_layers.md: real AC = 10 + sum of layers (Dex -2, dodge +1, armor 3: 12; ff 11)",
       (12, 12, 11, 11))(
    lambda: (lambda i: (acm.ac(i), L.ac_total(acm.parts(i)), acm.ac(i, acm.FLAT_FOOTED),
                        L.ac_total(acm.parts(i, acm.FLAT_FOOTED))))(
        acm.AcInput(dex_mod=-2, armor=3, bonuses=(dodge(1),))))

# ---- B: enhancement goes to the armor layer; other unlisted types go to flat ----
S.case("b-enhancement-armor", "defense_layers.md [OWNER Q26]: enhancement +2 raises the armor layer (4 -> 6)", (6, 0))(
    lambda: pick(layers(armor=4, bonuses=(bo.Bonus(2, bo.ENHANCEMENT, bo.AC),)), "armor", "flat"))
S.case("b-sacred-flat", "defense_layers.md: sacred +2 is not a layer; in AC it goes to flat (assumption)", (0, 2, 12))(
    lambda: (lambda p: (p["armor"], p["flat"], 10 + sum(p.values())))(
        layers(bonuses=(bo.Bonus(2, "sacred", bo.AC),))))
S.case("b-enhancement-touch", "defense.md: touch ignores armor, so its enhancement too", 0)(
    lambda: layers(acm.TOUCH, armor=4, bonuses=(bo.Bonus(2, bo.ENHANCEMENT, bo.AC),))["armor"])


# ---- C: shields: type on the card, heavy/tower add the shield bonus to balance max while in a hand ----
def shield_char(stype, in_hands=True, bonus=2):
    sh = Item("sh", "shield", kind=SHIELD, hands=1, in_hands=in_hands, shield=bonus, shield_type=stype)
    return Character(hp_rolls=(8,), hp_current=8, bp_current=2, items=(sh,))


S.case("c-heavy-in-hand", "training.md [OWNER Q28]: heavy shield +2 in hand -> balance max +2", 2)(
    lambda: dv.balance_max(shield_char("heavy")) - dv.balance_max(shield_char("")))
S.case("c-heavy-in-bag", "training.md: heavy shield in the bag -> no balance bonus", 0)(
    lambda: dv.balance_max(shield_char("heavy", in_hands=False)) - dv.balance_max(shield_char("")))
S.case("c-tower-light", "training.md: tower +3 -> +3; light shield -> +0", (3, 0))(
    lambda: (dv.shield_balance_bonus(shield_char("tower", bonus=3)), dv.shield_balance_bonus(shield_char("light"))))


# ---- F: parry from proficiency: armor 0/2/4/6, tower shields grade +2 ----
def parry_of(level, shield_grade):
    return dv.ac_input(Character(level=level, armor_grade="heavy", shield_grade=shield_grade)).parry


S.case("f-parry-proficiency", "training.md / defense.md [OWNER pkg 5]: heavy + tower grade: L1 8, L3 9; no shield 6",
       (8, 9, 6, 6))(
    lambda: (parry_of(1, "tower"), parry_of(3, "tower"), parry_of(1, "none"), parry_of(1, "heavy")))
S.case("f-tower-item-no-parry", "defense.md: a tower shield ITEM without the grade gives no parry", 6)(
    lambda: dv.ac_input(Character(level=1, armor_grade="heavy", items=(
        Item("t", "tower", kind=SHIELD, hands=1, in_hands=True, shield=4, shield_type="tower"),))).parry)


# ---- E: ids are made by the program (D7) ----
_RU_ELF = "".join(chr(c) for c in (1069, 1083, 1100, 1092, 1080, 1081, 1089, 1082, 1080, 1081))   # Elfiyskiy


def _two_langs():
    ch = Character(training=500)
    ch = dispatch(ch, "buy_language", title=_RU_ELF).state
    ch = dispatch(ch, "buy_language", title=_RU_ELF).state
    return tuple(lang.lid for lang in ch.languages)


S.case("e-language-no-id", "ARCH D7 [OWNER pkg 5]: language without id is bought; same name -> another id",
       ("elfiyskiy", "elfiyskiy_2"))(_two_langs)
S.case("e-status-no-id", "D7: two statuses 'Rage' without sid get rage and rage_2", ("rage", "rage_2"))(
    lambda: (lambda c: tuple(s.sid for s in c.statuses))(
        dispatch(dispatch(Character(), "add_status", status=Status("Rage"), ticks=3).state,
                 "add_status", status=Status("Rage"), ticks=3).state))


@S.case("e-language-no-name", "D7: a language with neither id nor name is refused", "rejected")
def _noname():
    try:
        dispatch(Character(training=500), "buy_language")
    except CommandError:
        return "rejected"
    return "accepted"


S.case("e-slug", "ids.py: punctuation and spaces -> one underscore; empty -> 'id'", ("long_sword_2", "id"))(
    lambda: (ids.slug("  Long-Sword (2) "), ids.slug("!!")))

if __name__ == "__main__":
    sys.exit(S.run())
