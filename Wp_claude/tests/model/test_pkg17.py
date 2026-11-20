"""Package 17: the remaining effect targets (Q125), level_up without a roll (Q111), DR stacking flag (Q115), percent
modifiers per element, attack kinds melee / ranged / thrown, master counters "once per combat".
Expected numbers are computed by hand from RULES and the owner's package 17 decisions.
Run: python Wp_claude/tests/model/test_pkg17.py"""
import os
import sys
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import magic as mg  # noqa: E402
from wp.core import pain as pn  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import defense_view as dfv  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import spell_view as sv  # noqa: E402
from wp.model.character import (ABILITIES, Ability, AttackRecord, Character, Item, RulesSettings,  # noqa: E402
                                WeaponEntry)
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg17")


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def reason(ch, name, /, **kw):
    try:
        dispatch(ch, name, **kw)
    except CommandError as e:
        return e.reason
    return "allowed"


def abil(**scores):
    return {a: Ability(base=scores.get(a, 10)) for a in ABILITIES}


def hero(**kw):
    base = dict(hp_rolls=(8,), hp_current=8, spirit_current=5, balance_current=5, bp_current=2, training=1000)
    base.update(kw)
    return Character(**base)


def buff(*effects, name="buff"):
    return Status(name, sid=name, effects=tuple(effects))


def fx(*effects, **kw):
    return hero(statuses=(buff(*effects),), **kw)


# ================================================================ 2. Q125 targets
PAIN10 = (PainEntry(10),)
S.case("t-pain-cap", "resources.md: pain 10 with cap 8 -> dead; pain_cap +4 -> cap 12 -> alive", (True, False))(
    lambda: (dv.is_dead(hero(pain=PAIN10)), dv.is_dead(fx(Effect("pain_cap", 4), pain=PAIN10))))
S.case("t-pain-per", "pkg 17: pain 2 -> -2; penalty_per_pain +1 -> -4; -1 -> 0", (-2, -4, 0))(
    lambda: tuple(dv.pain_penalty(fx(*e, pain=(PainEntry(2),))) for e in ((), (Effect("pain_penalty_per_pain", 1),),
                                                                         (Effect("pain_penalty_per_pain", -1),))))
S.case("t-damage-per-pain", "resources.md race bonus: pain 2, damage_per_pain +1 -> +2 damage", 2)(
    lambda: (lambda c: pn.damage_bonus(dv.pain_total(c), dv.pain_profile(c)))(fx(Effect("damage_per_pain", 1), pain=(PainEntry(2),))))
S.case("t-pain-stack", "defense.md stacking: enhancement +4 and +2 to pain_cap -> +4 (cap 12)", 12)(
    lambda: dv.pain_profile(fx(Effect("pain_cap", 4, "enhancement"), Effect("pain_cap", 2, "enhancement"))).cap)


def two_items(*effects):
    return fx(*effects, items=(Item("sw", "sword", hp=10, durability=5), Item("ax", "axe", hp=10, durability=5)))


S.case("t-item-hp-one", "pkg 17: item_hp +3 for the sword only -> 13 / 10", (13, 10))(
    lambda: (lambda c: (dv.item_view(c, "sw").hp_max, dv.item_view(c, "ax").hp_max))(two_items(Effect("item_hp", 3, weapon="sw"))))
S.case("t-item-hp-all", "pkg 17: item_hp +3 without an item id -> every item 13", (13, 13))(
    lambda: (lambda c: (dv.item_view(c, "sw").hp_max, dv.item_view(c, "ax").hp_max))(two_items(Effect("item_hp", 3))))
S.case("t-item-hardness", "pkg 17: hardness 5 + item_hardness 2 -> 7; -9 -> 0 (never below 0)", (7, 0))(
    lambda: (dv.item_view(two_items(Effect("item_hardness", 2)), "sw").durability,
             dv.item_view(two_items(Effect("item_hardness", -9)), "sw").durability))
S.case("t-item-stack-remove", "pkg 17: enhancement +3 and +2 -> 13; status deleted -> 10", (13, 10))(
    lambda: (lambda c: (dv.item_view(c, "sw").hp_max, dv.item_view(run(c, ("delete_status", {"sid": "buff"})), "sw").hp_max))(
        two_items(Effect("item_hp", 3, "enhancement"), Effect("item_hp", 2, "enhancement"))))
