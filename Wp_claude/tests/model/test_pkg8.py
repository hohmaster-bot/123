"""Package 8: fixes from REVIEW_REPORT_3 and owner decisions A-H.
Run: python Wp_claude/tests/model/test_pkg8.py"""
import os
import sys
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import ac as acm  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core import rest as rs  # noqa: E402
from wp.core import skills as sk  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.skills import Skill  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import records as rec  # noqa: E402
from wp.model.character import (SHIELD, Ability, AttackRecord, Character, Item,  # noqa: E402
                                WeaponEntry)

S = Suite("test_pkg8")


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def refused(fn):
    try:
        fn()
    except CommandError:
        return "refused"
    return "allowed"


def hero(**kw):
    """Level 1, HP 20/20, BP 5/5, balance 5."""
    base = dict(hp_rolls=(20,), hit_die=20, hp_current=20, bp_current=5, balance_current=5, spirit_current=10)
    base.update(kw)
    return Character(**base)


def abil(**scores):
    out = {a: Ability() for a in ("str", "dex", "con", "int", "wis", "cha")}
    for k, v in scores.items():
        out[k] = Ability(base=v)
    return out


def sword(**kw):
    base = dict(kind="weapon", hands=1, in_hands=True, groups=("blades",), hp=10, durability=10)
    base.update(kw)
    return Item("sw", "sword", **base)


SW_REC = AttackRecord("r", "sw", "blades")


def mastery(*bonuses):
    picks = tuple(Pick(slot, b) for slot, b in zip((5, 6, 7, 8, 9, 10), bonuses))
    return (WeaponEntry(Weapon("blades", grades=12), picks=picks),)


def atk(ch, rid="r"):
    return next(v for v in av.all_records(ch) if v.record == rid)


# ===================================================================== A. bugs
# R1: a buff "until end of combat" with temp HP 6 loses them at end_combat; an instant one keeps them (button pool).
@S.case("r1-eoc-temp-hp", "resources.md / buffs.md [OWNER pkg 8 R1]: eoc buff temp HP 6 -> 0 after end_combat", (6, 0))
def _r1():
    st = ef.Status("guard", duration=ef.END_OF_COMBAT, one_shot=(ef.OneShot(ef.TEMP_HP, 6),))
    c = run(hero(in_combat=True), ("add_status", {"active": True, "status": st}))
    a = dv.temp_hp_total(c)
    return (a, dv.temp_hp_total(run(c, ("end_combat", {}))))


S.case("r1-instant-temp-hp", "resources.md: instant temp HP go to the button pool, kept after combat", 6)(
    lambda: dv.temp_hp_total(run(hero(in_combat=True),
                                 ("add_status", {"active": True, "status": ef.Status("pot", duration=ef.INSTANT,
                                                                     one_shot=(ef.OneShot(ef.TEMP_HP, 6),))}),
                                 ("end_combat", {}))))


# R2: activated sword +3 at HP 0: no enchantment at all.
def _sword3(hp_now):
    c = hero(items=(sword(enchant=3, activation_day=1),), attacks=(SW_REC,))
    c = run(c, ("activate_item", {"iid": "sw"}), ("set_item_hp", {"iid": "sw", "value": hp_now}))
    v = atk(c)
    return (v.to_hit, v.damage, v.lucky, dv.item_view(c, "sw").durability)


S.case("r2-enchant-works", "gear.md [OWNER pkg 8 R2]: +3 sword at HP 8 of 13: +3/+3, lucky 17, hardness 16", (3, 3, 17, 16))(
    lambda: _sword3(8))
S.case("r2-enchant-hp0", "gear.md [OWNER pkg 8 R2]: +3 sword at HP 0: 0/0, lucky 20, hardness base 10", (0, 0, 20, 10))(
    lambda: _sword3(0))
S.case("r2-armor-hp0", "gear.md: +2 armor activated at HP 0 -> AC 10", 10)(
    lambda: dv.ac(run(hero(items=(Item("ar", "armor", equipped=True, armor=4, enchant=2, hp=10,
                                       activation_day=1),)),
                      ("activate_item", {"iid": "ar"}), ("set_item_hp", {"iid": "ar", "value": 0}))))


