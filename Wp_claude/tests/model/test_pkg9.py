"""Package 9: owner answers to Q33-Q40 and new rules A-K.
Run: python Wp_claude/tests/model/test_pkg9.py"""
import os
import sys
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.catalog import armor_catalog as ac_cat  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import ac as acm  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core import magic as mg  # noqa: E402
from wp.core import pain as pn  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.skills import Skill  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import items as itm  # noqa: E402
from wp.model import records as rec  # noqa: E402
from wp.model import spell_view as sv  # noqa: E402
from wp.model.character import SHIELD, Ability, AttackRecord, Character, Feat, Item, WeaponEntry  # noqa: E402

S = Suite("test_pkg9")


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
    base = dict(hp_rolls=(20,), hit_die=20, hp_current=20, bp_current=5, balance_current=5, spirit_current=10)
    base.update(kw)
    return Character(**base)


def abil(**scores):
    out = {a: Ability() for a in ("str", "dex", "con", "int", "wis", "cha")}
    for k, v in scores.items():
        out[k] = Ability(base=v)
    return out


def unarmed_hit(ch):
    return next(v for v in av.all_attacks(ch) if v.weapon == rec.UNARMED).to_hit


def sword(**kw):
    base = dict(kind="weapon", hands=1, in_hands=True, groups=("blades",), hp=10, durability=5)
    base.update(kw)
    return Item("sw", "sword", **base)


SW_REC = AttackRecord("r", "sw", "blades")


def mastery(gid, *bonuses):
    picks = tuple(Pick(slot, b) for slot, b in zip((5, 6, 7, 8, 9, 10), bonuses))
    return WeaponEntry(Weapon(gid, grades=12), picks=picks)


# ===================================================================== A. spirit (Q33)
S.case("a-spirit", "resources.md [OWNER pkg 9 A]: Cha -2 +3 -> 3; Cha -2 -1 -> 0; Cha +2 +3 -> 18", (3, 0, 18))(
    lambda: tuple(dv.spirit_max(Character(abilities=abil(cha=c), spirit_bonuses=(("x", b),)))
                  for c, b in ((6, 3), (6, -1), (14, 3))))


# ===================================================================== B. non-proficient (Q34)
def _armor_grid(atype):
    out = []
    for g in ("none", "light", "medium", "heavy"):
        c = hero(armor_grade=g, items=(Item("ar", "a", equipped=True, armor=4, armor_type=atype, skill_penalty=-2),))
        out.append(unarmed_hit(c))
    return tuple(out)


S.case("b-armor-light", "training.md [OWNER pkg 9 B]: light armor -2: none -2, light+ 0", (-2, 0, 0, 0))(
    lambda: _armor_grid("light"))
S.case("b-armor-medium", "training.md [OWNER pkg 9 B]: medium armor -2: none/light -2, medium+ 0", (-2, -2, 0, 0))(
    lambda: _armor_grid("medium"))
S.case("b-armor-heavy", "training.md [OWNER pkg 9 B]: heavy armor -2: only heavy grade 0", (-2, -2, -2, 0))(
    lambda: _armor_grid("heavy"))


def _shield_grid(stype):
    out = []
    for g in ("none", "light", "heavy", "tower"):
        c = hero(shield_grade=g, items=(Item("sh", "s", kind=SHIELD, hands=1, in_hands=True, shield=2,
                                             shield_type=stype, skill_penalty=-3),))
        out.append(unarmed_hit(c))
    return tuple(out)


S.case("b-shield-light", "training.md [OWNER pkg 9 B]: light shield -3: none -3", (-3, 0, 0, 0))(lambda: _shield_grid("light"))
S.case("b-shield-heavy", "training.md [OWNER pkg 9 B]: heavy shield -3: rank 2+", (-3, -3, 0, 0))(lambda: _shield_grid("heavy"))
S.case("b-shield-tower", "training.md [OWNER pkg 9 B]: tower shield -3: rank 3", (-3, -3, -3, 0))(lambda: _shield_grid("tower"))
S.case("b-mwk-broken", "pkg 9 B: non-proficient masterwork -3 -> -2; broken masterwork -3 -> -4", (-2, -4))(
    lambda: tuple(unarmed_hit(hero(items=(Item("ar", "a", equipped=True, armor=4, armor_type="heavy", skill_penalty=-3,
                                               masterwork=True, hp=10, hp_current=h),))) for h in (10, 4)))
