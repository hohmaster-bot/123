"""Package 38 P2 (owner decisions 1-5): the real feats Toughness and Endurance, the Mordon Wall of Bones (Toughness for
free, the bleeding x2 reminder, comfort per fight -1 / max 3, the buy-out), the general comfort per fight. Numbers by
hand from the owner decisions (RULES/resources.md "Comfort per fight", catalog.md, races.md "Package 38").
Hero: every stat 10, training 2000.
Run: python Wp_claude/tests/model/test_pkg38a.py"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import session as sm  # noqa: E402
from wp.catalog import feats_catalog as fcat  # noqa: E402
from wp.catalog import store as cs  # noqa: E402
from wp.catalog.convert import status_from_entry  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import fight_comfort as fc  # noqa: E402
from wp.model import screen_view as scr  # noqa: E402
from wp.model import sources as src  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_pkg38a")
TMP = tempfile.mkdtemp(prefix="wp38a_")
CAT = fcat.load_default()
RACES = {e["id"]: json.loads(json.dumps(e)) for e in cs.load_shipped("races").entries}
FEATS = {e["id"]: json.loads(json.dumps(e)) for e in cs.load_shipped("feats").entries}
STATUSES = {e["id"]: json.loads(json.dumps(e)) for e in cs.load_shipped("statuses").entries}


def run(ch, *steps):
    for n, p in steps:
        ch = dispatch(ch, n, **p).state
    return ch


def ref(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "no refusal"


def hero(**kw):
    base = dict(training=2000)
    base.update(kw)
    return Character(**base)


def hp_max(ch):
    with rd.using(ch):
        return dv.hp_pool(ch).max


# ---------------------------------------------------------------- 2.1 Toughness (decision 2)
def _tough(level):
    c = hero(level=level)
    t = run(c, ("add_feat", {"catalog": CAT, "fid": "toughness"}))
    return hp_max(t) - hp_max(c)


# HP bonus = max(3, Hit Dice), Hit Dice = level: 1 -> 3, 3 -> 3, 7 -> 7
S.case("toughness", "decision 2: Toughness HP bonus = max(3, level): level 1 -> +3, 3 -> +3, 7 -> +7", (3, 3, 7))(
    lambda: (_tough(1), _tough(3), _tough(7)))


# ---------------------------------------------------------------- 2.1 Endurance (decision 3)
def _endurance():
    c = hero()
    e = run(c, ("add_feat", {"catalog": CAT, "fid": "endurance"}))
    with rd.using(e):
        v = src.view(e, "fort")
    with rd.using(c):
        before = src.view(c, "fort")["total"]
    rows = sorted((n, text) for n, text, _s in v["situational"])
    return before == v["total"], rows


S.case("endurance", "decision 3: Endurance: two situational +4 rows in the Sources of Fort with their notes, the Fort "
       "total unchanged", (True, [(4, "vs nonlethal damage from hot or cold environments"),
                                  (4, "vs suffocation damage")]))(_endurance)
S.case("endurance-seven", "decision 3: Endurance carries seven situational +4 effects (Swim, four Con checks, two "
       "Fort saves), none counts in a total", (7, {4}, True))(
    lambda: (lambda t: (len(t.effects), {e.value for e in t.effects}, all(e.situational for e in t.effects)))(
        CAT.get("endurance")))


# ---------------------------------------------------------------- 2.1 Wall of Bones: Toughness free, linked
def mordon_wall(**kw):
    c = run(hero(**kw), ("take_race", {"race": RACES["mordon"]}))
    return run(c, ("buy_race_ability", {"aid": "wall_of_bones", "feats": [FEATS["toughness"]]}))


def _wall_free():
    c = run(hero(), ("take_race", {"race": RACES["mordon"]}))
    w = mordon_wall()
    t = next(f for f in w.feats if f.fid == "toughness")
    return (c.training - w.training, t.cost, t.held_by, hp_max(w) - hp_max(c),
            ref(lambda: dispatch(c, "buy_race_ability", aid="wall_of_bones")))


# Wall of Bones costs 0; Toughness cost 0, held by the ability; HP: Toughness +3 at level 1 (+2 Con = +1 mod: +1 HP)
S.case("wall-toughness", "decision 1: Wall of Bones gives Toughness for free, held by the ability; HP +3 (Toughness) "
       "+1 (Con 12); without the feat entry the purchase is refused", (0, 0, "feat:wall_of_bones", 4,
                                                                       "grant_entry_needed"))(_wall_free)
S.case("wall-pain", "decision 1: no wound penalty = no pain penalty (1 -> 0 per pain); the pain itself still counts 2",
       (0, 2))(lambda: (lambda w: (dv.pain_profile(w).penalty_per_pain, dv.pain_total(w)))(
           mordon_wall(pain=(__import__("wp.core.pain", fromlist=["PainEntry"]).PainEntry(2, "wound"),))))


# ---------------------------------------------------------------- 2.2 bleeding x2 reminder (decision 4)
def bleeding(ch):
    st = status_from_entry(STATUSES["bleeding"], sid="bleeding")
    return run(ch, ("add_status", {"status": st, "active": True}))


def _reminded(ch):
    with rd.using(ch):
        return ("reminder.bleeding_x2", ()) in scr.reminders(ch)


def _bleed():
    w = mordon_wall()
    b = bleeding(w)
    off = run(b, ("remove_status", {"sid": "bleeding"}))
    bought = run(b, ("buy_race_ability", {"aid": "wall_of_bones_buyout"}))
    bought_dry = run(w, ("buy_race_ability", {"aid": "wall_of_bones_buyout"}))
    other = bleeding(hero())
    return _reminded(w), _reminded(b), _reminded(off), _reminded(bought), _reminded(bought_dry), _reminded(other)


S.case("bleed-reminder", "decision 4: the reminder 'bleeding x2' only while a bleeding status is on a Wall of Bones "
       "character; gone when the bleeding is off, gone after the buy-out (with or without bleeding); never for others",
       (False, True, False, False, False, False))(_bleed)
S.case("bleed-not-counted", "decision 4: bleeding x2 is not computed: the bleeding status keeps the value the player "
       "set (0 here)", 0)(lambda: next(s for s in bleeding(mordon_wall()).statuses if s.sid == "bleeding").per_tick_hp)


# ---------------------------------------------------------------- 2.3 comfort per fight (decision 5)
def _gains(ch):
    with rd.using(ch):
        return tuple(fc.gain(ch, m) for m in (1, 2, 5, 8))


# max(0, min(|m|, 5) - 1), at most 4: 1 -> 0, 2 -> 1, 5 -> 4, 8 -> 4
S.case("comfort-rule", "decision 5: |morale| 1 -> 0, 2 -> 1, 5 -> 4, 8 -> 4 (cap 5, minus 1, at most 4)",
       (0, 1, 4, 4))(lambda: _gains(hero()))
# Mordon: minus 2, at most 3: 1 -> 0, 2 -> 0, 5 -> 3, 8 -> 3; bought out: back to 0, 1, 4, 4
S.case("comfort-mordon", "decision 5: Wall of Bones 1 more and at most 3: 2 -> 0, 5 -> 3; bought out: the normal rule",
       ((0, 0, 3, 3), (0, 1, 4, 4)))(
    lambda: (_gains(mordon_wall()), _gains(run(mordon_wall(), ("buy_race_ability", {"aid": "wall_of_bones_buyout"})))))
S.case("comfort-const", "decision 5: the numbers are rule data: a character override of the cap to 3 -> |morale| 5 "
       "gives 3 - 1 = 2", 2)(lambda: fc.gain(run(hero(), ("edit_rules", {"constants": {"comfort.fight_cap": 3}})), 5))
# cap raised to 10: |morale| 8 -> 8 - 1 = 7, at most 4 -> 4
S.case("comfort-max", "decision 5: at most 4 binds once the cap is raised (cap 10: |morale| 8 -> 7 -> 4)", 4)(
    lambda: fc.gain(run(hero(), ("edit_rules", {"constants": {"comfort.fight_cap": 10}})), 8))


def _fight(start_morale=0, *scales):
    c = run(hero(comfort_current=1), ("start_combat", {}))
    for m in scales:
        c = run(c, ("edit_sheet", {"morale_scale": m}))
    return run(c, ("end_combat", {}))


def _flow():
    c = _fight(0, -2, -5, 3)
    note = c.trigger_notes[-1]
    took = run(c, ("run_trigger_action", {"nid": note.nid}))
    return (c.combat_morale_peak, c.morale_scale, (note.action, note.target, note.amount), c.comfort_current,
            took.comfort_current, took.combat_morale_peak,
            ref(lambda: dispatch(took, "gain_fight_comfort")))


# morale -2, -5, +3 -> the largest |morale| 5 -> +4 comfort offered (not added: comfort stays 1); the button -> 5;
# the peak is cleared, a second gain is refused
S.case("comfort-flow", "decision 5: the combat keeps the largest |morale| (5 of -2, -5, +3); the end offers +4 as a "
       "button (comfort unchanged 1); the button adds it (5) and clears the peak; a second gain is refused",
       (5, 0, ("run_command", "gain_fight_comfort", 4), 1, 5, 0, "no_fight_comfort"))(_flow)
S.case("comfort-none", "decision 5: |morale| 1 gives 0: no reminder at the combat end", 0)(
    lambda: len(_fight(0, 1).trigger_notes))
S.case("comfort-start-clears", "decision 5: the next combat start clears the stored peak", (5, 0))(
    lambda: (lambda c: (c.combat_morale_peak, run(c, ("start_combat", {})).combat_morale_peak))(_fight(0, 5)))
S.case("comfort-in-combat", "decision 5: the gain is refused while the combat is on", "combat_still_active")(
    lambda: ref(lambda: dispatch(run(hero(), ("start_combat", {}), ("edit_sheet", {"morale_scale": 4})),
                                 "gain_fight_comfort")))


def _undo():
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    s.new("Hero", hero(comfort_current=1))
    s.dispatch("start_combat")
    s.dispatch("edit_sheet", morale_scale=5)
    s.dispatch("end_combat")
    s.dispatch("run_trigger_action", nid=s.character.trigger_notes[-1].nid)
    after = s.character.comfort_current, s.character.log[-1].command
    s.undo()
    return after, s.character.comfort_current, s.character.trigger_notes[-1].handled


S.case("comfort-undo", "decision 5: the gain is a journaled command; undo -> comfort 5 back to 1, the reminder open "
       "again", ((5, "run_trigger_action"), 1, False))(_undo)

if __name__ == "__main__":
    sys.exit(S.run())
