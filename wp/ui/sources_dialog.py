"""The generic "Sources" dialog (package 34, owner: every number shows its sources; the editor mode changes them).

SourcesDialog(win, number) is fed by session.view("sources", number=...): the total, then one table row per source:
name, kind (rule / stored / effect / manual; a derived row names the RULES file that made it), value, on.
Outside the editor mode the table is read-only. In the editor mode a MANUAL row's value and on / off are editable and
it can be removed; a new manual row (name + value) can be added; derived rows are never written (a manual row
corrects them). Every change is a Session command (source_add / source_edit / source_toggle / source_remove): a
journal line and an undo step. A refusal shows its i18n text in the message line. Non-blocking (open()).
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox,
                               QTableWidget, QTableWidgetItem, QVBoxLayout)

from wp.i18n import i18n

COLS = 5                               # name, kind, value, on, remove
C_NAME, C_KIND, C_VALUE, C_ON, C_REMOVE = range(COLS)
VALUE_LIMIT = 100000                   # the value spin box range (the core accepts any int)


class SourcesDialog(QDialog):
    def __init__(self, win, number):
        super().__init__(win)
        self.win, self.session, self.number = win, win.session, number
        self.setObjectName("sources")
        lay = QVBoxLayout(self)
        self.total = QLabel()
        self.total.setObjectName("big")
        lay.addWidget(self.total)
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
        rows = v["rows"]
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