S.case("b-every-attack", "pkg 9 B: the penalty reaches the weapon attack too (sword: -2)", -2)(
    lambda: next(v for v in av.all_attacks(hero(items=(sword(), Item("ar", "a", equipped=True, armor=4,
                                                                      armor_type="light", skill_penalty=-2)),
                                                attacks=(SW_REC,))) if v.record == "r").to_hit)
S.case("b-bag-shield", "pkg 9 B: a shield in the bag gives no attack penalty", 0)(
    lambda: unarmed_hit(hero(items=(Item("sh", "s", kind=SHIELD, hands=1, shield=2, shield_type="tower",
                                         skill_penalty=-10),))))


# ===================================================================== C. balance cap snapshot (Q35)
def _fighter(**kw):
    base = dict(hp_rolls=(20,), hp_current=20, bp_current=5, balance_current=7, abilities=abil(con=14),
                items=(Item("ar", "mail", equipped=True, armor=2),))
    base.update(kw)
    return run(Character(**base), ("start_combat", {}))


S.case("c-snapshot", "resources.md [OWNER pkg 9 C]: start_combat cap 7 (armor 2 + BP 5)", (7, 7))(
    lambda: (lambda c: (c.balance_cap_start, dv.balance_max(c)))(_fighter()))
S.case("c-spend-bp", "pkg 9 C: spending 2 BP mid-combat -> cap stays 7", 7)(
    lambda: dv.balance_max(run(_fighter(), ("spend_bp", {"n": 2}))))
S.case("c-armor-off", "pkg 9 C: taking armor off mid-combat -> cap stays 7", 7)(
    lambda: dv.balance_max(run(_fighter(), ("unequip_item", {"iid": "ar"}))))
S.case("c-bonus-con", "pkg 9 C: balance bonus +3 and Con 14 -> 8 mid-combat -> cap stays 7", 7)(
    lambda: dv.balance_max(replace(_fighter(), balance_bonus=3,
                                   abilities={**abil(), "con": Ability(base=14, damage=6)})))
S.case("c-regen-live", "pkg 9 C: regen stays live: Con 14 -> 8 mid-combat: 3 -> 1", (3, 1))(
    lambda: (dv.balance_regen(_fighter()),
             dv.balance_regen(replace(_fighter(), abilities={**abil(), "con": Ability(base=14, damage=6)}))))
S.case("c-hit", "pkg 9 C: a hit reaching HP/balance -> cap 7 -> 6", 6)(
    lambda: dv.balance_max(run(_fighter(), ("take_damage", {"amount": 3}))))
S.case("c-end", "pkg 9 C: end_combat recomputes from scratch (BP 3, no armor -> 3) and clears the snapshot", (3, None))(
    lambda: (lambda c: (dv.balance_max(c), c.balance_cap_start))(
        run(_fighter(), ("spend_bp", {"n": 2}), ("unequip_item", {"iid": "ar"}), ("end_combat", {}))))
S.case("c-spend-balance", "pkg 9 C: spend_balance 3 is a payment: balance 7 -> 4, cap 7", (4, 7))(
    lambda: (lambda c: (c.balance_current, dv.balance_max(c)))(run(_fighter(), ("spend_balance", {"n": 3}))))
S.case("c-spend-balance-short", "pkg 9 C: spend_balance more than the balance -> refused", "refused")(
    lambda: refused(lambda: dispatch(_fighter(), "spend_balance", n=8)))


@S.case("c-pay-hp", "pkg 9 C: pay_hp_cost 9 with balance 7: balance 0, HP 20, OT +2, pain +1, cap 7",
        (0, 20, 2, 1, 7))
def _pay_hp():
    c = run(_fighter(), ("pay_hp_cost", {"amount": 9}))
    return (c.balance_current, c.hp_current, c.trauma, pn.entries_total(c.pain), dv.balance_max(c))


S.case("c-pay-hp-small", "pkg 9 C: pay_hp_cost 3: balance 7 -> 4, no OT, no pain", (4, 0, 0))(
    lambda: (lambda c: (c.balance_current, c.trauma, pn.entries_total(c.pain)))(
        run(_fighter(), ("pay_hp_cost", {"amount": 3}))))


# ===================================================================== D. masterwork (Q39, Q40)
def _mwk_sword(enchant=0, activate=False, **kw):
    c = hero(items=(sword(masterwork=True, enchant=enchant, activation_day=1, **kw),), attacks=(SW_REC,))
    if activate:
        c = run(c, ("activate_item", {"iid": "sw"}))
    v = dv.item_view(c, "sw")
    return (v.masterwork_active, v.masterwork_reason, next(a for a in av.all_attacks(c) if a.record == "r").to_hit)


