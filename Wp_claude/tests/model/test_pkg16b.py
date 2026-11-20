"""Package 16 (part D-G): DR / resistances / SR, doll slots, narrative notebook, hit dice, comfort rate, status charges by
source (Q108), attention options 2 and 4, spell price, templates.
Expected numbers are computed by hand from RULES and the owner's package 16 decisions.
Run: python Wp_claude/tests/model/test_pkg16b.py"""
import os
import sys
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.commands import notebook_cmds as nbc  # noqa: E402
from wp.core.damage import Pool, Reductions  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.model import defense_view as dfv  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import doll  # noqa: E402
from wp.model.character import ABILITIES, Ability, Character, Feat, Item, ResourcePool, Usage  # noqa: E402
from wp.model.notebook import Drive, Quirk  # noqa: E402
from wp.model.template import Template  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg16b")


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


def hp_after(ch, **hit):
    return run(ch, ("take_damage", hit)).hp_current


# ================================================================ D. DR, resistances, SR
DR3 = buff(Effect("dr", 3, note="cold iron"))
S.case("d-dr-physical", "resources.md: 10 physical, DR 3 -> 7 reach HP: 8 -> 1", 1)(
    lambda: hp_after(hero(statuses=(DR3,)), amount=10))
S.case("d-dr-slashing", "pkg 16 D: slashing is physical: 10 - 3 -> HP 1", 1)(
    lambda: hp_after(hero(statuses=(DR3,)), amount=10, dtype="slashing"))
S.case("d-dr-not-fire", "resources.md: DR does not work on fire: 10 fire -> HP -2", -2)(
    lambda: hp_after(hero(statuses=(DR3,)), amount=10, dtype="fire"))
S.case("d-resist-fire", "pkg 16 D: resist:fire 5: 10 fire -> 5 -> HP 3", 3)(
    lambda: hp_after(hero(statuses=(buff(Effect("resist:fire", 5)),)), amount=10, dtype="fire"))
S.case("d-parts", "resources.md fire sword: 8 slashing (DR 3 -> 5) + 3 fire (resist 2 -> 1) = 6 -> HP 2", 2)(
    lambda: hp_after(hero(statuses=(buff(Effect("dr", 3), Effect("resist:fire", 2)),)), parts=[(8, "slashing"), (3, "fire")]))
S.case("d-stack-typed", "package 17 Q115: DR entries do not stack (larger wins): racial 3 + racial 2 -> 3; flat 3 + 2 -> 3", (3, 3))(
    lambda: (dfv.dr(hero(statuses=(buff(Effect("dr", 3, "racial"), Effect("dr", 2, "racial")),))),
             dfv.dr(hero(statuses=(buff(Effect("dr", 3), Effect("dr", 2)),)))))
S.case("d-skip", "resources.md: the player switches DR off for this hit -> 10 -> HP -2", -2)(
    lambda: hp_after(hero(statuses=(DR3,)), amount=10, skip=("dr",)))
S.case("d-percent-kept", "resources.md: typed 50% fire stays, then resist 2: 10 -> 5 -> 3 -> HP 5", 5)(
    lambda: hp_after(hero(statuses=(buff(Effect("resist:fire", 2)),)), amount=10, dtype="fire",
                     reductions=Reductions(percent={"fire": 50})))
S.case("d-removed", "pkg 16 D: removing the status removes the DR -> 0", 0)(
    lambda: dfv.dr(run(hero(statuses=(DR3,)), ("delete_status", {"sid": "buff"}))))
S.case("d-view", "pkg 16 D: the defense view lists DR 3 with its bypass text (narrative only), resist, SR 12",
       (3, (("buff", 3, "cold iron", False),), {"acid": 4}, 12))(
    lambda: (lambda v: (v.dr, v.dr_entries, v.resist, v.spell_resistance))(dfv.defense_view(hero(statuses=(
        replace(DR3, effects=DR3.effects + (Effect("resist:acid", 4), Effect("spell_resistance", 12))),)))))
S.case("d-sources", "pkg 16 D: a feat DR 2 counts always; a worn item DR 1 (stacks) only while worn: 2 + 1 = 3, then 2", (3, 2))(
    lambda: (lambda ch: (dfv.dr(ch), dfv.dr(run(ch, ("unequip_item", {"iid": "belt"})))))(
        hero(feats=(Feat("tough", effects=(Effect("dr", 2),)),),
             items=(Item("belt", "belt", equipped=True, effects_off=(Effect("dr", 1, stacks=True),)),))))
S.case("d-types", "pkg 16 D: 12 damage types from data + cold (package 17) = 13", 13)(lambda: len(dfv.TYPES))


# ================================================================ E. doll slots
def armors():
    return (Item("a1", "leather", armor=2, slot="armor"), Item("a2", "chain", armor=5, slot="armor"))