# R3: mastery picks reach item HP and hardness through the record's group.
S.case("r3-hp-pick", "weapons.md / gear.md [OWNER pkg 8 R3]: base 11 + 'HP +1' -> max 12", (11, 12))(
    lambda: (dv.item_view(hero(items=(sword(hp=11),), attacks=(SW_REC,)), "sw").hp_max,
             dv.item_view(hero(items=(sword(hp=11),), attacks=(SW_REC,),
                               weapons=mastery("parry_1", "attack_1", "crit_1", "hp_1")), "sw").hp_max))
S.case("r3-broken-with-pick", "gear.md: 6 of 12 = 50% -> broken; 6 of 11 -> ok", ("ok", "broken"))(
    lambda: (dv.item_view(hero(items=(sword(hp=11, hp_current=6),), attacks=(SW_REC,)), "sw").state,
             dv.item_view(hero(items=(sword(hp=11, hp_current=6),), attacks=(SW_REC,),
                               weapons=mastery("parry_1", "attack_1", "crit_1", "hp_1")), "sw").state))
S.case("r3-durability", "weapons.md: hardness 10 with +30% and +70% -> 20; +30% only -> 13", (13, 20))(
    lambda: (dv.item_view(hero(items=(sword(),), attacks=(SW_REC,), weapons=mastery("durability_30")), "sw").durability,
             dv.item_view(hero(items=(sword(),), attacks=(SW_REC,),
                               weapons=mastery("durability_30", "attack_1", "crit_1", "durability_70")), "sw").durability))
S.case("r3-no-record", "pkg 8 R3: an item without an attack record gets no picks", 10)(
    lambda: dv.item_view(hero(items=(sword(),), weapons=mastery("durability_30")), "sw").durability)
S.case("r3-damage-uses-pick", "gear.md: damage_item on 12/12 (with pick) by 1 -> 11", 11)(
    lambda: run(hero(items=(sword(hp=11),), attacks=(SW_REC,), weapons=mastery("parry_1", "attack_1", "crit_1", "hp_1")),
                ("damage_item", {"iid": "sw", "amount": 1})).item("sw").hp_current)


# D2: a shield gets its picks through group Contact when it is the weapon of a record.
def _shield_contact():
    sh = Item("sh", "shield", kind=SHIELD, hands=1, in_hands=True, shield=2, shield_type="light", hp=10, durability=5)
    c = hero(items=(sh,), weapons=(WeaponEntry(Weapon("contact", grades=12),
                                               picks=(Pick(5, "durability_30"), Pick(6, "parry_1"),
                                                      Pick(7, "attack_1"), Pick(8, "hp_1"))),))
    plain = dv.item_view(c, "sh")
    c = run(c, ("add_attack", {"iid": "sh"}))
    v = dv.item_view(c, "sh")
    return ((plain.hp_max, plain.durability), (v.hp_max, v.durability, v.group))


S.case("d2-shield-contact", "pkg 8 D2: shield + Contact record: HP 10 -> 11, hardness 5 -> 6", ((10, 5), (11, 6, "contact")))(
    _shield_contact)
S.case("d2-shield-attack-drops-ac", "pkg 8 D2: an attack with the shield flags 'no shield AC'; AC without it", (True, 12, 10))(
    lambda: (lambda c: (atk(c, c.attacks[0].rid).drops_shield_ac, dv.ac(c), dv.ac(c, shield_enabled=False)))(
        run(hero(items=(Item("sh", "shield", kind=SHIELD, hands=1, in_hands=True, shield=2),)),
            ("add_attack", {"iid": "sh"}))))


# R4: a shield in hand applies its skill penalty; masterwork lowers it by 1.
CLIMB = Skill("climb", "str", armor_penalty_applies=True)


def _shield_pen(**kw):
    sh = Item("sh", "shield", kind=SHIELD, hands=1, in_hands=True, shield=2, skill_penalty=-2, **kw)
    return hero(items=(sh,), skills=(CLIMB,))


