"""Package 19: settings structure: schema validation, app settings file (two layers, atomic save), rule and
character settings commands, layout profiles, cells against a real character, colour rules, quick button macros,
image registry, hotkey conflicts. Expected values by hand from the package text.
Run: python Wp_claude/tests/storage/test_settings.py"""
import io
import json
import os
import shutil
import sys
import tempfile
from dataclasses import fields

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.catalog import store as cs  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Status  # noqa: E402
from wp.model.character import ABILITIES, Ability, Character, ResourcePool, RulesSettings  # noqa: E402
from wp.settings import images as img  # noqa: E402
from wp.settings import layout as lay  # noqa: E402
from wp.settings import schema as sch  # noqa: E402
from wp.settings import settings_view as sv  # noqa: E402
from wp.settings import store as st  # noqa: E402
from wp.settings.settings_cmds import settings_dispatch as do  # noqa: E402

S = Suite("test_settings")
TMP = tempfile.mkdtemp(prefix="wp_set_")


def app():
    return st.AppSettings()


def run(a, *steps):
    for name, params in steps:
        a = do(a, name, **params).state
    return a


def reason(a, name, /, **kw):
    try:
        do(a, name, **kw)
    except CommandError as e:
        return e.reason
    return "allowed"


def creason(ch, name, /, **kw):
    try:
        dispatch(ch, name, **kw)
    except CommandError as e:
        return e.reason
    return "allowed"


def folder():
    return tempfile.mkdtemp(dir=TMP)


# ---------------------------------------------------------------- schema
S.case("v-range-type-enum", "pkg 19: ui_scale 1.5 ok; 5 out of range; 'x' wrong type; language 'de' not allowed",
       ("allowed", "out_of_range", "wrong_type", "not_allowed"))(
    lambda: (reason(app(), "settings_set", key="ui_scale", value=1.5), reason(app(), "settings_set", key="ui_scale", value=5),
             reason(app(), "settings_set", key="ui_scale", value="x"), reason(app(), "settings_set", key="language", value="de")))
S.case("v-map-values", "pkg 19: resource display 'pie' not allowed; hotkey 'Ctrl+Ctrl+A' is not a hotkey",
       ("not_allowed", "bad_hotkey"))(
    lambda: (reason(app(), "settings_set", key="resource_display", value={"hp": "pie"}),
             reason(app(), "settings_set", key="hotkeys", value={"x": "Ctrl+Ctrl+A"})))
S.case("v-color-point-rect", "pkg 19: color #FF0000 ok, 'red' bad; point needs 2 numbers; rect width -1 out of range",
       (None, "bad_color", "wrong_type", "out_of_range"))(
    lambda: (sch.check_value({"type": "color"}, "#FF0000"), sch.check_value({"type": "color"}, "red")[0],
             sch.check_value({"type": "point"}, [1])[0], sch.check_value({"type": "rect"}, [0, 0, -1, 5])[0]))
S.case("v-unknown-key", "pkg 19: an unknown key is refused by settings_set", "unknown_setting")(
    lambda: reason(app(), "settings_set", key="nope", value=1))
S.case("v-rules-key-not-app", "pkg 19: a rule setting is not set by the app command", "not_app_setting")(
    lambda: reason(app(), "settings_set", key="iterative_step", value=-3))
S.case("v-rules-mirror", "pkg 19/20: the schema's rule keys are the RulesSettings fields + the rule constants", True)(
    lambda: set(sch.keys_of("rules")) == {f.name for f in fields(RulesSettings) if f.name != "constants"} |
    set(__import__("wp.rules_data.rules", fromlist=["x"]).TABLE))
S.case("v-defaults-valid", "pkg 19: every default passes its own schema", [])(
    lambda: [k for k, s in sch.KEYS.items() if sch.check_value(s, s["default"])])


# ---------------------------------------------------------------- set / reset / view
def _reset_group():
    a = run(app(), ("settings_set", {"key": "font_size", "value": 14}), ("settings_set", {"key": "ui_scale", "value": 2.0}))
    v = sv.get(a, None, "font_size")
    b = run(a, ("settings_reset_group", {"group": "general"}))
    return v.value, v.changed, st.get(b, "font_size"), st.get(b, "ui_scale"), sv.get(b, None, "font_size").changed


S.case("r-set-reset-group", "pkg 19: font 14 (changed) -> reset group general -> 12 and 1.0, not changed",
       (14, True, 12, 1.0, False))(_reset_group)
