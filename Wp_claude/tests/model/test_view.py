"""Derived view vs RULES/. Run: python Wp_claude/tests/model/test_view.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core import skills as sk  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.pain import PainEntry as PE  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import Ability, Character, Item, WeaponEntry  # noqa: E402

S = Suite("test_view")


def ab(**scores):
    a = dict(Character().abilities)
    for k, v in scores.items():
        a[k] = v if isinstance(v, Ability) else Ability(v)
    return a


# rest.md Example [OWNER]: 4 max HP -> BP 1; leather armor 2; race +3 -> balance max 6.
@S.case("balance-max", "rest.md Example [OWNER]: 4 HP, leather 2, race +3 -> 6", (1, 6))
def _bal():
    ch = Character(hp_rolls=(4,), hp_current=4, bp_current=1, balance_bonus=3,
                   items=(Item("i1", "leather", equipped=True, armor=2),))
    return (dv.bp_max(ch), dv.balance_max(ch))


S.case("bp-from-max-hp", "rest.md: BP cap from MAX HP (HP 5 of 20 -> 5)", 5)(
    lambda: dv.bp_max(Character(level=3, hp_rolls=(8, 6, 6), hp_current=5)))
S.case("hp-max-con", "HP max = rolls + Con mod per level", 26)(
    lambda: dv.hp_max(Character(level=3, hp_rolls=(8, 6, 6), abilities=ab(con=14))))
S.case("regen", "rest.md: level + Con mod + other, min 1", (5, 1))(
    lambda: (dv.balance_regen(Character(level=3, abilities=ab(con=14))),
             dv.balance_regen(Character(level=1, abilities=ab(con=4)))))
S.case("stat-current", "stats.md Tests: Str 18/18, drain 1 -> 17; permanent 1 -> max 17",
       (17, 17, 18))(lambda: (dv.ability_current(Character(abilities=ab(str=Ability(18, damage=1))), "str"),
                              Ability(18, permanent=1).score_max, Ability(16, race=2).score_max))

# stats.md Tests [OWNER, corrected]: Str 18, damage 3 (current 15), permanent damage 1 -> 14/17.
# max = 18 - 1 = 17; current = 17 - 3 = 14.
S.case("stat-permanent-on-damaged", "stats.md [OWNER]: 15/18 + permanent 1 -> 14/17", (14, 17))(
    lambda: (lambda a: (a.current, a.score_max))(Ability(18, damage=3, permanent=1)))

# gear.md "Armor": skill penalty on Str/Dex skills. Worn mail with skill penalty -2, Dex 14 (+2), Int 14 (+2):
# stealth (Dex, penalty applies) = ranks 0 + Dex 2 - 2 = 0; arcana (Int, no penalty) = 0 + 2 = 2.
@S.case("armor-skill-penalty", "gear.md Armor: skill penalty to Str/Dex skills only", (0, 2, 2))
def _penalty():
    from wp.catalog import skills_catalog as sc
    cat = sc.load_default()
    mail = Item("m", "mail", equipped=True, armor=4, skill_penalty=-2)
    ch = Character(abilities=ab(dex=14, int=14), items=(mail,),
                   skills=(sc.make_skill(cat, "stealth"), sc.make_skill(cat, "know_magic")))
    no_armor = Character(abilities=ab(dex=14, int=14), skills=ch.skills)
    return (dv.skill_bonus(ch, "stealth"), dv.skill_bonus(ch, "know_magic"), dv.skill_bonus(no_armor, "stealth"))

# gear.md Weight: Str +2 -> light to 7.9 B (79 L).
S.case("load", "gear.md Weight Example: Str +2 -> 79 L light, 80 L heavy", ("light", "heavy"))(
    lambda: tuple(dv.load_status(Character(abilities=ab(str=14), items=(Item("b", "bag", weight_l=w),)))
                  for w in (79, 80)))

# Pain penalty on all rolls except lucky; morale only in combat.
S.case("pain-penalty", "resources.md [OWNER]: -1 per pain on rolls, not lucky", (-3, 0))(
    lambda: (dv.total(Character(pain=(PE(3),)), bo.SAVE), dv.total(Character(pain=(PE(3),)), bo.LUCKY)))
S.case("pain-hp", "resources.md: total pain includes HP below 0 (-7 -> 2)", 3)(
    lambda: dv.pain_total(Character(pain=(PE(1),), hp_current=-7)))
S.case("morale", "defense.md: morale scale 4 -> +2 in combat, 0 out of combat", (2, 0))(
    lambda: (dv.total(Character(morale_scale=4, in_combat=True), bo.ATTACK),
             dv.total(Character(morale_scale=4), bo.ATTACK)))

# defense.md AC: armor item, Dex, flat-footed.
_ARMORED = Character(abilities=ab(dex=16), items=(Item("a", "mail", equipped=True, armor=4, max_dex=2),
                                                  Item("s", "shield", kind="shield", in_hands=True, hands=1, shield=2)))
S.case("ac", "defense.md: front 10+2(max dex)+4+2, flat-footed no Dex/shield, touch", (18, 14, 12))(
    lambda: (dv.ac(_ARMORED), dv.ac(_ARMORED, "flat_footed"), dv.ac(_ARMORED, "touch")))


# gear.md D17: two tabs, exactly one acts.
@S.case("item-tabs", "gear.md [OWNER]: +5 sword inactive +1, active +5 (only one tab)", (1, 5))
def _tabs():
    it = Item("sw", "sword", equipped=True, effects_off=(Effect(bo.ATTACK, 1),),
              effects_on=(Effect(bo.ATTACK, 5, bo.ENHANCEMENT),))
    on = Item("sw", "sword", equipped=True, effects_off=it.effects_off, effects_on=it.effects_on, activated=True)
    return (dv.total(Character(items=(it,)), bo.ATTACK), dv.total(Character(items=(on,)), bo.ATTACK))


# buffs.md [OWNER]: natural weapon attack and damage = current overload.
@S.case("overload-source", "buffs.md [OWNER]: natural weapons bonus = current overload", (3, 3, 0))
def _ov():
    st = Status("feral", effects=(Effect(bo.ATTACK, value_source=ef.OVERLOAD, weapon="natural"),
                                  Effect(bo.DAMAGE, value_source=ef.OVERLOAD, weapon="natural")))
    ch = Character(statuses=(st,), overload=3)
    return (dv.total(ch, bo.ATTACK, "natural"), dv.total(ch, bo.DAMAGE, "natural"),
            dv.total(ch, bo.ATTACK, "sword"))


S.case("skill-bonus", "skills.md: ranks 3 + Int mod 2 + advanced 3 + morale 1", 9)(
    lambda: dv.skill_bonus(Character(level=3, abilities=ab(int=14), morale_scale=2, in_combat=True,
                                     skills=(sk.Skill("arcana", "int", sk.ADVANCED, 3),)), "arcana"))
S.case("weapon-level", "weapons.md Example: basics on sword, variety, group -> 4", 4)(
    lambda: dv.weapon_level(Character(weapons=(
        WeaponEntry(Weapon("g", 3, 1, basics=True)), WeaponEntry(Weapon("v", 2, 1, basics=True, parents=("g",))),
        WeaponEntry(Weapon("s", 1, 1, basics=True, parents=("v",))))), "s"))
# weapons.md / owner: "Unarmed combat" bonuses always work, even when armed: parry +1 there -> AC parry 11.
S.case("unarmed-combat-parry", "owner: Unarmed combat parry +1 works always (front 10, parry 11)", (10, 11))(
    lambda: (lambda ch: (dv.ac(ch), dv.ac(ch, "parry")))(
        Character(weapons=(WeaponEntry(Weapon("unarmed_combat", grades=5), picks=(Pick(5, "parry_1"),)),))))
# A group's parry from a weapon NOT in the hands gives nothing (no attack record visible): parry 10.
S.case("group-parry-not-held", "owner: group bonuses only through a primary attack record", 10)(
    lambda: dv.ac(Character(items=(Item("sw", "sword", kind="weapon", hands=1, groups=("blades",)),),
                            weapons=(WeaponEntry(Weapon("blades", grades=5), picks=(Pick(5, "parry_1"),)),)), "parry"))

if __name__ == "__main__":
    sys.exit(S.run())
