"""Package 26: actions as a resource (A), flask bars (B), experience log and level history (C).
Numbers by hand from the package text and RULES/combat.md "Actions". Run: python Wp_claude/tests/model/test_pkg26.py"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import session as sm  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.commands import action_cmds as ac  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.model import experience as xp  # noqa: E402
from wp.model import flask  # noqa: E402
from wp.model.character import Character, ResourcePool  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_pkg26")
TMP = tempfile.mkdtemp(prefix="wp_p26_")
HASTE = Status("haste", sid="haste", effects=(Effect("actions_max", 1),))


def refusal(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def cur_max(ch):
    with rd.using(ch):
        p = ac.actions_pool(ch)
    return p.current, p.max


# ---------------------------------------------------------------- A. actions
S.case("a-base", "owner (pkg 26 A): 3 actions per turn", (3, 3))(lambda: cur_max(Character()))
S.case("a-effect", "pkg 26 A: an effect actions_max +1 -> 4", (4, 4))(lambda: cur_max(Character(statuses=(HASTE,))))


def _spend():
    c = run(Character(), ("spend_actions", {"n": 2}))
    return cur_max(c), refusal(lambda: dispatch(c, "spend_actions", n=2))


S.case("a-spend", "pkg 26 A: spend 2 of 3 -> 1 left; then 2 more refused", ((1, 3), "not_enough_actions"))(_spend)
S.case("a-tick", "pkg 26 A: the zero-initiative tick restores the actions (1 -> 3)", (3, 3))(
    lambda: cur_max(run(Character(), ("start_combat", {}), ("spend_actions", {"n": 2}), ("tick", {}))))
S.case("a-end-combat", "pkg 26 A: end_combat restores the actions", (3, 3))(
    lambda: cur_max(run(Character(), ("start_combat", {}), ("spend_actions", {"n": 3}), ("end_combat", {}))))
S.case("a-restore", "pkg 26 A: restore_actions (manual) -> max", (3, 3))(
    lambda: cur_max(run(Character(), ("spend_actions", {"n": 3}), ("restore_actions", {}))))
S.case("a-presets", "combat.md: shift 1, move 1, standard 2, full round 3, complete round 4; unknown refused",
       (1, 1, 2, 3, 4, "unknown_action_cost"))(
    lambda: tuple(ac.preset_cost(n) for n in ("shift", "move", "standard", "full_round", "complete_round")) +
    (refusal(lambda: ac.preset_cost("bonus")),))
S.case("a-sources", "pkg 26 A: the tooltip lists the base 3 and the effect +1", (("base", 3), ("haste", 1)))(
    lambda: tuple((s, v) for s, v, _ in ac.actions_view(Character(statuses=(HASTE,)))["sources"]))
S.case("a-topics", "pkg 26 A: the topics table names spend_actions / restore_actions",
       (("combat", "resources", "log"), ("combat", "resources", "log")))(
    lambda: (sm.topics_of("spend_actions"), sm.topics_of("restore_actions")))


def _not_auto():
    from wp.model.character import AttackRecord
    c = Character(attacks=(AttackRecord("u", "unarmed", "unarmed_combat", cost_actions=2),))
    c = run(c, ("use_attack", {"rid": "u"}))
    return cur_max(c), c.attacks[0].cost_actions


S.case("a-not-automatic", "pkg 26 A: a record with cost_actions 2: using it spends nothing (3 of 3)", ((3, 3), 2))(_not_auto)

# ---------------------------------------------------------------- B. flasks
S.case("f-segments", "pkg 26 B: max 12, segment 5 -> [5, 5, 2]; current 7 -> fills [5, 2, 0]", ([5, 5, 2], [5, 2, 0]))(
    lambda: (flask.segments(12, 5), flask.fills(7, 12, 5)))
S.case("f-edges", "pkg 26 B: no ticks (0) -> one segment; over max fills all; max 10 by 5 -> [5, 5]",
       ([12], [5, 5, 2], [5, 5]))(lambda: (flask.segments(12, 0), flask.fills(15, 12, 5), flask.segments(10, 5)))


def _pool_view():
    c = Character(pools=(ResourcePool("dark", "Darkness", max=12, current=7),))
    with rd.using(c):
        v = flask.view(c)["pool:dark"]
    return v["segments"], v["fills"], v["segment_size"]


S.case("f-pool", "pkg 26 B: a class pool (darkness 7 / 12) by the default segment 5", ([5, 5, 2], [5, 2, 0], 5))(_pool_view)


def _balance():
    c = Character(balance_current=3, bp_current=6)
    with rd.using(c):
        v = flask.view(c)["balance"]
    return v["max"], v["segments"], v["fills"], v["cap"], v["restore"]


S.case("f-balance", "pkg 26 B: balance 3 of max 6 (current BP 6, no armor): segments [5, 1], fills [3, 0]; the cap 6; "
       "restore 1 per tick (level 1 + Con 0 -> min 1)", (6, [5, 1], [3, 0], 6, 1))(_balance)


def _setting():
    from wp.settings.settings_cmds import settings_dispatch
    from wp.settings import store as st
    app = settings_dispatch(st.AppSettings(), "settings_set", key="resource_display",
                            value={"hp": "flask", "mana": "flask"}).state
    app = settings_dispatch(app, "settings_set", key="resource_segments", value={"hp": 4}).state
    c = Character(hp_rolls=(10,), hp_current=10)
    with rd.using(c):
        v = flask.view(c, app)["hp"]
    return v["style"], v["segments"]


S.case("f-setting", "pkg 26 B: style flask and HP segment 4 from the app settings: max 10 -> [4, 4, 2]",
       ("flask", [4, 4, 2]))(_setting)

# ---------------------------------------------------------------- C. experience
def _log():
    c = run(Character(), ("add_experience", {"amount": 300, "note": "dragon"}), ("add_experience", {"amount": 400}))
    a = xp.total(c)
    c2 = run(c, ("remove_experience_entry", {"xid": c.xp_log[0].xid}))
    c3 = run(c2, ("add_experience", {"amount": -50, "note": "penalty"}))
    return a, xp.total(c2), xp.total(c3), [e.xid for e in c3.xp_log]


S.case("x-log", "pkg 26 C: 300 + 400 = 700; remove the 300 -> 400; -50 -> 350; ids never reused (xp2, xp3)",
       (700, 400, 350, ["xp2", "xp3"]))(_log)


def _history():
    c = run(Character(), ("add_experience", {"amount": 700}), ("level_up", {"hp_roll": 5, "note": "after the siege"}))
    h = c.level_history[0]
    return h.level, h.experience_total, h.hp_roll, h.note


S.case("x-history", "pkg 26 C: level_up writes the history: level 2, xp 700 at that moment, roll 5, the note",
       (2, 700, 5, "after the siege"))(_history)
S.case("x-progress", "pkg 26 C: goal 1000, total 700 -> 70%; no goal -> None", (70, None))(
    lambda: (xp.progress_pct(run(Character(), ("add_experience", {"amount": 700}),
                                 ("set_next_level_at", {"value": 1000}))),
             xp.progress_pct(run(Character(), ("add_experience", {"amount": 700})))))
S.case("x-edit", "pkg 26 C: edit an entry 300 -> 250 and its note; the total follows", (250, "fixed"))(
    lambda: (lambda c: (xp.total(c), c.xp_log[0].note))(
        run(Character(), ("add_experience", {"amount": 300}), ("edit_experience_entry", {"xid": "xp1", "amount": 250,
                                                                                        "note": "fixed"}))))
S.case("x-history-edit", "pkg 26 C: edit and remove a level history entry (edit mode)", ("typo fixed", 0))(
    lambda: (lambda c: (run(c, ("edit_level_history", {"lid": "lv1", "note": "typo fixed"})).level_history[0].note,
                        len(run(c, ("remove_level_history", {"lid": "lv1"})).level_history)))(
        run(Character(), ("level_up", {"hp_roll": 4}))))
S.case("x-no-auto", "pkg 26 C: no automatic level-up: 5000 xp over a goal of 1000 keeps level 1 (100%)", (1, 100))(
    lambda: (lambda c: (c.level, xp.progress_pct(c)))(
        run(Character(), ("set_next_level_at", {"value": 1000}), ("add_experience", {"amount": 5000}))))


class Clock(object):
    def __call__(self):
        return 1000.0


def _session():
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "user"), Clock())
    s.new("Hero", Character())
    s.dispatch("add_experience", amount=300)
    stamp = s.character.xp_log[0].at
    view = s.view("training")["experience"]
    s.undo()
    return stamp, view["total"], xp.total(s.character), s.character.log[-1].command


S.case("x-session", "pkg 26 C: the Session stamps the entry (clock 1000 s), the training view shows the total; undo "
       "removes it (journal line undo)", ("19700101-001640-000", 300, 0, "undo"))(_session)


def _roundtrip():
    from wp.storage import character_io as cio
    c = run(Character(), ("add_experience", {"amount": 10, "note": "n"}), ("level_up", {"hp_roll": 3}),
            ("set_next_level_at", {"value": 50}), ("spend_actions", {"n": 1}))
    return cio.loads(cio.dumps(c)) == c


S.case("x-roundtrip", "pkg 26: experience, level history, the goal and the actions left survive save / load", True)(_roundtrip)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