S.case("d-mwk-plain", "gear.md [OWNER pkg 9 D]: masterwork sword, no enchantment: active, +1", (True, "", 1))(
    lambda: _mwk_sword())
S.case("d-mwk-enchant-off", "pkg 9 D: +2 sword not activated counts as masterwork: active, +1", (True, "", 1))(
    lambda: _mwk_sword(2))
S.case("d-mwk-enchant-on", "pkg 9 D: +2 sword activated: masterwork off (enchant_active), +2", (False, itm.MW_ENCHANT_ACTIVE, 2))(
    lambda: _mwk_sword(2, True))
S.case("d-mwk-ability-only", "pkg 9 D: activated tab (fire d6), no enchantment: masterwork stays on, +1", (True, "", 1))(
    lambda: _mwk_sword(0, True, effects_on=(ef.Effect("damage", 0, dice="1d6", note="fire"),)))
S.case("d-mwk-not-flag", "pkg 9 D: no masterwork flag -> reason not_masterwork", (False, itm.MW_NOT_MASTERWORK))(
    lambda: (lambda v: (v.masterwork_active, v.masterwork_reason))(dv.item_view(hero(items=(sword(),)), "sw")))


@S.case("d-mwk-armor-enchant", "pkg 9 D: +2 masterwork armor -3, activated: penalty -2 and AC 10+4+2 = 16", (-2, 16, True))
def _mwk_armor():
    c = hero(armor_grade="heavy", items=(Item("ar", "a", equipped=True, armor=4, skill_penalty=-3, masterwork=True,
                                              enchant=2, activation_day=1),))
    c = run(c, ("activate_item", {"iid": "ar"}))
    return (dv.armor_skill_penalty(c), dv.ac(c), dv.item_view(c, "ar").masterwork_active)


S.case("d-mwk-armor-broken", "pkg 9 D: broken masterwork armor -3 -> -2 -> -4", -4)(
    lambda: dv.armor_skill_penalty(hero(items=(Item("ar", "a", equipped=True, armor=4, skill_penalty=-3,
                                                    masterwork=True, hp=10, hp_current=4),))))


# ===================================================================== E. condition tag (Q36)
def _numbers(ch):
    return (dv.ac(ch), unarmed_hit(ch), dv.skill_bonus(ch, "climb"), dv.balance_max(ch))


@S.case("e-tag-no-effect", "buffs.md [OWNER pkg 9 E]: tags combat_only / out_of_combat_only change no number", (True, True))
def _tags():
    it = Item("ar", "a", equipped=True, armor=4, skill_penalty=-2, armor_type="light")
    st = ef.Status("buff", sid="b", effects=(ef.Effect("ac", 1),))
    base = hero(items=(it,), statuses=(st,), skills=(Skill("climb", "str", armor_penalty_applies=True),))
    a = run(base, ("set_condition_tag", {"target": "item", "oid": "ar", "tag": "combat_only"}),
            ("set_condition_tag", {"target": "status", "oid": "b", "tag": "out_of_combat_only"}))
    return (_numbers(a) == _numbers(base), _numbers(replace(a, in_combat=True)) == _numbers(replace(base, in_combat=True)))


S.case("e-tag-view", "pkg 9 E: tags visible in derived views", ("combat_only", "combat_only"))(
    lambda: (lambda c: (dv.condition_tags(c)["items"]["ar"], dv.item_view(c, "ar").condition_tag))(
        run(hero(items=(Item("ar", "a"),)), ("set_condition_tag", {"target": "item", "oid": "ar", "tag": "combat_only"}))))
S.case("e-tag-bad", "pkg 9 E: unknown tag -> refused", "refused")(
    lambda: refused(lambda: dispatch(hero(items=(Item("ar", "a"),)), "set_condition_tag", target="item", oid="ar",
                                     tag="night_only")))


# ===================================================================== F. record kind, item number order (Q38)
@S.case("f-kinds", "combat.md [OWNER pkg 9 F]: first record main, second a maneuver on it, same group",
        (("main", ""), ("maneuver", "sw:blades:one"), "blades"))
def _kinds():
    c = run(hero(items=(sword(),)), ("add_attack", {"iid": "sw", "group": "blades"}), ("add_attack", {"iid": "sw"}))
    a, b = c.attacks
    return ((a.kind, a.base_record), (b.kind, b.base_record), b.group)