S.case("t-morale", "defense.md: scale 4 in combat -> +2; count 2 higher -> scale 6 -> +3; out of combat 0", (2, 3, 0))(
    lambda: (dv.morale_bonus(hero(morale_scale=4, in_combat=True)),
             dv.morale_bonus(fx(Effect("morale_scale", 2), morale_scale=4, in_combat=True)),
             dv.morale_bonus(fx(Effect("morale_scale", 2), morale_scale=4))))
S.case("t-short-rest-heal", "rest.md: free heal 2 + level 1 = 3: HP 2 -> 5; short_rest_heal +2 -> 7", (5, 7))(
    lambda: (run(hero(hp_current=2), ("short_rest", {})).hp_current,
             run(fx(Effect("short_rest_heal", 2), hp_current=2), ("short_rest", {})).hp_current))
S.case("t-short-rest-bp", "rest.md: +1 BP: 2 -> 3 (kept over max); short_rest_bp +1 -> 4", (3, 4))(
    lambda: (run(hero(), ("short_rest", {"keep_overcap": True})).bp_current,
             run(fx(Effect("short_rest_bp", 1)), ("short_rest", {"keep_overcap": True})).bp_current))


def mage(*effects, **kw):
    base = dict(level=5, hp_rolls=(8,) * 5, caster=mg.MAGE, mana=Pool(10, 10), mana_enabled=True, balance_current=5,
                bp_current=6)
    base.update(kw)
    return fx(*effects, **base)


S.case("t-spell-cost", "classes_magic.md: circle 2 = 3 mana: 10 -> 7; spell_cost +1 -> 4 -> 6", (7, 6))(
    lambda: (run(mage(), ("cast_spell", {"circle": 2})).mana.current,
             run(mage(Effect("spell_cost", 1)), ("cast_spell", {"circle": 2})).mana.current))
S.case("t-spell-overload", "classes_magic.md: mage standard circle 2 -> overload 2; spell_overload +1 -> 3", (2, 3))(
    lambda: (run(mage(), ("cast_spell", {"circle": 2})).overload,
             run(mage(Effect("spell_overload", 1)), ("cast_spell", {"circle": 2})).overload))
S.case("t-mana-level", "gear.md Q49: level 1, circle 2 (3 mana) refused; mana_level +2 -> 3 -> allowed", (1, 3, "allowed"))(
    lambda: (sv.mana_level(mage(level=1, hp_rolls=(8,))), sv.mana_level(mage(Effect("mana_level", 2), level=1, hp_rolls=(8,))),
             reason(mage(Effect("mana_level", 2), level=1, hp_rolls=(8,)), "cast_spell", circle=2)))
S.case("t-mana-level-refused", "gear.md: without the effect the circle-2 spell is refused at level 1", "over_mana_level")(
    lambda: reason(mage(level=1, hp_rolls=(8,)), "cast_spell", circle=2))


# ================================================================ 3. level_up without a roll (Q111)
def _level_up():
    r = dispatch(hero(), "level_up")
    c = r.state
    return c.hp_rolls, dv.hp_max(c), c.hp_current, r.info["warnings"]


S.case("l-default-1", "pkg 17 Q111: no roll -> die 1 + warning; max HP 8 -> 9; current HP stays 8",
       ((8, 1), 9, 8, ("hit_die_default_used",)))(_level_up)
S.case("l-roll", "progression.md: roll 6 -> max HP 14, no warning", (14, ()))(
    lambda: (lambda r: (dv.hp_max(r.state), r.info["warnings"]))(dispatch(hero(), "level_up", hp_roll=6)))
S.case("l-edit", "pkg 17: the die can be edited by hand in edit mode (hp_rolls 8, 5) -> 13", 13)(
    lambda: dv.hp_max(run(hero(), ("level_up", {}), ("edit_sheet", {"hp_rolls": (8, 5)}))))
S.case("l-no-cap", "Q103 [OWNER]: no level cap: level 20 -> 21", 21)(
    lambda: run(hero(level=20, hp_rolls=(8,) * 20), ("level_up", {"hp_roll": 4})).level)

