"""Package 10: owner answers (Q46, Q49, magic checks) and sheet stats (saves, initiative, CMB, CMD, size,
damage per pain, lucky effects, crit range). Run: python Wp_claude/tests/model/test_pkg10.py"""
import os
import sys
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.catalog.feats_catalog import FINESSE  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import ac as acm  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core import magic as mg  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.pain import PainEntry, PainProfile  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import records as rec  # noqa: E402
from wp.model import stats_view as stv  # noqa: E402
from wp.model.character import Ability, AttackRecord, Character, Feat, Item, WeaponEntry  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg10")


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


def abil(**scores):
    out = {a: Ability() for a in ("str", "dex", "con", "int", "wis", "cha")}
    for k, v in scores.items():
        out[k] = Ability(base=v)
    return out


def hero(**kw):
    base = dict(hp_rolls=(20,), hit_die=20, hp_current=20, bp_current=5, balance_current=5, spirit_current=10)
    base.update(kw)
    return Character(**base)


def status(*effects, sid="s"):
    return ef.Status(sid, sid=sid, effects=tuple(effects))


def unarmed(ch):
    return next(v for v in av.all_attacks(ch) if v.weapon == rec.UNARMED)


# ===================================================================== Part 1
# Q46: touch armor from effects; enchantment does not raise it.
ARM = Item("ar", "mail", equipped=True, armor=4, touch_bonus=2)
S.case("q46-touch-effect", "gear.md [OWNER pkg 10 Q46]: touch 2 + effect touch_armor +1 (flat) -> 13; front 14", (13, 14))(
    lambda: (lambda c: (dv.ac(c, acm.TOUCH), dv.ac(c)))(hero(items=(ARM,), statuses=(status(ef.Effect(bo.TOUCH_ARMOR, 1)),))))
S.case("q46-touch-same-type", "pkg 10 Q46: touch 2 + effect touch_armor +3 of type armor -> larger wins: 13", 13)(
    lambda: dv.ac(hero(items=(ARM,), statuses=(status(ef.Effect(bo.TOUCH_ARMOR, 3, bo.ARMOR)),)), acm.TOUCH))
S.case("q46-touch-no-armor", "pkg 10 Q46: no armor, spell touch_armor +2 -> touch 12, front 10", (12, 10))(
    lambda: (lambda c: (dv.ac(c, acm.TOUCH), dv.ac(c)))(hero(statuses=(status(ef.Effect(bo.TOUCH_ARMOR, 2)),))))


@S.case("q46-no-enchant", "gear.md [OWNER Q46]: +2 armor activated: front 16, touch stays 12", (16, 12))
def _q46_ench():
    c = run(hero(items=(replace(ARM, enchant=2, activation_day=1),)), ("activate_item", {"iid": "ar"}))
    return (dv.ac(c), dv.ac(c, acm.TOUCH))


# Q49: mana level = character level; cost + armor penalty above it -> refused.
PEN = Item("pm", "robe", equipped=True, armor=1, spell_penalty_mana=2)


def mage(level, *items, **kw):
    base = dict(level=level, caster=mg.MAGE, mana=Pool(20, 20), balance_current=10, balance_bonus=10, items=items)
    base.update(kw)
    return hero(**base)


def cast(ch, **kw):
    r = dispatch(ch, "cast_spell", **kw)
    return (r.state.mana.current, r.state.balance_current)


S.case("q49-fits", "classes_magic.md [OWNER pkg 10 Q49]: level 5, cost 3 + penalty 2 = 5 -> cast: mana 20 -> 15", (15, 7))(
    lambda: cast(mage(5, PEN), circle=2, mana_cost=3))
S.case("q49-penalty-over", "pkg 10 Q49: level 4, cost 3 + penalty 2 -> refused", "refused")(
    lambda: refused(lambda: cast(mage(4, PEN), circle=2, mana_cost=3)))
S.case("q49-cost-over", "pkg 10 Q49: level 4, cost 5, no armor -> refused", "refused")(
    lambda: refused(lambda: cast(mage(4), circle=3, mana_cost=5)))
S.case("q49-reduced", "pkg 10 Q49: level 4, penalty 2 lowered by a feat to 1: 3 + 1 = 4 -> cast", (16, 7))(
    lambda: cast(mage(4, PEN, statuses=(status(ef.Effect("spell_penalty_mana", -1)),)), circle=2, mana_cost=3))
S.case("q49-slots-no-limit", "pkg 10 Q49: the level limit is for mana casters; a slot caster at level 1 casts circle 3", 0)(
    lambda: run(hero(caster=mg.SLOTS, slots={3: Pool(1, 1)}), ("cast_spell", {"circle": 3})).slots[3].current)


@S.case("q49-old-file", "pkg 10 Q49: an old file with mana_level still loads (value not used); other unknown fields fail",
        ("loaded", "error"))
