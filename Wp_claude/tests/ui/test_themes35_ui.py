"""Package 35 P3 without a screen (offscreen; without PySide6 the suite is SKIPPED, exit 0): the theme editor (copy,
a colour changed LIVE, the shipped theme locked, reset, the contrast warning), the own background picture (none by
default; dimming 50 -> alpha 128; the readable overlay) and screenshots themes_*. Run:
python Wp_claude/tests/ui/test_themes35_ui.py"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
FONTS = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
if os.path.isdir(FONTS):
    os.environ.setdefault("QT_QPA_FONTDIR", FONTS)
try:
    from PySide6.QtGui import QColor, QImage
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("test_themes35_ui: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app.session import Session  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui import app as ua  # noqa: E402
from wp.ui.theme_editor import open_editor  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_themes35_ui")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_th35u_")
SHOTS = os.path.join(HERE, "..", "ui_shots")


def started(tag):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    ua.start_character(w)
    QAPP.processEvents()
    return s, w


def picture(tag):
    img = QImage(64, 40, QImage.Format_RGB32)
    img.fill(QColor("#336699"))
    path = os.path.join(TMP, tag + ".png")
    img.save(path, "PNG")
    return path


def _editor():
    s, w = started("editor")
    e = open_editor(w)
    locked = e.set_color("accent", "#ff00aa").reason, e.table.rowCount()
    e.copy()
    mine = s.setting("theme")
    e.set_color("accent", "#ff00aa")
    live = "#ff00aa" in w.qss
    e.set_color("text", "#777777")                       # on white: 4.48 < 4.5 (hand numbers in test_themes35)
    e.set_color("background", "#ffffff")
    e.set_color("surface", "#ffffff")
    warn = "low contrast" in e.contrast.text()
    shipped_dark = dict(themes.shipped().find("dark")["colors"])["accent"] != "#ff00aa"
    e.remove()
    return locked, mine != "dark", live, warn, shipped_dark, s.setting("theme")


S.case("t-editor", "owner 16: a shipped theme is locked (copy first), 56 token rows; copy -> an own theme made active; "
       "a colour changes LIVE (the window style has it); text #777777 on white warns (4.48 < 4.5, never refused); the "
       "shipped dark stays untouched; remove the own theme -> back to dark",
       (("shipped_theme", 56), True, True, True, True, "dark"))(_editor)


def _background():
    s, w = started("background")
    none = s.setting("background_image"), w.central.pixmap is None
    e = open_editor(w)
    e.add_picture(picture("bg"))
    w.set_setting("background_dim", 50)
    shown = w.central.pixmap is not None, w.central.alpha, "QFrame#block" in w.qss
    w.set_setting("background_readable", False)
    plain = "QFrame#block, QFrame#strip" in w.qss
    w.set_setting("background_image", "")
    return none, shown, plain, w.central.pixmap is None


S.case("t-background", "owner 16: no picture by default; an own picture with dimming 50 -> alpha 128 and the readable "
       "overlay behind the blocks; readable off -> no overlay; none again -> no picture",
       (("", True), (True, 128, True), False, True))(_background)


def _shots():
    s, w = started("shots")
    w.resize(1280, 800)
    w.show()
    os.makedirs(SHOTS, exist_ok=True)
    out = []
    for tid in themes.shipped_ids():
        w.choose_theme(tid)
        e = open_editor(w)
        e.show()
        QAPP.processEvents()
        path = os.path.join(SHOTS, "themes_%s.png" % tid)
        out.append(bool(e.grab().save(path, "PNG")) and os.path.getsize(path) > 0)
        e.close()
    e = open_editor(w)
    e.add_picture(picture("shot"))
    w.choose_theme("dark")
    QAPP.processEvents()
    path = os.path.join(SHOTS, "themes_background_dark.png")
    out.append(bool(w.grab().save(path, "PNG")) and os.path.getsize(path) > 0)
    w.close()
    return out


S.case("t-shots", "pkg 35 P3: screenshots themes_* (the editor in the three themes) and themes_background_dark",
       [True] * 4)(_shots)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