S.case("r4-shield-penalty", "gear.md [OWNER pkg 8 R4]: shield -2 in hand -> climb -2; in the bag -> 0", (-2, 0))(
    lambda: (dv.skill_bonus(_shield_pen(), "climb"),
             dv.skill_bonus(replace(_shield_pen(), items=(replace(_shield_pen().items[0], in_hands=False),)), "climb")))
S.case("r4-shield-plus-armor", "gear.md: shield -2 + worn armor -3 -> -5", -5)(
    lambda: dv.armor_skill_penalty(replace(_shield_pen(), items=_shield_pen().items + (
        Item("ar", "mail", equipped=True, armor=5, skill_penalty=-3),))))
S.case("d3-mwk-shield", "pkg 8 D3: masterwork shield -2 -> -1", -1)(
    lambda: dv.skill_bonus(_shield_pen(masterwork=True), "climb"))
S.case("d3-mwk-armor-floor", "pkg 8 D3: masterwork armor -1 -> 0, 0 -> 0 (never a bonus)", (0, 0))(
    lambda: tuple(dv.armor_skill_penalty(hero(items=(Item("ar", "a", equipped=True, armor=2, skill_penalty=p,
                                                          masterwork=True),))) for p in (-1, 0)))
S.case("d3-mwk-broken", "pkg 8 D3 + gear.md: masterwork armor -3 broken -> (-3 + 1) * 2 = -4", -4)(
    lambda: dv.armor_skill_penalty(hero(items=(Item("ar", "a", equipped=True, armor=4, skill_penalty=-3,
                                                    masterwork=True, hp=10, hp_current=4),))))


# R16: short rest "restore charges" also restores charges kept on statuses.
def _rage(cur):
    return ef.Status("rage", sid="rage", charges=Pool(cur, 3), active=False)


S.case("r16-status-charges", "rest.md / buffs.md [OWNER pkg 8 R16]: short rest charges option: rage 0/3 -> 3/3", 3)(
    lambda: run(hero(bp_current=5, statuses=(_rage(0),)),
                ("short_rest", {"spends": [(rs.OPT_CHARGES, {})]})).statuses[0].charges.current)
S.case("r16-long-rest", "buffs.md: long rest restores status charges 1/3 -> 3/3", 3)(
    lambda: run(hero(statuses=(_rage(1),)), ("long_rest", {})).statuses[0].charges.current)
S.case("r16-sheet-charges-kept", "rest.md: sheet charges stay separate from status charges", (1, 1))(
    lambda: (lambda c: (len(c.charges), len(c.statuses)))(
        run(hero(statuses=(_rage(0),), charges=(rs.Charge("ki", rs.ABILITY, Pool(0, 2)),)), ("long_rest", {}))))

# R17: divine casts only for a character with divine slots.
S.case("r17-divine", "rest.md [OWNER pkg 8 R17]: not divine -> refused; divine -> slot 0 -> 1", ("refused", 1))(
    lambda: (refused(lambda: dispatch(hero(slots={1: Pool(0, 2)}), "short_rest",
                                      spends=[(rs.OPT_DIVINE, {"circle": 1})])),
             run(hero(slots={1: Pool(0, 2)}, divine_slots=True),
                 ("short_rest", {"spends": [(rs.OPT_DIVINE, {"circle": 1})]})).slots[1].current))

# R18: racial mana (absorber, mana not enabled) comes back on the long rest.
S.case("r18-racial-mana", "rest.md [OWNER pkg 8 R18]: racial mana 1/6 -> 6/6 on long rest", 6)(
    lambda: run(hero(mana=Pool(1, 6), absorbers=("mana",)), ("long_rest", {})).mana.current)

# M13: spirit, Cha 6 (mod -2) with bonus +3. RULES (resources.md:100): floor 0 first, then bonuses -> 3.
# The package 8 prompt writes max(0, 5 + 5 * mod + bonuses) = 0: conflict, see OPEN_QUESTIONS Q33.
S.case("m13-spirit-neg-cha-bonus", "resources.md [OWNER]: Cha -2 -> base 0, bonus +3 -> 3 (Q33 open)", 3)(
    lambda: dv.spirit_max(Character(abilities=abil(cha=6), spirit_bonuses=(("ring", 3),))))

