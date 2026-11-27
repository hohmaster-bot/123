"""The effect editor dialog (package 38 P5, owner decision 9; ARCH decision D37; wp/app/effect_editor.py).

Opened from the entry editors (the Feats, Inventory, Injuries and Training tabs: the "Effects" button) and from the
catalog window. Character mode: a carrier chooser (every feat / race ability, item, status, quirk, training, injury)
and, for an item, the tab (not activated / activated); catalog mode: one catalog entry. The list of effects; the form
of one effect: the target (a search field over the view effect_targets, const:<id> included), the value or formula,
add or replace, the condition, the scope, the situational note, the bonus type; buttons Add / Change / Remove.
Character carriers change only through commands (journal, undo); a catalog entry is saved to its user file with its
module tag. Invalid input is never saved: the refusal text shows instead.
"""
from PySide6.QtWidgets import (QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QPushButton, QVBoxLayout)

from wp.app import effect_editor as ee
from wp.i18n import i18n
from wp.ui.dialog_size import SizedDialog

MODES = ("add", "replace")
SCOPES = ("", "melee", "ranged")
OPS = ("add", "change", "remove")


class EffectDialog(SizedDialog, QDialog):
    def __init__(self, win, catalog=None, collection="", oid=""):
        super().__init__(win)
        self.win, self.session, self.catalog = win, win.session, catalog       # catalog = (kind, eid) or None
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        self.carrier = QComboBox()
        self.carrier.currentIndexChanged.connect(lambda _=0: self.reload())
        self.field = QComboBox()
        self.field.currentIndexChanged.connect(lambda _=0: self._list())     # noqa: E731
        top.addWidget(self.carrier, 1)
        top.addWidget(self.field)
        lay.addLayout(top)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._pick)
        lay.addWidget(self.list, 1)
        form = QFormLayout()
        self.labels = {}
        self.search = QLineEdit()
        self.search.textChanged.connect(self._filter)
        self.target = QComboBox()
        self.target.setEditable(True)
        self.value, self.condition, self.situational = QLineEdit(), QLineEdit(), QLineEdit()
        self.mode, self.scope, self.btype = QComboBox(), QComboBox(), QComboBox()
        for box, items in ((self.mode, MODES), (self.scope, SCOPES), (self.btype, ee.BTYPES)):
            for x in items:
                box.addItem(x, x)
        for key, w in (("search", self.search), ("target", self.target), ("value", self.value), ("mode", self.mode),
                       ("condition", self.condition), ("scope", self.scope), ("situational", self.situational),
                       ("btype", self.btype)):
            lab = QLabel()
            self.labels[key] = lab
            form.addRow(lab, w)
        lay.addLayout(form)
        bar = QHBoxLayout()
        self.buttons = {}
        for op in OPS:
            b = QPushButton()
            b.clicked.connect(lambda _=False, o=op: self.act(o))
            self.buttons[op] = b
            bar.addWidget(b)
        bar.addStretch(1)
        lay.addLayout(bar)
        self.message = QLabel()
        self.message.setObjectName("message")
        self.message.setWordWrap(True)
        lay.addWidget(self.message)
        self.targets = tuple(self.session.view("effect_targets"))
        self.effects = ()
        self._fill_carriers(collection, oid)
        self.retranslate()
        self.setup_size(win, "effect_editor")

    def tr(self, key, **params):
        return self.win.tr(key, **params)

    # ------------------------------------------------------------ carriers, fields, list
    def _fill_carriers(self, collection, oid):
        self.carrier.blockSignals(True)
        self.carrier.clear()
        if self.catalog is not None:
            kind, eid = self.catalog
            self.carrier.addItem("%s: %s" % (kind, eid), ("catalog", kind, eid))
        else:
            for coll, cid, name, _fields in ee.carriers(self.session):
                self.carrier.addItem("%s: %s" % (self.tr("effects.kind." + coll), name), (coll, cid))
            i = self.carrier.findData((collection, oid))
            if i >= 0:
                self.carrier.setCurrentIndex(i)
        self.carrier.blockSignals(False)
        self.reload()

    def source(self):
        return self.carrier.currentData()

    def fields(self):
        s = self.source()
        if s is None:
            return ()
        if s[0] == "catalog":
            return ee.CATALOG_KINDS.get(s[1], ("effects",))
        return next((f for c, _k, f in ee.CHARACTER if c == s[0]), ("effects",))

    def reload(self):
        keep = self.field.currentData()
        self.field.blockSignals(True)
        self.field.clear()
        for f in self.fields():
            self.field.addItem(self.tr("effects.field." + f), f)
        if keep is not None and self.field.findData(keep) >= 0:
            self.field.setCurrentIndex(self.field.findData(keep))
        self.field.blockSignals(False)
        self.field.setVisible(len(self.fields()) > 1)
        self._list()

    def _list(self, keep=-1):
        s, field = self.source(), self.field.currentData() or "effects"
        if s is None:
            self.effects = ()
        elif s[0] == "catalog":
            _c, kind, eid = s
            self.effects = ee.catalog_effects(self.session, kind, eid, field)
        else:
            self.effects = ee.effects(self.session, s[0], s[1], field)
        self.list.blockSignals(True)
        self.list.clear()
        for e in self.effects:
            self.list.addItem(self.describe(e))
        if 0 <= keep < len(self.effects):
            self.list.setCurrentRow(keep)          # the edited row stays selected (its form stays as typed)
        self.list.blockSignals(False)

    def describe(self, e):
        parts = ["%s %s" % (e.target, e.value)]
        if e.note == "replace":
            parts.append(self.tr("effects.replace"))
        if e.condition:
            parts.append("[%s]" % e.condition)
        if e.scope:
            parts.append(e.scope)
        if e.situational:
            parts.append("(%s)" % e.situational)
        return " ".join(parts)

    def _filter(self, text):
        t = str(text or "").strip().lower()
        current = self.target.currentText()
        self.target.clear()
        for x in self.targets:
            if t in x.lower():
                self.target.addItem(x, x)
        self.target.setEditText(current if not t else (self.target.itemText(0) if self.target.count() else current))

    def _pick(self, row):
        if not 0 <= row < len(self.effects):
            return
        e = self.effects[row]
        self.target.setEditText(e.target)
        self.value.setText(str(e.value))
        self.mode.setCurrentIndex(MODES.index("replace" if e.note == "replace" else "add"))
        self.condition.setText(e.condition)
        self.scope.setCurrentIndex(max(0, self.scope.findData(e.scope)))
        self.situational.setText(e.situational)
        self.btype.setCurrentIndex(max(0, self.btype.findData(e.btype)))

    def form(self):
        return {"target": self.target.currentText().strip(), "value": self.value.text(),
                "mode": self.mode.currentData(), "condition": self.condition.text(), "scope": self.scope.currentData(),
                "situational": self.situational.text(), "btype": self.btype.currentData()}

    def set_form(self, **values):
        """Tests and the pages: fill the form fields by name."""
        if "target" in values:
            self.target.setEditText(values["target"])
        for key, w in (("value", self.value), ("condition", self.condition), ("situational", self.situational)):
            if key in values:
                w.setText(str(values[key]))
        for key, box in (("mode", self.mode), ("scope", self.scope), ("btype", self.btype)):
            if key in values:
                box.setCurrentIndex(max(0, box.findData(values[key])))

    # ------------------------------------------------------------ actions
    def act(self, op):
        s, field, row = self.source(), self.field.currentData() or "effects", self.list.currentRow()
        if s is None or (op != "add" and row < 0):
            return None
        if s[0] == "catalog":
            _c, kind, eid = s
            r = ee.catalog_apply(self.session, kind, eid, op, row, self.form(), field)
        else:
            r = ee.apply(self.session, op, s[0], s[1], row, self.form(), field)
        self.message.setText("" if r.ok else i18n.text_for(r, self.win.lang()))
        self._list(len(self.effects) if op == "add" and r.ok else (row if op != "remove" else -1))
        return r

    def retranslate(self):
        tr = self.tr
        self.setWindowTitle(tr("effects.title"))
        for key, lab in self.labels.items():
            lab.setText(tr("effects.form." + key))
        for op, b in self.buttons.items():
            b.setText(tr("effects." + op))
        for i, m in enumerate(MODES):
            self.mode.setItemText(i, tr("effects.mode." + m))
        for i, sc in enumerate(SCOPES):
            self.scope.setItemText(i, tr("effects.scope." + (sc or "all")))


def open_effects(win, catalog=None, collection="", oid=""):
    dlg = EffectDialog(win, catalog, collection, oid)
    win.effect_dialog = dlg
    if not win.quiet:
        dlg.open()
    return dlg
