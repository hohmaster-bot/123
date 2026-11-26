"""Package 36 P2: the engine "anything can change anything" (owner decisions 6-17): formulas over sheet numbers and
the cycle warning, tagged base slots, conditions, situational bonuses, rule switches, triggers, held-by links, movement
modes, race languages, typed absorbers. Numbers by hand from RULES (buffs.md, resources.md, training.md) and the owner
decisions. Hero: every stat 10, level 1, hp rolls (8,), base slots 5. Run: python Wp_claude/tests/model/test_pkg36b.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import views as vw  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.core.triggers import Trigger  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import formula_vars as fv  # noqa: E402
from wp.model import links  # noqa: E402
from wp.model import moves as mv  # noqa: E402
from wp.model import race_languages as rl  # noqa: E402
from wp.model import restores as rst  # noqa: E402
from wp.model import sheet_targets as stg  # noqa: E402
from wp.model import sources as src  # noqa: E402
from wp.model import switches as sw  # noqa: E402
from wp.model.character import Character, Feat, Item, ResourcePool  # noqa: E402
from wp.model.source_row import SourceRow  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_pkg36b")


def feat(fid, *effects, **kw):
    return Feat(fid, fid.title(), effects=tuple(effects), **kw)


def run(ch, *steps):
    for n, p in steps:
        ch = dispatch(ch, n, **p).state
    return ch


def ref(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


def sv(ch, number):
    with rd.using(ch):
        return src.view(ch, number)


# ---------------------------------------------------------------- P2.2 formulas over sheet numbers (decision 12)
RAGMAL = Character(source_rows=(SourceRow("m", "mana_max", "Mana", 25),),
                   feats=(feat("magic_body", Effect("stat:str", "mana_max / 10", "racial")),))
S.case("f-mana", "decision 12: mana_max 25 -> Str + 25 / 10 = 2 (integer division down): Str 12, mod +1",
       (25, 2, 1))(lambda: (dv.mana_pool(RAGMAL).max, stg.value(RAGMAL, "stat:str"), dv.ability_mod(RAGMAL, "str")))


def _skerde(level):
    return Character(level=level, hp_rolls=(8,) * level, base_slots=10,
                     feats=(feat("expedition", Effect("hp_max", "min(base_slots, 4 * level)")),))


# HP of level 1: die 8 + Con 0 = 8, + min(10, 4) = 12; level 3: 8 x 3 = 24 + min(10, 12) = 34
S.case("f-skerde", "owner: skerde HP + min(base slots, 4 x level): level 1 8 + 4 = 12; level 3 24 + 10 = 34",
       (12, 34))(lambda: (dv.hp_pool(_skerde(1)).max, dv.hp_pool(_skerde(3)).max))
CYCLE = Character(source_rows=(SourceRow("m", "mana_max", "Mana", 25),),
                  feats=(feat("a", Effect("stat:str", "mana_max / 10")), feat("b", Effect("mana_max", "str_mod"))))
S.case("f-cycle", "decision 12: Str reads mana_max and mana_max reads the Str modifier: no exception, one pass, the "
       "targets on the cycle and the Sources warning", (True, True))(
    lambda: ({"stat:str", "mana_max"} <= fv.cycles(CYCLE), sv(CYCLE, "mana_max")["cycle"]))
TROPHIES = Character(items=(Item("t1", "claw", carried=False, base_slot_cost=2, tags=("trophy",)),
                            Item("t2", "horn", carried=False, base_slot_cost=3, tags=("trophy",)),
                            Item("t3", "eye", carried=False, base_slot_cost=2, tags=("trophy", "rare")),
                            Item("x", "chest", carried=False, base_slot_cost=4),
                            Item("t4", "fang", carried=True, base_slot_cost=5, tags=("trophy",))),
                     feats=(feat("trophy_saves", Effect("save", "tagged_base_slots:trophy / 2", "racial")),))
S.case("f-trophy", "decision 13: trophies at the base 2 + 3 + 2 = 7 slots (the carried fang and the untagged chest "
       "do not count); saves + 7 / 2 = 3", (7, 3))(
    lambda: (fv.tagged_base_slots(TROPHIES, "trophy"), vw.VIEWS["sheet"](TROPHIES)["stats"]["fort"].total))


# ---------------------------------------------------------------- P2.3 conditions and situational (decisions 7, 8)
def _elf(hp, bp):
    return Character(hp_rolls=(8,), hp_current=hp, bp_current=bp, abilities=Character().abilities,
                     feats=(feat("integrity", Effect("ac", 2, "dodge", condition="hp_full"),
                                 Effect("save:will", 2, "racial", condition="bp_full"),
                                 Effect("save", 2, "racial", situational="vs magic")),))


def _cell(ch):
    with rd.using(ch):
        return vw.VIEWS["defense"](ch)["cells"]["2"]["full"], vw.VIEWS["sheet"](ch)["stats"]["will"].total


S.case("c-hp-bp", "decision 7: HP max -> AC 10 + 2 = 12, else 10; BP max -> Will +2, else 0; the situational +2 vs "
       "magic never counts", ((12, 2), (10, 2), (12, 0)))(
    lambda: (_cell(_elf(8, dv.bp_pool(Character()).max)), _cell(_elf(5, dv.bp_pool(Character()).max)),
             _cell(_elf(8, -1))))
S.case("c-situational", "decision 8: Fort sources show the situational row (2, vs magic), the total stays 0",
       (0, ((2, "vs magic", "integrity"),)))(
    lambda: (lambda v: (v["total"], v["situational"]))(sv(_elf(8, 0), "fort")))
REFLECTED = Character(feats=(feat("zero", Effect("rolls", 4, "racial", condition="pressure_eq:0")),))
S.case("c-pressure", "owner: Reflected +4 on all rolls while the combat pressure (morale scale) is 0; at 1 nothing",
       (4, 0))(lambda: (vw.VIEWS["sheet"](REFLECTED)["stats"]["initiative"].total,
                        vw.VIEWS["sheet"](run(REFLECTED, ("edit_sheet", {"morale_scale": 1})))["stats"]["initiative"].total))
COMBAT = Character(feats=(feat("fury", Effect("cmb", 3, condition="in_combat")),))
S.case("c-combat", "decision 7: in combat CMB +3, out of combat 0", (0, 3))(
    lambda: (vw.VIEWS["sheet"](COMBAT)["stats"]["cmb"].total,
             vw.VIEWS["sheet"](run(COMBAT, ("start_combat", {})))["stats"]["cmb"].total))
MOUNTED = Character(feats=(feat("rider", Effect("cmd", 2, condition="manual:mounted")),))
S.case("c-manual", "decision 7: a manual condition is a checkbox: off -> CMD 10, on -> 12, off -> 10",
       (10, 12, 10))(lambda: (lambda on: (vw.VIEWS["sheet"](MOUNTED)["stats"]["cmd"].total,
                                          vw.VIEWS["sheet"](on)["stats"]["cmd"].total,
                                          vw.VIEWS["sheet"](run(on, ("set_manual_condition", {"text": "mounted",
                                                                                              "on": False})))["stats"]["cmd"].total))(
    run(MOUNTED, ("set_manual_condition", {"text": "mounted", "on": True}))))


# ---------------------------------------------------------------- P2.4 rule switches
def _switches():
    half = Character(hp_rolls=(20,), hp_current=2, feats=(feat("poison", Effect("heal_percent", -50)),))
    healed = run(half, ("restore", {"resource": "hp", "amount": 10})).hp_current
    xp = run(Character(feats=(feat("fallen", Effect("exp_percent", -25)),)),
             ("add_experience", {"amount": 100}))
    pain = Character(pain=(PainEntry(3, "wound"),), feats=(feat("puppet", Effect("pain_reduction", 2)),))
    before = Character(hp_rolls=(20,), hp_current=5, feats=(feat("blessing", Effect("natural_regen_percent", 100)),))
    after = rst.rest_hp(before, Character(hp_rolls=(20,), hp_current=8, feats=before.feats))
    return healed, xp.xp_log[-1].amount, dv.pain_total(pain), after.hp_current


# heal 10 at -50 % -> 5: 2 + 5 = 7; xp 100 at -25 % -> 75; pain 3 - 2 = 1; a rest gave 3 -> doubled 6: 5 + 6 = 11
S.case("s-numbers", "switches: heal_percent -50: 2 + 10 x 50 % = 7; exp_percent -25: 100 -> 75; pain_reduction 2: "
       "3 -> 1; natural_regen_percent 100: rest gain 3 -> 6, 5 + 6 = 11", (7, 75, 1, 11))(_switches)
CONFUSED = Status("Confused", sid="confused", active=False)
AZANA = Character(hp_rolls=(8,), hp_current=2, statuses=(CONFUSED,),
                  feats=(feat("unkillable", Effect("switch:at_negative_hp", 0, note="status:confused")),))
S.case("s-negative", "owner (Azana): at_negative_hp = status:confused; 2 HP - 5 damage = -3 -> confused is on, "
       "not dying; without the switch the default is dying", ("status:confused", True, None, "dying"))(
    lambda: (lambda c: (sw.value(AZANA, "at_negative_hp"), c.statuses[0].active, c.negative_state,
                        sw.value(Character(), "at_negative_hp")))(run(AZANA, ("take_damage", {"amount": 5}))))


# ---------------------------------------------------------------- P2.5 triggers (decision 6)
REAR = Trigger("rear", "cycle_end", "Reliable rear: +2 comfort", "change_resource", "comfort", 2)
ANKALIAN = Character(level=2, feats=(feat("shadow_of_the_crown", triggers=(REAR,)),))


def _cycle():
    a = run(ANKALIAN, ("end_cycle", {}))
    notes = [(n.text, n.handled) for n in a.trigger_notes]
    b = run(a, ("run_trigger_action", {"nid": a.trigger_notes[0].nid}))
    c = run(b, ("end_cycle", {}))
    unhandled = [n.nid for n in c.trigger_notes if not n.handled]
    view = vw.VIEWS["statuses"](c)["triggers"]
    return notes, b.comfort_current - a.comfort_current, b.trigger_notes[0].handled, len(unhandled), view[0][-1], \
        ref(lambda: dispatch(b, "run_trigger_action", nid=a.trigger_notes[0].nid))


S.case("t-cycle", "decision 6: end of cycle -> the reminder 'Reliable rear' (not handled); its button: comfort + 2, "
       "handled; the next cycle: a new unhandled one stays visible (unhandled first); pressing twice refused",
       ([("Reliable rear: +2 comfort", False)], 2, True, 1, False, "already_handled"))(_cycle)
SESSION_END = Trigger("session", "manual", "End of session: injury points - 4", "reduce_injury_points", "", 4)


def _manual():
    c = Character(trauma=6, feats=(feat("dynamo", triggers=(SESSION_END,)),))
    a = run(c, ("fire_trigger", {"source": "feat:dynamo", "tid": "session"}))
    b = run(a, ("run_trigger_action", {"nid": a.trigger_notes[0].nid}))
    lower = run(Character(trauma=2, feats=c.feats), ("fire_trigger", {"source": "feat:dynamo", "tid": "session"}))
    return a.trauma, b.trauma, run(lower, ("run_trigger_action", {"nid": lower.trigger_notes[0].nid})).trauma


S.case("t-manual", "owner (Azana): a manual trigger button -> the note; its action lowers injury points (OT) 6 - 4 = "
       "2; never below 0 (2 - 4 -> 0)", (6, 2, 0))(_manual)
LOW = Trigger("low", "hp_below_one", "Regeneration 5 while static > 0")
S.case("t-hp", "decision 6: HP 3 - 5 = -2 (below 1) fires hp_below_one; a hit that stays above 0 does not",
       (1, 0))(lambda: (len(run(Character(hp_rolls=(8,), hp_current=3, feats=(feat("dyn", triggers=(LOW,)),)),
                                ("take_damage", {"amount": 5})).trigger_notes),
                        len(run(Character(hp_rolls=(8,), hp_current=8, feats=(feat("dyn", triggers=(LOW,)),)),
                                ("take_damage", {"amount": 2})).trigger_notes)))


# ---------------------------------------------------------------- P2.6 held-by links (decision 14)
def _links():
    c = Character(items=(Item("ring", "golden ring", tags=("jewellery",)),),
                  feats=(feat("history_2", held_by="item:ring"), feat("text_held", held_by="text:the oath")))
    gone = run(c, ("remove_entry", {"collection": "items", "oid": "ring"}))
    back = run(gone, ("add_entry", {"collection": "items", "record": Item("ring", "golden ring")}))
    lost = run(c, ("set_held_kept", {"collection": "feats", "oid": "text_held", "kept": False}))
    return (links.not_backed(c), [x[1] for x in links.not_backed(gone)], links.not_backed(back),
            [x[1] for x in links.not_backed(lost)], len(gone.feats), links.reminders(gone)[0][0])


S.case("l-held", "decision 14: the ring holds history 2: removed -> 'not backed' + a reminder, nothing removed (2 "
       "feats stay); the ring back -> backed; a text holder unticked -> not backed",
       ((), ["history_2"], (), ["text_held"], 2, "reminder.not_backed"))(_links)


# ---------------------------------------------------------------- P2.7 - P2.9 moves, languages, absorbers
RAHIM = Character(feats=(feat("wings", Effect("move:fly", 20, note="average")), feat("sea", Effect("move:swim", 15)),
                         feat("better", Effect("move:fly", 30, note="good"))))
S.case("m-moves", "decision 10: fly 20 average + swim 15; a better flight (fly 30 good) replaces it per mode; feet",
       (("fly", 30, "good"), ("swim", 15, "")))(lambda: tuple(m[:3] for m in mv.moves(RAHIM)))
S.case("m-languages", "decision 16 (training.md): the first race language is native (free), the others known",
       [("Draconic", True), ("City A", False), ("City B", False)])(
    lambda: [(lg.name, lg.native) for lg in rl.languages(["Draconic", "City A", "City B"])])
STATIC = ResourcePool("static", "Static", "10 * level", 10)
AZ = Character(hp_rolls=(8,), hp_current=8, pools=(STATIC,),
               feats=(feat("dynamo", Effect("absorber:pool:static", 0, note="lightning")),))
MAGE = Character(hp_rolls=(8,), hp_current=8, mana=Pool(6, 6),
                 feats=(feat("magic_body", Effect("absorber:mana", 0)),))


def _absorb():
    a = run(AZ, ("take_damage", {"amount": 7, "dtype": "lightning"}))
    b = run(AZ, ("take_damage", {"amount": 5, "dtype": "fire"}))
    c = run(AZ, ("take_damage", {"parts": [(4, "lightning"), (3, "fire")]}))
    m = run(MAGE, ("take_damage", {"amount": 4}))
    return (a.pools[0].current, a.hp_current), (b.pools[0].current, b.hp_current), \
        (c.pools[0].current, c.hp_current), (m.mana.current, m.hp_current)


S.case("a-typed", "P2.9: the static pool (10) takes only lightning: 7 lightning -> pool 3, HP 8; 5 fire -> pool 10, "
       "HP 3; 4 lightning + 3 fire -> pool 6, HP 5; mana (6) before HP: 4 -> mana 2, HP 8",
       ((3, 8), (10, 3), (6, 5), (2, 8)))(_absorb)

if __name__ == "__main__":
    sys.exit(S.run())
