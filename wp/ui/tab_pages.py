"""The content tabs of the right column (package 35 P4; UI_WISHES "Classic screen v2" point 9), in the style of the
combat tab: Injuries, Drives, Rest, Inventory, Training, Skills, Feats, Catalogs. Each page reads views through the
Session (tab_logic arranges the rows: no game number is computed here) and changes the character only with existing
Session commands (D25): add_injury, drive_buy_up / drive_buy_down, short_rest / long_rest, equip_item /
unequip_item, buy_item_qualification, buy_skill_rank, set_favorite (a feat), nothing in Catalogs (read-only). A view
with nothing to show gives the empty state. Heavy tabs (Skills, Inventory, Training, Catalogs) have "Expand": the
window hides the other blocks for a while and NEVER rewrites the saved profile (window.expand_block).
Race and Class stay placeholders (game-module neutrality: no class, race or weapon-group content now).
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from wp.ui import tab_logic as tl

SEVERITIES = ("light", "medium", "heavy")


class Page(QWidget):
    TAB = ""
    COLS = ()
    ACTIONS = ()

    def __init__(self, block):
        super().__init__()
        self.block, self.session, self._tr, self.rows = block, None, None, []
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        top = QHBoxLayout()
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        top.addWidget(self.summary, 1)
        self.expand_button = None
        if self.TAB in tl.HEAVY:
            self.expand_button = QPushButton()
            self.expand_button.setObjectName("small")
            self.expand_button.clicked.connect(self.toggle_expand)
            top.addWidget(self.expand_button)
        lay.addLayout(top)
        self.extra = QHBoxLayout()
        lay.addLayout(self.extra)
        self.table = QTableWidget(0, len(self.COLS))
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        lay.addWidget(self.table, 1)
        self.empty = QLabel()
        self.empty.setObjectName("muted")
        self.empty.setWordWrap(True)
        lay.addWidget(self.empty)
        bar = QHBoxLayout()
        self.buttons = {}
        for key in self.ACTIONS:
            b = QPushButton()
            b.setObjectName("small")
            b.clicked.connect(lambda _=False, k=key: self.act(k))
            self.buttons[key] = b
            bar.addWidget(b)
        bar.addStretch(1)
        lay.addLayout(bar)

    # ------------------------------------------------------------ common
    def retranslate(self, tr):
        self._tr = tr
        self.table.setHorizontalHeaderLabels([tr("tabs_page.col." + c) for c in self.COLS])
        for k, b in self.buttons.items():
            b.setText(tr("tabs_page.%s.%s" % (self.TAB, k)))
        if self.expand_button is not None:
            self.expand_button.setText(tr("tabs_page.collapse") if self.expanded() else tr("tabs_page.expand"))
        self._show()

    def refresh(self, session):
        self.session = session
        self._show()

    def expanded(self):
        win = self.block.win
        return bool(win is not None and getattr(win, "expanded", None) == self.block.item.get("id", self.block.pid))

    def toggle_expand(self):
        win = self.block.win
        if win is None:
            return None
        bid = self.block.item.get("id", self.block.pid)
        r = win.expand_block(None if self.expanded() else bid)
        if self._tr is not None:
            self.retranslate(self._tr)
        return r

    def selected(self):
        r = self.table.currentRow()
        return self.rows[r] if 0 <= r < len(self.rows) else None

    def select(self, index):
        self.table.selectRow(index)

    def run(self, command, **params):
        return self.block.run(command, **params)

    def open_effects(self, collection="", oid="", catalog=None):
        """Package 38 P5: the effect editor for one carrier (or one catalog entry)."""
        from wp.ui.effect_dialog import open_effects
        win = self.block.win
        return None if win is None else open_effects(win, catalog, collection, oid)

    def fill(self, rows, texts):
        self.rows = rows
        self.table.setRowCount(len(rows))
        for i, row in enumerate(texts):
            for c, v in enumerate(row):
                it = QTableWidgetItem(str(v))
                it.setFlags(it.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, c, it)
        self.table.resizeColumnsToContents()
        self.empty.setText(self._tr("tabs_page.%s.empty" % self.TAB) if not rows else "")
        self.empty.setVisible(not rows)
        for b in self.buttons.values():
            b.setEnabled(bool(rows) or not self.NEEDS_ROW)

    NEEDS_ROW = True

    def _show(self):
        if self._tr is None or self.session is None or self.session.character is None:
            return
        self.show_data(self._tr, self.session)

    def show_data(self, tr, s):
        raise NotImplementedError

    def act(self, key):
        raise NotImplementedError


def yes(tr, v):
    return tr("tabs_page.yes") if v else ""


class InjuriesPage(Page):
    TAB = "injuries"
    COLS = ("name", "severity", "heal_rating", "permanent", "charges")
    ACTIONS = ("take", "effects")
    NEEDS_ROW = False

    def __init__(self, block):
        super().__init__(block)
        self.severity = QComboBox()
        for sv in SEVERITIES:
            self.severity.addItem(sv, sv)
        self.extra.addWidget(self.severity)
        self.extra.addStretch(1)

    def show_data(self, tr, s):
        v = s.view("injuries")
        rows = tl.injury_rows(v)
        self.summary.setText(tr("tabs_page.injuries.summary", ot=v["trauma"], n=len(rows)))
        for i, sv in enumerate(SEVERITIES):
            self.severity.setItemText(i, tr("tabs_page.severity." + sv))
        self.fill(rows, [(name, tr("tabs_page.severity." + sev) if sev in SEVERITIES else sev, heal, yes(tr, perm),
                          charges) for _jid, name, sev, heal, perm, charges in rows])

    def act(self, key):
        if key == "effects":
            row = self.selected()
            return self.open_effects("injuries", row[0] if row else "")
        return self.run("add_injury", severity=self.severity.currentData())


class DrivesPage(Page):
    TAB = "drives"
    COLS = ("name", "type", "level", "principle", "quest", "comfort_received")
    ACTIONS = ("up", "down")

    def __init__(self, block):
        super().__init__(block)
        self.quests = {}
        self.table.cellClicked.connect(self.cell_clicked)

    def show_data(self, tr, s):
        v = s.view("notebook")
        rows = tl.drive_rows(v)
        dist, start, rem = tl.drive_summary(v)
        comfort = s.view("training")["comfort"]
        lines = [tr("tabs_page.drives.summary", dist=dist, start=start, comfort=comfort["current"])]
        lines += [tr(k, values=tuple(vals)) for k, vals in rem]
        self.summary.setText("\n".join(lines))
        self.fill(rows, [(name + (" !" if remind else ""), dtype, level, principle, quest, yes(tr, got))
                         for _did, name, dtype, level, principle, quest, got, remind in rows])
        self.quests = {d["did"]: d["quest"] for d in s.view("notebook")["drives"]}
        for r, row in enumerate(rows):
            text = self.quests.get(row[0]) or tr("tabs_page.drives.no_quest")
            self.table.item(r, self.COLS.index("quest")).setToolTip(text)

    def quest_text(self, row):
        """The quest of a drive (a click on its quest state; owner, package 36 P1.4)."""
        return self.quests.get(self.rows[row][0], "") if 0 <= row < len(self.rows) else ""

    def cell_clicked(self, row, col):
        if col == self.COLS.index("quest") and self.block.win is not None and self._tr is not None:
            self.block.win.info(self._tr("tabs_page.drives.quest_title"),
                                self.quest_text(row) or self._tr("tabs_page.drives.no_quest"))

    def act(self, key):
        row = self.selected()
        if row is None:
            return None
        return self.run("drive_buy_up" if key == "up" else "drive_buy_down", did=row[0])


class RestPage(Page):
    TAB = "rest"
    COLS = ("option", "bp_cost")
    ACTIONS = ("short", "long")
    NEEDS_ROW = False

    def show_data(self, tr, s):
        v = s.view("rest")
        rows = tl.rest_rows(v)
        res = s.view("resources")
        self.summary.setText(tr("tabs_page.rest.summary", heal=v["free_heal"], bp=res["bp"]["current"],
                                bp_max=res["bp"]["max"]))
        self.fill(rows, [(tr("tabs_page.rest.option." + o), c) for o, c in rows])

    def act(self, key):
        return self.run("short_rest" if key == "short" else "long_rest")
