"""Package 21: themes as token data (validation, layers, active theme, QSS) and the panel registry (profiles check
panel ids). Expected values by hand. Run: python Wp_claude/tests/storage/test_themes_panels.py"""
import glob
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import ROOT, Suite  # noqa: E402

from wp.catalog import store as cs  # noqa: E402
from wp.commands import CommandError  # noqa: E402
from wp.panels import registry  # noqa: E402
from wp.settings import store as st  # noqa: E402
from wp.settings.settings_cmds import settings_dispatch as do  # noqa: E402
from wp.theme import qss, themes  # noqa: E402

S = Suite("test_themes_panels")
TMP = tempfile.mkdtemp(prefix="wp_thm_")


def layers():
    return themes.load_layers(tempfile.mkdtemp(dir=TMP))


def light():
    return json.loads(json.dumps(cs._plain(themes.shipped().find("light"))))


def reason(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


# ---------------------------------------------------------------- validation
S.case("v-shipped", "pkg 21: the shipped themes pass the schema and build a QSS (package 31: dark, light, grey_blue)",
       [None, None, None])(
    lambda: [themes.check(e) for e in themes.shipped().entries])


def broken(**change):
    t = light()
    t.pop("id")
    t["name"] = "Mine"
    for k, v in change.items():
        if k == "drop_hp":
            del t["colors"]["hp"]
        elif k == "color":
            t["colors"]["accent"] = v
        elif k == "font":
            t["fonts"]["base"] = v
    return t


S.case("v-refusals", "pkg 21: colour '#12345' bad; colors.hp missing; font size 0 bad",
       ("bad_color", "missing_token", "bad_size"))(
    lambda: (reason(lambda: themes.theme_add(layers(), broken(color="#12345"))),
             reason(lambda: themes.theme_add(layers(), broken(drop_hp=True))),
             reason(lambda: themes.theme_add(layers(), broken(font=0)))))

# ---------------------------------------------------------------- QSS
TEMPLATE = [{"selector": "QWidget", "declarations": [["color", "{text}"], ["font-size", "{font_base}px"]]},
            {"selector": "QLabel#hp", "declarations": [["color", "{hp}"]]}]
TOKENS = {"colors": {"text": "#111111", "hp": "#ff0000"}, "fonts": {"base": 12}}
S.case("q-output", "pkg 21: QSS from a hand-written token set",
       "QWidget {\n    color: #111111;\n    font-size: 12px;\n}\n\nQLabel#hp {\n    color: #ff0000;\n}\n")(
    lambda: qss.build(TOKENS, TEMPLATE))


def _missing():
    try:
        qss.build(TOKENS, [{"selector": "X", "declarations": [["color", "{nope}"]]}])
    except qss.ThemeError as e:
        return e.reason, e.params["token"]
    return "built"


S.case("q-missing-token", "pkg 21: a token the theme lacks -> missing_token", ("missing_token", "nope"))(_missing)
S.case("q-no-qt", "pkg 21: no PySide6 import anywhere in wp/", [])(
    lambda: [p for p in glob.glob(os.path.join(ROOT, "wp", "**", "*.py"), recursive=True) if any(ln.lstrip().startswith(("import PySide", "from PySide")) for ln in open(p, encoding="ascii"))])


# ---------------------------------------------------------------- layers, active theme
def _override():
    before = open(themes.SHIPPED, encoding="utf-8").read()
    lay = themes.theme_edit(layers(), "light", colors={"accent": "#000000"})
    e = next(e for e, layer in cs.merged(lay) if e["id"] == "light")
    layer = next(layer for e, layer in cs.merged(lay) if e["id"] == "light")
    return e["colors"]["accent"], e["colors"]["text"], layer, open(themes.SHIPPED, encoding="utf-8").read() == before


S.case("l-override", "pkg 21: editing a shipped theme writes a user override (accent #000000, text kept); shipped file unchanged",
       ("#000000", "#1e1e1e", "override", True))(_override)
S.case("l-duplicate-remove", "pkg 21: duplicate Dark -> dark_1; removing the shipped dark hides it (tombstone)",
       ("dark_1", ["dark_1", "grey_blue", "light"]))(
    lambda: (lambda r: (r[1], sorted(e["id"] for e, _ in cs.merged(themes.theme_remove(r[0], "dark")))))(
        themes.theme_duplicate(layers(), "dark")))


def _active():
    lay = layers()
    app = themes.theme_set_active(st.AppSettings(), lay, "dark")
    gone = do(st.AppSettings(), "settings_set", key="theme", value="nope").state
    return st.get(app, "theme"), themes.active(gone, lay)["id"], reason(lambda: themes.theme_set_active(st.AppSettings(), lay, "nope"))


S.case("l-active", "pkg 21: set active dark; an unknown active id falls back to dark (owner, package 31: the default); "
       "set active unknown refused", ("dark", "dark", "not_found"))(_active)


def _round_trip():
    d = tempfile.mkdtemp(dir=TMP)
    lay, tid = themes.theme_add(themes.load_layers(d), broken())
    themes.save(lay, d)
    back = themes.load_layers(d)
    code = themes.theme_export(back, tid)
    lay2, tid2 = themes.theme_import(back, code)
    e1, e2 = back.user.find(tid), lay2.user.find(tid2)
    return tid, tid2, e1["colors"] == e2["colors"]


S.case("l-round-trip", "pkg 21: add Mine, save, load; export / import -> mine_1 with the same colours", ("mine", "mine_1", True))(_round_trip)

# ---------------------------------------------------------------- panels
S.case("p-registry", "pkg 21: 18 panels; lite panels resources, combat, attacks, statuses, log, notebook, settings",
       (18, ("resources", "combat", "attacks", "statuses", "log", "notebook", "settings")))(
    lambda: (len(registry.PANELS), tuple(p["id"] for p in registry.list_panels("lite"))))
S.case("p-undescribed", "pkg 21: sheet, spells, injuries, editor: id + title only, defaults filled (classic, resizable)",
       [("editor", ["classic"], True), ("injuries", ["classic"], True), ("sheet", ["classic"], True), ("spells", ["classic"], True)])(
    lambda: sorted((p["id"], p["modes"], p["resizable"]) for p in registry.PANELS.values() if not p["described"]))
S.case("p-default-profiles", "pkg 21: the shipped profiles name registry panels only (no warnings)", {})(
    lambda: registry.warnings(st.AppSettings()))


def add(mode, collection, item):
    return lambda: do(st.AppSettings(), "layout_add", mode=mode, pid="default", collection=collection, item=item)


S.case("p-refusals", "pkg 21: unknown panel refused; a classic-only panel in lite refused; a classic panel item needs a panel",
       ("unknown_panel", "panel_not_in_mode", "panel_needed", "allowed"))(
    lambda: (reason(add("classic", "panels", {"panel": "nope"})), reason(add("lite", "elements", {"kind": "bar", "panel": "maneuvers"})),
             reason(add("classic", "panels", {"dock": "left"})), reason(add("classic", "panels", {"panel": "maneuvers"}))))
S.case("p-edit-refused", "pkg 21: editing a panel item to an unknown panel is refused", "unknown_panel")(
    lambda: reason(lambda: do(st.AppSettings(), "layout_edit", mode="classic", pid="default", collection="panels",
                              item_id="log", panel="nope")))


def _load_warning():
    data = st.to_data(st.AppSettings())
    data["profiles"]["classic"][0]["panels"][0]["panel"] = "ghost"
    app = st.loads(json.dumps(data))
    return registry.warnings(app)


S.case("p-load-warning", "pkg 21: a stored profile with an unknown panel loads with a warning, not a refusal",
       {("classic", "default"): (("unknown_panel", "resources", "ghost"),)})(_load_warning)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
