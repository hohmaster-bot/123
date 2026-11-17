"""Attack records, weapon groups, hands (RULES/combat.md, weapons.md, defense.md, gear.md).
Run: python Wp_claude/tests/model/test_attack.py

Every expected number is worked out in a comment. Shared sample hero:
  level 5, BAB 5, Str 16 (+3), Dex 18 (+4), Con 10 (+0), in combat.
  Longsword (1 hand) in the hands, groups: long_swords and heavy_blades.
  Its tab "not activated": +1 enhancement to attack and damage.
  Groups (mastery nodes):
    heavy_blades: level 8, picks 5 attack +1, 6 balance regen +1, 7 parry +1, 8 damage +3
    long_swords:  level 6, parent heavy_blades, picks 5 attack +1, 6 crit +1
  Records: "ls" = longsword + long_swords, one hand; "hb" = longsword + heavy_blades, one hand.
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
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import Ability, AttackRecord, Character, Feat, Item, WeaponEntry  # noqa: E402

S = Suite("test_attack")


def abil(**scores):
    a = dict(Character().abilities)
    for k, v in scores.items():
        a[k] = Ability(v)
    return a


SWORD = Item("sw", "longsword", kind="weapon", hands=1, in_hands=True, groups=("long_swords", "heavy_blades"),
             effects_off=(Effect(bo.ATTACK, 1, bo.ENHANCEMENT), Effect(bo.DAMAGE, 1, bo.ENHANCEMENT)))
HB = WeaponEntry(Weapon("heavy_blades", 3, 1, grades=8), "heavy blades",
                 (Pick(5, "attack_1"), Pick(6, "balance_regen_1"), Pick(7, "parry_1"), Pick(8, "damage_3")))
LS = WeaponEntry(Weapon("long_swords", 2, 1, grades=6, parents=("heavy_blades",)), "long swords",
                 (Pick(5, "attack_1"), Pick(6, "crit_1")))
R_LS = AttackRecord("ls", "sw", "long_swords", "one")
R_HB = AttackRecord("hb", "sw", "heavy_blades", "one")


def hero(**kw):
    base = dict(level=5, bab=5, abilities=abil(str=16, dex=18), in_combat=True,
                items=(SWORD,), weapons=(HB, LS), attacks=(R_LS,))
    base.update(kw)
    return Character(**base)


def view(ch, rid):
    return av.by_record(ch, rid)


def rejected(fn):
    try:
        fn()
    except (CommandError, ValueError, KeyError):
        return "rejected"
    return "allowed"


# ---------------------------------------------------------- records and groups

# Record "ls": BAB 5 + Str 3 + proficiency 1 (long_swords "attack +1") + enhancement 1 = 10.
# Damage: Str 3 (one hand) + enhancement 1 = 4. Parry: long_swords has no parry pick -> 0.
S.case("record-ls", "weapons.md: record = weapon + one group", (10, 4, 0))(
    lambda: (lambda v: (v.to_hit, v.damage, v.parry))(view(hero(), "ls")))


# One weapon, two records, two groups -> different bonuses.
# Record "hb": BAB 5 + Str 3 + proficiency 1 (heavy_blades) + enhancement 1 = 10 to hit;
# damage Str 3 + enhancement 1 + mastery damage 3 = 7; parry 1 (heavy_blades "parry +1").
@S.case("one-weapon-two-groups", "owner: one weapon with two records gives different bonuses", ((10, 4, 0), (10, 7, 1)))
def _two_groups():
    ch = hero(attacks=(R_LS, R_HB))
    return tuple((v.to_hit, v.damage, v.parry) for v in (view(ch, "ls"), view(ch, "hb")))


# No bonuses from two groups at once: both groups have "attack +1" (proficiency adds with itself!),
# yet record "ls" stays at 10 (not 11) and gets no damage +3 from heavy_blades.
S.case("no-two-groups", "owner: bonuses come only from the ONE chosen group", (10, 4))(
    lambda: (lambda v: (v.to_hit, v.damage))(view(hero(attacks=(R_LS, R_HB)), "ls")))


# Parent group adds no bonuses: heavy_blades is the parent of long_swords. A status +1 competence
# to attacks with heavy_blades counts for record "hb" (11) but NOT for record "ls" (10).
@S.case("parent-no-bonus", "owner: parent group bonuses are not added", (10, 11))
def _parent():
    st = Status("style", effects=(Effect(bo.ATTACK, 1, "competence", weapon="heavy_blades"),))
    ch = hero(attacks=(R_LS, R_HB), statuses=(st,))
    return (view(ch, "ls").to_hit, view(ch, "hb").to_hit)


# Two weapons in the hands, each with its own record and group:
# sword (long_swords) one hand -> 10; dagger (basic_simple) off-hand: BAB 5 + Str 3 = 8 to hit,
# damage Str 3 * 0.5 = 1.5 -> 1 (no tab, no mastery).
@S.case("two-weapons", "owner: two weapons in the hands, each with its own record", ((10, 4), (8, 1)))
def _two_weapons():
    dagger = Item("dg", "dagger", kind="weapon", hands=1, in_hands=True, groups=("basic_simple",))
    ch = hero(items=(SWORD, dagger), attacks=(R_LS, AttackRecord("dg", "dg", "basic_simple", "off")))
    return tuple((v.to_hit, v.damage) for v in (view(ch, "ls"), view(ch, "dg")))


# Attacks only for weapons in the hands, plus unarmed always.
S.case("visible-in-hands", "owner: attacks only for weapons in the hands + unarmed always",
       (("ls", "unarmed"), ("unarmed",)))(
    lambda: (tuple(v.record for v in av.all_attacks(hero())),
             tuple(v.record for v in av.all_attacks(hero(items=(replace(SWORD, in_hands=False),))))))


# Basic/simple: no qualification. Dagger needs level 3. In basic_simple: no penalty -> 8.
# The same dagger in a normal group "knives" at level 0 (3 below) -> -4 -> 4.
@S.case("basic-no-penalty", "owner: Basic/simple has no -4/-2 qualification penalty", (8, 4))
def _basic():
    dagger = Item("dg", "dagger", kind="weapon", hands=1, in_hands=True, groups=("basic_simple", "knives"),
                  required_level=3)
    ch = hero(items=(dagger,), weapons=(HB, LS, WeaponEntry(Weapon("knives"))),
              attacks=(AttackRecord("b", "dg", "basic_simple"), AttackRecord("k", "dg", "knives")))
    return (view(ch, "b").to_hit, view(ch, "k").to_hit)


S.case("basic-untrainable", "owner: Basic/simple cannot be trained", "rejected")(
    lambda: rejected(lambda: dispatch(hero(weapons=(WeaponEntry(Weapon("basic_simple", basic=True)),)),
                                      "buy_weapon_grade", wid="basic_simple")))


# Qualification in a normal group: long_swords level 6; sword needs 7 -> -2: 10 - 2 = 8.
S.case("qualification", "weapons.md: -2 one level below", 8)(
    lambda: view(hero(items=(replace(SWORD, required_level=7),)), "ls").to_hit)


# -------------------------------------------------------------- primary records

# Balance regen: level 5 + Con 0 = 5. Primary "hb" (heavy_blades has balance regen +1) -> 6.
# Primary "ls" (no such pick) -> 5.
@S.case("regen-from-primary", "owner: passive group bonus (regen +1) from the primary record", (6, 5))
def _regen():
    a = hero(attacks=(replace(R_HB, primary=True), R_LS))
    b = hero(attacks=(R_HB, replace(R_LS, primary=True)))
    return (dv.balance_regen(a), dv.balance_regen(b))


S.case("single-record-primary", "owner: a single record is primary automatically", 6)(
    lambda: dv.balance_regen(hero(attacks=(R_HB,))))


@S.case("max-two-primary", "owner: at most two primary records", "rejected")
def _max2():
    ch = hero(attacks=(R_LS, R_HB, AttackRecord("x", "sw", "long_swords", "two")))
    for rid in ("ls", "hb"):
        ch = dispatch(ch, "set_primary_attack", rid=rid).state
    return rejected(lambda: dispatch(ch, "set_primary_attack", rid="x"))


# Unarmed combat works always, even armed: its "balance regen +1" -> 5 + 1 = 6 with the sword record "ls".
@S.case("unarmed-always-works", "owner: Unarmed combat bonuses work even when armed", 6)
def _unarmed():
    uc = WeaponEntry(Weapon("unarmed_combat", 1, 1, grades=6, parents=("contact",)), "",
                     (Pick(5, "attack_1"), Pick(6, "balance_regen_1")))
    return dv.balance_regen(hero(weapons=(HB, LS, uc)))


# Unarmed attack (always listed): BAB 5 + Str 3 + Unarmed combat "attack +1" = 9; damage Str 3.
@S.case("unarmed-attack", "owner: unarmed record uses Unarmed combat", (9, 3))
def _unarmed_atk():
    uc = WeaponEntry(Weapon("unarmed_combat", 1, 1, grades=5, parents=("contact",)), "", (Pick(5, "attack_1"),))
    v = view(hero(weapons=(HB, LS, uc)), "unarmed")
    return (v.to_hit, v.damage)


# ---------------------------------------------------- morale, pain, stats, grip

# Morale scale 4 -> +2; pain 1 -> -1: 10 + 2 - 1 = 11.
S.case("morale-pain", "defense.md + resources.md", 11)(
    lambda: view(hero(morale_scale=4, pain=(PainEntry(1),)), "ls").to_hit)
S.case("morale-out-of-combat", "defense.md: morale only in combat", 10)(
    lambda: view(hero(morale_scale=4, in_combat=False), "ls").to_hit)
S.case("pain-no-penalty", "resources.md: 'pain gives no penalties'", 10)(
    lambda: view(hero(pain=(PainEntry(3),), pain_profile=PainProfile(no_penalty=True)), "ls").to_hit)


# defense.md Example [OWNER]: morale +1 (scale 2) and a spell morale -2 on attacks:
# attack -2 wins -> 10 - 2 = 8; damage keeps +1 -> 4 + 1 = 5.
@S.case("morale-same-type", "defense.md Example [OWNER]", (8, 5))
def _mt():
    v = view(hero(morale_scale=2, statuses=(Status("bane", effects=(Effect(bo.ATTACK, -2, bo.MORALE),)),)), "ls")
    return (v.to_hit, v.damage)


# Finesse: rapier + Finesse training -> better of Str 3 / Dex 4 = Dex: 5 + 4 = 9; without the feat: 5 + 3 = 8.
@S.case("finesse", "combat.md + Finesse training", ((9, "dex"), (8, "str")))
def _fin():
    rapier = Item("rp", "rapier", kind="weapon", hands=1, in_hands=True, finesse=True, groups=("rapiers",))
    rec = AttackRecord("rp", "rp", "rapiers")
    a = view(hero(items=(rapier,), attacks=(rec,), feats=(Feat("finesse_training", flags=(fc.FINESSE,)),)), "rp")
    b = view(hero(items=(rapier,), attacks=(rec,)), "rp")
    return ((a.to_hit, a.stat), (b.to_hit, b.stat))


# Chosen stat (quirk/race): Wis 14 (+2): 5 + 2 + 1 + 1 = 9.
S.case("chosen-stat", "combat.md: attack stat chosen on the record", (9, "wis"))(
    lambda: (lambda v: (v.to_hit, v.stat))(view(hero(abilities=abil(str=16, dex=18, wis=14),
                                                     attacks=(replace(R_LS, stat="wis"),)), "ls")))


S.case("str-grip", "owner: +3 -> two hands 4, off 1, one 3; -2 any grip -2",
       ((4, 1, 3), (-2, -2, -2)))(
    lambda: (tuple(av.str_damage(3, g) for g in ("two", "off", "one")),
             tuple(av.str_damage(-2, g) for g in ("two", "off", "one"))))
S.case("crit-hint", "combat.md: tooltip x2 +0, x3 +4, x4 +8", ("+0", "+4", "+8"))(
    lambda: tuple(av.crit_hint(m) for m in (2, 3, 4)))


# Another weapon's own +2 enhancement does not leak into record "ls": stays 10.
@S.case("other-weapon-no-leak", "a weapon's own bonuses stay with that weapon", 10)
def _leak():
    dagger = Item("dg", "dagger", kind="weapon", hands=1, in_hands=True, groups=("basic_simple",),
                  effects_off=(Effect(bo.ATTACK, 2, bo.ENHANCEMENT),))
    return view(hero(items=(SWORD, dagger)), "ls").to_hit


S.case("lines-sum", "attack view: lines add up", True)(
    lambda: (lambda v: sum(x.value for x in v.to_hit_lines) == v.to_hit
             and sum(x.value for x in v.damage_lines) == v.damage)(
        view(hero(morale_scale=4, pain=(PainEntry(1),), attacks=(R_HB,)), "hb")))


# ------------------------------------------------------------- hands (gear.md)

SHIELD = Item("sh", "shield", kind="shield", hands=1, shield=2)
GREAT = Item("gs", "greatsword", kind="weapon", hands=2, groups=("heavy_blades",))
SWORD_FREE = replace(SWORD, in_hands=False)


def equip(ch, *iids):
    for iid in iids:
        ch = dispatch(ch, "equip_hands", iid=iid).state
    return ch


# Shield + sword: AC front 10 + Dex 4 + shield 2 = 16; one sword record + unarmed.
@S.case("shield-and-sword", "gear.md [OWNER]: shield + weapon; shield counts in hand", (16, ("ls", "unarmed")))
def _shield_sword():
    ch = equip(hero(items=(SWORD_FREE, SHIELD)), "sw", "sh")
    return (dv.ac(ch), tuple(v.record for v in av.all_attacks(ch)))


S.case("two-one-handed", "gear.md: two one-handed weapons", 2)(
    lambda: dv.hands_used(equip(hero(items=(SWORD_FREE, replace(SWORD_FREE, iid="sw2"))), "sw", "sw2")))
S.case("two-handed-and-shield", "gear.md [OWNER]: two-handed weapon and shield together -> rejected", "rejected")(
    lambda: rejected(lambda: equip(hero(items=(GREAT, SHIELD)), "gs", "sh")))
# Shield in the bag (not in a hand): AC 10 + Dex 4 = 14, no shield bonus.
S.case("shield-in-bag", "gear.md [OWNER]: shield in the bag gives no AC", 14)(
    lambda: dv.ac(hero(items=(SWORD, SHIELD))))
S.case("two-handed-grip", "a two-handed weapon needs grip two", "rejected")(
    lambda: rejected(lambda: dispatch(hero(items=(GREAT,)), "add_attack", iid="gs", group="heavy_blades", grip="one")))
S.case("group-must-match", "a record's group must be one of the weapon's groups", "rejected")(
    lambda: rejected(lambda: dispatch(hero(), "add_attack", iid="sw", group="axes")))


if __name__ == "__main__":
    sys.exit(S.run())