S.case("e-occupied", "doll.md: one item per slot: the second armor is refused (slot_occupied)", "slot_occupied")(
    lambda: reason(run(hero(items=armors()), ("equip_item", {"iid": "a1"})), "equip_item", iid="a2"))
S.case("e-swap", "doll.md: swapping is allowed: chain on, leather off (stays in the bag); armor bonus 5",
       (False, True, 5))(
    lambda: (lambda c: (c.items[0].equipped, c.items[1].equipped, dv.armor_bonus(c)))(
        run(hero(items=armors()), ("equip_item", {"iid": "a1"}), ("equip_item", {"iid": "a2", "swap": True}))))
S.case("e-hands", "pkg 16 E: the hands slot is equip_hands", "use_hands")(
    lambda: reason(hero(items=(Item("st", "staff", slot="hands"),)), "equip_item", iid="st"))
S.case("e-unknown", "pkg 16 E: an unknown slot is refused", "unknown_slot")(
    lambda: reason(hero(items=(Item("t", "tail ring", slot="tail"),)), "equip_item", iid="t"))
S.case("e-no-slot-old", "pkg 16 E: items without a slot behave as before (two rings worn)", (True, True))(
    lambda: tuple(i.equipped for i in run(hero(items=(Item("r1", "ring"), Item("r2", "ring"))),
                                          ("equip_item", {"iid": "r1"}), ("equip_item", {"iid": "r2"})).items))
S.case("e-slots", "doll.md: 22 slots; the view shows the worn armor", (22, "a2"))(
    lambda: (len(doll.SLOT_IDS), doll.doll_view(run(hero(items=armors()), ("equip_item", {"iid": "a2"})))["armor"]))


# ================================================================ F. notebook
def lens(**kw):
    return run(hero(), ("add_note", dict(kind="lens", name="New World", **kw)))


S.case("f-lens", "narrative.md: new lens 1/15; 11/15 + 4 -> 15/15 green; +3 stays 15", ((1, ""), (15, "green"), 15))(
    lambda: (lambda c: ((c.lenses[0].value, nbc.notebook_view(c)["lenses"][0][3]),
                        (lambda d: (d.lenses[0].value, nbc.notebook_view(d)["lenses"][0][3]))(
                            run(c, ("change_lens", {"lid": "new_world", "delta": 10}), ("change_lens", {"lid": "new_world", "delta": 4}))),
                        run(c, ("change_lens", {"lid": "new_world", "delta": 17})).lenses[0].value))(lens(max=15)))
S.case("f-lens-red", "narrative.md: 1/15 - 1 -> 0/15 red; cannot go to -1", (0, "red", 0))(
    lambda: (lambda c: (c.lenses[0].value, nbc.notebook_view(c)["lenses"][0][3],
                        run(c, ("change_lens", {"lid": "new_world", "delta": -1})).lenses[0].value))(
        run(lens(max=15), ("change_lens", {"lid": "new_world", "delta": -1}))))
S.case("f-court", "narrative.md: court Skull level 5 tier 1 -> 'Skull 5t1'", "Skull 5t1")(
    lambda: nbc.notebook_view(run(hero(), ("add_note", {"kind": "court", "name": "Skull", "level": 5, "tier": 1})))["courts"][0][1])
S.case("f-drive-range", "pkg 16 F: drive level 0..5: 6 refused", "drive_level_range")(
    lambda: reason(hero(), "add_note", kind="drive", name="Growth", level=6))
S.case("f-drive-attention", "narrative.md Example: level 7, two drives 4+ (set by command) -> 1 + 2 + 2 = 5", 5)(
    lambda: dv.attention_per_cycle(run(hero(level=7, hp_rolls=(8,) * 7), ("add_note", {"kind": "drive", "name": "A"}),
                                       ("add_note", {"kind": "drive", "name": "B", "level": 5}),
                                       ("set_drive_level", {"did": "a", "level": 4}),
                                       ("add_note", {"kind": "drive", "name": "C", "level": 3}))))
S.case("f-quirk-burn", "narrative.md: quirk +2 Str -> 12; burned -> 10 (destroyed); restored -> 12; deleted -> none",
       (12, (10, "destroyed"), 12, 0))(
    lambda: (lambda c: (dv.ability_current(c, "str"),
                        (lambda b: (dv.ability_current(b, "str"), nbc.notebook_view(b)["quirks"][0][1]))(
                            run(c, ("burn_quirk", {"kid": "q"}))),
                        dv.ability_current(run(c, ("burn_quirk", {"kid": "q"}), ("burn_quirk", {"kid": "q", "burned": False})), "str"),
                        len(run(c, ("remove_entry", {"collection": "quirks", "oid": "q"})).quirks)))(
        hero(quirks=(Quirk("q", "Bull", effects=(Effect("stat:str", 2),)),))))
