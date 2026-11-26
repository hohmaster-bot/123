"""The Narrative tab (package 36 P1.4; RULES/narrative.md): quests (court quests show their court as the giver),
courts, stories and quirks of the notebook. A kind switch, a table (name, state, text; the full text on hover), and
the actions through existing commands: Add (add_note), Edit text (edit_entry), Close / reopen a quest (edit_entry
done), Burn / restore a quirk (burn_quirk), Remove (remove_entry). Read-only otherwise (D25).
"""
from PySide6.QtWidgets import QComboBox, QLineEdit

from wp.ui import tab_logic as tl
from wp.ui.tab_pages import Page

KINDS = ("quest", "court", "story", "quirk")
COLLECTION = {"quest": "quests", "court": "courts", "story": "stories", "quirk": "quirks"}
TEXT_FIELD = {"quest": "text", "court": "note", "story": "text", "quirk": "text"}


class NarrativePage(Page):
    TAB = "narrative"
    COLS = ("name", "state", "text")
    ACTIONS = ("add", "edit", "close", "remove")
    NEEDS_ROW = False

    def __init__(self, block):
        super().__init__(block)
        self.kind = QComboBox()
        for k in KINDS:
            self.kind.addItem(k, k)
        self.kind.currentIndexChanged.connect(lambda _=0: self._show())
        self.name_edit, self.text_edit = QLineEdit(), QLineEdit()
        self.extra.addWidget(self.kind)
        self.extra.addWidget(self.name_edit)
        self.extra.addWidget(self.text_edit, 1)

    def current_kind(self):
        return self.kind.currentData() or KINDS[0]

    def show_data(self, tr, s):
        for i, k in enumerate(KINDS):
            self.kind.setItemText(i, tr("tabs_page.narrative.kind." + k))
        self.name_edit.setPlaceholderText(tr("tabs_page.narrative.name"))
        self.text_edit.setPlaceholderText(tr("tabs_page.narrative.text"))
        kind = self.current_kind()
        rows = tl.narrative_rows(s.character, kind)
        self.summary.setText(tr("tabs_page.narrative.summary", n=len(rows)))
        texts = [(name, tr("tabs_page.narrative.state." + state) if state else "", text)
                 for _oid, name, state, text in rows]
        self.fill(rows, texts)
        for r, (_oid, _name, _state, text) in enumerate(rows):
            for c in range(self.table.columnCount()):
                self.table.item(r, c).setToolTip(text)
        self.buttons["close"].setText(tr("tabs_page.narrative.close." + kind))
        self.buttons["close"].setEnabled(bool(rows) and kind in ("quest", "quirk"))
        for key in ("edit", "remove"):
            self.buttons[key].setEnabled(bool(rows))

    def act(self, key):
        kind = self.current_kind()
        if key == "add":
            r = self.run("add_note", kind=kind, name=self.name_edit.text().strip(),
                         **{TEXT_FIELD[kind]: self.text_edit.text().strip()})
            if r.ok:
                self.name_edit.clear()
                self.text_edit.clear()
            return r
        row = self.selected()
        if row is None:
            return None
        oid, _name, state, _text = row
        if key == "edit":
            return self.run("edit_entry", collection=COLLECTION[kind], oid=oid,
                            **{TEXT_FIELD[kind]: self.text_edit.text().strip()})
        if key == "remove":
            return self.run("remove_entry", collection=COLLECTION[kind], oid=oid)
        if kind == "quest":
            return self.run("edit_entry", collection="quests", oid=oid, done=state != "done")
        if kind == "quirk":
            return self.run("burn_quirk", kid=oid, burned=state != "burned")
        return None