def _old_file():
    import json
    data = json.loads(cio.dumps(hero()))
    data["character"]["mana_level"] = 7
    ok = type(cio.loads(json.dumps(data))).__name__ == "Character" and "loaded"
    data["character"]["mana_levels"] = 7
    try:
        cio.loads(json.dumps(data))
        bad = "loaded"
    except cio.StorageError:
        bad = "error"
    return (ok, bad)


# Circle table, overload, balance, concentration, magic items.
S.case("m-table", "spells.md [OWNER pkg 10]: mana cost by circle 0..9", (0, 1, 3, 5, 7, 9, 11, 13, 15, 17))(
    lambda: tuple(mg.circle_mana(c) for c in range(10)))
S.case("m-table-default", "pkg 10: circle 3 without a typed cost -> 5 mana, balance -5 (level 5)", (15, 5))(
    lambda: cast(mage(5), circle=3))
S.case("m-overload", "classes_magic.md: mage standard 2 / full 3; slots 4 / 6; mage cantrip 4", (2, 3, 4, 6, 4))(
    lambda: (mg.cast_cost(mg.MAGE, 1, 2, 1).overload, mg.cast_cost(mg.MAGE, 1, 3, 1).overload,
             mg.cast_cost(mg.SLOTS, 1, 2).overload, mg.cast_cost(mg.SLOTS, 1, 3).overload,
             mg.cast_cost(mg.MAGE, 0, 2).overload))


@S.case("m-concentration", "classes_magic.md: level 5, balance 2, cost 5 -> balance 0, OT 3, DC 16", (0, 3, 16))
def _conc():
    r = dispatch(mage(5, balance_current=2), "cast_spell", circle=3, mana_cost=5)
    return (r.state.balance_current, r.state.trauma, r.info["result"].concentration_dc)


@S.case("m-item-spell", "classes_magic.md: spell from an item: no overload, no balance, no mana; activation costs spirit",
        ((0, 10, 20), 9))
def _item_spell():
    c = run(mage(1), ("cast_spell", {"circle": 5, "from_item": True}))
    wand = Item("w", "wand", activation_day=1)
    s = run(hero(items=(wand,)), ("activate_item", {"iid": "w"}))
    return ((c.overload, c.balance_current, c.mana.current), s.spirit_current)


# ===================================================================== Part 2
# Saves.
def saver(**kw):
    base = dict(abilities=abil(con=14, dex=12, wis=8, cha=16), save_base={"fort": 3, "ref": 1, "will": 2})
    base.update(kw)
    return hero(**base)


def save_totals(ch):
    return tuple(stv.save(ch, k).total for k in stv.SAVES)


S.case("s-saves", "classes_magic.md + stats: base + stat: Fort 3+2, Ref 1+1, Will 2-1", (5, 2, 1))(
    lambda: save_totals(saver()))
S.case("s-typed", "defense.md: save +1 resistance (all) and save:fort +2 resistance -> Fort +2 only (larger), Ref +1",
       (7, 3, 2))(
    lambda: save_totals(saver(statuses=(status(ef.Effect(bo.SAVE, 1, "resistance"),
                                               ef.Effect(bo.SAVE_PREFIX + "fort", 2, "resistance")),))))
S.case("s-pain-morale", "resources.md / defense.md: pain 2 -> -2; morale scale 4 in combat -> +2", ((3, 0, -1), (7, 4, 3)))(
    lambda: (save_totals(saver(pain=(PainEntry(2),))), save_totals(saver(morale_scale=4, in_combat=True))))
S.case("s-stat-data", "pkg 10 Q55: save stat is data: Will from Cha (16 -> +3) -> 5", 5)(
    lambda: stv.save(saver(save_stats={"fort": "con", "ref": "dex", "will": "cha"}), "will").total)

# Initiative.
S.case("i-init", "pkg 10: Dex 14 (+2) + competence +2 -> 4; pain 1 -> 3; morale scale 2 in combat -> 5", (4, 3, 5))(
    lambda: tuple(stv.initiative(hero(abilities=abil(dex=14), statuses=(status(ef.Effect(bo.INITIATIVE, 2, "competence")),),
                                      **kw)).total
                  for kw in ({}, {"pain": (PainEntry(1),)}, {"morale_scale": 2, "in_combat": True})))

# CMB and CMD.
def man(**kw):
    base = dict(bab=3, abilities=abil(str=16, dex=14), size="large")   # pkg 11 C: large = size CMB +1
    base.update(kw)
    return hero(**base)


S.case("c-cmb", "combat.md: BAB 3 + Str 3 + size 1 + cmb +2 -> 9; pain 1 -> 8", (9, 8))(
    lambda: (stv.cmb(man(statuses=(status(ef.Effect(bo.CMB, 2)),))).total,
             stv.cmb(man(statuses=(status(ef.Effect(bo.CMB, 2)),), pain=(PainEntry(1),))).total))
