"""The notes part of the layout editor (package 38, owner decision 8): add / edit the text / move / delete a "!" note.

A list of the notes of the active classic profile (place: text), a place chooser (every block of the profile and
every tab), a text field and the buttons Add, Save text, Move here, Delete. Every change is a settings command
(note_add / note_edit / note_move / note_remove); a refusal shows its text; nothing is saved from bad input.
"""
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QVBoxLayout, QWidget

from wp.app import ui_data
from wp.i18n import i18n

CLASSIC = "classic"
KEYS = ("add", "save", "move", "delete")


class NotesPanel(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor, self.win, self.session = editor, editor.win, editor.session
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.title = QLabel()
        lay.addWidget(self.title)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._sync)
        lay.addWidget(self.list)
        row = QHBoxLayout()
        self.place = QComboBox()
        self.text = QLineEdit()
        row.addWidget(self.place)
        row.addWidget(self.text, 1)
        self.buttons = {}
        for k in KEYS:
            b = QPushButton()
            b.setObjectName("small")
            b.clicked.connect(lambda _=False, k=k: self.act(k))
            self.buttons[k] = b
            row.addWidget(b)
        lay.addLayout(row)
        self.message = QLabel()
        self.message.setObjectName("message")
        self.message.setWordWrap(True)
        lay.addWidget(self.message)
        self.items = ()

    def tr(self, key, **params):
        return self.win.tr(key, **params)

    def profile(self):
        return self.session.profile(CLASSIC)

    def place_name(self, target):
        if target.startswith(ui_data.NOTE_TAB):
            return self.tr("notes.on_tab", tab=self.tr("tab." + target[len(ui_data.NOTE_TAB):]))
        item = next((i for i in self.profile().get("panels", ()) if i.get("id", i.get("panel")) == target), {})
        return self.tr("panel." + item.get("panel", target))

    def reload(self, keep=None):
        tr = self.tr
        self.title.setText(tr("notes.title"))
        self.text.setPlaceholderText(tr("notes.text"))
        for k, b in self.buttons.items():
            b.setText(tr("notes." + k))
        current = self.place.currentData()
        self.place.clear()
        for t in ui_data.note_targets(self.session):
            self.place.addItem(self.place_name(t), t)
        if current is not None and self.place.findData(current) >= 0:
            self.place.setCurrentIndex(self.place.findData(current))
        self.items = ui_data.notes(self.session)
        self.list.clear()
        for n in self.items:
            self.list.addItem("%s: %s" % (self.place_name(n["target"]), n["text"]))
        ids = [n["id"] for n in self.items]
        if keep in ids:
            self.list.setCurrentRow(ids.index(keep))

    def current(self):
        r = self.list.currentRow()
        return self.items[r] if 0 <= r < len(self.items) else None

    def select(self, nid):
        ids = [n["id"] for n in self.items]
        self.list.setCurrentRow(ids.index(nid))

    def choose_place(self, target):
        self.place.setCurrentIndex(self.place.findData(target))

    def _sync(self, _row=None):
        n = self.current()
        if n is not None:
            self.text.setText(n["text"])
            self.choose_place(n["target"])

    def act(self, key):
        pid, n = self.profile().get("id"), self.current()
        if key == "add":
            r = self.session.settings("note_add", pid=pid, target=self.place.currentData() or "",
                                      text=self.text.text())
        elif n is None:
            return None
        elif key == "save":
            r = self.session.settings("note_edit", pid=pid, nid=n["id"], text=self.text.text())
        elif key == "move":
            r = self.session.settings("note_move", pid=pid, nid=n["id"], target=self.place.currentData() or "")
        else:
            r = self.session.settings("note_remove", pid=pid, nid=n["id"])
        self.message.setText("" if r.ok else i18n.text_for(r, self.win.lang()))
        keep = dict(r.info).get("id") if r.ok and key != "delete" else None
        self.reload(keep)
        return r
