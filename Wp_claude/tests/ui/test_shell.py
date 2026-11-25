"""Package 32: the Classic window shell (wp/ui) without a screen (QT_QPA_PLATFORM=offscreen). Plain Suite + one
QApplication; without PySide6 the suite is SKIPPED with a message (exit 0). Numbers by hand from wp/ui/data/demo.json:
experience 1450 of the goal 1000 (package 33: the level-up cost) -> 100 % (capped); level 1 + one level_up = 2.
Screenshots of each shipped theme go to Wp_claude/tests/ui_shots/<theme>.png (the owner checks the look by hand).
Run: python Wp_claude/tests/ui/test_shell.py"""
import ast
import glob
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import ROOT, Suite  # noqa: E402

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
FONTS = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
if os.path.isdir(FONTS):
    os.environ.setdefault("QT_QPA_FONTDIR", FONTS)
try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("test_shell: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app.session import Session  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui import app as ua  # noqa: E402
from wp.ui.shell_data import SHELL  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_shell")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_shell_")
SHOTS = os.path.join(HERE, "..", "ui_shots")
AC_RU = "\u041a\u043b\u0430\u0441\u0441 \u0431\u0440\u043e\u043d\u0438"      # "Klass broni" in ru.json


def dirs(tag):
    return os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings")


def window(tag, **kw):
    s = Session(*dirs(tag))
    w = MainWindow(s, quiet=True, **kw)
    return s, w


def started(tag, lang=None):
    s, w = window(tag)
    if lang:
        w.set_setting("language", lang)
    ua.start_character(w)
    QAPP.processEvents()
    return s, w


# ---------------------------------------------------------------- opens with the demo, six regions
def _opens():
    s, w = started("open")
    return s.name, s.list_characters(), "Demo" in w.windowTitle(), w.messages


S.case("s-opens", "pkg 32: the first start builds and opens the demo character, no message", ("Demo", ("Demo",), True, []))(
    _opens)


def _regions():
    s, w = started("regions")
    by = {}
    for bid, dock in w.region_of.items():
        by.setdefault(dock, []).append(bid)
    return {k: sorted(v) for k, v in by.items()}, w.rows["center"][0], sorted(w.rows)


S.case("s-regions", "Classic v2: experience strip on top, left = identity + resources, middle = AC and parameters on one "
       "row then statuses / favourites / reminders, right = tabs + combat, bottom strip",
       ({"top": ["experience_strip"], "left": ["identity", "resources"],
         "center": ["ac_block", "favorites", "parameters", "reminders", "statuses"], "right": ["combat", "tabs"],
         "bottom": ["bottom_strip"]}, ["ac_block", "parameters"], ["center", "left", "right"]))(_regions)


def _sizes():
    s, w = started("sizes")
    b = w.blocks
    return ((b["ac_block"].sizeHint().width(), b["ac_block"].sizeHint().height()), b["ac_block"].width(),
            b["experience_strip"].height(), b["identity"].height())


S.case("s-sizes", "pkg 32: blocks keep the saved sizes of the default profile (AC 330 x 300, strip height 56, identity "
       "height 170)", ((330, 300), 330, 56, 170))(_sizes)


# ---------------------------------------------------------------- real data: experience strip, identity
def _xp():
    s, w = started("xp", "en")
    x = w.blocks["experience_strip"]
    return x.bar.value(), x.total.text(), x.goal.text(), x.title.text()


S.case("s-xp", "pkg 32 / 33: the experience strip shows the demo numbers: 1450 of the goal 1000 -> 100 %, 1450 xp",
       (100, "1450 xp", "to next level: 1000", "Experience"))(_xp)


def _identity():
    s, w = started("identity", "en")
    i = w.blocks["identity"]
    return i.name.text(), i.klass.text(), i.level.text()


S.case("s-identity", "pkg 32: the identity block: name, class and level from the sheet view",
       ("Demo", "Sample fighter", "Level 2"))(_identity)


def _command():
    s, w = started("command", "en")
    before = {k: b.refreshed for k, b in w.blocks.items()}
    r1 = s.dispatch("level_up", hp_roll=5)
    level = w.blocks["identity"].level.text()
    mid = {k: b.refreshed for k, b in w.blocks.items()}
    r2 = s.dispatch("add_experience", amount=50)
    after = {k: b.refreshed for k, b in w.blocks.items()}
    return (r1.ok, level, sorted(k for k in mid if mid[k] > before[k]) == sorted(w.blocks),
            sorted(k for k in after if after[k] > mid[k]), w.blocks["experience_strip"].bar.value())


S.case("s-command", "D25: level_up through the Session -> Level 3 (topics all: every block re-reads); "
       "add_experience 50 (topics training, sheet, log) refreshes only the blocks reading them (pkg 34: the combat tab reads sheet too); 1450 - 1000 + 50 = "
       "500 of 1000 = 50 %",
       (True, "Level 3", True, ["bottom_strip", "combat", "experience_strip", "identity", "parameters"], 50))(_command)


# ---------------------------------------------------------------- theme, language, scale (live)
def _theme():
    s, w = started("theme")
    dark = w.qss
    w.choose_theme("light")
    light = w.qss
    s2 = Session(*dirs("theme"))
    bg = themes.shipped().find("light")["colors"]["background"]
    return dark != light, "background-color: %s;" % bg in light, s.setting("theme"), s2.setting("theme"), \
        w.actions["theme.light"].isChecked()


S.case("s-theme", "owner: View > Theme light switches the style sheet live and saves the setting (a new Session reads "
       "light)", (True, True, "light", "light", True))(_theme)