S.case("c-cmb-finesse", "combat.md: with the Finesse feat and Dex 18 (+4) > Str 16 (+3): 3 + 4 + 1 = 8", 8)(
    lambda: stv.cmb(man(abilities=abil(str=16, dex=18), feats=(Feat("ft", flags=(FINESSE,)),))).total)
S.case("c-cmd", "pkg 10 Q59: 10 + BAB 3 + Str 3 + Dex 2 + size 1 + cmd +1 = 20; pain and morale do not change it",
       (20, 20, 20))(
    lambda: tuple(stv.cmd(man(statuses=(status(ef.Effect(bo.CMD, 1)),), **kw)).total
                  for kw in ({}, {"pain": (PainEntry(2),)}, {"morale_scale": 4, "in_combat": True})))

# Size in the attack roll.
S.case("z-size-attack", "combat.md (R9): size +1 -> attack +1; size -1 -> -1", (1, -1))(
    lambda: (unarmed(hero(size="small")).to_hit, unarmed(hero(size="large")).to_hit))   # pkg 11 C: small +1, large -1


# Damage per pain (R6): damage = Str by grip + pain (-1 per pain) + race bonus (+N per pain) + typed.
def dmg(str_score, pain, dpp):
    return unarmed(hero(abilities=abil(str=str_score), pain=(PainEntry(pain),) if pain else (),
                        pain_profile=PainProfile(damage_per_pain=dpp))).damage


S.case("p-pain-damage", "resources.md (R6): Str -2, pain 2, +1/pain -> -2 -2 +2 = -2; Str +2, pain 3 -> 2 -3 +3 = 2; "
       "no race bonus -> -1", (-2, 2, -1))(
    lambda: (dmg(6, 2, 1), dmg(14, 3, 1), dmg(14, 3, 0)))


# Lucky attack (R7) and crit range (R8).
def sword(**kw):
    base = dict(kind="weapon", hands=1, in_hands=True, groups=("blades",), enchant=2, activation_day=1)
    base.update(kw)
    return Item("sw", "sword", **base)


def blades(*bonuses):
    return (WeaponEntry(Weapon("blades", grades=12), picks=tuple(Pick(s, b) for s, b in zip((5, 8, 9, 10, 11, 12), bonuses))),)


def att(ch):
    return next(v for v in av.all_attacks(ch) if v.record == "r")


def lucky(weapons=(), statuses=(), active=True):
    c = hero(items=(sword(),), attacks=(AttackRecord("r", "sw", "blades"),), weapons=weapons, statuses=statuses)
    if active:
        c = run(c, ("activate_item", {"iid": "sw"}))
    return att(c).lucky


FEAT_LUCKY = status(ef.Effect(bo.LUCKY, 1, weapon="sw"), sid="feat")
S.case("l-sources", "combat.md (R7): enchant 2 -> 18; + mastery pick -> 17; + feat +1 for this weapon -> 16", (18, 17, 16))(
    lambda: (lucky(), lucky(blades("lucky_1")), lucky(blades("lucky_1"), (FEAT_LUCKY,))))
S.case("l-other-weapon", "combat.md: a feat +1 for ANOTHER weapon does not count -> 18", 18)(
    lambda: lucky(statuses=(status(ef.Effect(bo.LUCKY, 1, weapon="axe"), sid="f2"),)))
S.case("l-cap", "combat.md (Q60): mastery capped at 3; enchant 2 and feat 1 add on top: 20 - 3 - 2 - 1 = 14", 14)(
    lambda: lucky(blades("lucky_1", "lucky_1", "lucky_1", "lucky_1"), (FEAT_LUCKY,)))


def dagger(**kw):
    base = dict(kind="weapon", hands=1, in_hands=True, groups=("blades",), crit_range=19, crit_mult=2)
    base.update(kw)
    return Item("dg", "dagger", **base)


def crit(item, weapons=(), statuses=()):
    c = hero(items=(item,), attacks=(AttackRecord("r", "dg", "blades"),), weapons=weapons, statuses=statuses)
    v = att(c)
    return (v.crit_range, v.crit_hint)


S.case("k-dagger", "combat.md (R8): dagger 19+ x2 -> 19, hint +0; pick crit +1 -> 18", ((19, "+0"), (18, "+0")))(
    lambda: (crit(dagger()), crit(dagger(), blades("crit_1"))))
S.case("k-keen-feat", "combat.md: keen dagger 19+ -> 17; feat crit_range +1 -> 18", (17, 18))(
    lambda: (crit(dagger(keen=True))[0], crit(dagger(), statuses=(status(ef.Effect(bo.CRIT_RANGE, 1, weapon="dg")),))[0]))

if __name__ == "__main__":
    sys.exit(S.run())
