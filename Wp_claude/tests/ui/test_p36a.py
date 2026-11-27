"""Package 36 P1 without a screen (offscreen; without PySide6 the suite is SKIPPED, exit 0): the top menus Settings
and Catalog (own windows; their tabs are gone), the Narrative tab, the drive quest text, the font / scale fit (no block
overlaps another and every block fits its content after three changes in a row). Shots fonts_before / fonts_after,
narrative_*. Run: python Wp_claude/tests/ui/test_p36a.py"""
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
    from PySide6.QtCore import QPoint, QRect
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("test_p36a: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app.session import Session  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui import app as ua  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_p36a")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_p36a_")
SHOTS = os.path.join(HERE, "..", "ui_shots")


def started(tag):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    ua.start_character(w)
    QAPP.processEvents()
    return s, w


def _menus():
    s, w = started("menus")
    tabs = w.blocks["tabs"].tabs
    titles = [a.text() for a in w.menuBar().actions()]
    w.actions["top.settings"].trigger()
    w.actions["top.catalog"].trigger()
    st, ca = w.page_windows["settings"], w.page_windows["catalogs"]
    st.page.set("font_size", 13)                          # the settings page works in its own window
    ca.page.kind.setCurrentIndex(ca.page.kind.findData("feats"))
    return ("settings" in tabs, "catalogs" in tabs), titles, s.setting("font_size"), ca.page.table.rowCount()


S.case("m-menus", "owner P1.3: Settings and Catalog are top menus next to View and Help; their tabs are gone; the "
       "Settings window changes a setting (font 13); the Catalog window lists the 5 shipped feats",
       ((False, False), ["Character", "View", "Settings", "Catalog", "Help"], 13, 5))(_menus)


def _narrative():
    s, w = started("narrative")
    w.blocks["tabs"].select("narrative")
    p = w.blocks["combat"].pages["narrative"]
    p.kind.setCurrentIndex(p.kind.findData("court"))
    p.name_edit.setText("Court of Ash")
    p.act("add")
    cid = s.character.courts[0].cid
    s.dispatch("add_note", kind="quest", name="Find the bell", text="North tower", giver=cid)
    p.kind.setCurrentIndex(p.kind.findData("quest"))
    first = [p.table.item(0, c).text() for c in range(3)], p.table.item(0, 0).toolTip()
    p.select(0)
    p.act("close")
    closed = p.table.item(0, 1).text()
    p.select(0)
    p.text_edit.setText("South tower")
    p.act("edit")
    return first, closed, s.character.quests[0].text


S.case("n-tab", "owner P1.4: a court and its quest (the court named as the giver; the text on hover); Close -> done; "
       "Set the text -> South tower", ((["Find the bell (Court of Ash)", "open", "North tower"], "North tower"),
                                       "done", "South tower"))(_narrative)


def _drive_quest():
    s, w = started("drives")
    s.dispatch("add_drive", name="Growth", level=3)
    did = s.character.drives[0].did
    s.dispatch("set_drive_quest", did=did, quest="Plant the grove", state="taken")
    w.blocks["tabs"].select("drives")
    p = w.blocks["combat"].pages["drives"]
    col = p.COLS.index("quest")
    p.cell_clicked(0, col)
    return p.table.item(0, col).toolTip(), w.messages[-1]


S.case("d-quest", "owner P1.4: the Drives tab shows the drive's quest text (hover, and a click on the quest state)",
       ("Plant the grove", "Plant the grove"))(_drive_quest)


def _rects(w):
    out = {}
    for k, b in w.blocks.items():
        if b.isVisible():
            out[k] = QRect(b.mapTo(w.central, QPoint(0, 0)), b.size())
    return out


def _problems(w):
    r = _rects(w)
    keys = sorted(r)
    bad = [(a, b) for i, a in enumerate(keys) for b in keys[i + 1:] if r[a].intersects(r[b])]
    bad += [(k, "outside") for k, q in r.items() if not w.central.rect().contains(q)]
    for k, b in w.blocks.items():
        need = b.layout().minimumSize()
        if b.isVisible() and (need.width() > b.width() or need.height() > b.height()):
            bad.append((k, "content"))
    return bad


def _fonts():
    s, w = started("fonts")
    w.resize(1280, 800)
    w.show()
    QAPP.processEvents()
    QAPP.processEvents()
    os.makedirs(SHOTS, exist_ok=True)
    w.grab().save(os.path.join(SHOTS, "fonts_before.png"), "PNG")
    out = [_problems(w)]
    for family, size, scale in (("Arial", 16, 1.0), ("Times New Roman", 20, 1.25), ("Segoe UI", 12, 1.0)):
        w.set_setting("font_family", family)
        w.set_setting("font_size", size)
        w.set_setting("ui_scale", scale)
        QAPP.processEvents()
        QAPP.processEvents()
        out.append(_problems(w))
    w.set_setting("font_size", 20)
    QAPP.processEvents()
    QAPP.processEvents()
    ok = w.grab().save(os.path.join(SHOTS, "fonts_after.png"), "PNG")
    w.close()
    return out, ok


S.case("f-fit", "owner P1.5: before and after three font / scale changes in a row no block overlaps another, every "
       "block is inside the window area and fits its content; shots fonts_before / fonts_after",
       ([[], [], [], []], True))(_fonts)


def _shots():
    s, w = started("shots")
    s.dispatch("add_note", kind="quest", name="Find the bell", text="North tower")
    w.resize(1280, 800)
    w.show()
    out = []
    for tid in themes.shipped_ids():
        w.choose_theme(tid)
        w.blocks["tabs"].select("narrative")
        QAPP.processEvents()
        path = os.path.join(SHOTS, "narrative_%s.png" % tid)
        out.append(bool(w.blocks["combat"].grab().save(path, "PNG")))
    w.close()
    return out


S.case("s-shots", "pkg 36 P1: screenshots narrative_* in the three shipped themes", [True] * 3)(_shots)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