def _follow():
    s, w = window("follow", system_dark=False)
    w.set_setting("theme_follow_system", True)
    light_bg = themes.shipped().find("light")["colors"]["background"]
    on = "background-color: %s;" % light_bg in w.qss
    w._system_dark = True
    w.apply_settings()
    dark_bg = themes.shipped().find("dark")["colors"]["background"]
    return on, "background-color: %s;" % dark_bg in w.qss


S.case("s-follow", "owner: follow the system: a light system -> the light theme, a dark one -> dark", (True, True))(
    _follow)


def _language():
    s, w = started("lang")
    ru = w.blocks["ac_block"].title.text()
    w.set_setting("language", "en")
    en = w.blocks["ac_block"].title.text(), w.menus["view"].title()
    return ru, en


S.case("s-language", "D4: RU / EN switch live: the AC block title and the View menu", (AC_RU, ("Armour class", "View")))(
    _language)


def _scale():
    s, w = started("scale")
    w.set_setting("ui_scale", 1.5)
    return "font-size: 18px;" in w.qss, s.setting("ui_scale"), w.actions["scale.1.5"].isChecked()


S.case("s-scale", "pkg 32: scale 150 %: dark base font 12 -> 18 px in the sheet; the setting saved; the menu item checked",
       (True, 1.5, True))(_scale)


# ---------------------------------------------------------------- one-time hint, geometry
def _hint():
    s, w = started("hint")
    first = not w.hint.isHidden()
    w.hint.button.click()
    gone = w.hint.isHidden()
    s2, w2 = window("hint")
    again = not w2.hint.isHidden()
    w2.session_settings("hints_reset")
    return first, gone, again, not w2.hint.isHidden(), tuple(s2.setting("hints_seen"))


S.case("s-hint", "owner: the first-run hint shows once; Understood hides it, also in a new window; Show hints again "
       "brings it back", (True, True, False, True, ()))(_hint)


def _geometry():
    s, w = started("geo")
    w.setGeometry(50, 60, 1000, 700)
    w.close()
    s2, w2 = window("geo")
    g = w2.geometry()
    return (g.x(), g.y(), g.width(), g.height()), tuple(s2.setting("window_classic"))


S.case("s-geometry", "pkg 32: closing saves the window geometry, a reopen restores it",
       ((50, 60, 1000, 700), (50, 60, 1000, 700)))(_geometry)


# ---------------------------------------------------------------- files: corrupt file, save as
def _corrupt():
    s, w = started("corrupt", "en")
    chars = dirs("corrupt")[0]
    with open(os.path.join(chars, "Broken.json"), "w", encoding="utf-8") as f:
        f.write("{ not json")
    ok = w.files.open_name("Broken")
    return ok, s.name, w.messages


S.case("s-corrupt", "pkg 32: a damaged file shows the refusal text (no backup to offer), the open character stays",
       (False, "Demo", ["the file of Broken is damaged"]))(_corrupt)


def _save_as():
    s, w = started("saveas")
    chars = dirs("saveas")[0]
    inside = w.files.save_as_path(os.path.join(chars, "Copy.json"))
    out = os.path.join(TMP, "export_copy.json")
    outside = w.files.save_as_path(out)
    return inside, s.name, sorted(s.list_characters()), outside, os.path.exists(out), s.setting("last_character")


S.case("s-save-as", "pkg 32: Save as into the characters folder = a new character (opened); elsewhere = an exported "
       "copy", (True, "Copy", ["Copy", "Demo"], True, True, "Copy"))(_save_as)


def _restart():
    s, w = started("restart")
    w.files.save_as_path(os.path.join(dirs("restart")[0], "Second.json"))
    w.close()
    s2, w2 = started("restart")
    return s2.name


S.case("s-last", "pkg 32: a new start opens the last character", "Second")(_restart)
S.case("s-data-dirs", "pkg 32: run_wp.py keeps characters and settings in <home>/WipeFinder; --data DIR moves both",
       ((os.path.join("H", "WipeFinder", "characters"), os.path.join("H", "WipeFinder", "settings")),
        (os.path.join("D", "characters"), os.path.join("D", "settings"))))(
    lambda: (ua.data_dirs(["run_wp.py"], home="H"), ua.data_dirs(["run_wp.py", "--data", "D"], home="H")))


# ---------------------------------------------------------------- D25: the UI talks only to the Session
FORBIDDEN = ("wp.core", "wp.model", "wp.commands", "wp.storage", "wp.settings", "wp.catalog", "wp.rules_data")


def _imports():
    bad = []
    for p in sorted(glob.glob(os.path.join(ROOT, "wp", "ui", "*.py"))):
        for node in ast.walk(ast.parse(open(p, encoding="ascii").read())):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                [node.module or ""] if isinstance(node, ast.ImportFrom) else []
            bad += ["%s: %s" % (os.path.basename(p), n) for n in names if n.startswith(FORBIDDEN)]
    return bad


S.case("s-only-session", "D25: wp/ui imports nothing of the core, model, commands, storage, settings, catalogs", [])(
    _imports)


# ---------------------------------------------------------------- screenshots for the owner
def _shots():
    s, w = started("shots")
    w.resize(1280, 800)
    w.show()
    os.makedirs(SHOTS, exist_ok=True)
    out = []
    for tid in themes.shipped_ids():
        w.choose_theme(tid)
        QAPP.processEvents()
        img = w.grab().scaledToWidth(int(SHELL["shot_width"]), Qt.SmoothTransformation)
        path = os.path.join(SHOTS, "%s.png" % tid)
        out.append(bool(img.save(path, "PNG")) and os.path.getsize(path) > 0)
    w.close()
    return out


S.case("s-shots", "pkg 32: a screenshot of each shipped theme in tests/ui_shots", [True, True, True])(_shots)

if __name__ == "__main__":
    code = S.run()
    shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
