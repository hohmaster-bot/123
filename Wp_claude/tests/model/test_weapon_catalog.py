"""Weapon catalog rows, Unarmed combat as a weapon, owner answers Q16 and Q19.
Run: python Wp_claude/tests/model/test_weapon_catalog.py
(Russian text is not compared here: code files are ASCII only; ids and numbers are.)"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from dataclasses import replace  # noqa: E402

from wp.catalog import feats_catalog as fc  # noqa: E402
from wp.catalog import store as cs  # noqa: E402
from wp.catalog import weapons_catalog as wc  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import Ability, AttackRecord, Character, Feat, Item, WeaponEntry  # noqa: E402
from wp.model.factory import new_character  # noqa: E402

S = Suite("test_weapon_catalog")
CAT = wc.load_default()
DATA = json.load(io.open(cs.shipped_path(wc.WEAPONS), encoding="utf-8"))   # catalog file (package 18)
LEVELS = DATA["meta"]["qualification_levels"]


def card(wid):
    return wc.make_item(CAT, wid, "x")


def rejected(fn):
    try:
        fn()
    except (CommandError, ValueError, KeyError):
        return "rejected"
    return "allowed"


# ----------------------------------------------------------------- catalog rows

S.case("contact-rows", "weapons.md [OWNER]: group Contact rows",
       ("unarmed_combat", "stiletto", "spiked_gauntlet", "improvised", "hidden_thief"))(
    lambda: wc.group_weapons(CAT, "contact"))
S.case("basic-rows", "weapons.md [OWNER]: group Basic/simple rows",
       ("dagger", "club", "quarterstaff", "light_crossbow", "bolts"))(
    lambda: wc.group_weapons(CAT, "basic_simple"))

# Dagger: 1 gp = 10 sp, 1d3/1d4, 19+ (x2), 10 ft, weight L (-> 1 L, Q21), P/S, finesse, 1H, HD 10, HP 1.
S.case("dagger-card", "owner table: Dagger",
       (10, "1d3", "1d4", 19, 2, 10, 1, "P/S", True, 1, 10, 1))(
    lambda: (lambda c: (c.price_sp, c.damage_small, c.damage_medium, c.crit_range, c.crit_mult, c.range_ft,
                        c.weight_l, c.dmg_type, c.finesse, c.hands, c.durability, c.hp))(card("dagger")))
# Light crossbow: 1 gp, 1d6/1d8, 19-20 (x2), 80 ft, weight 1 (-> 10 L, Q21), P, 2H, HD 3, HP 2.
S.case("crossbow-card", "owner table: Light crossbow", (10, "1d6", "1d8", 19, 80, 10, "P", 2, 3, 2))(
    lambda: (lambda c: (c.price_sp, c.damage_small, c.damage_medium, c.crit_range, c.range_ft, c.weight_l,
                        c.dmg_type, c.hands, c.durability, c.hp))(card("light_crossbow")))
# Stiletto: 5 sp, x3 (crit on 20), HD 10, HP 1, qualification Skilled -> level 4.
S.case("stiletto-card", "owner table: Stiletto, qualification Skilled = 4", (5, 20, 3, 10, 1, 4, True))(
    lambda: (lambda c: (c.price_sp, c.crit_range, c.crit_mult, c.durability, c.hp, c.required_level, c.finesse))(
        card("stiletto")))
S.case("qualification-words", "weapons.md: qualification as words, mapped to levels",
       (LEVELS[card("unarmed_combat").qualification], 6))(
    lambda: (card("unarmed_combat").required_level, card("hidden_thief").required_level))
S.case("vary-fields", "weapons.md: 'Vary.' -> empty field marked variable",
       (("damage_small", "damage_medium", "weight_l", "dmg_type", "hands"), "", 0))(
    lambda: (lambda c: (c.variable, c.damage_small, c.hands))(card("improvised")))
S.case("quarterstaff-double", "owner (B1, Q21): Quarterstaff is a double weapon, two damage rows",
       (True, ("1d4", "1d6"), ("1d4", "1d6"), 2))(
    lambda: (lambda c: (c.double, (c.damage_small, c.damage_medium), (c.damage_small2, c.damage_medium2), c.hands))(
        card("quarterstaff")))
S.case("bolts-ammo", "weapons.md: bolts are ammo with a quantity of 10 (pkg 14, Q86: count -> quantity)", ("ammo", 10, 1, 0, 1))(
    lambda: (lambda c: (c.kind, c.quantity, c.price_sp, c.durability, c.hp))(card("bolts")))

# ------------------------------------------------------------ unarmed as weapon

# New character: Contact node, Unarmed combat node (scale 1, parent contact) and the Unarmed combat card.
S.case("new-character-unarmed", "weapons.md [OWNER]: Unarmed combat is a weapon in Contact",
       ((("contact", 3, ()), ("unarmed_combat", 1, ("contact",))), "unarmed", ("contact",), True, False))(
    lambda: (lambda ch: (tuple((e.weapon.name, e.weapon.scale, e.weapon.parents) for e in ch.weapons),
                         ch.items[0].iid, ch.items[0].groups, ch.items[0].finesse, ch.items[0].in_hands))(
        new_character()))


def abil(**scores):
    a = dict(Character().abilities)
    for k, v in scores.items():
        a[k] = Ability(v)
    return a


# The unarmed attack uses the card: finesse + Finesse training -> Dex. Level 5, BAB 5, Str 12 (+1), Dex 16 (+3).
# Unarmed combat node raised to level 4 (Skilled, so no qualification penalty): 5 + Dex 3 = 8.
@S.case("unarmed-finesse", "card finesse: unarmed uses the better of Str/Dex with the feat", (8, "dex"))
def _fin():
    ch = new_character(level=5, bab=5, abilities=abil(str=12, dex=16),
                       feats=(Feat("finesse_training", flags=(fc.FINESSE,)),))
    ch = replace(ch, weapons=(ch.weapons[0], replace(ch.weapons[1], weapon=replace(ch.weapons[1].weapon, grades=4))))
    v = av.by_record(ch, "unarmed")
    return (v.to_hit, v.stat)


# Q20 (open): the table gives Unarmed combat qualification Skilled (4); a new character has the node at 0
# -> 3+ levels below -> -4. Level 1, BAB 0, Str 10: 0 + 0 - 4 = -4.
S.case("unarmed-qualification-new", "weapons.md + table, see OPEN_QUESTIONS Q20: new character unarmed -4", -4)(
    lambda: av.by_record(new_character(), "unarmed").to_hit)


# -------------------------------------------------------------------- Q16, Q19

def sheet(attacks, weapons, items):
    return Character(level=5, bab=5, abilities=abil(str=16), items=items, weapons=weapons, attacks=attacks)


A = WeaponEntry(Weapon("blades", grades=6), "", (Pick(5, "attack_1"), Pick(6, "balance_regen_1")))
B = WeaponEntry(Weapon("axes", grades=6), "", (Pick(5, "attack_1"), Pick(6, "balance_regen_1")))
SW = Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("blades",))
AX = Item("ax", "axe", kind="weapon", hands=1, in_hands=True, groups=("axes", "blades"))

# Q16 [OWNER]: two primary records with DIFFERENT groups: regen +1 +1. Level 5 + Con 0 + 2 = 7.
S.case("q16-different-groups-add", "combat.md [OWNER, Q16]: different groups add up", 7)(
    lambda: dv.balance_regen(sheet((AttackRecord("s", "sw", "blades", primary=True),
                                    AttackRecord("a", "ax", "axes", "off", primary=True)), (A, B), (SW, AX))))
# Same group on both primary records counts once: 5 + 1 = 6.
S.case("q16-same-group-once", "combat.md [OWNER, Q16]: the same group counts once", 6)(
    lambda: dv.balance_regen(sheet((AttackRecord("s", "sw", "blades", primary=True),
                                    AttackRecord("a", "ax", "blades", "off", primary=True)), (A, B), (SW, AX))))

RAP = Item("rp", "rapier", kind="weapon", hands=1, finesse=True, groups=("blades",))
MACE = Item("mc", "mace", kind="weapon", hands=1, groups=("blades",))

# Q19 [OWNER]: non-finesse one-hander two-handed is allowed (Str 3 x 1.5 = 4.5 -> 4);
# finesse one-hander two-handed is rejected; finesse off-hand is allowed.
S.case("q19-two-hands-non-finesse", "combat.md [OWNER, Q19]: mace in two hands, Str x1.5", 4)(
    lambda: (lambda ch: av.by_record(ch, "mc:blades:two").damage)(
        dispatch(sheet((), (A,), (replace(MACE, in_hands=True),)), "add_attack", iid="mc", group="blades",
                 grip="two").state))
S.case("q19-finesse-two-hands", "combat.md [OWNER, Q19]: finesse weapon cannot be two-handed", "rejected")(
    lambda: rejected(lambda: dispatch(sheet((), (A,), (RAP,)), "add_attack", iid="rp", group="blades", grip="two")))
S.case("q19-finesse-off-hand", "combat.md [OWNER, Q19]: finesse weapon off-hand is fine", "allowed")(
    lambda: rejected(lambda: dispatch(sheet((), (A,), (RAP,)), "add_attack", iid="rp", group="blades", grip="off")))
S.case("q19-unarmed-two-hands", "Q19: the unarmed card is finesse -> no two-handed unarmed record", "rejected")(
    lambda: rejected(lambda: dispatch(new_character(), "add_attack", iid="unarmed", group="unarmed_combat", grip="two")))

if __name__ == "__main__":
    sys.exit(S.run())