S.case("f-save", "D11: notebook entries survive save / load", True)(
    lambda: (lambda c: cio.loads(cio.dumps(c)) == c)(run(lens(max=3), ("add_note", {"kind": "quest", "name": "Find"}),
                                                       ("add_note", {"kind": "story", "name": "Origin"}),
                                                       ("add_note", {"kind": "court", "name": "Skull", "level": 2}))))


# ================================================================ G7 base contents
def base(*items, **kw):
    return hero(items=items, **kw)


S.case("g7-base-strong", "gear.md Base example: item 'Strong' at the base gives +2 Str and takes 10 slots; 10 of 5 -> red",
       (12, (10, 5, True)))(
    lambda: (lambda c: (dv.ability_current(c, "str"), dv.base_view(c)))(
        base(Item("strong", "Strong", carried=False, base_slot_cost=10, effects_off=(Effect("stat:str", 2),)))))
S.case("g7-base-grey", "gear.md: a grey (spent) item takes 0 slots; normal items 1 each -> 2 of 5", (2, 5, False))(
    lambda: dv.base_view(base(Item("a", "a", carried=False), Item("b", "b", carried=False),
                              Item("p", "potion", carried=False, consumable=True, quantity=0))))
S.case("g7-carried-not-base", "gear.md: a carried item is not in the base and gives no base effect", (10, 0))(
    lambda: (lambda c: (dv.ability_current(c, "str"), dv.base_view(c)[0]))(
        base(Item("strong", "Strong", carried=True, effects_off=(Effect("stat:str", 2),)))))


# ================================================================ G1 hit dice
S.case("g1-min-1-per-die", "pkg 16 G1: rolls 8, 1 with Con 4 (-3): max(1, 5) + max(1, -2 -> 1) = 6", 6)(
    lambda: dv.hp_max(hero(level=2, hp_rolls=(8, 1), abilities=abil(con=4))))
S.case("g1-extra-die", "pkg 16 G1: effect extra_hit_dice 6 with Con 14 (+2): (8 + 2) + (6 + 2) = 18", 18)(
    lambda: dv.hp_max(hero(abilities=abil(con=14), statuses=(buff(Effect("extra_hit_dice", 6)),))))
S.case("g1-no-level-cap", "pkg 16 G1: level 1 with three extra dice of 6: 8 + 18 = 26 (no level cap)", 26)(
    lambda: dv.hp_max(hero(statuses=(buff(Effect("extra_hit_dice", 6), Effect("extra_hit_dice", 6), Effect("extra_hit_dice", 6)),))))


# ================================================================ G2 comfort rate
S.case("g2-comfort-rate", "training.md: 2 comfort at level 1, rate 10 + effect 3 -> 26 training", 1026)(
    lambda: run(hero(comfort_current=3, statuses=(buff(Effect("comfort_rate_bonus", 3)),)),
                ("exchange_comfort", {"n": 2})).training)


# ================================================================ G3 status charges by source (Q108)
def charged(ref="", **kw):
    return hero(statuses=(Status("rage", sid="rage", charges=Pool(0, 2), source_ref=ref, active=False),), **kw)


S.case("g3-unlinked", "Q108 [OWNER pkg 16]: a status without a source is NOT refilled by the long rest", 0)(
    lambda: run(charged(), ("long_rest", {})).statuses[0].charges.current)
S.case("g3-feat-long", "Q108: linked to a feat recharging on the long rest -> 2", 2)(
    lambda: run(charged("feat:f", feats=(Feat("f", usage=Usage(recharge="long_rest")),)), ("long_rest", {})).statuses[0].charges.current)
S.case("g3-pool-short", "Q108: linked to a pool restored on the short rest -> the short rest refills it", 2)(
    lambda: run(charged("pool:ki", pools=(ResourcePool("ki", "Ki", 3, 0, restore="short_rest"),)),
                ("short_rest", {})).statuses[0].charges.current)
S.case("g3-manual", "Q108: linked to an item with manual recharge -> not refilled", 0)(
    lambda: run(charged("item:r", items=(Item("r", "ring", usage=Usage(recharge="manual")),)), ("long_rest", {}))
    .statuses[0].charges.current)
S.case("g3-combat-start", "Q108: linked to a feat recharging at combat start -> start_combat refills it", 2)(
    lambda: run(charged("feat:f", feats=(Feat("f", usage=Usage(recharge="combat_start")),)), ("start_combat", {}))
    .statuses[0].charges.current)


