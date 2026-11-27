"""The Training tab (package 35 P4; package 37 P1.2, owner decision 2): the summary (training points, level, base
slots, reactions, comfort, attention), the item qualifications (buy_item_qualification) and the CATALOG TRAININGS
(kind trainings: name, module, price per unit, units bought, limit; Buy N units = buy_training). Locked trainings are
hidden until "show locked" is ticked; then they show the reason ("needs the ability Magic body"). A training's hover
shows its links (held by / holds). Every change is a Session command (D25).
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem)

from wp.app import ui_data
from wp.ui import tab_logic as tl
from wp.ui.tab_pages import Page, yes

CAT_COLS = ("name", "module", "price", "units", "limit", "state")
UNITS_MAX = 1000                       # the units spin box range (the limit is checked by the command)


class TrainingPage(Page):
    TAB = "training"
    COLS = ("name", "qualification", "bought")
    ACTIONS = ("qualify",)

    def __init__(self, block):
        super().__init__(block)
        lay = self.layout()
        self.cat_title = QLabel()
        self.cat_title.setObjectName("block_title")
        lay.addWidget(self.cat_title)
        self.show_locked = QCheckBox()
        self.show_locked.toggled.connect(lambda _=False: self._show())
        lay.addWidget(self.show_locked)
        self.catalog = QTableWidget(0, len(CAT_COLS))
        self.catalog.verticalHeader().setVisible(False)
        self.catalog.setSelectionBehavior(QTableWidget.SelectRows)
        self.catalog.setSelectionMode(QTableWidget.SingleSelection)
        lay.addWidget(self.catalog, 1)
        bar = QHBoxLayout()
        self.units = QSpinBox()
        self.units.setRange(1, UNITS_MAX)
        self.buy_button = QPushButton()
        self.buy_button.setObjectName("small")
        self.buy_button.clicked.connect(lambda _=False: self.buy())
        bar.addWidget(self.units)
        bar.addWidget(self.buy_button)
        bar.addStretch(1)
        lay.addLayout(bar)
        self.cat_rows = []

    def show_data(self, tr, s):
        v = s.view("training")
        tp, level, slots, reactions, comfort, attention = tl.training_summary(v)
        self.summary.setText(tr("tabs_page.training.summary", tp=tp, level=level, slots=slots, reactions=reactions,
                                comfort=comfort, attention=attention))
        rows = tl.qualification_rows(s.character.items)
        self.fill(rows, [(name, n, yes(tr, bought)) for _iid, name, n, bought in rows])
        self.cat_title.setText(tr("tabs_page.training.catalog"))
        self.show_locked.setText(tr("tabs_page.training.show_locked"))
        self.buy_button.setText(tr("tabs_page.training.buy"))
        self.catalog.setHorizontalHeaderLabels([tr("tabs_page.col." + c) for c in CAT_COLS])
        links = s.view("links")
        danger = s.theme(self.block.win.system_dark() if self.block.win is not None else None)["colors"]["danger"]
        show = self.show_locked.isChecked()
        cat = [(tid, name, module, price, units, limit, ok, why)
               for tid, name, module, price, units, limit, ok, why in s.view("trainings") if ok or show]
        self.cat_rows = cat
        self.catalog.setRowCount(len(cat))
        for i, (tid, name, module, price, units, limit, ok, why) in enumerate(cat):
            state = tr("tabs_page.training.open") if ok else tr(why[0], values=tuple(why[1]))
            texts = (name, module, price, units, "" if limit is None else limit, state)
            for c, t in enumerate(texts):
                it = QTableWidgetItem(str(t))
                it.setFlags(it.flags() & ~Qt.ItemIsEditable)
                it.setToolTip(tl.link_tooltip(links, "training:" + tid, tr, danger, state))
                self.catalog.setItem(i, c, it)
        self.catalog.resizeColumnsToContents()
        self.buy_button.setEnabled(bool(cat))

    def select_training(self, tid):
        ids = [r[0] for r in self.cat_rows]
        self.catalog.selectRow(ids.index(tid))

    def buy(self, units=None):
        r = self.catalog.currentRow()
        if not 0 <= r < len(self.cat_rows):
            return None
        entry = ui_data.catalog_entry(self.session, "trainings", self.cat_rows[r][0])
        return self.run("buy_training", training=entry, units=int(units or self.units.value()))

    def act(self, key):
        row = self.selected()
        return None if row is None else self.run("buy_item_qualification", iid=row[0])