# Validation: duplicate status id; N-ticks status without a number.
S.case("val-dup-sid", "pkg 8: a status id already on the sheet -> refused", "refused")(
    lambda: refused(lambda: dispatch(hero(statuses=(ef.Status("haste", sid="h"),)), "add_status", active=True,
                                     status=ef.Status("haste", sid="h"))))
S.case("val-ticks-no-number", "pkg 8: N-ticks status with no number -> refused; with ticks=3 ok", ("refused", 3))(
    lambda: (refused(lambda: dispatch(hero(), "add_status", active=True, status=ef.Status("b", duration=ef.TICKS))),
             run(hero(), ("add_status", {"active": True, "status": ef.Status("b", duration=ef.TICKS), "ticks": 3})).statuses[0].remaining))

# Flank: checkbox "flank drops shield" (default on).
S.case("flank-option", "defense.md [OWNER pkg 8]: flank shield 2: default 10, checkbox off 12, front 12", (10, 12, 12))(
    lambda: (lambda c: (dv.ac(c, acm.FLANK), dv.ac(c, acm.FLANK, flank_drops_shield=False), dv.ac(c)))(
        hero(items=(Item("sh", "shield", kind=SHIELD, hands=1, in_hands=True, shield=2),))))


# ===================================================================== B. attack availability
def _twf_char(in_a=True, in_b=True, extra=()):
    a = Item("a", "sword A", kind="weapon", hands=1, in_hands=in_a, groups=("blades",))
    b = Item("b", "dagger B", kind="weapon", hands=1, in_hands=in_b, groups=("blades",))
    recs = (AttackRecord("ra", "a", "blades", twf=True, twf_off="rb"),
            AttackRecord("rb", "b", "blades", grip="off", twf=True, twf_off="ra"))
    return hero(items=(a, b) + tuple(extra), attacks=recs)


S.case("b-twf-both-orders", "combat.md [OWNER pkg 8 B]: A+B and B+A in the hands -> both available", (True, True))(
    lambda: tuple(rec.attack_available(_twf_char(), r)[0] for r in _twf_char().attacks))
S.case("b-twf-one-weapon", "pkg 8 B: only A in hands -> unavailable, missing B", (False, ("b",), ("a",)))(
    lambda: (lambda ok, d: (ok, d["missing"], d["in_hands"]))(
        *rec.attack_available(_twf_char(in_b=False), _twf_char().attacks[0])))
S.case("b-sword-shield", "pkg 8 B: sword A + shield in hands, TWF A+B -> unavailable; data says in hands: a, sh",
       (False, ("a", "b"), ("b",), ("a", "sh")))(
    lambda: (lambda ok, d: (ok, d["required"], d["missing"], d["in_hands"]))(
        *rec.attack_available(_twf_char(in_b=False, extra=(Item("sh", "shield A", kind=SHIELD, hands=1, in_hands=True,
                                                                shield=1),)), _twf_char().attacks[0])))


def _staff(in_hands):
    st = Item("st", "staff", kind="weapon", hands=2, in_hands=in_hands, groups=("staves",), double=True)
    return hero(items=(st,), attacks=(AttackRecord("rs", "st", "staves", grip="two", twf=True),))


S.case("b-double", "pkg 8 B: double weapon in hands -> available; not in hands -> missing st", (True, False, ("st",)))(
    lambda: (rec.attack_available(_staff(True), _staff(True).attacks[0])[0],
             rec.attack_available(_staff(False), _staff(False).attacks[0])[0],
             rec.attack_available(_staff(False), _staff(False).attacks[0])[1]["missing"]))
S.case("b-unequipped", "pkg 8 B: a weapon in the bag: all_records shows it unavailable; all_attacks hides it",
       ((("r", False), ("unarmed", True)), ("unarmed",)))(
    lambda: (lambda c: (tuple((v.record, v.available) for v in av.all_records(c)),
                        tuple(v.record for v in av.all_attacks(c))))(
        hero(items=(sword(in_hands=False),), attacks=(SW_REC,))))