S.case("r-reset-one", "pkg 19: settings_reset brings one key back to its default", "ru")(
    lambda: st.get(run(app(), ("settings_set", {"key": "language", "value": "en"}), ("settings_reset", {"key": "language"})),
                   "language"))


# ---------------------------------------------------------------- files
def _round_trip():
    d = folder()
    a = run(st.load(d), ("settings_set", {"key": "language", "value": "en"}))
    st.save(a)
    b = st.load(d)
    return st.get(b, "language"), st.get(b, "font_size"), st.to_data(b) == st.to_data(a)


S.case("f-round-trip", "pkg 19: empty folder -> defaults; set en, save, load -> en; the rest default", ("en", 12, True))(_round_trip)


def _unknown_kept():
    text = json.dumps({"kind": "app_settings", "format": 1, "values": {"future_key": 7}, "zzz": 1})
    a = run(st.loads(text), ("settings_set", {"key": "font_size", "value": 10}))
    data = st.to_data(a)
    return data["values"]["future_key"], "zzz" in data


S.case("f-unknown", "pkg 19: an unknown key inside values is kept; an unknown top-level field is dropped", (7, False))(_unknown_kept)


def _atomic():
    d = folder()
    a = run(st.load(d), ("settings_set", {"key": "font_size", "value": 10}))
    st.save(a)
    path = os.path.join(d, st.FILE)
    old = io.open(path, encoding="utf-8").read()

    def boom(x, y):
        raise OSError("disk full")
    real, cs._replace = cs._replace, boom
    try:
        st.save(run(a, ("settings_set", {"key": "font_size", "value": 20})))
        return "saved"
    except st.SettingsError:
        pass
    finally:
        cs._replace = real
    return io.open(path, encoding="utf-8").read() == old, os.path.exists(path + ".tmp")


S.case("f-atomic", "pkg 19: a failed save keeps the old file, no temp file", (True, False))(_atomic)
S.case("f-shipped-read-only", "pkg 19: the shipped settings folder is never written", "refused")(
    lambda: _refused(lambda: st.save(app(), os.path.join(os.path.dirname(st.DEFAULT_PROFILES), "x.json"))))


def _refused(fn):
    try:
        fn()
    except st.SettingsError:
        return "refused"
    return "saved"


S.case("f-export-import", "pkg 19: settings_export -> text -> settings_import gives the same values", "en")(
    lambda: st.get(do(app(), "settings_import", text=do(run(app(), ("settings_set", {"key": "language", "value": "en"})),
                                                         "settings_export").info["text"]).state, "language"))


# ---------------------------------------------------------------- rule and character settings
def hero(**kw):
    base = dict(hp_rolls=(8,), hp_current=5, abilities={a: Ability(base=14 if a == "str" else 10) for a in ABILITIES},
                statuses=(Status("Rage", sid="rage", charges=Pool(2, 3), active=False, duration="infinite"),),
                pools=(ResourcePool("ki", "Ki", 3, 1),))
    base.update(kw)
    return Character(**base)


def _rules():
    r = dispatch(hero(), "set_rule_setting", key="iterative_step", value=-3)
    c = r.state
    return c.rules_settings.iterative_step, c.log[-1].kind, sv.get(app(), c, "iterative_step").changed, \
        dispatch(c, "reset_rule_setting", key="iterative_step").state.rules_settings.iterative_step


S.case("c-rule-set", "pkg 19: set_rule_setting iterative_step -3 (journal kind settings, changed); reset -> -5",
       (-3, "settings", True, -5))(_rules)
S.case("c-rule-range", "pkg 19: iterative_step +1 is out of range (max 0)", "out_of_range")(
    lambda: creason(hero(), "set_rule_setting", key="iterative_step", value=1))
S.case("c-rule-list", "pkg 19: damage_order as a list of the allowed steps; 'zzz' not allowed", (("flat", "percent", "modifier"), "not_allowed"))(
    lambda: (dispatch(hero(), "set_rule_setting", key="damage_order", value=["flat", "percent", "modifier"]).state.rules_settings.damage_order,
             creason(hero(), "set_rule_setting", key="damage_order", value=["zzz"])))
