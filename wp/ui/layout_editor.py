"""The Classic layout editor (package 35 P5, ROADMAP step 8; UI_WISHES "Classic screen v2" point 13).

A dialog (SizedDialog, id "layout_editor"), opened in the editor mode (View > Layout editor, or the Settings tab):
one row per block of the active classic profile (name, column, position, size, visible). Controls: show / hide
(visible), up / down inside its column, move to another column (left / center / right), width / height - / + by the
grid step (data/screen_blocks.json "layout_grid": snap), the tab bar pin (tab_rows, as in the tabs block), "Restore
the default profile" (profile_reset) and the layout warnings (screen_settings.layout_warnings: a block under its
minimum, all HP controls hidden, a block outside the window): warnings never forbid. Free placement is only for Lite
(not built). Every change is a settings command (layout_edit / profile_set / profile_reset) saved in the profile
(data); a window resize alone never writes it. The window rebuilds its regions when the profile panels change.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QHBoxLayout, QLabel, QPushButton, QSpinBox,
                               QTableWidget, QTableWidgetItem, QVBoxLayout)

from wp.app import ui_data
from wp.i18n import i18n
from wp.ui import layout_logic as ll
from wp.ui.dialog_size import SizedDialog
from wp.ui.screen_blocks import SB

CLASSIC = "classic"
PANELS = "panels"
COLS = ("block", "column", "position", "size", "visible")


class LayoutEditor(SizedDialog, QDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win, self.session = win, win.session
        lay = QVBoxLayout(self)
        self.table = QTableWidget(0, len(COLS))
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        lay.addWidget(self.table, 1)
        bar = QHBoxLayout()
        self.buttons = {}
        for key in ("up", "down", "narrower", "wider", "lower", "higher"):
            b = QPushButton()
            b.setObjectName("small")
            b.clicked.connect(lambda _=False, k=key: self.act(k))
            self.buttons[key] = b
            bar.addWidget(b)
        self.column = QComboBox()
        for c in ll.COLUMNS:
            self.column.addItem(c, c)
        self.column.activated.connect(lambda i: self.to_column(self.column.itemData(i)))
        bar.addWidget(self.column)
        self.visible = QCheckBox()
        self.visible.clicked.connect(lambda on: self.set_visible(bool(on)))
        bar.addWidget(self.visible)
        lay.addLayout(bar)
        bottom = QHBoxLayout()
        self.tab_rows_label = QLabel()            # the tab bar pin (P1): 0 = automatic wrapping
        self.tab_rows = QSpinBox()
        self.tab_rows.setRange(*ui_data.profile_field_range(CLASSIC, "tab_rows"))
        self.tab_rows.editingFinished.connect(lambda: self.set_tab_rows(self.tab_rows.value()))
        bottom.addWidget(self.tab_rows_label)
        bottom.addWidget(self.tab_rows)
        self.reset_button = QPushButton()
        self.reset_button.setObjectName("small")
        self.reset_button.clicked.connect(self.reset)
        bottom.addWidget(self.reset_button)
        bottom.addStretch(1)
        lay.addLayout(bottom)
        self.warnings = QLabel()
        self.warnings.setWordWrap(True)
        lay.addWidget(self.warnings)
        self.message = QLabel()
        self.message.setObjectName("message")
        self.message.setWordWrap(True)
        lay.addWidget(self.message)
        self.items = []
        self.table.itemSelectionChanged.connect(self._sync)
        self.reload()
        self.setup_size(win, "layout_editor")

    def tr(self, key, **params):
        return self.win.tr(key, **params)

    def profile(self):
        return self.session.profile(CLASSIC)

    # ------------------------------------------------------------ show
    def reload(self, keep=None):
        tr = self.tr
        self.setWindowTitle(tr("layout_editor.title"))
        self.table.setHorizontalHeaderLabels([tr("layout_editor.col." + c) for c in COLS])
        for k, b in self.buttons.items():
            b.setText(tr("layout_editor." + k))
        for i, c in enumerate(ll.COLUMNS):
            self.column.setItemText(i, tr("layout_editor.column." + c))
        self.visible.setText(tr("layout_editor.visible"))
        self.reset_button.setText(tr("layout_editor.reset"))
        self.tab_rows_label.setText(tr("layout_editor.tab_rows"))
        self.tab_rows.setValue(int(self.profile().get("tab_rows", 0) or 0))
        items = [dict(i) for i in self.profile().get(PANELS, ())]
        self.items = sorted(items, key=lambda i: (ll.COLUMNS.index(i.get("dock")) if i.get("dock") in ll.COLUMNS
                                                  else -1, ll._key(i)))
        self.table.setRowCount(len(self.items))
        for r, it in enumerate(self.items):
            pos, size = it.get("position") or (0, 0), it.get("size") or (0, 0)
            texts = (tr("panel." + it.get("panel", "")), it.get("dock", ""), "%d, %d" % (pos[0], pos[1]),
                     "%d x %d" % (size[0], size[1]), tr("tabs_page.yes") if it.get("visible", True) else "-")
            for c, t in enumerate(texts):
                cell = QTableWidgetItem(str(t))
                cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(r, c, cell)
        self.table.resizeColumnsToContents()
        if keep is not None:
            ids = [i["id"] for i in self.items]
            if keep in ids:
                self.table.selectRow(ids.index(keep))
        warn = ui_data.layout_warnings(self.session, CLASSIC)
        self.warning_ids = [w[0] for w in warn]
        self.warnings.setText("\n".join(("%s: %s" % (tr("panel." + p), tr("warning." + w))) if p else
                                        tr("warning." + w) for w, _i, p in warn) or tr("layout_editor.no_warnings"))
        self.warnings.setObjectName("message" if warn else "muted")
        self._sync()

    def _sync(self):
        it = self.current()
        self.visible.setChecked(bool(it.get("visible", True)) if it else False)
        if it and it.get("dock") in ll.COLUMNS:
            self.column.setCurrentIndex(ll.COLUMNS.index(it["dock"]))

    def current(self):
        r = self.table.currentRow()
        return self.items[r] if 0 <= r < len(self.items) else None

    def select(self, item_id):
        ids = [i["id"] for i in self.items]
        self.table.selectRow(ids.index(item_id))

    # ------------------------------------------------------------ commands (settings only)
    def _edit(self, item_id, **fields):
        return self.win.session_settings("layout_edit", mode=CLASSIC, pid=self.profile().get("id"),
                                         collection=PANELS, item_id=item_id, **fields)

    def _done(self, r, keep):
        if r is not None and not r.ok:
            text = i18n.text_for(r, self.win.lang())
            self.message.setText(text)
        else:
            self.message.setText("")
        self.reload(keep)
        return r

    def act(self, key):
        it = self.current()
        if it is None:
            return None
        step = int(SB["layout_grid"])
        if key in ("up", "down"):
            r = None
            for iid, fields in ll.move_fields(self.items, it["id"], -1 if key == "up" else 1).items():
                r = self._edit(iid, **fields)
            return self._done(r, it["id"])
        dw = {"narrower": -step, "wider": step}.get(key, 0)
        dh = {"lower": -step, "higher": step}.get(key, 0)
        return self._done(self._edit(it["id"], **ll.resize_fields(it.get("size") or (step, step), dw, dh, step)),
                          it["id"])

    def to_column(self, dock):
        it = self.current()
        if it is None or it.get("dock") == dock:
            return None
        return self._done(self._edit(it["id"], **ll.to_column(self.items, it["id"], dock, int(SB["layout_grid"]))),
                          it["id"])

    def set_visible(self, on):
        it = self.current()
        return None if it is None else self._done(self._edit(it["id"], visible=bool(on)), it["id"])

    def set_tab_rows(self, rows):
        """The tab bar pin (profile field tab_rows; 0 = the tabs wrap by themselves)."""
        return self._done(self.win.session_settings("profile_set", mode=CLASSIC, pid=self.profile().get("id"),
                                                    tab_rows=int(rows)), None)

    def reset(self):
        return self._done(self.win.session_settings("profile_reset", mode=CLASSIC, pid=self.profile().get("id")),
                          None)


def open_layout_editor(win):
    dlg = LayoutEditor(win)
    win.layout_editor = dlg
    if not win.quiet:
        dlg.open()
    return dlg
