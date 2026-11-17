"""Attack and damage breakdown vs RULES/combat.md, weapons.md, defense.md.
Run: python Wp_claude/tests/model/test_attack.py

Every expected number is worked out line by line in a comment, so the owner can
check it by hand. Shared sample hero (unless a test says otherwise):
  level 5, BAB 5, Str 16 (mod +3), Dex 18 (mod +4), in combat.
  Longsword in one hand: weapon node "longsword" (6 bought grades -> level 6),
  parent group "heavy_blades"; mastery picks: slot 5 "attack +1", slot 6 "crit +1".
  The sword item: tab "not activated" gives +1 enhancement to attack and damage.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from dataclasses import replace  # noqa: E402

from wp.catalog import feats_catalog as fc  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.pain import PainEntry, PainProfile  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model.character import Ability, Character, Feat, Item, WeaponEntry  # noqa: E402

S = Suite("test_attack")


def abil(**scores):
    a = dict(Character().abilities)
    for k, v in scores.items():
        a[k] = Ability(v)
    return a


SWORD = Item("i-sword", "longsword", equipped=True, weapon_id="longsword", grip="one",
             effects_off=(Effect(bo.ATTACK, 1, bo.ENHANCEMENT), Effect(bo.DAMAGE, 1, bo.ENHANCEMENT)))
WEAPONS = (WeaponEntry(Weapon("heavy_blades", 3, 1), "heavy blades"),
           WeaponEntry(Weapon("longsword", 2, 1, grades=6, parents=("heavy_blades",)), "long swords",
                       (Pick(5, "attack_1"), Pick(6, "crit_1"))))


def hero(**kw):
    base = dict(level=5, bab=5, abilities=abil(str=16, dex=18), in_combat=True,
                items=(SWORD,), weapons=WEAPONS)
    base.update(kw)
    return Character(**base)


# ---------------------------------------------------------------- to hit

# BAB 5
# + Str mod +3              (default attack stat is Str)
# + proficiency +1           (mastery pick "attack +1" on the longsword node)
# + enhancement +1           (the sword's own tab)
# = 10                       (out of combat? no: in combat, but morale scale 0 -> +0)
S.case("to-hit-basic", "combat.md / weapons.md: BAB + Str + proficiency + enhancement", 10)(
    lambda: av.attack(hero(), SWORD).to_hit)


# Same + group bonus: status "Blade style" +1 competence to attacks with group heavy_blades.
# Sword (in heavy_blades): 10 + competence 1 = 11.
# Axe (not in the group, no mastery, no tab): BAB 5 + Str 3 = 8 (no competence).
@S.case("to-hit-group", "weapons.md: group bonus counts only for a weapon of that group", (11, 8))
def _group():
    st = Status("Blade style", effects=(Effect(bo.ATTACK, 1, "competence", weapon="heavy_blades"),))
    axe = Item("i-axe", "axe", equipped=True, weapon_id="axe")
    ch = hero(statuses=(st,), items=(SWORD, axe), weapons=WEAPONS + (WeaponEntry(Weapon("axe")),))
    return (av.attack(ch, SWORD).to_hit, av.attack(ch, axe).to_hit)


# Morale scale 4 in combat -> trunc(4/2) = +2 morale; pain: one entry of 1 -> -1.
# 10 + morale 2 - pain 1 = 11
S.case("to-hit-morale-pain", "defense.md morale + resources.md pain", 11)(
    lambda: av.attack(hero(morale_scale=4, pain=(PainEntry(1, "overflow"),)), SWORD).to_hit)

# Morale counts only in combat: out of combat morale 0 -> 10.
S.case("morale-out-of-combat", "defense.md: morale only while combat is active", 10)(
    lambda: av.attack(hero(morale_scale=4, in_combat=False), SWORD).to_hit)

# Pain profile "pain gives no penalties": pain 3 -> 0. To hit stays 10.
S.case("pain-no-penalty", "resources.md: 'pain gives no penalties' race", 10)(
    lambda: av.attack(hero(pain=(PainEntry(3),), pain_profile=PainProfile(no_penalty=True)), SWORD).to_hit)


# defense.md Example [OWNER]: morale +1 on everything (scale 2 -> trunc(2/2) = 1) and a spell
# morale penalty -2 on attacks. Same type morale: +1 vs -2 -> the larger absolute value wins: -2.
# To hit: 10 + morale(-2) = 8.   Damage: Str 3 + enhancement 1 + morale(+1) = 5.
@S.case("morale-same-type", "defense.md Example [OWNER]: attacks -2, damage +1", (8, 5))
def _morale_type():
    spell = Status("bane", effects=(Effect(bo.ATTACK, -2, bo.MORALE),))
    v = av.attack(hero(morale_scale=2, statuses=(spell,)), SWORD)
    return (v.to_hit, v.damage)


# defense.md Example [OWNER]: heroism +4 morale on attacks, morale scale -2 (-> -1 on everything).
# To hit: +4 vs -1 -> +4: 10 + 4 = 14.   Damage: Str 3 + enhancement 1 + morale(-1) = 3.
@S.case("heroism", "defense.md Example [OWNER]: attacks +4, damage -1", (14, 3))
def _heroism():
    h = Status("heroism", effects=(Effect(bo.ATTACK, 4, bo.MORALE),))
    v = av.attack(hero(morale_scale=-2, statuses=(h,)), SWORD)
    return (v.to_hit, v.damage)


# Enhancement +1 on the sword and "magic weapon" status +1 enhancement -> +1, not +2 (defense.md Example).
# To hit stays 10.
S.case("enchant-not-stack", "defense.md Example: +1 sword + magic weapon +1 -> +1", 10)(
    lambda: av.attack(hero(statuses=(Status("magic weapon", effects=(Effect(bo.ATTACK, 1, bo.ENHANCEMENT),)),)),
                      SWORD).to_hit)


# Another equipped weapon's own +2 enhancement does NOT leak into the longsword attack: stays 10.
@S.case("other-weapon-no-leak", "attack: one weapon's bonuses stay with that weapon", 10)
def _leak():
    dagger = Item("i-dag", "dagger", equipped=True, weapon_id="dagger", grip="off",
                  effects_off=(Effect(bo.ATTACK, 2, bo.ENHANCEMENT),))
    return av.attack(hero(items=(SWORD, dagger), weapons=WEAPONS + (WeaponEntry(Weapon("dagger")),)),
                     SWORD).to_hit


# weapons.md qualification: the longsword node needs level 7, the hero has level 6 -> one below -> -2.
# 10 - 2 = 8.   Needs 8 (two below) -> -4: 10 - 4 = 6.
@S.case("qualification", "weapons.md: -2 one level below, -4 further below", (8, 6))
def _qual():
    def need(n):
        w = (WEAPONS[0], WeaponEntry(Weapon("longsword", 2, 1, grades=6, parents=("heavy_blades",),
                                            required_level=n), "long swords", WEAPONS[1].picks))
        return av.attack(hero(weapons=w), SWORD).to_hit
    return (need(7), need(8))


# Finesse: a rapier (finesse weapon) with the "Finesse training" feat uses the better of Str/Dex.
# Rapier has no mastery and no tab bonus: BAB 5 + Dex 4 = 9.  Without the feat: BAB 5 + Str 3 = 8.
@S.case("finesse", "combat.md + feat Finesse training: better of Str/Dex", ((9, "dex"), (8, "str")))
def _finesse():
    rapier = Item("i-rap", "rapier", equipped=True, weapon_id="rapier", finesse=True)
    w = WEAPONS + (WeaponEntry(Weapon("rapier")),)
    feat = Feat("finesse_training", flags=(fc.FINESSE,))
    a = av.attack(hero(items=(rapier,), weapons=w, feats=(feat,)), rapier)
    b = av.attack(hero(items=(rapier,), weapons=w), rapier)
    return ((a.to_hit, a.stat), (b.to_hit, b.stat))


# Any stat may be chosen for a special attack (quirk/race): Wis 14 (+2): BAB 5 + Wis 2 + prof 1 + ench 1 = 9.
S.case("chosen-stat", "combat.md: attack stat can be chosen (quirk/race effects)", (9, "wis"))(
    lambda: (lambda v: (v.to_hit, v.stat))(
        av.attack(hero(abilities=abil(str=16, dex=18, wis=14)), SWORD, stat="wis")))


# Unarmed (nothing in hand): BAB 5 + Str 3 = 8; damage Str 3 (one hand factor 1x).
@S.case("unarmed", "combat.md: unarmed attack uses BAB + Str", ("unarmed", 8, 3))
def _unarmed():
    v = av.all_attacks(hero(items=()))[0]
    return (v.weapon, v.to_hit, v.damage)


# ---------------------------------------------------------------- damage

# One hand: Str +3 x1 = 3, + enhancement 1 = 4.
S.case("damage-one-hand", "owner: one hand 1x Str", 4)(lambda: av.attack(hero(), SWORD).damage)

# Str to damage by grip, owner examples: mod +3 two hands: 3 * 1.5 = 4.5 -> round down 4;
# off-hand: 3 * 0.5 = 1.5 -> 1; one hand: 3.
S.case("str-grip-positive", "owner: +3 -> two hands 4, off-hand 1, one hand 3", (4, 1, 3))(
    lambda: (av.str_damage(3, "two"), av.str_damage(3, "off"), av.str_damage(3, "one")))

# Negative mod is not multiplied: -2 with any grip -> -2.
S.case("str-grip-negative", "owner: -2 with any grip -> -2", (-2, -2, -2))(
    lambda: (av.str_damage(-2, "two"), av.str_damage(-2, "off"), av.str_damage(-2, "one")))

# Odd mods round down: +1 two hands 1.5 -> 1; +1 off-hand 0.5 -> 0; +5 two hands 7.5 -> 7.
S.case("str-grip-round-down", "owner: positive bonus rounds DOWN", (1, 0, 7))(
    lambda: (av.str_damage(1, "two"), av.str_damage(1, "off"), av.str_damage(5, "two")))


# Two-handed greatsword, Str 16 (+3): Str 4 (4.5 down) + no tab = 4.
@S.case("damage-two-hands", "owner: two hands 1.5x Str, round down", 4)
def _two():
    gs = Item("i-gs", "greatsword", equipped=True, weapon_id="greatsword", grip="two")
    return av.attack(hero(items=(gs,), weapons=WEAPONS + (WeaponEntry(Weapon("greatsword")),)), gs).damage


# Str 6 (mod -2) with the sword in one hand: damage = -2 + enhancement 1 = -1; to hit = 5 - 2 + 1 + 1 = 5.
S.case("damage-negative-str", "owner: negative Str applied once", (-1, 5))(
    lambda: (lambda v: (v.damage, v.to_hit))(av.attack(hero(abilities=abil(str=6, dex=18)), SWORD)))


# Mastery "damage +3" (expert pick) on the node, level 8 with 3 specialist picks:
# damage = Str 3 + enhancement 1 + mastery 3 = 7.
@S.case("damage-mastery", "weapons.md: mastery damage +3 as flat", 7)
def _mastery_dmg():
    picks = (Pick(5, "attack_1"), Pick(6, "crit_1"), Pick(7, "parry_1"), Pick(8, "damage_3"))
    w = (WEAPONS[0], WeaponEntry(Weapon("longsword", 2, 1, grades=8, parents=("heavy_blades",)),
                                 "long swords", picks))
    return av.attack(hero(weapons=w), SWORD).damage


# Pain on damage too: pain 2 -> damage 4 - 2 = 2 (pain hits damage rolls, resources.md).
S.case("damage-pain", "resources.md: pain -1 per pain on damage", 2)(
    lambda: av.attack(hero(pain=(PainEntry(2),)), SWORD).damage)


# Group bonus to damage: status +2 flat damage with heavy_blades -> 4 + 2 = 6.
S.case("damage-group", "weapons.md: group bonus to damage", 6)(
    lambda: av.attack(hero(statuses=(Status("style", effects=(Effect(bo.DAMAGE, 2, weapon="heavy_blades"),)),)),
                      SWORD).damage)

# --------------------------------------------------------- shape and hint

S.case("lines-sum", "attack view: lines add up to the totals", True)(
    lambda: (lambda v: sum(x.value for x in v.to_hit_lines) == v.to_hit
             and sum(x.value for x in v.damage_lines) == v.damage)(
        av.attack(hero(morale_scale=4, pain=(PainEntry(1),)), SWORD)))
S.case("crit-hint", "combat.md: tooltip only: x2 +0, x3 +4, x4 +8", ("+0", "+4", "+8"))(
    lambda: tuple(av.crit_hint(m) for m in (2, 3, 4)))


# Feat catalog: Finesse training is data, costs 200 from training; race source is free.
@S.case("feat-catalog", "training.md: feat from catalog, 200; only training spends",
        ("finesse_training", ("finesse",), 800, 1000))
def _feat():
    cat = fc.load_default()
    t = cat.get("finesse_training")
    a = dispatch(Character(), "add_feat", catalog=cat, fid="finesse_training").state
    b = dispatch(Character(), "add_feat", catalog=cat, fid="finesse_training", source="race").state
    return (t.fid, t.flags, a.training, b.training)


@S.case("feat-twice", "a feat can be taken only once", "rejected")
def _twice():
    cat = fc.load_default()
    ch = dispatch(Character(), "add_feat", catalog=cat, fid="finesse_training").state
    try:
        dispatch(ch, "add_feat", catalog=cat, fid="finesse_training")
    except CommandError:
        return "rejected"
    return "allowed"


if __name__ == "__main__":
    sys.exit(S.run())
