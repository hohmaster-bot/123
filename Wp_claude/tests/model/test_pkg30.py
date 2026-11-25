"""Package 30: core data of the Classic screen v2 (owner decisions; RULES/gear.md "Load display", RULES/combat.md
"General attack numbers"). Numbers by hand. Run: python Wp_claude/tests/model/test_pkg30.py"""
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
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.i18n import i18n  # noqa: E402
from wp.model.character import ABILITIES, Ability, AttackRecord, Character, Item, ResourcePool  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402
from wp.settings import layout  # noqa: E402

S = Suite("test_pkg30")
TMP = tempfile.mkdtemp(prefix="wp_p30_")


def hero(**kw):
    base = {"str": 14, "dex": 20}
    return Character(bab=2, abilities={a: Ability(base=base.get(a, 10)) for a in ABILITIES}, **kw)


def view(name, ch, key=None):
    with rd.using(ch):
        v = vw.VIEWS[name](ch)
    return v if key is None else v[key]


def ref(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


# ---------------------------------------------------------------- load (gear.md)
def _load(kg):
    v = view("items", hero(items=(Item("b", "bag", weight_l=kg),)), "load")
    return v["category"], v["light_max_l"], v["heavy_max_l"], v["text"]


S.case("l-light", "gear.md: Str 14 (+2): light to 7.9 B = 79 L, max 12.9 B = 129 L; 40 L -> light, '40 of 129'",
       ("light", 79, 129, ("load.of", (40, 129))))(lambda: _load(40))
S.case("l-load", "owner: 100 L (above light, up to the max) -> the load state (key heavy)", "heavy")(lambda: _load(100)[0])
S.case("l-over", "owner: 130 L (above the max 129) -> overload", "overload")(lambda: _load(130)[0])
S.case("l-texts", "owner: the names light / load / overloaded (ru: \u041b\u0451\u0433\u043a\u0430\u044f, \u041d\u0430\u0433\u0440\u0443\u0437\u043a\u0430, \u0412\u044b \u043f\u0435\u0440\u0435\u0433\u0440\u0443\u0436\u0435\u043d\u044b ...)",
       ("load", "\u041d\u0430\u0433\u0440\u0443\u0437\u043a\u0430", "40 of 129"))(
    lambda: (i18n.t("load.heavy", "en"), i18n.t("load.heavy", "ru"), i18n.t("load.of", "en", values=(40, 129))))


# ---------------------------------------------------------------- attack numbers (combat.md)
def att(ch, kind):
    return view("sheet", ch, "attack_" + kind)["total"]


S.case("a-default", "owner: Str 14 (+2) + BAB 2 -> melee +4; Dex 20 (+5) + BAB 2 -> ranged +7", (4, 7))(
    lambda: (att(hero(), "melee"), att(hero(), "ranged")))
S.case("a-source-stat", "owner: melee from Dex + BAB -> +7", 7)(
    lambda: att(dispatch(hero(), "set_attack_source", kind="melee", source="dex").state, "melee"))
S.case("a-pain", "owner: pain 1 counts always (out of combat too): melee 4 - 1 = 3, ranged 6", (3, 6))(
    lambda: (att(hero(pain=(PainEntry(1),)), "melee"), att(hero(pain=(PainEntry(1),)), "ranged")))
S.case("a-morale", "owner: morale scale 4 only in combat: out 4, in combat 4 + 2 = 6; the flag morale_active",
       (4, 6, False, True))(lambda: (att(hero(morale_scale=4), "melee"), att(hero(morale_scale=4, in_combat=True), "melee"),
                                     view("combat", hero())["morale_active"],
                                     view("combat", hero(in_combat=True))["morale_active"]))


def _record():
    ch = hero(items=(Item("sw", "sword", kind="weapon", groups=("blades",)),),
              attacks=(AttackRecord("r1", "sw", "blades"),))
    ch = dispatch(ch, "set_attack_source", kind="melee", source="record:r1").state
    v = view("sheet", ch, "attack_melee")
    with rd.using(ch):
        rec_to_hit = vw.attacks(ch)[0].to_hit
    return v["weapon"], v["source"], v["total"] == rec_to_hit


S.case("a-record", "owner: a specific weapon as the source: the record's to-hit and the weapon name",
       ("sword", "record:r1", True))(_record)
S.case("a-refused", "pkg 30: kind 'thrown' and source 'luck' refused; an unknown record refused",
       ("not_allowed", "not_allowed", "no_attack_record"))(
    lambda: (ref(lambda: dispatch(hero(), "set_attack_source", kind="thrown", source="str")),
             ref(lambda: dispatch(hero(), "set_attack_source", kind="melee", source="luck")),
             ref(lambda: dispatch(hero(), "set_attack_source", kind="melee", source="record:zz"))))


# ---------------------------------------------------------------- adjust_value (the tube editor)
def adj(ch, resource, delta):
    return dispatch(ch, "adjust_value", resource=resource, delta=delta).state


def _adjust():
    ch = Character(hp_rolls=(10,), hp_current=5, spirit_current=2, mana=Pool(12, 20), overload=2,
                   pools=(ResourcePool("dark", "Darkness", max=12, current=7),))
    return (adj(ch, "mana", 3).mana.current, adj(ch, "hp", -8).hp_current, adj(ch, "pool:dark", 10).pools[0].current,
            adj(ch, "pool", -2).pools[0].current, adj(ch, "overload", 1).overload,
            ref(lambda: adj(ch, "mana", -20)), ref(lambda: adj(ch, "spirit", -3)), ref(lambda: adj(ch, "overload", -5)))


S.case("v-adjust", "owner: mana 12 + 3 = 15; HP 5 - 8 = -3 (allowed); pool 7 + 10 = 17 (over max kept); 'pool' = the "
       "first pool 7 - 2 = 5; overload 2 + 1 = 3; mana -20, spirit -3, overload -5 below 0 -> out_of_range",
       (15, -3, 17, 5, 3, "out_of_range", "out_of_range", "out_of_range"))(_adjust)


def _over_max():
    ch = adj(Character(pools=(ResourcePool("dark", "Darkness", max=12, current=7),)), "pool:dark", 10)
    return view("resources", ch)["pools"][0][2]


S.case("v-over-max", "owner: no clamp above max: the pool shows 17 / 12 over_max", {"current": 17, "max": 12,
                                                                                    "over_max": True})(_over_max)


# ---------------------------------------------------------------- run_quick through the Session
def session(ch):
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "c"), os.path.join(d, "u"), lambda: 1000.0)
    s.new("hero", ch)
    return s