S.case("f-second-main", "pkg 9 F: a second main record of one item -> refused", "refused")(
    lambda: refused(lambda: run(hero(items=(sword(),)), ("add_attack", {"iid": "sw"}),
                                ("add_attack", {"iid": "sw", "kind": "main"}))))
S.case("f-remove-main", "pkg 9 F: removing a main record with maneuvers -> refused", "refused")(
    lambda: refused(lambda: run(hero(items=(sword(),)), ("add_attack", {"iid": "sw"}), ("add_attack", {"iid": "sw"}),
                                ("remove_attack", {"rid": "sw:blades:one"}))))
S.case("f-main-picks-only", "pkg 9 F: only the MAIN record's group changes item HP (primary maneuver of axes ignored)",
       (10, 11))(
    lambda: (dv.item_view(hero(items=(sword(groups=("blades", "axes")),),
                               weapons=(mastery("blades"), mastery("axes", "parry_1", "attack_1", "crit_1", "hp_1")),
                               attacks=(AttackRecord("m", "sw", "blades"),
                                        AttackRecord("x", "sw", "axes", primary=True, kind="maneuver", base_record="m"))),
                          "sw").hp_max,
             dv.item_view(hero(items=(sword(),), weapons=(mastery("blades", "parry_1", "attack_1", "crit_1", "hp_1"),),
                               attacks=(AttackRecord("m", "sw", "blades"),)), "sw").hp_max))


def _hard(*bonuses, active=True):
    c = hero(items=(sword(enchant=2, activation_day=1),), attacks=(SW_REC,), weapons=(mastery("blades", *bonuses),))
    if active:
        c = run(c, ("activate_item", {"iid": "sw"}))
    v = dv.item_view(c, "sw")
    return (v.durability, v.hp_max)


S.case("f-order-30", "gear.md [OWNER pkg 9 F]: hardness (5 + 2*2) * 130% = 11 (not 5*1.3 + 4 = 10); HP 10 + 2", (11, 12))(
    lambda: _hard("durability_30"))
S.case("f-order-both", "pkg 9 F: +30% and +70% add up: (5 + 4) * 200% = 18; HP 10 + 2 + 1 = 13", (18, 13))(
    lambda: _hard("durability_30", "attack_1", "crit_1", "durability_70", "hp_1"))
S.case("f-order-off", "pkg 9 F: not activated: 5 * 200% = 10; HP 10 + 1 = 11", (10, 11))(
    lambda: _hard("durability_30", "attack_1", "crit_1", "durability_70", "hp_1", active=False))
S.case("f-maneuver-view", "pkg 9 F: a maneuver's attack uses the main record's group and stat", ("blades", "dex"))(
    lambda: (lambda v: (v.group, v.stat))(next(
        a for a in av.all_records(hero(items=(sword(),), attacks=(AttackRecord("m", "sw", "blades", stat="dex"),
                                                                    AttackRecord("x", "sw", "axes", kind="maneuver",
                                                                                 base_record="m"))))
        if a.record == "x")))


# ===================================================================== G. notches
def _hit(item, damage, **kw):
    c = hero(items=(item,), **kw)
    r = dispatch(c, "hit_item", iid=item.iid, damage=damage)
    return r.info.get("notches", r.info.get("refused"))


S.case("g-hardness-5", "gear.md [OWNER pkg 9 G]: hardness 5: damage 4/5/9/10 -> 0/1/1/2 notches", (0, 1, 1, 2))(
    lambda: tuple(_hit(sword(), d) for d in (4, 5, 9, 10)))
S.case("g-durable", "pkg 9 G: durable sword: 10 -> 1; armor durable by default: 10 -> 1; armor durable=False -> 2", (1, 1, 2))(
    lambda: (_hit(sword(durable=True), 10), _hit(Item("ar", "a", equipped=True, armor=4, hp=10, durability=5), 10),
             _hit(Item("ar", "a", equipped=True, armor=4, hp=10, durability=5, durable=False), 10)))
S.case("g-hp-after", "pkg 9 G: sword 10 HP, damage 10 at hardness 5 -> HP 8", 8)(
    lambda: run(hero(items=(sword(),)), ("hit_item", {"iid": "sw", "damage": 10})).item("sw").hp_current)


