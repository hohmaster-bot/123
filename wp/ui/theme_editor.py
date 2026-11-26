"""The theme editor (package 35 P3, ROADMAP step 1b; UI_WISHES "Classic screen v2" point 16).

A dialog (SizedDialog, id "theme_editor") opened from the Settings tab: the theme list (shipped and own; the active
one is shown live), "Copy" (theme_copy: a new own theme with the same tokens, made active), "Reset to the shipped one"
(theme_reset: drops a user override of a shipped theme), "Remove" (an own theme), every colour token with its colour
(a click picks a colour: theme_edit, saved at once, so the window restyles LIVE), the contrast lines (a warning under
4.5:1, never a refusal), the background picture (none by default; "Add picture..." copies a file into the image
registry: image_add kind background), its dimming (background_dim 0..100) and "keep numbers readable"
(background_readable). The three shipped themes are never edited: the token buttons are disabled on them (copy one).
Every change is a Session theme command or a settings command; nothing touches the character (D25).
"""
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QCheckBox, QColorDialog, QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel,
                               QPushButton, QSlider, QTableWidget, QTableWidgetItem, QVBoxLayout)
from PySide6.QtCore import Qt

from wp.i18n import i18n
from wp.theme import themes
from wp.ui import theme_logic as tl
from wp.ui.dialog_size import SizedDialog

C_TOKEN, C_COLOR = range(2)
COLS = 2
NO_IMAGE = ""
HEX_RGB = 7                            # "#rrggbb" of a "#rrggbbaa" token (the alpha is not shown)


