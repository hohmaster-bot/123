"""Package 35 P1 (owner review of package 34): one action / reaction returned (return_action / return_reaction), own
temp HP with the effect target temp_hp (Q229 closed), the AC variants of a cell in the sources view.
Numbers by hand from RULES (combat.md "Actions", resources.md "HP and temp HP", rest.md, ac_zones.md).
Hero: Str 14, Dex 20 (+5), Con 12 (+1), others 10; bab 2, hp rolls (10,): HP max 10 + 1 = 11; actions 3, reactions 1.
Run: python Wp_claude/tests/model/test_pkg35a.py"""
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
from wp.core.effects import Status  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import sources as src  # noqa: E402
from wp.model.character import ABILITIES, Ability, Character  # noqa: E402
from wp.model.source_row import SourceRow  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg35a")
TMP = tempfile.mkdtemp(prefix="wp_p35a_")


def hero(**kw):
    base = {"str": 14, "dex": 20, "con": 12}
    return Character(bab=2, hp_rolls=(10,), abilities={a: Ability(base=base.get(a, 10)) for a in ABILITIES}, **kw)


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


def squares(ch, key="action_squares"):
    return [spent for _, spent in vw.VIEWS["combat"](ch)[key]]


def cur(ch, key="actions"):
    return vw.VIEWS["combat"](ch)[key]["current"]


# ---------------------------------------------------------------- P1.2 actions one by one
def _actions():
    c = hero()
    one = run(c, ("spend_actions", {"n": 1}))
    two = run(one, ("spend_actions", {"n": 1}))
    back = run(two, ("return_action", {"n": 1}))
    full = run(back, ("return_action", {"n": 1}))
    return ([cur(x) for x in (c, one, two, back, full)], squares(two), squares(back), squares(full),
            full.actions_current, ref(lambda: dispatch(full, "return_action", n=1)),
            ref(lambda: dispatch(one, "return_action", n=2)))


S.case("a-return", "owner review 2: 3 -> spend 2 -> 1 (squares 1, 2 spent); return one -> 2 (only square 1 spent: "
       "smallest first); return one -> 3 (stored None = full); nothing spent -> refused; 2 of 1 spent -> refused",
       ([3, 2, 1, 2, 3], [True, True, False], [True, False, False], [False, False, False], None, "nothing_spent",
        "nothing_spent"))(_actions)


def _reactions():
    c = hero()
    spent = run(c, ("spend_reaction", {"n": 1}))
    back = run(spent, ("return_reaction", {"n": 1}))
    return (cur(spent, "reactions"), squares(spent, "reaction_squares"), cur(back, "reactions"),
            back.reactions_current, ref(lambda: dispatch(back, "return_reaction", n=1)))


S.case("a-reaction", "owner review 2: reactions 1 -> spent 0 (square spent) -> returned 1 (full); again refused",
       (0, [True], 1, None, "nothing_spent"))(_reactions)


def _session():
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    s.new("Hero", hero())
    s.dispatch("spend_actions", n=1)
    r = s.dispatch("return_action", n=1)
    after = s.view("combat")["actions"]["current"]
    line = [e.command for e in s.character.log][-1:]
    s.undo()
    return r.ok, after, line, s.view("combat")["actions"]["current"]


S.case("a-undo", "pkg 35: return_action is a command: 2 -> 3, a journal line, undo -> 2",
       (True, 3, ["return_action"], 2))(_session)

# ---------------------------------------------------------------- P1.8 own temp HP (owner, Q229 closed)
BUFF = Status("Ward", sid="ward", active=True, temp_hp_left=4)


def _own():
    c = hero(temp_hp=3, statuses=(BUFF,))
    a = run(c, ("source_add", {"number": "temp_hp", "name": "Inner fire", "value": 5}))
    v = src.view(a, "temp_hp")
    return (dv.temp_hp_total(c), dv.temp_hp_total(a), v["total"], v["external"],
            sum(r["value"] for r in v["rows"] if r["counted"]), [r["id"] for r in v["rows"]])


S.case("t-own", "owner Q229: button 3 + buff 4 = 7; + own row 5 = 12; the sources total is the OWN 3 + 5 = 8, the buff "
       "4 is external (statuses block), rows add up to 8", (7, 12, 8, 4, 8, ["temp_button", "inner_fire"]))(_own)


def _damage():
    c = run(hero(temp_hp=3, statuses=(BUFF,)), ("source_add", {"number": "temp_hp", "name": "Inner fire", "value": 5}))
    a = run(c, ("take_damage", {"amount": 6}))
    b = run(a, ("take_damage", {"amount": 4}))
    rest = run(a, ("short_rest", {}))              # own 2 still left: the rest clears it too
    more = run(rest, ("source_add", {"number": "temp_hp", "name": "Second", "value": 2}))
    va = src.view(a, "temp_hp")
    return ((a.temp_hp, a.temp_hp_spent, dv.temp_hp_own_effects(a), a.statuses[0].temp_hp_left, dv.temp_hp_total(a),
             a.hp_current),
            (b.temp_hp_spent, dv.temp_hp_own_effects(b), b.statuses[0].temp_hp_left, dv.temp_hp_total(b), b.hp_current),
            (va["total"], sum(r["value"] for r in va["rows"] if r["counted"])),
            (dv.temp_hp_total(rest), rest.temp_hp_spent), dv.temp_hp_total(more))


S.case("t-damage", "resources.md + Q239: 6 damage: button 3 first, then own 3 (spent 3; own 2 left), buff 4 untouched: "
       "temp 12 - 6 = 6, HP stays 8 (the new hero's current); 4 more: own 2, then buff 2 -> 2 left, HP 8; sources after "
       "the first hit: own 2 = rows 0 + 5 - 3; short rest clears all (spent = 5); a new own row +2 -> 7 - 5 = 2",
       ((0, 3, 2, 4, 6, 8), (5, 0, 2, 2, 8), (2, 2), (0, 5), 2))(_damage)
S.case("t-stored", "pkg 35: temp_hp_spent is a stored base value (save / load keeps it); the target temp_hp is data",
       (True, True))(lambda: (
           (lambda ch: cio.loads(cio.dumps(ch)).temp_hp_spent == 3)(
               run(hero(source_rows=(SourceRow("f", "temp_hp", "F", 5),)), ("take_damage", {"amount": 3}))),
           "temp_hp" in __import__("wp.model.sheet_targets", fromlist=["TARGETS"]).TARGETS))
S.case("t-editable", "owner Q229: own temp HP sources are editable now (a target); a status's effects stay read-only",
       ("allowed", "sources_read_only"))(
    lambda: (ref(lambda: dispatch(hero(), "source_add", number="temp_hp", name="x", value=1)),
             ref(lambda: dispatch(hero(statuses=(BUFF,)), "source_add", number="status:ward", name="x", value=1))))


# ---------------------------------------------------------------- P1.6 AC variants named in the sources view
def _variants():
    c = hero(source_rows=(SourceRow("w", "ac:2", "Ward", 1),))
    with rd.using(c):
        v2, v8 = src.view(c, "ac:2"), src.view(c, "ac:8")
    return v2["total"], [(i, ac) for i, _, ac in v2["variants"]], v8["total"], [(i, ac) for i, _, ac in v8["variants"]]


S.case("v-ac", "ac_zones.md: front cell 2: 10 + Dex 5 + Ward 1 = 16 in every variant; back cell 8 loses Dex (Ward "
       "is a cell 2 row): 10", (16, [("melee", 16), ("melee_parry", 16), ("ranged", 16)], 10,
                                       [("melee", 10), ("ranged", 10)]))(_variants)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