@S.case("g-enchanted", "pkg 9 G: +2 sword activated: hardness 9: damage 17 -> 1, 18 -> 2", (9, 1, 2))
def _ench():
    c = run(hero(items=(sword(enchant=2, activation_day=1),)), ("activate_item", {"iid": "sw"}))
    return (dv.item_view(c, "sw").durability, dispatch(c, "hit_item", iid="sw", damage=17).info["notches"],
            dispatch(c, "hit_item", iid="sw", damage=18).info["notches"])


S.case("g-no-hardness", "pkg 9 G: hardness 0 -> soft refusal, item unchanged", ("item has no hardness: use damage_item", None))(
    lambda: (_hit(sword(durability=0), 20),
             dispatch(hero(items=(sword(durability=0),)), "hit_item", iid="sw", damage=20).state.item("sw").hp_current))
S.case("g-broken", "pkg 9 G: broken sword 5/10 hit 10 -> 3, still broken; again 15 -> 0 not working", (3, "broken", 0, "not_working"))(
    lambda: (lambda a: (lambda b: (a.item("sw").hp_current, dv.item_view(a, "sw").state,
                                   b.item("sw").hp_current, dv.item_view(b, "sw").state))(
        run(a, ("hit_item", {"iid": "sw", "damage": 15}))))(
        run(hero(items=(sword(hp_current=5),)), ("hit_item", {"iid": "sw", "damage": 10}))))


# ===================================================================== H. touch AC
def _touch(**kw):
    it = Item("ar", "a", equipped=True, armor=4, touch_bonus=2, **kw)
    c = hero(bp_current=0, items=(it,))
    return (dv.ac(c, acm.TOUCH), dv.ac(c), dv.balance_max(c))


S.case("h-touch", "defense.md [OWNER pkg 9 H]: armor 4 touch 2: touch 12, front 14, balance 4 (touch adds none)", (12, 14, 4))(
    lambda: _touch())
S.case("h-touch-broken", "pkg 9 H: broken armor: touch 2 -> 1 (11), front 4 -> 2 (12)", (11, 12, 2))(
    lambda: _touch(hp=10, hp_current=4))
S.case("h-touch-hp0", "pkg 9 H: armor at HP 0: touch 10, front 10", (10, 10, 0))(lambda: _touch(hp=10, hp_current=0))
S.case("h-touch-not-worn", "pkg 9 H: not worn: touch 10", 10)(
    lambda: dv.ac(hero(items=(Item("ar", "a", armor=4, touch_bonus=2),)), acm.TOUCH))


# ===================================================================== I. spell penalties
def _caster(*items, **kw):
    base = dict(caster=mg.MAGE, mana=Pool(10, 10), balance_current=6, balance_bonus=6, items=items, level=5)
    base.update(kw)
    return hero(**base)


ARM = Item("ar", "mail", equipped=True, armor=4, spell_penalty_mana=2, spell_failure_pct=20)
SHD = Item("sh", "shield", kind=SHIELD, hands=1, in_hands=True, shield=1, spell_penalty_mana=1, spell_failure_pct=15)


S.case("i-sum", "gear.md [OWNER pkg 9 I]: armor 2/20% + shield 1/15% -> 3 and 35%", (3, 35, ("ar", "sh")))(
    lambda: (lambda v: (v.mana_penalty, v.failure_pct, v.sources))(sv.view(_caster(ARM, SHD))))
S.case("i-bag-shield", "pkg 9 I: shield in the bag does not count -> 2 / 20%", (2, 20))(
    lambda: (lambda v: (v.mana_penalty, v.failure_pct))(sv.view(_caster(ARM, replace(SHD, in_hands=False)))))
def _reduced():
    # package 11 D: the feat's reduction is a feat effect (it used to be entered as a status)
    return _caster(ARM, SHD, feats=(Feat("feat", title="feat", effects=(ef.Effect(sv.TARGET_MANA, -2),
                                                                      ef.Effect(sv.TARGET_FAILURE, -50))),))


S.case("i-reduction", "pkg 9 I: feat -2 mana, -50% failure -> 1 and 0 (floor, also the raw chance)", (1, 0, 0, 3, 35))(
    lambda: (lambda v: (v.mana_penalty, v.failure_pct, sv.failure_pct_raw(_reduced()), v.mana_penalty_items,
                        v.failure_items))(sv.view(_reduced())))
S.case("i-cap-100", "pkg 9 I: failure 60% + 60% -> 100", 100)(
    lambda: sv.view(_caster(replace(ARM, spell_failure_pct=60), replace(SHD, spell_failure_pct=60))).failure_pct)