class ThemeEditor(SizedDialog, QDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win, self.session = win, win.session
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        self.theme = QComboBox()
        self.theme.activated.connect(lambda i: self.choose(self.theme.itemData(i)))
        self.copy_button, self.reset_button, self.remove_button = QPushButton(), QPushButton(), QPushButton()
        self.copy_button.clicked.connect(self.copy)
        self.reset_button.clicked.connect(self.reset)
        self.remove_button.clicked.connect(self.remove)
        top.addWidget(self.theme, 1)
        for b in (self.copy_button, self.reset_button, self.remove_button):
            b.setObjectName("small")
            top.addWidget(b)
        lay.addLayout(top)
        self.note = QLabel()
        self.note.setObjectName("muted")
        self.note.setWordWrap(True)
        lay.addWidget(self.note)
        self.table = QTableWidget(0, COLS)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.cell_clicked)
        lay.addWidget(self.table, 1)
        self.contrast = QLabel()
        self.contrast.setWordWrap(True)
        lay.addWidget(self.contrast)
        bg = QHBoxLayout()
        self.image = QComboBox()
        self.image.activated.connect(lambda i: self.win.set_setting("background_image", self.image.itemData(i)))
        self.add_image = QPushButton()
        self.add_image.setObjectName("small")
        self.add_image.clicked.connect(self.pick_image)
        self.dim = QSlider(Qt.Horizontal)
        self.dim.setRange(0, tl.PCT)
        self.dim.sliderReleased.connect(lambda: self.win.set_setting("background_dim", int(self.dim.value())))
        self.readable = QCheckBox()
        self.readable.toggled.connect(lambda on: None if self._busy else self.win.set_setting("background_readable",
                                                                                              bool(on)))
        for w in (self.image, self.add_image, self.dim, self.readable):
            bg.addWidget(w)
        self.bg_label = QLabel()
        lay.addWidget(self.bg_label)
        lay.addLayout(bg)
        self.message = QLabel()
        self.message.setObjectName("message")
        self.message.setWordWrap(True)
        lay.addWidget(self.message)
        self._busy = False
        self.reload()
        self.setup_size(win, "theme_editor")

    def tr(self, key, **params):
        return self.win.tr(key, **params)

    # ------------------------------------------------------------ show
    def current(self):
        return self.session.theme(self.win.system_dark())

    def reload(self):
        tr = self.tr
        self._busy = True
        try:
            self.setWindowTitle(tr("theme_editor.title"))
            view = self.session.themes_view(self.win.system_dark())
            self.theme.clear()
            for tid, name, _layer, _warn in view["themes"]:
                self.theme.addItem(name or tid, tid)
            self.theme.setCurrentIndex(max(0, self.theme.findData(view["active"])))
            t = self.current()
            own = tl.editable(t["id"], themes.shipped_ids())
            self.copy_button.setText(tr("theme_editor.copy"))
            self.reset_button.setText(tr("theme_editor.reset"))
            self.remove_button.setText(tr("theme_editor.remove"))
            self.reset_button.setEnabled(not own)
            self.remove_button.setEnabled(own)
            self.note.setText(tr("theme_editor.own") if own else tr("theme_editor.shipped"))
            self.table.setHorizontalHeaderLabels([tr("theme_editor.token"), tr("theme_editor.color")])
            tokens = tl.color_tokens()
            self.table.setRowCount(len(tokens))
            colors = dict(t.get("colors") or {})
            for i, tok in enumerate(tokens):
                name = QTableWidgetItem(tok)
                name.setFlags(name.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, C_TOKEN, name)
                val = colors.get(tok, "")
                cell = QTableWidgetItem(val)
                cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
                if val:
                    cell.setBackground(QColor(val[:HEX_RGB]))
                self.table.setItem(i, C_COLOR, cell)
            self.table.setEnabled(True)
            self.editable = own
            rows = tl.contrast_rows(t)
            bad = [r for r in rows if not r[-1]]
            self.contrast.setText("; ".join(tr("theme_editor.low_contrast", fg=fg, bg=bg, ratio=ratio)
                                            for fg, bg, ratio, _ in bad) or tr("theme_editor.contrast_ok"))
            self.contrast.setObjectName("message" if bad else "muted")
            self.bg_label.setText(tr("theme_editor.background"))
            self.image.clear()
            self.image.addItem(tr("theme_editor.no_image"), NO_IMAGE)
            for rec in self.session.app.images:
                if rec.get("kind") == "background":
                    self.image.addItem(rec.get("name") or rec["id"], rec["id"])
            self.image.setCurrentIndex(max(0, self.image.findData(self.session.setting("background_image"))))
            self.add_image.setText(tr("theme_editor.add_image"))
            self.dim.setValue(int(self.session.setting("background_dim")))
            self.readable.setText(tr("theme_editor.readable"))
            self.readable.setChecked(bool(self.session.setting("background_readable")))
            self.table.resizeColumnsToContents()
        finally:
            self._busy = False

    # ------------------------------------------------------------ commands
    def _done(self, r):
        if not r.ok:
            text = i18n.text_for(r, self.win.lang())
            self.message.setText(text)
            self.win.messages.append(text)
        else:
            self.message.setText("")
        self.reload()
        return r

    def choose(self, tid):
        return self._done(self.win.choose_theme(tid))

    def copy(self):
        t = self.current()
        r = self.session.theme_command("theme_copy", tid=t["id"], name=self.tr("theme_editor.copy_name",
                                                                              name=t.get("name", t["id"])))
        if r.ok:
            self.win.choose_theme(r.info["id"])
        return self._done(r)

    def reset(self):
        return self._done(self.session.theme_command("theme_reset", tid=self.current()["id"]))

    def remove(self):
        tid = self.current()["id"]
        r = self.session.theme_command("theme_remove", tid=tid)
        if r.ok:
            self.win.choose_theme(themes.DEFAULT)
        return self._done(r)

    def set_color(self, token, color):
        """One token of an own theme (live: the window restyles at once)."""
        t = self.current()                # a shipped theme is refused by the Session (shipped_theme)
        return self._done(self.session.theme_command("theme_edit", tid=t["id"], colors={token: color}))

    def cell_clicked(self, row, col):
        token = self.table.item(row, C_TOKEN).text()
        if not self.editable or self.win.quiet:
            return None
        c = QColorDialog.getColor(QColor(self.table.item(row, C_COLOR).text()[:HEX_RGB]), self)
        return self.set_color(token, c.name()) if c.isValid() else None

    def add_picture(self, path):
        r = self.win.session_settings("image_add", source=path, kind="background", user_folder=self.session.user_dir)
        if r.ok:
            self.win.set_setting("background_image", r.info["id"])
        return self._done(r)

    def pick_image(self):
        if self.win.quiet:
            return None
        path, _ = QFileDialog.getOpenFileName(self, self.tr("theme_editor.add_image"))
        return self.add_picture(path) if path else None


def open_editor(win):
    dlg = ThemeEditor(win)
    win.theme_editor = dlg
    if not win.quiet:
        dlg.open()
    return dlg