S.case("b-view-flag", "pkg 8 B: all_attacks exposes the flag: TWF A+B with only A visible and unavailable",
       (("ra", False, ("b",)),))(
    lambda: tuple((v.record, v.available, v.missing) for v in av.all_attacks(_twf_char(in_b=False)) if v.weapon != "unarmed"))


# ===================================================================== C. balance overcap
S.case("c-default-drop", "rest.md [OWNER pkg 8 C]: BP 5/5 short rest -> +1 -> 6 -> dropped to 5", 5)(
    lambda: run(hero(), ("short_rest", {})).bp_current)
S.case("c-keep", "rest.md [OWNER pkg 8 C]: keep_overcap -> 6/5 kept, balance max 6", (6, 6))(
    lambda: (lambda c: (c.bp_current, dv.balance_max(c)))(run(hero(), ("short_rest", {"keep_overcap": True}))))
S.case("c-long-rest", "rest.md [OWNER pkg 8 C]: long rest 7/5 -> 5", 5)(
    lambda: run(hero(bp_current=7), ("long_rest", {})).bp_current)
S.case("c-end-cycle", "narrative.md [OWNER pkg 8 C]: end of cycle 7/5 -> 5", 5)(
    lambda: run(hero(bp_current=7), ("end_cycle", {})).bp_current)
S.case("c-manual", "pkg 8 C: the player fixes it by hand: set BP 8 -> 8 (over max flagged)", 8)(
    lambda: run(hero(), ("set_value", {"resource": "bp", "value": 8})).bp_current)


# ===================================================================== D1. shield grades x types
GRADES = ("none", "light", "heavy", "tower")


def _shield_grid(stype):
    out = []
    for g in GRADES:
        c = hero(shield_grade=g, items=(Item("sh", "s", kind=SHIELD, hands=1, in_hands=True, shield=2,
                                             shield_type=stype),))
        out.append((dv.shield_proficient(c, c.item("sh")), dv.shield_balance_bonus(c)))
    return tuple(out)


S.case("d1-light", "training.md [OWNER pkg 8 D1]: light shield: proficient from rank 1, never balance",
       ((False, 0), (True, 0), (True, 0), (True, 0)))(lambda: _shield_grid("light"))
S.case("d1-heavy", "training.md [OWNER pkg 8 D1]: heavy shield: rank 2+ proficient and balance +2",
       ((False, 0), (False, 0), (True, 2), (True, 2)))(lambda: _shield_grid("heavy"))
S.case("d1-tower", "training.md [OWNER pkg 8 D1]: tower shield: rank 3 only",
       ((False, 0), (False, 0), (False, 0), (True, 2)))(lambda: _shield_grid("tower"))
S.case("d1-tower-parry-once", "training.md: tower grade parry +2, not doubled by a tower shield in hand", (2, 2))(
    lambda: (dv.ac_input(hero(shield_grade="tower")).parry,
             dv.ac_input(hero(shield_grade="tower", items=(Item("sh", "s", kind=SHIELD, hands=1, in_hands=True,
                                                                shield=4, shield_type="tower"),))).parry))
S.case("d1-buy-grades", "training.md: 3 grades x 100 -> tower, training 700", ("tower", 700))(
    lambda: (lambda c: (c.shield_grade, c.training))(
        run(hero(), ("buy_shield_grade", {}), ("buy_shield_grade", {}), ("buy_shield_grade", {}))))


# ===================================================================== D3. masterwork weapon
def _mw(enchant=0, active=False, **kw):
    it = sword(masterwork=True, enchant=enchant, activation_day=1 if enchant else 0, **kw)
    c = hero(items=(it,), attacks=(SW_REC,))
    if active:
        c = run(c, ("activate_item", {"iid": "sw"}))
    v = atk(c)
    return (v.to_hit, v.damage, v.lucky)


S.case("d3-mwk-attack", "gear.md [OWNER pkg 8 D3]: masterwork sword: +1 attack, damage 0, lucky 20", (1, 0, 20))(
    lambda: _mw())
S.case("d3-mwk-plus1", "pkg 8 D3: masterwork +1 and enchantment +1 (active) -> +1, not +2", (1, 1, 19))(
    lambda: _mw(1, True))
