"""Package 36 P3: a race in the character (owner decision 15; RULES/races.md): take_race copies the race entries with
the source race:<id> (stat changes and HP are effects), priced abilities are bought, change_race lists and removes the
old race entries (quirks and paid traits too) after a confirmation, no refund, one undo step; a catalog change never
changes a taken copy. Hero: every stat 10, hp rolls (8,), training 1000. Run: python Wp_claude/tests/model/test_pkg36c.py"""
import copy
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import session as sm  # noqa: E402
from wp.app import views as vw  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import Character  # noqa: E402

S = Suite("test_pkg36c")
TMP = tempfile.mkdtemp(prefix="wp_p36c_")
TESTLING = {"id": "testling", "name": "Testling", "module": "test", "type_tags": ["humanoid"], "speed": 25,
            "effects": [{"target": "stat:str", "value": 2}, {"target": "stat:int", "value": -2},
                        {"target": "hp_max", "value": 6}],
            "abilities": [{"id": "keen", "name": "Keen", "text": "+1 to saves.", "effects": [{"target": "save",
                                                                                              "value": 1}]},
                          {"id": "wings", "name": "Wings", "price": 600, "effects": [{"target": "move:fly",
                                                                                       "value": 20, "note": "average"}]},
                          {"id": "better_wings", "name": "Better wings", "price": 300, "needs": "wings",
                           "effects": [{"target": "move:fly", "value": 20, "note": "good"}]}],
            "quirks": [{"id": "oath", "name": "Oath", "text": "Keeps the oath."}],
            "statuses": [{"id": "rage", "name": "Rage", "effects": [{"target": "attack", "value": 2}]}],
            "languages": ["Old tongue", "City"]}
OTHER = {"id": "other", "name": "Other", "module": "test", "speed": 20,
         "effects": [{"target": "stat:dex", "value": 2}], "abilities": [], "languages": ["City"]}


def hero():
    return Character(training=1000)


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


TAKEN = run(hero(), ("take_race", {"race": TESTLING}))


def _take():
    c = TAKEN
    return ((dv.ability_current(c, "str"), dv.ability_current(c, "int")), dv.hp_pool(c).max, dv.speed(c),
            sorted(f.fid for f in c.feats), [(q.kid, q.source) for q in c.quirks],
            [(lg.name, lg.native) for lg in c.languages], c.statuses[0].active, c.abilities["str"].base)


S.case("r-take", "decision 15: Str 10 + 2 = 12, Int 8 (effects, the base stays 10); HP 8 + 6 = 14; speed 25; the free "
       "ability Keen taken, the priced ones not; the quirk with source race:testling; Old tongue native, City not; the "
       "race status copied off", ((12, 8), 14, 25, ["keen", "race_testling"], [("oath", "race:testling")],
                                  [("Old tongue", True), ("City", False)], False, 10))(_take)


def _buy():
    a = run(TAKEN, ("buy_race_ability", {"aid": "wings"}))
    return (ref(lambda: dispatch(TAKEN, "buy_race_ability", aid="better_wings")), a.training,
            [m[:3] for m in vw.VIEWS["sheet"](a)["moves"]],
            [x[0] for x in vw.VIEWS["race"](a)["abilities"] if x[-1]])


S.case("r-buy", "decision 9: a chain: better wings needs wings first (refused); wings for 600: training 1000 - 600 = "
       "400, fly 20 average", ("needs_ability", 400, [("fly", 20, "average")], ["keen", "wings"]))(_buy)


def _change():
    paid = run(TAKEN, ("buy_race_ability", {"aid": "wings"}))
    try:
        dispatch(paid, "change_race", race=OTHER)
        listed = []
    except CommandError as e:
        listed = sorted(oid for _c, oid, _n in e.params["removed"])
    c = run(paid, ("change_race", {"race": OTHER, "confirm": True}))
    return (listed, (dv.ability_current(c, "str"), dv.ability_current(c, "dex")), sorted(f.fid for f in c.feats),
            c.quirks, c.statuses, c.training, dv.speed(c), [lg.name for lg in c.languages], c.race_id,
            [e.command for e in c.log][-1])


S.case("r-change", "decision 15: without confirm the list of all race entries (quirk, status, both languages, paid wings); "
       "confirmed: the old entries gone, Other's Dex +2, training stays 400 (no refund), speed 20, one journal line",
       (["city", "keen", "oath", "old_tongue", "race_testling", "rage", "wings"], (10, 12), ["race_other"], (), (), 400, 20,
        ["City"], "other", "change_race"))(_change)


def _undo():
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    s.new("Hero", hero())
    s.dispatch("take_race", race=TESTLING)
    s.dispatch("change_race", race=OTHER, confirm=True)
    after = s.character.race_id
    s.undo()
    return after, s.character.race_id, dv.ability_current(s.character, "str")


S.case("r-undo", "decision 15: change_race is one undo step: other -> undo -> testling (Str 12 again)",
       ("other", "testling", 12))(_undo)


def _snapshot():
    entry = copy.deepcopy(TESTLING)
    c = run(hero(), ("take_race", {"race": entry}))
    entry["effects"][0]["value"] = 10                  # the catalog changes later
    entry["abilities"][1]["price"] = 1
    a = run(c, ("buy_race_ability", {"aid": "wings"}))
    return dv.ability_current(c, "str"), a.training, ref(lambda: dispatch(c, "take_race", race=OTHER))


S.case("r-snapshot", "decision 15: a later catalog change never changes the taken copy: Str stays 12 and wings still "
       "cost 600 (the snapshot); a second take_race is refused", (12, 400, "race_taken"))(_snapshot)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