# ================================================================ 4. DR stacks (Q115)
S.case("d-example", "pkg 17 [OWNER]: DR 1/- stacking + DR 10/piercing -> 11; 15 physical -> 4 reach HP: 8 -> 4", (11, 4))(
    lambda: (lambda c: (dfv.dr(c), run(c, ("take_damage", {"amount": 15})).hp_current))(
        fx(Effect("dr", 1, stacks=True, note="-"), Effect("dr", 10, note="piercing"))))
S.case("d-no-stack", "pkg 17: two non-stacking DR 5 and 10 -> 10; two stacking 2 + 3 -> 5", (10, 5))(
    lambda: (dfv.dr(fx(Effect("dr", 5), Effect("dr", 10))), dfv.dr(fx(Effect("dr", 2, stacks=True), Effect("dr", 3, stacks=True)))))
S.case("d-resist-never-stacks", "pkg 17: resist fire 5 and 3 (also flat) -> 5", 5)(
    lambda: dfv.resist(fx(Effect("resist:fire", 5), Effect("resist:fire", 3)), "fire"))
S.case("d-bypass-narrative", "pkg 17: the bypass text never changes the number (silver vs magic both 4)", (4, 4))(
    lambda: (dfv.dr(fx(Effect("dr", 4, note="silver"))), dfv.dr(fx(Effect("dr", 4, note="magic")))))
S.case("d-removed", "pkg 17: the source removed -> DR 0", 0)(
    lambda: dfv.dr(run(fx(Effect("dr", 1, stacks=True)), ("delete_status", {"sid": "buff"}))))


# ================================================================ 5. percent per element
def hp(ch, amount, dtype):
    return run(ch, ("take_damage", {"amount": amount, "dtype": dtype})).hp_current


IMM = fx(Effect("percent:cold", -100), Effect("percent:fire", 50))
S.case("p-immune-and-weak", "pkg 17: immunity cold -100: 10 cold -> 0 (HP 8); fire +50: 10 -> 15 (HP -7)", (8, -7))(
    lambda: (hp(IMM, 10, "cold"), hp(IMM, 10, "fire")))
S.case("p-two-sources", "pkg 17: +50 and -25 -> +50 (larger absolute); +25 and -50 -> -50: 10 -> 5 (HP 3)", (50, 3))(
    lambda: (dfv.modifier(fx(Effect("percent:fire", 50), Effect("percent:fire", -25)), "fire"),
             hp(fx(Effect("percent:fire", 25), Effect("percent:fire", -50)), 10, "fire")))
S.case("p-order", "defense.md order (data): resist 2 THEN +50: (10 - 2) * 1.5 = 12 (HP -4); order modifier first: "
       "15 - 2 = 13 (HP -5)", (-4, -5))(
    lambda: (hp(fx(Effect("resist:fire", 2), Effect("percent:fire", 50)), 10, "fire"),
             hp(fx(Effect("resist:fire", 2), Effect("percent:fire", 50),
                   rules_settings=RulesSettings(damage_order=("percent", "modifier", "flat"))), 10, "fire")))
S.case("p-round-up", "resources.md rounding up: 5 fire with +50 -> 7.5 -> 8 (HP 0)", 0)(lambda: hp(fx(Effect("percent:fire", 50)), 5, "fire"))
S.case("p-view-remove", "pkg 17: the defense view lists cold -100 and fire +50; source removed -> nothing",
       ((("fire", 50), ("cold", -100)), ()))(
    lambda: (dfv.defense_view(IMM).percent, dfv.defense_view(run(IMM, ("delete_status", {"sid": "buff"}))).percent))


# ================================================================ 6. attack kinds
def armed(item, **rec):
    return hero(abilities=abil(str=16, dex=14), items=(item,), attacks=(AttackRecord("r", item.iid, "g", **rec),),
                weapons=(WeaponEntry(Weapon("g")),))


def view(ch):
    a = av.attack(ch, ch.attacks[0])
    return a.stat, a.damage_lines[0].value


