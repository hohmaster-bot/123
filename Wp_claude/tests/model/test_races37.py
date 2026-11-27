"""Package 37 P2 / P3: the 12 races done properly (owner decisions 2-6): charges that follow the race ability and its
recharge rule, the short effects (Heavy swing, Rahim tail, Hunt stacks, the Mordon -4 counter), the effect-less
Copying / Universality, the catalog Mana training, Lomit Adaptation, Ulstanger Rage (melee), Mordon Wall of Bones,
Ankalian Adrenaline, the placeholder feats of the Northerner and the language texts. Numbers by hand from RULES and the
owner decisions. Hero: every stat 10, level 1, hit die roll 8, training 2000.
Run: python Wp_claude/tests/model/test_races37.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.catalog import store as cs  # noqa: E402
from wp.commands import dispatch  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import AttackRecord, Character  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_races37")
RACES = {e["id"]: json.loads(json.dumps(e)) for e in cs.load_shipped("races").entries}
TRAIN = {e["id"]: json.loads(json.dumps(e)) for e in cs.load_shipped("trainings").entries}
FEATS = {e["id"]: e for e in cs.load_shipped("feats").entries}


def took(rid, **kw):
    base = dict(training=2000)
    base.update(kw)
    return dispatch(Character(**base), "take_race", race=RACES[rid]).state


def run(ch, *steps):
    for n, p in steps:
        ch = dispatch(ch, n, **p).state
    return ch


def pressed(ch, aid, tid):
    """The trigger button of a race ability, then its action."""
    ch = run(ch, ("fire_trigger", {"source": "feat:" + aid, "tid": tid}))
    return run(ch, ("run_trigger_action", {"nid": ch.trigger_notes[-1].nid}))


def status(ch, sid):
    return next(s for s in ch.statuses if s.sid == sid)


def charges(ch, sid):
    return status(ch, sid).charges.current


def total(ch, target):
    with rd.using(ch):
        return dv.total(ch, target)


# ---------------------------------------------------------------- P2.1 charges follow the race ability
def _elf():
    c = took("moon_elf")
    used = run(c, ("activate_status", {"sid": "dance_with_blades"}))
    fight = run(used, ("start_combat", {}))
    shadow = run(c, ("activate_status", {"sid": "shadow_of_santerra", "ticks": 2}))
    short = run(shadow, ("short_rest", {}))
    long_ = run(shadow, ("long_rest", {}))
    return (charges(c, "dance_with_blades"), charges(used, "dance_with_blades"), charges(fight, "dance_with_blades"),
            status(c, "dance_with_blades").source_ref, (charges(shadow, "shadow_of_santerra"),
                                                         charges(short, "shadow_of_santerra"),
                                                         charges(long_, "shadow_of_santerra")))


# Dance 1 charge: used -> 0, the next combat start -> 1 (the ability's rule combat_start); Shadow 2: used 1 -> 1, the
# short rest keeps 1, the long rest -> 2 (rule long_rest)
S.case("elf-charges", "P2.1: Dance with blades 1 -> 0 -> 1 at the combat start (source the race ability); Shadow of "
       "Santerra 2 -> 1, the short rest keeps 1, the long rest refills 2",
       (1, 0, 1, "feat:dance_with_blades_moon", (1, 1, 2)))(_elf)


def _silver():
    c = took("silver_elf")
    used = run(c, ("activate_status", {"sid": "eradication"}))
    return charges(used, "eradication"), charges(run(used, ("long_rest", {})), "eradication"), \
        charges(run(used, ("start_combat", {})), "eradication")


S.case("silver-charges", "P2.1: Eradication of filth 2 -> 1; the long rest -> 2; a combat start does not refill (1)",
       (1, 2, 1))(_silver)


# ---------------------------------------------------------------- P2.2 the short effects
def _swing():
    c = took("ragmal")
    on = pressed(c, "heavy_swing", "swing")
    after = run(on, ("tick", {}))
    return dv.temp_hp_total(c), (status(on, "heavy_swing").active, dv.temp_hp_total(on)), \
        (status(after, "heavy_swing").active, dv.temp_hp_total(after))


# 2 temporary HP for one tick: 0 -> 2 -> 0 after the zero-initiative tick
S.case("heavy-swing", "P2.2: Heavy swing: its button turns the status on: temp HP 0 -> 2; the next tick ends it (0)",
       (0, (True, 2), (False, 0)))(_swing)


def _tail():
    c = run(took("rahim"), ("start_combat", {}))
    on = pressed(c, "dragon_tail", "tail")
    return total(c, bo.AC), total(on, bo.AC), total(run(on, ("tick", {})), bo.AC)


# the AC bonuses: 0 -> -2 until the next zero-initiative tick -> 0
S.case("rahim-tail", "P2.2: Rahim tail: AC bonuses 0 -> -2 until the next zero-initiative tick -> 0", (0, -2, 0))(_tail)


def _hunt():
    c = run(took("ragmal"), ("buy_training", {"training": TRAIN["ragmal_mana"], "units": 3}),
            ("set_value", {"resource": "mana", "value": 9}), ("start_combat", {}))
    paid = pressed(c, "hunt_for_incarnations", "hunt_pay")
    one = pressed(paid, "hunt_for_incarnations", "hunt")
    two = pressed(pressed(one, "hunt_for_incarnations", "hunt_pay"), "hunt_for_incarnations", "hunt")
    done = run(two, ("end_combat", {}))
    try:
        pressed(two, "hunt_for_incarnations", "hunt_pay")
        third = "paid"
    except Exception as e:                 # noqa: BLE001 - the refusal is the expected result
        third = type(e).__name__
    return (dv.mana_pool(c).current, dv.mana_pool(paid).current, dv.mana_pool(two).current, third), \
        (total(c, bo.DAMAGE), total(one, bo.DAMAGE), total(two, bo.DAMAGE), total(done, bo.DAMAGE))


# mana 6 + 3 trained = 9: 9 - 4 = 5, 5 - 4 = 1, a third use refused (1 < 4); damage + 1 per stack: 0, 1, 2; the end of
# combat -> 0
S.case("hunt", "P2.2: Hunt for incarnations: 4 mana per use (9 -> 5 -> 1, then refused), +1 fire / acid damage per "
       "stack (0 / 1 / 2), gone at the end of combat", ((9, 5, 1, "CommandError"), (0, 1, 2, 0)))(_hunt)


def _plain_again():
    c = run(took("ragmal"), ("start_combat", {}))
    on = pressed(c, "heavy_swing", "swing")
    try:
        pressed(on, "heavy_swing", "swing")
        again = "stacked"
    except Exception as e:                 # noqa: BLE001 - the refusal is the expected result
        again = getattr(e, "reason", type(e).__name__)
    return status(on, "heavy_swing").stacks, again


# Heavy swing reads no "stacks": turning it on again is refused as before package 37 (already active), no stack
S.case("plain-again", "P2.2: only a status whose effects read 'stacks' stacks; Heavy swing pressed twice: stacks 0, "
       "the second press refused (already active)", (0, "status_already_active"))(_plain_again)


def _counter():
    c = run(took("mordon"), ("buy_race_ability", {"aid": "goddess_of_humanity"}))
    fight = run(c, ("start_combat", {}))
    spend = ("spend_charge", {"owner_kind": "feat", "owner_id": "goddess_of_humanity"})
    four = run(fight, *[spend] * 4)
    five = run(four, spend)
    again = run(run(five, ("end_combat", {})), ("start_combat", {}))
    bought = run(again, ("buy_race_ability", {"aid": "goddess_of_humanity_buyout"}))
    return total(c, bo.ATTACK), total(fight, bo.ATTACK), total(four, bo.ATTACK), total(five, bo.ATTACK), \
        total(again, bo.ATTACK), total(bought, bo.ATTACK)


# out of combat 0; in combat -4 while a charge is left: after 4 attacks still -4, after the 5th 0; the next combat -4
# again; the buy-out (500) cancels it: 0
S.case("mordon-counter", "P2.2: Mordon type 5: -4 on the first five attacks: 0 out of combat, -4, -4 after 4 charges, "
       "0 after 5, -4 in the next combat, 0 after the buy-out", (0, -4, -4, 0, -4, 0))(_counter)


# ---------------------------------------------------------------- P2.3 effect-less abilities, placeholders, texts
def _effectless():
    a = {x["id"]: x for x in RACES["white_maiden"]["abilities"]}["copying"]
    u = {x["id"]: x for x in RACES["lomit_renegade"]["abilities"]}["universality"]
    return (a.get("effects", []), "link the taken feat" in a["text"], u.get("effects", []),
            "link the taken feat" in u["text"])


S.case("effectless", "decision 4: Copying and Universality have no effects; the text says to link the taken feat",
       ([], True, [], True))(_effectless)


def _northerner():
    return [(FEATS[f]["sample"], FEATS[f]["cost"], "owner's text is needed" in FEATS[f]["desc"])
            for f in ("endurance", "toughness")]


# package 38 (owner decisions 2, 3): the two feats are real catalog feats (no sample flag, the default feat price 200)
S.case("northerner", "P2 / package 38: Endurance and Toughness are real feats (not samples, price 200, no placeholder "
       "text)", [(False, 200, False), (False, 200, False)])(_northerner)


S.case("languages", "P2: races with 'two city languages' say 'choose two languages of the region' (9 of 12)",
       9)(lambda: sum(1 for r in RACES.values() if "choose two languages of the region" in r.get("text", "")))


# ---------------------------------------------------------------- P3 acceptance rows
def _ragmal():
    c = took("ragmal")
    a = run(c, ("buy_training", {"training": TRAIN["ragmal_mana"], "units": 3}))
    return dv.mana_pool(c).max, dv.mana_pool(a).max, a.training, dv.ability_current(a, "str")


# mana 6 + 3 units = 9 (Str + 9 / 10 = 0); 3 x 200 = 600 -> 1400
S.case("ragmal-training", "P3: Ragmal Mana training 3 units: mana 6 -> 9, training 2000 -> 1400, Str 10",
       (6, 9, 1400, 10))(_ragmal)


def _lomit():
    c = took("lomit_renegade", level=2, hp_rolls=(8, 8), comfort_current=5)
    plain = Character(level=2, hp_rolls=(8, 8), comfort_current=5, training=2000)

    def gain(x):
        return run(x, ("exchange_comfort", {"n": 1})).training - x.training
    return gain(plain), gain(c), dv.attention_per_cycle(plain), dv.attention_per_cycle(c)


# level 2: 5 + 5 x 2 = 15; Adaptation one level higher: 5 + 5 x 3 = 20; Attention 1 + 2 / 3 = 1 -> 1 + 3 / 3 = 2
S.case("lomit", "P3: Lomit Adaptation at level 2: comfort exchange 15 -> 20; Attention 1 -> 2", (15, 20, 1, 2))(_lomit)


def _rage():
    att = (AttackRecord("u", "unarmed", "unarmed"),)
    c = took("ulstanger_fugitive", pain=(PainEntry(3, "wound"),), attacks=att)
    lines = dict((x.label, x.value) for x in av.attack(c, c.attacks[0]).damage_lines)
    return lines.get("pain: race bonus"), dv.pain_profile(c).damage_per_pain


# pain 3 x 1 = +3 on the melee (unarmed) attack; the unscoped profile value stays 0
S.case("rage", "P3: Ulstanger Rage: pain 3 -> +3 melee damage; nothing outside melee (profile 0)", (3, 0))(_rage)


def _adrenaline():
    c = took("ankalian_survivor", bp_current=5)
    spent = pressed(c, "adrenaline", "adrenaline")
    return dv.bp_pool(c).max, spent.bp_current, run(spent, ("short_rest", {})).bp_current, \
        run(spent, ("long_rest", {})).bp_current


# BP max 5 (read from the core; the race only spends); Adrenaline 5 - 2 = 3; the short rest stops at 5 - 2 = 3; the
# long rest -> 5
S.case("adrenaline", "P3: Ankalian Adrenaline: its button spends 2 BP (5 -> 3); the short rest leaves 3; the long "
       "rest -> 5", (5, 3, 3, 5))(_adrenaline)


def _wall():
    c = run(took("mordon", pain=(PainEntry(2, "wound"),)),
            ("buy_race_ability", {"aid": "wall_of_bones", "feats": [json.loads(json.dumps(FEATS["toughness"]))]}))
    return dv.pain_profile(took("mordon")).penalty_per_pain, dv.pain_profile(c).penalty_per_pain


# no wound penalty: 1 per pain - 1 = 0
S.case("wall-of-bones", "P2: Mordon Wall of Bones: no wound penalty (pain penalty 1 -> 0 per pain)", (1, 0))(_wall)

if __name__ == "__main__":
    sys.exit(S.run())
