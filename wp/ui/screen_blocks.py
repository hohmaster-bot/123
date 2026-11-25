"""The Parameters block and the AC block of the Classic window (package 34, Phase 5 step 3; UI_WISHES "Classic screen
v2" point 7). Both are separate blocks of the layout profile on one row of the middle column (window regions).

Parameters: a 3x3 grid (rows from the layout item's "cells" or data/screen_blocks.json): melee, ranged, initiative /
CMB, CMD, load / Fort, Ref, Will. Numbers from the sheet view (attack_melee / attack_ranged, stats) and the items
view (load: "40 of X (light / load / overload)"; overload in the danger colour). AC: the 3x3 zones (cell 5 = you):
the primary variant large, the secondary small, the zone label; a cell where the held shield counts gets the
shield border (token ac_shield) and the shield mark; the header line shows flat-footed and touch (reference).
A click on any number opens the Sources dialog (sources_dialog.py): read-only, or editable in the editor mode.
Reads only session.view(...); never changes the character itself (D25).
"""
import io
import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from wp.ui import params_logic as pl
from wp.ui.blocks import Block
from wp.ui.sources_dialog import open_sources

CELL_PAD = 2                           # px inside a number cell (UI, not a rule)
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "screen_blocks.json")


def load(path=DATA):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


SB = load()


def _repolish(w, name):
    if w.objectName() != name:
        w.setObjectName(name)
        w.style().unpolish(w)
        w.style().polish(w)


class Cell(QFrame):
    """A clickable number cell: caption (small), value (medium or large), note (small)."""

    def __init__(self, nid, on_click, level="working"):
        super().__init__()
        self.nid, self.on_click = nid, on_click
        self.setObjectName("cell")
        self.setCursor(Qt.PointingHandCursor)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(CELL_PAD, CELL_PAD, CELL_PAD, CELL_PAD)
        lay.setSpacing(0)
        self.caption = QLabel()
        self.caption.setObjectName("muted")
        self.caption.setAlignment(Qt.AlignCenter)
        self.value = QLabel()
        self.value.setObjectName(SB["levels"][level])
        self.value.setAlignment(Qt.AlignCenter)
        self.note = QLabel()
        self.note.setObjectName("muted")
        self.note.setAlignment(Qt.AlignCenter)
        self.note.setWordWrap(True)
        for w in (self.caption, self.value, self.note):
            lay.addWidget(w)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_click(self.nid)
        super().mouseReleaseEvent(event)


class ParametersBlock(Block):
    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell)
        self.grid = QGridLayout()
        self.box.addLayout(self.grid, 1)
        self.cells = {}
        for r, row in enumerate(pl.cells_of(item, SB["parameters"])):
            for c, nid in enumerate(row):
                cell = Cell(nid, self.open_sources)
                self.cells[nid] = cell
                self.grid.addWidget(cell, r, c)
        self._tr, self.sheet, self.items = None, None, None

    def open_sources(self, nid):
        return open_sources(self.win, nid) if self.win is not None else None

    def retranslate(self, tr):
        super().retranslate(tr)
        self._tr = tr
        self._show()

    def refresh(self, session):
        super().refresh(session)
        if session.character is None:
            return
        self.sheet, self.items = session.view("sheet"), session.view("items")
        self._show()

    def _show(self):
        if self._tr is None or self.sheet is None:
            return
        tr = self._tr
        for nid, cell in self.cells.items():
            cell.caption.setText(tr("number." + nid))
            text, style = pl.number_of(self.sheet, self.items, nid)
            if isinstance(text, tuple):            # the load: "40 of X" + the category
                key, values, cat = text
                cell.value.setText(tr(key, values=values))
                cell.note.setText(tr(cat))
            else:
                cell.value.setText(text)
                src = self.sheet[nid].get("weapon") if nid.startswith("attack_") else ""
                cell.note.setText(src or "")
            _repolish(cell.value, "overload" if style == pl.OVER else SB["levels"]["working"])
            _repolish(cell.note, "overload" if style == pl.OVER else "muted")


class AcBlock(Block):
    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell)
        self.modes = QLabel()
        self.modes.setObjectName("muted")
        self.box.addWidget(self.modes)
        self.grid = QGridLayout()
        self.box.addLayout(self.grid, 1)
        self.cells = {}
        for r, row in enumerate(SB["ac_grid"]):
            for c, cid in enumerate(row):
                cell = Cell("ac:" + cid, self.open_sources, level="critical")
                if cid == SB["ac_you"]:
                    cell.setCursor(Qt.ArrowCursor)
                self.cells[cid] = cell
                self.grid.addWidget(cell, r, c)
        self._tr, self.defense = None, None

    def open_sources(self, nid):
        if nid == "ac:" + SB["ac_you"] or self.win is None:
            return None
        return open_sources(self.win, nid)

    def retranslate(self, tr):
        super().retranslate(tr)
        self._tr = tr
        self._show()

    def refresh(self, session):
        super().refresh(session)
        if session.character is not None:
            self.defense = session.view("defense")
        self._show()

    def shield_cells(self):
        return sorted(c for c, cell in self.cells.items() if cell.objectName() == "shield_cell")

    def _show(self):
        if self._tr is None or self.defense is None:
            return
        tr, d = self._tr, self.defense
        info = pl.ac_cells(d, SB["ac_grid"], SB["ac_you"])
        modes = dict(d.get("modes", {}))
        self.modes.setText(tr("ac.modes", flat=modes.get("flat_footed", ""), touch=modes.get("touch", "")))
        for cid, cell in self.cells.items():
            if cid == SB["ac_you"]:
                cell.caption.setText(tr("ac_cell." + cid))
                side = d.get("shield_side") or ""
                cell.value.setText(tr("ac.shield_side." + side) if side else "")
                cell.note.setText("")
                continue
            primary, secondary, label, shield = info[cid]
            cell.caption.setText(tr(label) + (" " + tr("ac.shield_mark") if shield else ""))
            cell.value.setText(str(primary))
            cell.note.setText(str(secondary) if secondary != primary else "")
            _repolish(cell, "shield_cell" if shield else "cell")
