"""Package 36 P4: acceptance on the owner's 12 races (Wp_claude/RACES_SOURCE.md) entered as catalog data
(wp/catalog/data/races/<module>.json). For every race a character takes the race (take_race with the catalog entry)
and hand numbers are checked: stats, HP at level 1, speed and the key effects / formulas / conditions / switches /
triggers of the race. Hero: every stat 10, level 1, hit die roll 8 (HP 8 + Con mod), training 2000.
Run: python Wp_claude/tests/model/test_races36.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import views as vw  # noqa: E402
from wp.catalog import store as cs  # noqa: E402
from wp.commands import dispatch  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import links  # noqa: E402
from wp.model import sheet_targets as stg  # noqa: E402
from wp.model.character import Character, Item  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_races36")
CATALOG = {e["id"]: json.loads(json.dumps(e)) for e in cs.load_shipped("races").entries}
STATS = ("str", "dex", "con", "int", "wis", "cha")


def took(rid, **kw):
    base = dict(training=2000)
    base.update(kw)
    return dispatch(Character(**base), "take_race", race=CATALOG[rid]).state


def run(ch, *steps):
    for n, p in steps:
        ch = dispatch(ch, n, **p).state
    return ch


def stats(ch):
    return tuple(dv.ability_current(ch, a) for a in STATS)


def sheet(ch):
    with rd.using(ch):
        return vw.VIEWS["sheet"](ch)


def basics(ch):
    return stats(ch), dv.hp_pool(ch).max, dv.speed(ch)


def full_hp(ch):
    return run(ch, ("set_value", {"resource": "hp", "value": dv.hp_pool(ch).max}))


S.case("catalog", "P4: 12 races, 3 of the module godbound and 9 of ranniag, one data file per module",
       (12, 3, 9))(lambda: (len(CATALOG), sum(1 for e in CATALOG.values() if e["module"] == "godbound"),
                            sum(1 for e in CATALOG.values() if e["module"] == "ranniag")))


# ---------------------------------------------------------------- module godbound
def _ankalian():
    c = took("ankalian_survivor")
    a = run(c, ("end_cycle", {}))
    b = run(a, ("run_trigger_action", {"nid": a.trigger_notes[0].nid}))
    return basics(c), [(lg.name, lg.native) for lg in c.languages], b.comfort_current - a.comfort_current


# Str / Dex / Con / Cha 10 + 2 = 12; HP 8 + Con 1 + 8 = 17; speed 20; the reliable rear: comfort + 2 by its button
S.case("ankalian", "Ankalian: stats 12 / 12 / 12 / 10 / 10 / 12, HP 8 + 1 + 8 = 17, speed 20; Kerez native; the "
       "cycle_end trigger gives +2 comfort by its button",
       (((12, 12, 12, 10, 10, 12), 17, 20), [("Kerez", True)], 2))(_ankalian)


def _lomit():
    c = took("lomit_renegade")
    with rd.using(c):
        fort = vw.VIEWS["sources"](c, number="fort")
    a = run(c, ("end_cycle", {}))
    return basics(c), (fort["total"], [x[:2] for x in fort["situational"]]), [n.text[:12] for n in a.trigger_notes]


S.case("lomit", "Lomit: Con 12, Int 12, HP 8 + 1 + 6 = 15; +2 vs magical effects is situational (Fort stays Con 1); "
       "the "
       "cycle reminder about drive points", (((10, 10, 12, 12, 10, 10), 15, 20), (1, [(2, "vs magical effects")]),
                                             ["Flexible min"]))(_lomit)


def _ulstanger():
    c = took("ulstanger_fugitive", hp_current=5)
    healed = run(c, ("restore", {"resource": "hp", "amount": 10})).hp_current
    return basics(c), healed, dv.pain_profile(c).cap, stg.value(c, "damage_per_pain")


# heal 10 at -50 % = 5: 5 + 5 = 10; death at 8 + 4 = 12 pain; +1 damage per pain
S.case("ulstanger", "Ulstanger: Str 12, Con 14, HP 8 + 2 + 10 = 20; Heal 10 -> 5 (half: 5 + 5 = 10); dies at 12 pain; "
       "rage +1 damage per pain", (((12, 10, 14, 10, 10, 10), 20, 20), 10, 12, 1))(_ulstanger)


# ---------------------------------------------------------------- module ranniag
def _azana():
    c = took("azana", hp_current=2, trauma=6)
    c = run(c, ("restore_pool", {"pid": "static"}))
    zap = run(c, ("take_damage", {"amount": 7, "dtype": "lightning"}))
    hit = run(c, ("take_damage", {"amount": 5}))
    regen = next(n for n in hit.trigger_notes if n.tid == "regen")
    on = run(hit, ("run_trigger_action", {"nid": regen.nid}))
    sess = run(c, ("fire_trigger", {"source": "feat:end_of_session", "tid": "session"}))
    sess = run(sess, ("run_trigger_action", {"nid": sess.trigger_notes[-1].nid}))
    fours = run(c, ("set_manual_condition", {"text": "running on all fours", "on": True}))
    st = {s.sid: s.active for s in on.statuses}
    return (basics(c), (zap.pools[0].current, zap.hp_current), (hit.hp_current, st["confused"], hit.negative_state),
            st["static_regeneration"], sess.trauma, dv.speed(fours))


# static 10 x 1 = 10; 7 lightning -> pool 3, HP 2; 5 physical: HP 2 - 5 = -3 -> confused (not dying); regeneration on
# by its button; injury points 6 - 4 = 2; all fours 20 + 10 = 30
S.case("azana", "Azana: Con 12, Int 8, HP 8 + 1 + 12 = 21; static pool 10 takes 7 lightning (pool 3, HP 2); HP 2 - 5 = "
       "-3 -> confused, not dying; the regeneration reminder turns the status on; end of session OT 6 - 4 = 2; all "
       "fours speed 30", (((10, 10, 12, 8, 10, 10), 21, 20), (3, 2), (-3, True, None), True, 2, 30))(_azana)


def _maiden():
    c = took("white_maiden", hp_current=2, pain=(PainEntry(3, "wound"),))
    healed = run(c, ("restore", {"resource": "hp", "amount": 4})).hp_current
    fight = run(c, ("start_combat", {}))
    return basics(c), dv.pain_total(c), healed, (dv.temp_hp_total(c), dv.temp_hp_total(fight)), \
        [q.kid for q in c.quirks]


# pain 3 - 2 = 1; heal 4 at -50 % = 2: 2 + 2 = 4; own temp HP 2 x 1 = 2 only in combat
S.case("white_maiden", "White maiden: Int 12, Wis 12, Con 8, HP 8 - 1 = 7; pain 3 - 2 = 1; Heal 4 -> 2 (4); temp HP "
       "2 x level = 2 only in combat; the principle quirk", (((10, 10, 8, 12, 12, 10), 7, 20), 1, 4, (0, 2),
                                                             ["maiden_principle"]))(_maiden)


def _moon_elf():
    c = took("moon_elf")
    with rd.using(c):
        sit = vw.VIEWS["situational"](c)
    return basics(c), sit["initiative"][0][:2], {s.sid: (s.charges.current if s.charges else None)
                                                  for s in c.statuses}


S.case("moon_elf", "Moon elf: Dex 12, Wis 12, Con 8, HP 8 - 1 + 6 = 13, speed 25; -4 vs blinding is situational "
       "(on every roll); dance with blades 1 charge, Shadow of Santerra 2", (((10, 12, 8, 10, 12, 10), 13, 25),
                                                                            (-4, "vs blinding and similar"),
                                                                            {"dance_with_blades": 1,
                                                                             "shadow_of_santerra": 2}))(_moon_elf)


def _mordon():
    c = took("mordon", items=(Item("ring", "golden ring", tags=("jewellery",)),))
    plus = run(c, ("set_manual_condition", {"text": "Mordon +2 Str", "on": True}))
    t1 = run(c, ("buy_race_ability", {"aid": "feast_of_ravens"}))
    t4 = run(c, ("buy_race_ability", {"aid": "fallen_of_dantalian"}))
    xp = run(t4, ("add_experience", {"amount": 100})).xp_log[-1].amount
    bought = run(t4, ("buy_race_ability", {"aid": "fallen_of_dantalian_buyout"}))
    xp2 = run(bought, ("add_experience", {"amount": 100})).xp_log[-1].amount
    held = run(t1, ("edit_entry", {"collection": "feats", "oid": "feast_of_ravens", "held_by": "item:ring"}))
    lost = run(held, ("remove_entry", {"collection": "items", "oid": "ring"}))
    return (basics(c), dv.ability_current(plus, "str"), (dv.ability_current(t1, "dex"), dv.speed(t1)),
            (dv.mana_pool(t4).max, xp, bought.training, xp2), (links.not_backed(held), [x[1] for x in
                                                                                        links.not_backed(lost)]))


# Int 8, HP 8 + 8 = 16, speed 25; +2 Str by the box: 12; history 1: Dex 12, speed 25 + 5 = 30; history 4: mana 3,
# experience 100 -> 75; the buy-out 500: training 2000 - 500 = 1500, experience 100 again; history held by the ring
S.case("mordon", "Mordon: Int 8, HP 16, speed 25; the box 'Mordon +2 Str' -> 12; history 1 Dex 12 and speed 30; "
       "history 4 mana 3 and xp 100 -> 75, its buy-out (500) -> 100; a history held by the ring is not backed when "
       "the ring is gone", (((10, 10, 10, 8, 10, 10), 16, 25), 12, (12, 30), (3, 75, 1500, 100),
                           ((), ["feast_of_ravens"])))(_mordon)


def _reflected():
    c = took("reflected")
    fight = run(c, ("start_combat", {}))
    pressed = run(fight, ("edit_sheet", {"morale_scale": 1}))
    return basics(c), [sheet(x)["stats"]["initiative"].total for x in (c, fight, pressed)]


def _midnight():
    from wp.model.character import ABILITIES, Ability
    agile = {a: Ability(base=14 if a == "dex" else 10) for a in ABILITIES}
    m = took("mordon", abilities=agile)
    plain = Character(abilities=agile)
    with rd.using(m):
        back = vw.VIEWS["defense"](m)["cells"]["8"]["full"]
    return back, vw.VIEWS["defense"](plain)["cells"]["8"]["full"]


# Dex 14 (+2): the back cell of an ordinary hero loses Dex (10); the Mordon keeps it (10 + 2 = 12)
S.case("mordon_back", "Mordon midnight instinct: the back cells keep Dex: 12 instead of 10 (Dex 14)", (12, 10))(_midnight)


S.case("reflected", "Reflected: Cha 14, Int 8, HP 8 + 4 = 12; +4 on rolls only in combat while the pressure is 0: "
       "initiative 0 / 4 / 0 (pressure 1)", (((10, 10, 10, 8, 10, 14), 12, 20), [0, 4, 0]))(_reflected)


def _rahim():
    c = took("rahim")
    fly = run(c, ("buy_race_ability", {"aid": "dragon_flight"}))
    good = run(fly, ("buy_race_ability", {"aid": "dragon_good_flight"}))
    return basics(c), (stg.value(c, "spell_resistance"), stg.value(c, "resist:fire"), stg.value(c, "resist:lightning")), \
        [m[:3] for m in sheet(fly)["moves"]], [m[:3] for m in sheet(good)["moves"]], good.training


# SR 12 + 1 = 13; flight 600 then good flight 300: 2000 - 900 = 1100
S.case("rahim", "Rahim: Str 12, Con 12, Int 8, HP 8 + 1 + 10 = 19; SR 12 + level 1 = 13, resist fire / electricity 5; "
       "flight 20 average for 600, good for 300 more (training 1100)",
       (((12, 10, 12, 8, 10, 10), 19, 20), (13, 5, 5), [("fly", 20, "average")], [("fly", 20, "good")],
        1100))(_rahim)


def _silver():
    c = took("silver_elf")
    full = full_hp(c)
    bp_full = run(c, ("set_value", {"resource": "bp", "value": dv.bp_pool(c).max}))
    bp_low = run(c, ("set_value", {"resource": "bp", "value": max(0, dv.bp_pool(c).max - 1)}))

    def nums(x):
        with rd.using(x):
            st = vw.VIEWS["sheet"](x)["stats"]
            return vw.VIEWS["defense"](x)["cells"]["2"]["full"], st["cmb"].total, st["cmd"].total
    will = sheet(bp_full)["stats"]["will"].total - sheet(bp_low)["stats"]["will"].total
    return basics(c), nums(c), nums(full), will


# HP 8 + 0 + 4 = 12 (not full at 8): AC 10 + 1 = 11, CMB 0 + 1 = 1, CMD 10 + 1 + 1 = 12; at 12 HP: AC 13, CMB 5,
# CMD 16; BP max -> Will + 2
S.case("silver_elf", "Silver elf: Str 12, Dex 12, Wis 8, HP 12, speed 25; HP not max: AC 11, CMB 1, CMD 12; HP max: "
       "AC 13 (+2 dodge), CMB 5, CMD 16 (+4); BP max: Will + 2",
       (((12, 12, 10, 10, 8, 10), 12, 25), (11, 1, 12), (13, 5, 16), 2))(_silver)


def _skerde():
    trophies = (Item("t1", "claw", carried=False, base_slot_cost=2, tags=("trophy",)),
                Item("t2", "horn", carried=False, base_slot_cost=3, tags=("trophy",)),
                Item("t3", "eye", carried=False, base_slot_cost=2, tags=("trophy",)))
    c = took("skerde")
    t = took("skerde", items=trophies, base_slots=10)
    swim = run(c, ("buy_race_ability", {"aid": "sea_dweller"}))
    return basics(c), (dv.ability_current(t, "cha"), sheet(t)["stats"]["fort"].total, dv.hp_pool(t).max), \
        [m[:2] for m in sheet(swim)["moves"]], swim.training


# HP 8 + 0 + min(5 base slots, 4 x 1) = 12; trophies 2 + 3 + 2 = 7 slots: Cha 10 + 7 / 4 = 11, saves + 7 / 2 = 3;
# with 10 base slots HP still 8 + min(10, 4) = 12; swim 15 for 100
S.case("skerde", "Skerde: Str 8, Int 12, HP 8 + min(5, 4) = 12; trophies 7 base slots: Cha 11, Fort + 3, HP 12 (4 x "
       "level caps it); swim 15 ft for 100 training", (((8, 10, 10, 12, 10, 10), 12, 20), (11, 3, 12),
                                                         [("swim", 15)], 1900))(_skerde)


def _ragmal():
    c = took("ragmal")
    rich = run(c, ("source_add", {"number": "mana_max", "name": "Training", "value": 14}))
    hit = run(run(c, ("set_value", {"resource": "mana", "value": 6})), ("take_damage", {"amount": 4}))
    return basics(c), dv.mana_pool(c).max, (dv.mana_pool(rich).max, dv.ability_current(rich, "str")), \
        (hit.mana.current, hit.hp_current), (dv.balance_pool(c).max - dv.balance_pool(Character()).max,
                                             sheet(c)["stats"]["fort"].total, stg.value(c, "load_mod"),
                                             stg.value(c, "natural_regen_percent"))


# mana 6 (Str + 6 / 10 = 0); mana 6 + 14 = 20 -> Str + 2 = 12; mana before HP: 4 damage -> mana 2, HP stays 8 (the
# new hero's current); balance + 3,
# Fort Con 1 + 2 = 3, load + 3, regeneration + 100 %
S.case("ragmal", "Ragmal: Con 12, Cha 8, HP max 9, mana 6; mana 20 -> Str 12 (+1 per 10); damage 4 goes to mana (6 -> "
       "2), HP stays 8; balance + 3, Fort 3, load + 3, natural regeneration x2",
       (((10, 10, 12, 10, 10, 8), 9, 20), 6, (20, 12), (2, 8), (3, 3, 3, 100)))(_ragmal)

if __name__ == "__main__":
    sys.exit(S.run())