S.case("c-char-setting", "pkg 19: char_portrait stored in the character file; survives save / load; reset -> gone",
       ("img1", "img1", ""))(
    lambda: (lambda c: (c.char_settings["char_portrait"], __import__("wp.storage.character_io", fromlist=["x"]).loads(
        __import__("wp.storage.character_io", fromlist=["x"]).dumps(c)).char_settings["char_portrait"],
        sv.get(app(), dispatch(c, "reset_char_setting", key="char_portrait").state, "char_portrait").value))(
        dispatch(hero(), "set_char_setting", key="char_portrait", value="img1").state))
S.case("c-group-reset", "pkg 19: reset_settings_group rules brings ignore_pain back to False", False)(
    lambda: dispatch(dispatch(hero(), "set_rule_setting", key="ignore_pain", value=True).state, "reset_settings_group",
                     group="rules").state.rules_settings.ignore_pain)


# ---------------------------------------------------------------- profiles
def _profiles():
    a = run(app(), ("profile_create", {"mode": "classic", "name": "Combat"}))
    b = run(a, ("profile_duplicate", {"mode": "classic", "pid": "combat"}), ("profile_set_active", {"mode": "classic", "pid": "combat"}))
    return tuple(p["id"] for p in b.profiles["classic"]), b.active["classic"], \
        reason(b, "profile_delete", mode="classic", pid="combat"), \
        tuple(p["id"] for p in run(b, ("profile_delete", {"mode": "classic", "pid": "combat_1"})).profiles["classic"])


S.case("p-create-dup-switch-delete", "pkg 19: create Combat, duplicate -> combat_1, switch; deleting the active one "
       "refused (Q138); deleting the copy works", (("default", "combat", "combat_1"), "combat", "profile_active", ("default", "combat")))(_profiles)
S.case("p-last", "pkg 19: the last (and active) profile cannot be deleted", "profile_active")(
    lambda: reason(app(), "profile_delete", mode="lite", pid="default"))
S.case("p-lite-fields", "pkg 19: lite opacity 150 out of range; 60 with click-through and its own hotkey ok",
       ("out_of_range", (60, True, "Ctrl+T")))(
    lambda: (reason(app(), "profile_set", mode="lite", pid="default", opacity=150),
             (lambda p: (p["opacity"], p["click_through"], p["click_through_hotkey"]))(st.profile(run(app(), (
                 "profile_set", {"mode": "lite", "pid": "default", "opacity": 60, "click_through": True,
                                 "click_through_hotkey": "Ctrl+T"})), "lite"))))


def _export():
    a = run(app(), ("profile_create", {"mode": "classic", "name": "Combat"}),
            ("layout_add", {"mode": "classic", "pid": "combat", "collection": "cells",
                            "item": {"label": "HP", "source": "resource:hp", "kind": "bar"}}))
    text = do(a, "profile_export", mode="classic", pid="combat").info["text"]
    b = do(a, "profile_import", mode="classic", text=text)
    new = st.profile(b.state, "classic", b.info["id"])
    return b.info["id"], new["cells"][0]["source"], reason(a, "profile_import", mode="lite", text=text)


S.case("p-export-import", "pkg 19: export a profile and import it back -> a new id with the same cells; into lite refused",
       ("combat_1", "resource:hp", "wrong_mode"))(_export)
S.case("p-cell-kind", "pkg 19: a cell kind 'pie' is not allowed", "not_allowed")(
    lambda: reason(app(), "layout_add", mode="classic", pid="default", collection="cells", item={"kind": "pie"}))


# ---------------------------------------------------------------- hotkeys
S.case("h-conflict", "pkg 19: Shift+Ctrl+W on a quick button = the app's Ctrl+Shift+W -> refused (Q139); lite show hotkey too",
       ("hotkey_conflict", "hotkey_conflict", "allowed"))(
    lambda: (reason(app(), "quick_add", button={"label": "Rest", "hotkey": "Shift+Ctrl+W", "action": {"command": "tick"}}),
             reason(app(), "profile_set", mode="lite", pid="default", show_hotkey="Ctrl+Shift+W"),
             reason(app(), "quick_add", button={"label": "Rest", "hotkey": "Ctrl+R", "action": {"command": "tick"}})))