def _quick():
    s = session(Character(hp_rolls=(10,), hp_current=10, mana=Pool(12, 20), spirit_current=3))
    ok = s.run_quick({"label": "q", "macro": [{"command": "adjust_value", "params": {"resource": "mana", "delta": -2}},
                                              {"command": "set_value", "params": {"resource": "hp", "value": 3}}]})
    after = (s.character.mana.current, s.character.hp_current)
    s.undo()
    undone = (s.character.mana.current, s.character.hp_current)
    bad = s.run_quick({"label": "b", "macro": [{"command": "adjust_value", "params": {"resource": "mana", "delta": -2}},
                                               {"command": "adjust_value", "params": {"resource": "spirit", "delta": -9}}]})
    return ok.ok, after, undone, bad.ok, bad.reason, bad.params.get("step"), s.character.mana.current


S.case("q-macro", "owner: a macro = ONE undo step (mana 12 - 2 = 10, HP 3; undo -> 12, 10); a refused step 2 rolls "
       "the whole macro back (mana stays 12)", (True, (10, 3), (12, 10), False, "out_of_range", 2, 12))(_quick)


# ---------------------------------------------------------------- squares, defense, labels
def _squares():
    c = run(Character(), ("spend_actions", {"n": 2}))
    haste = Character(statuses=(Status("haste", sid="h", effects=(Effect("actions_max", 1),)),))
    return view("combat", c)["action_squares"], view("combat", run(haste, ("spend_actions", {"n": 1})))["action_squares"]


def run(ch, *steps):
    for n, p in steps:
        ch = dispatch(ch, n, **p).state
    return ch


