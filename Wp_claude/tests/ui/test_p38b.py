"""Package 38 P4 in the window (offscreen; without PySide6 the suite is SKIPPED, exit 0): the "!" notes. The layout
editor adds a note on a block and on a tab, edits, moves and deletes one; the window shows a "!" mark with the text
as its tooltip and in an info box on click; a tab note shows only while its tab is open; marks survive a restart.
Shots notes_<theme>.png in the three themes.
Run: python Wp_claude/tests/ui/test_p38b.py"""
import os
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
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("test_p38b: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app.session import Session  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.ui.layout_editor import open_layout_editor  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_p38b")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_p38b_")
SHOTS = os.path.join(HERE, "..", "ui_shots")


def started(tag):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    s.new("Hero", Character())
    w.character_changed()
    QAPP.processEvents()
    return s, w


def add(ed, target, text):
    p = ed.notes
    p.choose_place(target)
    p.text.setText(text)
    return p.act("add")


def marks(w):
    return [(m.parentWidget() is w.blocks.get("combat" if m.tab else m.note["target"]), m.text(), m.toolTip(),
             m.isVisibleTo(m.parentWidget())) for m in w.note_marks]


def _editor():
    s, w = started("editor")
    ed = open_layout_editor(w)
    add(ed, "parameters", "Check Fort")
    add(ed, "tab:training", "Ask the GM about mana")
    QAPP.processEvents()
    on_combat = marks(w)
    w.blocks["tabs"].select("training")
    QAPP.processEvents()
    on_training = marks(w)
    ed.notes.select("note_1")
    ed.notes.text.setText("Check Fort and Will")
    ed.notes.act("save")
    ed.notes.choose_place("bottom_strip")
    ed.notes.act("move")
    ed.notes.select("note_2")
    ed.notes.act("delete")
    QAPP.processEvents()
    last = [(m.note["target"], m.toolTip()) for m in w.note_marks]
    bad = add(ed, "parameters", "   ")
    return on_combat, on_training, last, ed.notes.list.count(), bad.ok, ed.notes.message.text()


S.case("editor", "decision 8: add on a block and on a tab: two '!' marks (the tab one hidden until its tab opens); "
       "edit, move to the bottom strip, delete; an empty text is refused with a message",
       ([(True, "!", "Check Fort", True), (True, "!", "Ask the GM about mana", False)],
        [(True, "!", "Check Fort", True), (True, "!", "Ask the GM about mana", True)],
        [("bottom_strip", "Check Fort and Will")], 1, False, "a note needs its text"))(_editor)


def _click():
    s, w = started("click")
    s.settings("note_add", target="identity", text="Portrait later")
    QAPP.processEvents()
    w.messages.clear()
    w.note_marks[0].click()
    return list(w.messages)[-1:]


S.case("click", "decision 8: a click on '!' opens the text", ["Portrait later"])(_click)


def _restart():
    s, w = started("restart")
    s.settings("note_add", target="rerolls", text="Coin flip")
    s2 = Session(os.path.join(TMP, "restart", "characters"), os.path.join(TMP, "restart", "settings"))
    s2.new("Hero2", Character())
    w2 = MainWindow(s2, quiet=True, system_dark=True)
    QAPP.processEvents()
    return [(m.note["target"], m.toolTip()) for m in w2.note_marks]


S.case("restart", "decision 8: the note is back after a restart", [("rerolls", "Coin flip")])(_restart)


def _shots():
    out = []
    for theme in ("dark", "light", "grey_blue"):
        s, w = started("shot_" + theme)
        w.set_setting("theme", theme)
        s.settings("note_add", target="parameters", text="Check Fort")
        s.settings("note_add", target="combat", text="Use the reroll")
        QAPP.processEvents()
        path = os.path.join(SHOTS, "notes_%s.png" % theme)
        w.grab().save(path)
        out.append(os.path.getsize(path) > 0)
    return out


S.case("shots", "the window with two '!' notes in the three themes (the owner looks at them)", [True, True, True])(_shots)

if __name__ == "__main__":
    sys.exit(S.run())