S.case("d3-mwk-plus3", "pkg 8 D3: masterwork +1 and enchantment +3 -> +3", (3, 3, 17))(
    lambda: _mw(3, True))
S.case("d3-mwk-inactive", "pkg 8 D3: masterwork +3 sword not activated -> masterwork +1 only", (1, 0, 20))(
    lambda: _mw(3, False))
S.case("d3-mwk-cancel", "defense.md: masterwork +1 enhancement vs -1 enhancement penalty -> 0", 0)(
    lambda: atk(hero(items=(sword(masterwork=True),), attacks=(SW_REC,),
                     statuses=(ef.Status("rust", sid="x", effects=(ef.Effect(bo.ATTACK, -1, bo.ENHANCEMENT),)),))).to_hit)
S.case("d3-mwk-hp0", "gear.md: masterwork weapon at HP 0 -> nothing", 0)(
    lambda: atk(hero(items=(sword(masterwork=True, hp_current=0),), attacks=(SW_REC,))).to_hit)
S.case("d3-cmd", "pkg 8 D3: set_item_masterwork on/off", (True, False))(
    lambda: (lambda c: (c.item("sw").masterwork,
                        run(c, ("set_item_masterwork", {"iid": "sw", "value": False})).item("sw").masterwork))(
        run(hero(items=(sword(),)), ("set_item_masterwork", {"iid": "sw"}))))


# ===================================================================== E. bag weight
def _bag(ignore=False):
    items = (Item("bp", "rope", weight_l=30), Item("sw", "sword", kind="weapon", hands=1, in_hands=True, weight_l=20),
             Item("ar", "mail", equipped=True, armor=4, weight_l=50), Item("ax", "axe", kind="weapon", weight_l=15),
             Item("hm", "anvil", weight_l=99, carried=False))
    return hero(items=items, ignore_bag_weight=ignore)


S.case("e-bag-counted", "gear.md [OWNER pkg 8 E]: 30 bag + 20 + 50 + 15 = 115 L, flag off", (115, 30, False))(
    lambda: (lambda w: (w.carried_l, w.bag_l, w.ignore_bag_weight))(dv.weight_view(_bag())))
S.case("e-bag-ignored", "gear.md [OWNER pkg 8 E]: flag on -> 85 L, view shows the flag", (85, 30, True))(
    lambda: (lambda w: (w.carried_l, w.bag_l, w.ignore_bag_weight))(
        dv.weight_view(run(_bag(), ("set_ignore_bag_weight", {"value": True})))))
S.case("e-load-changes", "gear.md: 115 L heavy -> 85 L heavy; 70 L -> light when the bag is ignored", ("heavy", "light"))(
    lambda: (dv.load_status(hero(items=(Item("b", "b", weight_l=40), Item("a", "a", equipped=True, weight_l=30)))),
             dv.load_status(hero(ignore_bag_weight=True,
                                 items=(Item("b", "b", weight_l=40), Item("a", "a", equipped=True, weight_l=30))))))


# ===================================================================== F. skill pricing
MIX = (Skill("a", "dex", sk.ADVANCED), Skill("b", "dex", sk.SPECIALIZED), Skill("c", "dex"),
       Skill("d", "int", sk.SPECIALIZED))
S.case("f-mix", "skills.md [OWNER pkg 8 F]: 1 adv + 2 spec: make c advanced 40 + 20*3 = 100; a specialized 200 + 50*2 = 300",
       (100, 300, 400))(
    lambda: (sk.promote_cost(MIX, "c"), sk.specialize_cost(MIX, "a"), sk.tier_cost(MIX, "c", sk.SPECIALIZED)))


# ===================================================================== G. ticks, DoT, regen
def _ticks(ch, n):
    out = []
    for _ in range(n):
        ch = run(ch, ("tick", {}))
        out.append((ch.hp_current, sum(1 for s in ch.statuses if s.active)))   # pkg 11 A: entry stays inactive
    return out


