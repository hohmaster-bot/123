"""The Journal tab of the right column (package 35 P2; UI_WISHES "Classic screen v2" points 9, 10; D29).

Lines from the Session: the short mode shows the lines in memory (journal_short_max), the full mode the whole journal
with the archive (Session.full_log); newest first; a filter by kind (the journal kinds) and by text; Undo / Redo
through the Session stack (enabled by can_undo / can_redo); the mode switch short / full (the app setting
journal_mode, a settings command); a note field: the command journal_note (a journal line with the player's text).
Read-only otherwise: nothing else changes the character (D25).
"""
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLineEdit, QListWidget, QPushButton, QVBoxLayout, QWidget

from wp.app import ui_data
from wp.ui import strip_logic as sl

MODES = ("short", "full")


class JournalPage(QWidget):
    def __init__(self, block):
        super().__init__()
        self.block, self.session, self._tr = block, None, None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        top = QHBoxLayout()
        self.kind = QComboBox()
        self.kind.currentIndexChanged.connect(lambda _=0: self._show())
        self.text = QLineEdit()
        self.text.textChanged.connect(lambda _="": self._show())
        self.mode = QComboBox()
        self.mode.activated.connect(self.set_mode)
        top.addWidget(self.kind)
        top.addWidget(self.text, 1)
        top.addWidget(self.mode)
        lay.addLayout(top)
        buttons = QHBoxLayout()
        self.undo_button, self.redo_button = QPushButton(), QPushButton()
        for b, fn in ((self.undo_button, self.undo), (self.redo_button, self.redo)):
            b.setObjectName("small")
            b.clicked.connect(fn)
            buttons.addWidget(b)
        buttons.addStretch(1)
        lay.addLayout(buttons)
        self.list = QListWidget()
        lay.addWidget(self.list, 1)
        note = QHBoxLayout()
        self.note = QLineEdit()
        self.note_button = QPushButton()
        self.note_button.setObjectName("small")
        self.note_button.clicked.connect(lambda: self.add_note(self.note.text()))
        note.addWidget(self.note, 1)
        note.addWidget(self.note_button)
        lay.addLayout(note)
        self.kinds = ("",) + ui_data.journal_kinds()
        for _ in self.kinds:
            self.kind.addItem("")
        for _ in MODES:
            self.mode.addItem("")
        self.lines = []

    def retranslate(self, tr):
        self._tr = tr
        for i, k in enumerate(self.kinds):
            self.kind.setItemText(i, tr("journal.kind." + (k or "all")))
        for i, m in enumerate(MODES):
            self.mode.setItemText(i, tr("journal.mode." + m))
        self.text.setPlaceholderText(tr("journal.filter"))
        self.undo_button.setText(tr("journal.undo"))
        self.redo_button.setText(tr("journal.redo"))
        self.note.setPlaceholderText(tr("journal.note"))
        self.note_button.setText(tr("journal.add_note"))
        self._show()

    def refresh(self, session):
        self.session = session
        self._show()

    def source(self):
        s = self.session
        if s is None or s.character is None:
            return ()
        if s.setting("journal_mode") == MODES[1]:
            return s.full_log()
        return s.journal_view(count=int(s.setting("journal_short_max")))

    def _show(self):
        if self._tr is None or self.session is None:
            return
        s = self.session
        self.mode.setCurrentIndex(MODES.index(s.setting("journal_mode")))
        self.undo_button.setEnabled(s.can_undo())
        self.redo_button.setEnabled(s.can_redo())
        self.lines = sl.journal_lines(self.source(), self.kinds[max(0, self.kind.currentIndex())], self.text.text())
        self.list.clear()
        for e in self.lines:
            self.list.addItem("%s  [%s]  %s" % (e.at or "-", self._tr("journal.kind." + e.kind), sl.line_text(e)))

    # ------------------------------------------------------------ actions (Session only)
    def set_mode(self, index):
        return self.block.win.set_setting("journal_mode", MODES[index]) if self.block.win is not None else None

    def undo(self):
        return self.block.step(self.session.undo())

    def redo(self):
        return self.block.step(self.session.redo())

    def add_note(self, text):
        r = self.block.run("journal_note", text=str(text))
        if r.ok:
            self.note.clear()
        return r