# ================================================================ G4 attention options 2 and 4
S.case("g4-opt2", "training.md option 2: Dex 16 (+3) -> 1.5 comfort x rate 10 = 15 per attention; 2 -> 30; attention 3 -> 1",
       (1030, 1))(lambda: (lambda c: (c.training, c.attention))(
           run(hero(attention=3, abilities=abil(dex=16)), ("attention_to_training", {"n": 2}))))
S.case("g4-opt2-min", "training.md: Dex 10 -> min 1 comfort -> 10", 1010)(
    lambda: run(hero(attention=1), ("attention_to_training", {})).training)
S.case("g4-opt2-course", "Q102: course +1 adds to the stat: (3 + 1) / 2 = 2.0 comfort -> 20", 1020)(
    lambda: run(hero(attention=1, attention_course=1, abilities=abil(dex=16)), ("attention_to_training", {})).training)
S.case("g4-opt4", "training.md option 4: 5 attention at the minimum 0.4 = 2.0 -> +2 base slots (5 -> 7)", (20, 7))(
    lambda: (lambda c: (c.base_points_tenths, dv.base_slots(c)))(run(hero(attention=5), ("attention_to_base_points", {"n": 5}))))
S.case("g4-opt4-int", "training.md: Int 18 (+4) -> 0.8 per attention; 1 attention: 8 tenths, still 5 slots", (8, 5))(
    lambda: (lambda c: (c.base_points_tenths, dv.base_slots(c)))(
        run(hero(attention=1, abilities=abil(int=18)), ("attention_to_base_points", {}))))
S.case("g4-fractions-kept", "training.md: fractions are kept: 0.4 + 0.4 + 0.4 = 1.2 -> 6 slots", (12, 6))(
    lambda: (lambda c: (c.base_points_tenths, dv.base_slots(c)))(
        run(hero(attention=3), ("attention_to_base_points", {}), ("attention_to_base_points", {}), ("attention_to_base_points", {}))))
S.case("g4-refused", "pkg 16 G4: no attention -> refused", "not_enough_attention_have")(
    lambda: reason(hero(attention=0), "attention_to_training"))


# ================================================================ G5 spell price
def price(circle, discount=False, minus=0):
    st = (buff(Effect("spell_price_discount", minus)),) if minus else ()
    return hero(statuses=st).training - run(hero(statuses=st), ("learn_spell", {"name": "x", "circle": circle,
                                                                               "discount": discount})).training


S.case("g5-price", "training.md: circle 2 -> 60; book -> 30; book and discount 5 -> 25; no book circle 1: 30 - 5 = 25",
       (60, 30, 25, 25))(lambda: (price(2), price(2, True), price(2, True, 5), price(1, False, 5)))
S.case("g5-min-1", "pkg 16 G5: circle 0 with a book 10, discount 15 -> minimum 1", 1)(lambda: price(0, True, 15))


# ================================================================ G6 templates
def template():
    return Template("", "Half-orc", effects=(Effect("stat:con", 2),), hit_dice=(5,),
                    feats=(Feat("darkvision", title="Darkvision"),), pools=(ResourcePool("", "Fury", 2, 2),),
                    statuses=(Status("Rage", charges=Pool(1, 1)),))


S.case("g6-add", "pkg 16 G6: template Con +2 (-> +1), die 5: (8 + 1) + (5 + 1) = 15; feat, pool, status added",
       (15, ("darkvision",), ("fury",), ("rage",), "template:half_orc"))(
    lambda: (lambda c: (dv.hp_max(c), tuple(f.fid for f in c.feats), tuple(p.pid for p in c.pools),
                        tuple(s.sid for s in c.statuses), c.feats[0].source))(
        run(hero(), ("add_template", {"template": template()}))))
S.case("g6-remove", "pkg 16 G6: removing the template removes all its contributions: HP 8, nothing left",
       (8, (), (), (), ()))(
    lambda: (lambda c: (dv.hp_max(c), c.feats, c.pools, c.statuses, c.templates))(
        run(hero(), ("add_template", {"template": template()}), ("remove_template", {"tid": "half_orc"}))))
S.case("g6-keeps-own", "pkg 16 G6: the character's own feat stays after the template is removed", ("own",))(
    lambda: tuple(f.fid for f in run(hero(feats=(Feat("own"),)), ("add_template", {"template": template()}),
                                     ("remove_template", {"tid": "half_orc"})).feats))
S.case("g6-clash", "pkg 16 G6: a feat the sheet already has is refused", "feat_already_sheet")(
    lambda: reason(hero(feats=(Feat("darkvision"),)), "add_template", template=template()))
S.case("g6-save", "D11: a template survives save / load", True)(
    lambda: (lambda c: cio.loads(cio.dumps(c)) == c)(run(hero(), ("add_template", {"template": template()}))))

if __name__ == "__main__":
    sys.exit(S.run())