# ---------------------------------------------------------------- cells against a character
S.case("l-resolve", "pkg 19: cells read HP 5/8, Str 14 (+2), Rage 2/3 inactive, Ki 1/3, training 1000; unknown -> warning",
       ({"current": 5, "max": 8}, {"score": 14, "mod": 2}, (False, 2, 3), {"current": 1, "max": 3}, {"value": 1000},
        (None, "unknown_source")))(
    lambda: (lay.resolve(hero(), "resource:hp")[0], lay.resolve(hero(), "ability:str")[0],
             (lambda r: (r["active"], r["charges"], r["charges_max"]))(lay.resolve(hero(), "status:rage")[0]),
             lay.resolve(hero(), "pool:ki")[0], lay.resolve(hero(), "value:training")[0], lay.resolve(hero(), "nope:x")))
RULES = [{"below": 3, "color": "#FF0000"}, {"below": 6, "color": "#FFFF00"}, {"above": 7, "color": "#00FF00"}]
S.case("l-color", "pkg 19: first matching rule: HP 2 red, 5 yellow, 8 green, 7 none", ("#FF0000", "#FFFF00", "#00FF00", None))(
    lambda: tuple(lay.cell_view(hero(hp_current=h), {"source": "resource:hp", "color_rules": RULES})[1] for h in (2, 5, 8, 7)))


def _macro():
    b = {"macro": [{"command": "spend_pool", "params": {"pid": "ki", "n": 1}},
                   {"command": "activate_status", "params": {"sid": "rage"}}]}
    c = lay.run_quick(hero(), b)
    return c.pools[0].current, c.statuses[0].active, c.statuses[0].charges.current


S.case("q-macro", "pkg 19: a macro of real commands: Ki 1 -> 0, Rage active, charges 2 -> 1", (0, True, 1))(_macro)


def _macro_refused():
    ch = hero()
    b = {"macro": [{"command": "activate_status", "params": {"sid": "rage"}},
                   {"command": "spend_pool", "params": {"pid": "ki", "n": 5}}]}
    try:
        lay.run_quick(ch, b)
    except CommandError as e:
        return e.reason, e.params["step"], ch.statuses[0].active
    return "ran"


S.case("q-macro-refused", "pkg 19: a refused step stops the macro; the character is unchanged (Q141)",
       ("not_enough_need_have", 2, False))(_macro_refused)
S.case("q-needs-action", "pkg 19: a quick button needs an action or a macro", "action_needed")(
    lambda: reason(app(), "quick_add", button={"label": "X"}))


# ---------------------------------------------------------------- images
def png(name="icon.png", size=10):
    p = os.path.join(folder(), name)
    with open(p, "wb") as f:
        f.write(b"\x89PNG" + b"0" * (size - 4))
    return p


def _images():
    d = folder()
    a = run(app(), ("image_add", {"source": png(), "name": "Icon", "user_folder": d}),
            ("image_set_for", {"target_kind": "feat", "target_id": "power", "image_id": "icon"}))
    ok = img.image_of(a, "feat", "power", d)[0] == os.path.join(d, "images", "icon.png")
    os.remove(os.path.join(d, "images", "icon.png"))
    missing = img.image_of(a, "feat", "power", d)
    b = run(a, ("image_remove", {"image_id": "icon", "user_folder": d}),
            ("image_add", {"source": png(), "name": "Icon", "user_folder": d}))
    return ok, missing, b.images[0]["id"], dict(b.image_for), img.resolve(b, "icon", d)


S.case("i-registry", "pkg 19: add copies the file and resolves; a missing file -> placeholder + warning; removed id "
       "retired, a new Icon -> icon_1, references dropped", (True, ("placeholder", "image_missing"), "icon_1", {},
                                                              ("placeholder", "no_image")))(_images)
S.case("i-checks", "pkg 19: .exe refused; 2 KB over a 1 KB limit refused; an unknown target kind refused",
       ("bad_image_type", "image_too_big", "unknown_target"))(
    lambda: (reason(app(), "image_add", source=png("x.exe"), name="x", user_folder=folder()),
             reason(run(app(), ("settings_set", {"key": "image_max_kb", "value": 1})), "image_add", source=png(size=2048),
                    name="big", user_folder=folder()),
             reason(app(), "image_set_for", target_kind="planet", target_id="x", image_id="")))


def _image_save():
    d = folder()
    a = run(st.load(d), ("image_add", {"source": png(), "name": "Icon", "user_folder": d}))
    st.save(a)
    return st.load(d).images[0]["file"]


S.case("i-save", "pkg 19: the registry survives save / load", "images/icon.png")(_image_save)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