S.case("s-squares", "owner: 3 actions, 2 spent -> squares 1 and 2 grey, 3 free; 4 actions (haste), 1 spent -> 1 grey",
       (((1, True), (2, True), (3, False)), ((1, True), (2, False), (3, False), (4, False))))(_squares)
SHIELD = Item("sh", "heavy shield", kind="shield", hands=1, shield=2, shield_type="heavy")


def _shield(side):
    ch = run(Character(items=(SHIELD,)), ("equip_hands", {"iid": "sh", "side": side}))
    d = view("defense", ch)
    return d["shield_side"], 10 + sum(v for _, v in d["cell_lines"]["4"]), d["cells"]["4"]["full"]


S.case("d-shield-left", "pkg 24 rules: heavy shield 2 left covers cell 4: 10 + 2 = 12; lines sum = the cell number",
       ("left", 12, 12))(lambda: _shield("left"))
S.case("d-shield-right", "pkg 24 rules: shield right: cell 4 uncovered = 10", ("right", 10, 10))(lambda: _shield("right"))
S.case("d-labels", "owner: zone labels: cell 4 side left (ru: \u0441\u0431\u043e\u043a\u0443 \u0441\u043b\u0435\u0432\u0430), cell 8 back",
       ("side left", "\u0441\u0431\u043e\u043a\u0443 \u0441\u043b\u0435\u0432\u0430", "back", "ac_cell.4"))(
    lambda: (i18n.t("ac_cell.4", "en"), i18n.t("ac_cell.4", "ru"), i18n.t("ac_cell.8", "en"),
             view("defense", Character())["cell_labels"]["4"]))


# ---------------------------------------------------------------- statuses, favourites, reminders, cells
def _note():
    ch = Character(statuses=(Status("rage", sid="rage", note="until the bell"),))
    return view("statuses", ch)["container"].entries[0].note


S.case("n-note", "owner: a status chip shows its note", "until the bell")(_note)


def _favorites():
    ch = run(Character(), ("set_favorite", {"kind": "feat", "oid": "power"}), ("set_favorite", {"kind": "item", "oid": "x"}),
             ("set_favorite", {"kind": "item", "oid": "x", "on": False}))
    return view("statuses", ch)["favorites"]["abilities"], ref(lambda: dispatch(ch, "set_favorite", kind="race", oid="x"))


S.case("f-favorites", "owner: favourite abilities: feat:power stays, item:x removed; kind race refused",
       (("feat:power",), "not_allowed"))(_favorites)
S.case("r-reminders", "owner: the reminders row collects the drive reminders: level 2 without a principle",
       (("drive.remind.principle", ("growth",)),))(
    lambda: view("statuses", run(Character(), ("add_drive", {"dtype": "growth", "level": 2})))["reminders"])


def _cells():
    ch = hero()
    with rd.using(ch):
        melee = layout.resolve(ch, "stat:attack_melee")[0]
        load = layout.resolve(ch, "counter:load")[0]
    s = session(ch)
    ids = [x[0] for x in s.cell_sources()]
    return melee, load, "stat:attack_melee" in ids and "counter:pain" in ids and "resource:hp" in ids


S.case("c-sources", "owner: a cell may show any number: stat:attack_melee = 4, counter:load = 0 L; the source list "
       "has them", ({"value": 4}, {"value": 0}, True))(_cells)


def _profile():
    from wp.settings import store as st
    from wp.settings.settings_cmds import settings_dispatch
    a = st.AppSettings()
    p = st.profile(a, "classic")
    bad = ref(lambda: settings_dispatch(a, "profile_set", mode="classic", pid="default", quick_cells=17))
    ok = settings_dispatch(a, "profile_set", mode="classic", pid="default", quick_cells=16, quick_columns=8,
                           strips=[[{"source": "counter:ot"}]]).state
    q = st.profile(ok, "classic")
    return p["quick_cells"], p["quick_columns"], bad, q["quick_cells"], len(q["strips"])


S.case("g-grid", "owner: the quick grid default 8 cells (4 columns, Q203); 17 refused (4-16); 16 and a second strip saved",
       (8, 4, "out_of_range", 16, 1))(_profile)
S.case("k-class", "pkg 30: the sheet gives the class snapshot (None without a class)", None)(
    lambda: view("sheet", Character())["class"])

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
