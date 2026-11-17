"""Group B: double weapon, light = finesse flag, catalog weight, spiked gauntlets, Q20.
Run: python Wp_claude/tests/model/test_group_b.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from dataclasses import replace  # noqa: E402

from wp.catalog import weapons_catalog as wc  # noqa: E402
from wp.commands import dispatch  # noqa: E402
from wp.core import ac as acm  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import AttackRecord, Character, WeaponEntry  # noqa: E402
from wp.model.factory import new_character  # noqa: E402

S = Suite("test_group_b")
CAT = wc.load_default()


def card(wid, iid=None, **kw):
    return replace(wc.make_item(CAT, wid, iid or wid), **kw)


# B1: the normal attack with a double weapon uses the TOP damage row.
# The real quarterstaff has equal rows, so a test double weapon with DIFFERENT rows proves which one is used:
# top row 1d4/1d6, other end 1d3/1d4 -> the normal attack shows the top row.
@S.case("b1-double-top-row", "owner: double weapon, normal attack uses the top row", ("1d4", "1d6"))
def _b1():
    staff = card("quarterstaff", in_hands=True, damage_small2="1d3", damage_medium2="1d4")
    ch = Character(items=(staff,), weapons=(WeaponEntry(Weapon("basic_simple", basic=True)),),
                   attacks=(AttackRecord("q", "quarterstaff", "basic_simple", "two"),))
    return av.by_record(ch, "q").dice


S.case("b1-second-row", "owner: the other end has its own row", ("1d4", "1d6"))(
    lambda: av.dice_row(card("quarterstaff"), 2))
S.case("b1-single-weapon-row2", "a normal weapon has no second row: row 2 = row 1", ("1d3", "1d4"))(
    lambda: av.dice_row(card("dagger"), 2))
S.case("b1-double-two-hands", "owner: a double weapon is fine for fighting two-handed", "allowed")(
    lambda: (lambda: "allowed")() if dispatch(Character(items=(card("quarterstaff"),)), "add_attack",
                                               iid="quarterstaff", group="basic_simple", grip="two") else "rejected")

# B2: light and finesse are ONE flag ("F."); unarmed always light.
S.case("b2-light-flag", "owner: light = finesse (column F.); unarmed always light",
       (True, False, True, True))(
    lambda: (wc.is_light(card("dagger")), wc.is_light(card("club")), wc.is_light(None),
             wc.is_light(card("unarmed_combat", "unarmed"))))

# B3: weight 'L' -> 1 L; a plain number N -> N * 10 L (club '1' -> 10 L).
S.case("b3-weight", "catalog.md [OWNER]: L = 1 L, 1 = 10 L", (1, 10, 10))(
    lambda: (card("dagger").weight_l, card("club").weight_l, card("light_crossbow").weight_l))


# B4: spiked gauntlets cannot parry: their record parry is 0 even if the group has "parry +1";
# as primary record the group's parry does not reach AC; Unarmed combat parry still works (empty hand).
# (AC parry numbers include the level-1 base parry 1, training.md pkg 4 / Q27.)
@S.case("b4-gauntlets-no-parry", "owner: no parry with spiked gauntlets = empty-hand parry", (0, 11, 12))
def _b4():
    g = card("spiked_gauntlet", "sg", in_hands=True)
    contact = WeaponEntry(Weapon("contact", 3, grades=5), "", (Pick(5, "parry_1"),))
    uc = WeaponEntry(Weapon("unarmed_combat", 1, grades=5, parents=("contact",)), "", (Pick(5, "parry_1"),))
    base = Character(items=(g,), weapons=(contact,), attacks=(AttackRecord("g", "sg", "contact", primary=True),))
    with_uc = replace(base, weapons=(contact, uc))
    return (av.by_record(base, "g").parry, dv.ac(base, acm.PARRY), dv.ac(with_uc, acm.PARRY))


# B5 / Q20: unarmed combat has no privileges: -4 until trained to level 4 (Skilled).
@S.case("b5-unarmed-qualification", "weapons.md [OWNER, Q20]: unarmed -4 at level 0, none at level 4", (-4, 0))
def _b5():
    ch = new_character()
    trained = replace(ch, weapons=(ch.weapons[0], replace(ch.weapons[1], weapon=replace(ch.weapons[1].weapon, grades=4))))
    return (av.by_record(ch, "unarmed").to_hit, av.by_record(trained, "unarmed").to_hit)


if __name__ == "__main__":
    sys.exit(S.run())
