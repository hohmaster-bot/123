"""The "!" marks of the layout notes in the window (package 38, owner decision 8; wp/settings/notes.py).

apply(win): every note of the active classic profile becomes a small "!" button (object name note_mark: theme
tokens) in the top right corner of its block; a note on a tab ("tab:<id>") sits on the combat block and shows only
while that tab is open (sync). The text is the tooltip (hover) and opens in an info box on click. Marks are rebuilt
after every settings change; they never change the layout.
"""
from PySide6.QtWidgets import QToolButton

from wp.app import ui_data

COMBAT = "combat"
MARK = "!"


class NoteMark(QToolButton):
    def __init__(self, parent, win, note):
        super().__init__(parent)
        self.win, self.note = win, dict(note)
        self.setObjectName("note_mark")
        self.setText(MARK)
        self.setToolTip(self.note.get("text", ""))
        self.clicked.connect(self.open_text)

    def open_text(self):
        return self.win.info(self.win.tr("notes.title"), self.note.get("text", ""))


def _place(marks):
    for i, m in enumerate(marks):
        p = m.parentWidget()
        m.adjustSize()
        m.move(max(0, p.width() - m.width() * (i + 1)), 0)
        m.raise_()


def clear(win):
    for m in getattr(win, "note_marks", ()):
        m.hide()
        m.setParent(None)
        m.deleteLater()
    win.note_marks = []


def apply(win):
    clear(win)
    by_parent = {}
    tab = ui_data.NOTE_TAB
    for n in ui_data.notes(win.session):
        target = n.get("target", "")
        bid = COMBAT if target.startswith(tab) else target
        block = win.blocks.get(bid)
        if block is None:
            continue
        m = NoteMark(block, win, n)
        m.tab = target[len(tab):] if target.startswith(tab) else None
        win.note_marks.append(m)
        by_parent.setdefault(bid, []).append(m)
    sync(win)
    for marks in by_parent.values():
        _place(marks)


def sync(win):
    """A tab note is visible only while its tab is open in the combat block."""
    combat = win.blocks.get(COMBAT)
    now = getattr(combat, "tab", None)
    for m in getattr(win, "note_marks", ()):
        m.setVisible(m.tab is None or m.tab == now)


def place_all(win):
    groups = {}
    for m in getattr(win, "note_marks", ()):
        groups.setdefault(id(m.parentWidget()), []).append(m)
    for marks in groups.values():
        _place([m for m in marks if m.isVisibleTo(m.parentWidget())] or marks)