S.case("g-dot-like-buff", "buffs.md [OWNER pkg 8 G]: DoT -1 for 3 ticks out of combat: 3 hits, then gone",
       [(17, 1), (14, 1), (11, 0), (11, 0)])(
    lambda: _ticks(hero(balance_current=0, balance_bonus=-5,
                        statuses=(ef.Status("bleed", sid="b", per_tick_hp=-3, duration=ef.TICKS, remaining=3),)), 4))
S.case("g-long-manual", "buffs.md [OWNER pkg 8 G]: 20-tick regen lowered by hand to 2 -> 2 heals, then gone",
       [(12, 1), (14, 0), (14, 0)])(
    lambda: _ticks(run(hero(hp_current=10, statuses=(ef.Status("regen", sid="g", per_tick_hp=2, duration=ef.TICKS,
                                                               remaining=20),)),
                       ("set_status_duration", {"sid": "g", "remaining": 2})), 3))
S.case("g-manual-zero", "pkg 8 G: set duration 0 ends the status (pkg 11 A: inactive, entry stays)", (("x", False, 0),))(
    lambda: tuple((s.sid, s.active, s.remaining) for s in run(hero(statuses=(ef.Status("x", sid="x", duration=ef.TICKS, remaining=5),)),
                ("set_status_duration", {"sid": "x", "remaining": 0})).statuses))


# ===================================================================== H. max HP
S.case("h-formula", "progression.md [OWNER pkg 8 H]: rolls 10+6+6, Con 8 (-1) x3, race 2, other 1 -> 22", 22)(
    lambda: dv.hp_max(Character(level=3, hp_rolls=(10, 6, 6), hit_die=10, hp_race=2, hp_bonus=1, abilities=abil(con=8))))
S.case("h-min-1", "progression.md: Con 1 (-5) at level 1 with roll 4 -> 1", 1)(
    lambda: dv.hp_max(Character(hp_rolls=(4,), hit_die=4, abilities=abil(con=1))))
S.case("h-current-con", "progression.md [OWNER pkg 8 H]: Con 14 (+2) -> 24; 4 damage -> current 10 (0) -> 20", (24, 20))(
    lambda: (dv.hp_max(Character(level=2, hp_rolls=(10, 10), hit_die=10, abilities=abil(con=14))),
             dv.hp_max(Character(level=2, hp_rolls=(10, 10), hit_die=10,
                                 abilities={**abil(), "con": Ability(base=14, damage=4)}))))


@S.case("h-con-mid-combat", "resources.md [OWNER pkg 8 H]: Con damage mid-combat: regen 3 -> 1, balance cap stays 9", ((3, 9), (1, 9)))
def _con_mid():
    c = Character(level=2, hp_rolls=(10, 10), hit_die=10, hp_current=22, bp_current=6, balance_current=0,
                  balance_bonus=3, abilities=abil(con=12))
    c = run(c, ("start_combat", {}))
    a = (dv.balance_regen(c), dv.balance_max(c))
    c = replace(c, abilities={**c.abilities, "con": Ability(base=12, damage=4)})
    return (a, (dv.balance_regen(c), dv.balance_max(c)))


S.case("h-buy-hp", "training.md [OWNER pkg 8 H]: rolls 10+6, die 10: +1 HP for 50 -> 10+7, training 950", ((10, 7), 950))(
    lambda: (lambda c: (c.hp_rolls, c.training))(
        run(Character(level=2, hp_rolls=(10, 6), hit_die=10), ("buy_hp", {}))))
S.case("h-buy-hp-cap", "training.md [OWNER pkg 8 H]: rolls 10+10 at die 10 -> refused (cap 20)", "refused")(
    lambda: refused(lambda: dispatch(Character(level=2, hp_rolls=(10, 10), hit_die=10), "buy_hp")))
S.case("h-set-roll", "progression.md: edit level 2 roll to 8 ok; 11 over the die 10 refused", ((10, 8), "refused"))(
    lambda: (run(Character(level=2, hp_rolls=(10, 6), hit_die=10), ("set_hp_roll", {"level": 2, "value": 8})).hp_rolls,
             refused(lambda: dispatch(Character(level=2, hp_rolls=(10, 6), hit_die=10), "set_hp_roll", level=2, value=11))))

if __name__ == "__main__":
    sys.exit(S.run())
