"""The bottom strip of the Classic window (package 35 P2, Phase 5 step 6; UI_WISHES "Classic screen v2" point 10).

Full width (the profile region "bottom"): OT, Pain, Morale (only while the combat flag is on), Speed, Encumbrance
("X of max", the category light / load / overload and the limits). Every cell opens the Sources dialog of its number
(read-only, or editable in the editor mode where the number has an effect target: morale, speed, load). An optional
second strip comes from the profile field "strips" (empty by default); "+ strip" adds it (data "second_strip"),
"- strip" removes it: profile_set, a settings command. The "Journal" button opens the Journal tab of the right column.
Reads only views (strip_logic); never changes the character itself (D25).
"""
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout

from wp.ui import strip_logic as sl
from wp.ui.blocks import Block
from wp.ui.screen_blocks import SB, Cell, _repolish
from wp.ui.sources_dialog import open_sources

CLASSIC = "classic"


class BottomStrip(Block):
    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell)
        self.rows_box = QVBoxLayout()
        self.box.addLayout(self.rows_box, 1)
        side = QVBoxLayout()
        self.journal_button = QPushButton()
        self.journal_button.setObjectName("small")
        self.journal_button.clicked.connect(self.open_journal)
        self.strip_button = QPushButton()
        self.strip_button.setObjectName("small")
        self.strip_button.clicked.connect(self.toggle_strip)
        side.addWidget(self.journal_button)
        side.addWidget(self.strip_button)
        self.box.addLayout(side)
        self.reads = tuple(self.reads) + ("resources", "combat", "sheet", "items")
        self.cells, self.layout_rows, self.session, self._tr, self.data = {}, [], None, None, None
        self.row_height = self.saved.height()

    # ------------------------------------------------------------ build the rows of cells
    def _build(self, rows):
        if rows == self.layout_rows:
            return
        while self.rows_box.count():
            it = self.rows_box.takeAt(0)
            lay = it.layout()
            while lay is not None and lay.count():
                w = lay.takeAt(0).widget()
                if w is not None:
                    w.hide()
                    w.setParent(None)
                    w.deleteLater()
        self.cells = {}
        for r, row in enumerate(rows):
            line = QHBoxLayout()
            for nid in row:
                c = Cell(nid, self.open_sources)
                self.cells[(r, nid)] = c
                line.addWidget(c, 1)
            self.rows_box.addLayout(line)
        self.layout_rows = [list(r) for r in rows]
        self.setFixedHeight(self.row_height * max(1, len(rows)))

    def open_sources(self, nid):
        if self.win is None or self.session is None or self.session.character is None:
            return None
        return open_sources(self.win, sl.number_of(nid))

    def open_journal(self):
        if self.win is not None and "tabs" in self.win.blocks:
            return self.win.blocks["tabs"].select("journal")
        return None

    def toggle_strip(self):
        if self.win is None or self.session is None:
            return None
        prof = self.session.profile(CLASSIC)
        strips = [] if prof.get("strips") else [list(SB["second_strip"])]
        return self.win.session_settings("profile_set", mode=CLASSIC, pid=prof.get("id"), strips=strips)

    # ------------------------------------------------------------ show
    def retranslate(self, tr):
        super().retranslate(tr)
        self._tr = tr
        self.journal_button.setText(tr("strip.journal"))
        self._show()

    def refresh(self, session):
        super().refresh(session)
        self.session = session
        if session.character is not None:
            self.data = {v: session.view(v) for v in ("resources", "combat", "sheet", "items")}
            self.data["totals"] = {sl.MORALE: session.view("sources", number=sl.MORALE)["total"]}
        self._show()

    def apply_look(self, colors, scale, session):
        self.session = session
        self._show()

    def _show(self):
        if self._tr is None or self.session is None:
            return
        tr = self._tr
        rows = sl.strips(self.session.profile(CLASSIC), SB)
        self._build(rows)
        self.strip_button.setText(tr("strip.remove") if len(rows) > 1 else tr("strip.add"))
        if self.data is None:
            return
        d = self.data
        for (r, nid), c in self.cells.items():
            c.caption.setText(tr("number." + nid))
            got = sl.cell(nid, d["resources"], d["combat"], d["sheet"], d["items"], d["totals"])
            c.setVisible(got is not None)
            if got is None:
                continue
            value, note, style = got
            if got == sl.OTHER:            # any other sheet number: its sources total
                value = str(self.session.view("sources", number=nid)["total"])
            if isinstance(value, tuple):
                key, values = value
                c.value.setText(tr(key, values=values))
            else:
                c.value.setText(value)
            if isinstance(note, tuple):
                key, values, cat = note
                c.note.setText("%s; %s" % (tr(cat), tr(key, values=values)))
            else:
                c.note.setText(tr(note) if note else "")
            _repolish(c.value, "overload" if style == "overload" else SB["levels"]["working"])