BOW = Item("bow", "bow", kind="weapon", hands=2, in_hands=True, groups=("g",), attack_kind="ranged")
DAGGER = Item("dg", "dagger", kind="weapon", hands=1, in_hands=True, groups=("g",), attack_kind="thrown")
SWORD = Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("g",))
S.case("k-ranged", "combat.md [OWNER pkg 17]: ranged: attack Dex, no Str to damage (Str 16 +3) -> (dex, 0)", ("dex", 0))(
    lambda: view(armed(BOW)))
S.case("k-thrown", "combat.md: thrown: attack Dex, Str to damage x1 -> (dex, 3)", ("dex", 3))(lambda: view(armed(DAGGER)))
S.case("k-melee", "combat.md: melee unchanged: Str one hand 3, two hands 3 * 1.5 = 4", (("str", 3), ("str", 4)))(
    lambda: (view(armed(SWORD)), view(armed(SWORD, grip="two"))))
S.case("k-override", "pkg 17: ranged with damage_stat str -> 3; melee damage_mult 2 -> 6; attack stat cha by hand",
       (3, 6, "cha"))(
    lambda: (view(armed(BOW, damage_stat="str"))[1], view(armed(SWORD, damage_mult=2))[1], view(armed(SWORD, stat="cha"))[0]))
S.case("k-record-kind", "pkg 17: a melee sword record of kind thrown -> (dex, 3); damage_stat none -> 0", (("dex", 3), 0))(
    lambda: (view(armed(SWORD, kind="thrown")), view(armed(DAGGER, damage_stat="none"))[1]))
S.case("k-settings", "pkg 17: data defaults: ranged damage stat str x1 in rules_settings -> 3", 3)(
    lambda: view(replace(armed(BOW), rules_settings=RulesSettings(ranged_damage_stat="str")))[1])
S.case("k-negative", "combat.md grip rule: a negative Str counts once: thrown with Str 6 (-2) -> -2", -2)(
    lambda: view(replace(armed(DAGGER), abilities=abil(str=6, dex=14)))[1])

# ================================================================ 7. master counters
MASTER = WeaponEntry(Weapon("blades", grades=12), picks=(Pick(12, "restore_balance"), Pick(11, "reroll_d20"),
                                                        Pick(5, "attack_1")))


def master(**kw):
    return hero(weapons=(MASTER,), in_combat=True, combat_round=1, balance_current=0, **kw)


def used(ch, slot):
    return next(p.used for p in ch.weapons[0].picks if p.slot == slot)


S.case("m-spend", "weapons.md [OWNER pkg 17]: reroll once per combat: spend -> used; again refused", (1, "not_enough_charges_have"))(
    lambda: (lambda c: (used(c, 11), reason(c, "spend_charge", owner_kind="pick", owner_id="blades:11")))(
        run(master(), ("spend_charge", {"owner_kind": "pick", "owner_id": "blades:11"}))))
S.case("m-combat-end", "pkg 17: the end of combat gives the charge back", 0)(
    lambda: used(run(master(), ("spend_charge", {"owner_kind": "pick", "owner_id": "blades:11"}), ("end_combat", {})), 11))
S.case("m-restore-balance", "pkg 17: restore all balance: balance 0 -> max (BP 2) = 2; second time refused",
       (2, "not_enough_charges_have"))(
    lambda: (lambda c: (c.balance_current, reason(c, "restore_all_balance", pick_id="blades:12")))(
        run(master(), ("restore_all_balance", {"pick_id": "blades:12"}))))
S.case("m-wrong-pick", "pkg 17: restore_all_balance with the reroll pick refused; a non-counter pick has no charge",
       ("wrong_pick", "not_found"))(
    lambda: (reason(master(), "restore_all_balance", pick_id="blades:11"),
             reason(master(), "spend_charge", owner_kind="pick", owner_id="blades:5")))
S.case("m-blocked", "buffs.md block_restore balance: restore all balance refused (Q128)", "restoring_blocked")(
    lambda: reason(replace(master(), statuses=(buff(Effect("block_restore", block_resources=("balance",))),)),
                   "restore_all_balance", pick_id="blades:12"))
S.case("m-save", "D11: a spent counter survives save / load", 1)(
    lambda: used(cio.loads(cio.dumps(run(master(), ("spend_charge", {"owner_kind": "pick", "owner_id": "blades:12"})))), 12))

if __name__ == "__main__":
    sys.exit(S.run())
