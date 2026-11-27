"""The generic "Sources" dialog (package 34, owner: every number shows its sources; the editor mode changes them).

SourcesDialog(win, number) is fed by session.view("sources", number=...): the total, then one table row per source:
name, kind (rule / stored / effect / manual; a derived row names the RULES file that made it), value, on.
Outside the editor mode the table is read-only. In the editor mode a MANUAL row's value and on / off are editable and
it can be removed; a new manual row (name + value) can be added; derived rows are never written (a manual row
corrects them). Every change is a Session command (source_add / source_edit / source_toggle / source_remove): a
journal line and an undo step. A refusal shows its i18n text in the message line. Non-blocking (open()).
Package 35 P1: rows whose value is 0 are hidden unless "show all" is on (the app setting sources_show_all; in the
editor mode the toggle starts ON and is not saved); an AC cell names every variant (the small second number of the
cell is the variant "with parry"); temp HP names the buff temp HP shown in the statuses block; the dialog takes the
size of its content or the size the owner dragged it to (dialog_size.SizedDialog, id "sources").
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox,
                               QTableWidget, QTableWidgetItem, QVBoxLayout)

from wp.i18n import i18n
from wp.ui import dialog_logic as dl
from wp.ui.dialog_size import SizedDialog

COLS = 5                               # name, kind, value, on, remove
C_NAME, C_KIND, C_VALUE, C_ON, C_REMOVE = range(COLS)
VALUE_LIMIT = 100000                   # the value spin box range (the core accepts any int)
SCREEN_SHARE = 2                       # the table asks for at most 1 / SCREEN_SHARE of the screen height (UI)
SHOW_ALL = "sources_show_all"
FRAME_SIDES = 2                        # the table frame is on both sides (UI)


class SourcesDialog(SizedDialog, QDialog):
    def __init__(self, win, number):
        super().__init__(win)
        self.win, self.session, self.number = win, win.session, number
        self.setObjectName("sources")
        lay = QVBoxLayout(self)
        self.total = QLabel()
        self.total.setObjectName("big")
        lay.addWidget(self.total)
        self.extra = QLabel()                 # AC variants / buff temp HP (package 35)
        self.extra.setObjectName("muted")
        self.extra.setWordWrap(True)
        lay.addWidget(self.extra)
        self.show_all = QCheckBox()
        self.show_all.setChecked(dl.show_all_start(win.session.setting(SHOW_ALL), win.session.editor_mode))
        self.show_all.toggled.connect(self.set_show_all)
        lay.addWidget(self.show_all)
        self.table = QTableWidget(0, COLS)
        self.table.verticalHeader().setVisible(False)
        lay.addWidget(self.table, 1)
        add = QHBoxLayout()
        self.new_name = QLineEdit()
        self.new_value = QSpinBox()
        self.new_value.setRange(-VALUE_LIMIT, VALUE_LIMIT)
        self.add_button = QPushButton()
        self.add_button.clicked.connect(lambda: self.add(self.new_name.text(), self.new_value.value()))
        add.addWidget(self.new_name, 1)
        add.addWidget(self.new_value)
        add.addWidget(self.add_button)
        lay.addLayout(add)
        self.message = QLabel()
        self.message.setObjectName("message")
        self.message.setWordWrap(True)
        lay.addWidget(self.message)
        self.view = None
        self.reload()
        self.setup_size(win, "sources")

    def tr(self, key, **params):
        return self.win.tr(key, **params)

    # ------------------------------------------------------------ show
    def reload(self):
        if self.session.character is None:
            return
        tr = self.tr
        self.view = v = self.session.view("sources", number=self.number)
        edit = bool(v["editable"])
        self.setWindowTitle(tr("sources.title", number=tr("number." + self.number)
                               if not self.number.startswith(("pool:", "ac:", "status:")) else self.number))
        self.total.setText(tr("sources.effects") if v.get("effects_only") else tr("sources.total", total=v["total"]))
        self.table.setHorizontalHeaderLabels([tr("sources.col." + c) for c in ("name", "kind", "value", "on")] + [""])
        self.show_all.setText(tr("sources.show_all"))
        rows = dl.visible_rows(v["rows"], self.show_all.isChecked())
        self.hidden = len(v["rows"]) - len(rows)
        extra = []
        if v.get("variants"):
            extra.append(", ".join(tr("ac.variant_value", label=tr(label), ac=ac) for _, label, ac in v["variants"]))
        if v.get("external"):
            extra.append(tr("sources.external", n=v["external"]))
        if self.hidden:
            extra.append(tr("sources.hidden", n=self.hidden))
        for value, text, src in v.get("situational", ()):        # package 36: never in the total
            extra.append(tr("sources.situational", value="%+d" % value, text=text, source=src))
        for src, cond, holds, value in v.get("conditions", ()):
            extra.append(tr("sources.condition", value="%+d" % value, cond=cond, source=src,
                            state=tr("sources.holds") if holds else tr("sources.not_holds")))
        if v.get("cycle"):
            extra.append(tr("sources.cycle"))
        if v.get("warning"):
            extra.append(tr("sources." + v["warning"]))
        self.extra.setText("; ".join(extra))
        self.extra.setVisible(bool(extra))
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            name = tr(r["name"]) if r["name"].startswith(("source.", "layer.")) else r["name"]
            self._cell(i, C_NAME, name)
            kind = tr("sources.kind." + r["kind"]) + (" (%s)" % r["rule"] if r["rule"] else "")
            self._cell(i, C_KIND, kind)
            if edit and r["manual"]:
                spin = QSpinBox()
                spin.setRange(-VALUE_LIMIT, VALUE_LIMIT)
                spin.setValue(int(r["value"]))
                spin.editingFinished.connect(lambda sid=r["id"], w=spin: self.set_value(sid, w.value()))
                self.table.setCellWidget(i, C_VALUE, spin)
                box = QCheckBox()
                box.setChecked(r["on"])
                box.toggled.connect(lambda on, sid=r["id"]: self.toggle(sid, on))
                self.table.setCellWidget(i, C_ON, box)
                rm = QPushButton(tr("sources.remove"))
                rm.setObjectName("small")
                rm.clicked.connect(lambda _=False, sid=r["id"]: self.remove(sid))
                self.table.setCellWidget(i, C_REMOVE, rm)
            else:
                for col in (C_VALUE, C_ON, C_REMOVE):
                    self.table.removeCellWidget(i, col)
                self._cell(i, C_VALUE, "%+d" % r["value"] if r["value"] else "0")
                self._cell(i, C_ON, tr("sources.on") if r["on"] else tr("sources.off"))
                lost = r["on"] and not r["counted"] and r["value"]
                self._cell(i, C_REMOVE, tr("sources.not_counted") if lost else "")
        for w in (self.new_name, self.new_value, self.add_button):
            w.setVisible(edit)
        self.add_button.setText(tr("sources.add"))
        self.new_name.setPlaceholderText(tr("sources.new_name"))
        if not v["editable_target"]:
            self.message.setText(tr("sources.read_only_number"))
        elif not edit:
            self.message.setText(tr("sources.read_only"))
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self._fit_table()

    def _fit_table(self):
        """The table asks for the size of its rows and columns (no fixed frame, no empty area)."""
        t = self.table
        frame = FRAME_SIDES * t.frameWidth()
        w = sum(t.columnWidth(c) for c in range(t.columnCount())) + frame
        h = t.horizontalHeader().height() + sum(t.rowHeight(r) for r in range(t.rowCount())) + frame
        screen = self.screen()
        if screen is not None:
            h = min(h, screen.availableGeometry().height() // SCREEN_SHARE)
        t.setMinimumSize(w, h)
        t.setMaximumHeight(h)                     # no empty table area under the last row

    def set_show_all(self, on):
        if not self.session.editor_mode:          # the editor starts ON and is not remembered
            self.win.set_setting(SHOW_ALL, bool(on))
        self.reload()

    def _cell(self, row, col, text):
        it = QTableWidgetItem(str(text))
        it.setFlags(it.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, col, it)

    # ------------------------------------------------------------ changes (Session commands only)
    def _run(self, command, **params):
        r = self.session.dispatch(command, **params)
        if not r.ok:
            text = i18n.text_for(r, self.win.lang())
            self.message.setText(text)
            self.win.messages.append(text)
        else:
            self.message.setText("")
        self.reload()
        return r

    def add(self, name, value):
        r = self._run("source_add", number=self.number, name=name, value=int(value))
        if r.ok:
            self.new_name.clear()
            self.new_value.setValue(0)
        return r

    def set_value(self, sid, value):
        return self._run("source_edit", sid=sid, value=int(value))

    def toggle(self, sid, on):
        return self._run("source_toggle", sid=sid, on=bool(on))

    def remove(self, sid):
        return self._run("source_remove", sid=sid)


def open_sources(win, number):
    """Open (or re-point) the one Sources dialog of the window; tests (quiet) get it without showing it."""
    dlg = SourcesDialog(win, number)
    win.sources = dlg
    if not win.quiet:
        dlg.open()
    return dlg