def _cast(ch, **kw):
    r = dispatch(ch, "cast_spell", circle=1, mana_cost=3, **kw)
    return (r.state.mana.current, r.state.balance_current, r.info["penalty"], False)


S.case("i-cast-mana", "classes_magic.md [OWNER pkg 9 I]: cost 3 + penalty 2 by mana: mana 10 -> 5, balance 6 -> 3",
       (5, 3, 2, False))(lambda: _cast(_caster(ARM)))
S.case("i-cast-mix", "pkg 9 I: penalty 2 paid with balance: mana 7, balance 1", (7, 1, 2, False))(
    lambda: _cast(_caster(ARM), penalty_balance=2))
S.case("i-cast-cap", "pkg 10 Q49: mana level = level 4: cost 3 + penalty 2 -> refused (no silent cut)", "refused")(
    lambda: refused(lambda: _cast(_caster(ARM, level=4))))
S.case("i-cast-no-armor", "pkg 9 I: no armor -> no penalty", (7, 3, 0, False))(lambda: _cast(_caster()))
S.case("i-failure-applies", "pkg 9 I: slot caster always; mage only with chance > 0", (True, False, True))(
    lambda: (sv.view(_caster(caster=mg.SLOTS)).failure_applies, sv.view(_caster()).failure_applies,
             sv.view(_caster(ARM)).failure_applies))
S.case("i-modes", "pkg 9 I: default cancel; divine -> zero_balance; set by hand", ("cancel", "zero_balance", "zero_balance"))(
    lambda: (sv.failure_mode(_caster()), sv.failure_mode(_caster(caster=mg.SLOTS, divine_slots=True)),
             sv.failure_mode(_caster(spell_failure_mode="zero_balance"))))


@S.case("i-resolve", "pkg 9 I: failed + cancel -> not cast, balance 6; failed + zero_balance -> cast, balance 0; ok -> cast",
        ((False, 6), (True, 0), (True, 6)))
def _resolve():
    def r(ch, failed):
        x = dispatch(ch, "resolve_spell_failure", failed=failed)
        return (x.info["cast"], x.state.balance_current)
    return (r(_caster(ARM), True), r(_caster(ARM, divine_slots=True), True), r(_caster(ARM), False))


# ===================================================================== K. armor catalog data
SETS = ac_cat.load_sets()


S.case("k-sets", "catalog.md [OWNER pkg 9 K]: two data sets with 8 and 15 rows", {"set_1": 8, "set_2": 15})(
    lambda: {k: len(v.rows) for k, v in SETS.items()})
S.case("k-set1-spot", "pkg 9 K: set 1: griffin scale touch 1 / magic 4 / 20%; lamellar slow 5 HD 10; moss weight 10",
       ((1, 4, 20), (5, 10, "heavy"), (10, "15 pr.", 2)))(
    lambda: (lambda s: ((s.row("griffin_scale").touch_bonus, s.row("griffin_scale").spell_penalty_mana,
                         s.row("griffin_scale").spell_failure_pct),
                        (s.row("lamellar_armor").speed_penalty_ft, s.row("lamellar_armor").hardness,
                         s.row("lamellar_armor").category),
                        (s.row("moss_garment").weight_l, s.row("moss_garment").price,
                         s.row("moss_garment").access_class)))(SETS["set_1"]))
S.case("k-set2-spot", "pkg 9 K: set 2: tower shield max dex 2 / -10 / 50%; buckler 5 sp, 1 L; full plate +9, max dex 1",
       ((2, 10, 50), ("5 sp", 1, "shield"), (9, 1, None)))(
    lambda: (lambda s: ((s.row("tower_shield").max_dex, s.row("tower_shield").skill_penalty,
                         s.row("tower_shield").spell_failure_pct),
                        (s.row("buckler").price, s.row("buckler").weight_l, s.row("buckler").kind),
                        (s.row("full_plate").ac_bonus, s.row("full_plate").max_dex,
                         s.row("full_plate").access_class)))(SETS["set_2"]))
S.case("k-make-item", "pkg 9 K: tower shield row -> shield item +4 tower, penalty -10, durable, hand 1",
       (4, "tower", -10, True, 1, 50))(
    lambda: (lambda it: (it.shield, it.shield_type, it.skill_penalty, itm.is_durable(it), it.hands, it.spell_failure_pct))(
        ac_cat.make_item(SETS["set_2"].row("tower_shield"), "ts")))

if __name__ == "__main__":
    sys.exit(S.run())
