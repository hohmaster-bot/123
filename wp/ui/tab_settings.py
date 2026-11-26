"""The Settings tab of the right column (package 35 P2; UI_WISHES "Classic screen v2" points 13-16).

Language RU / EN, the theme (shipped and own) and follow-the-system, the font family / numbers font / size, the UI
scale, the one-time hints ("show all hints again", "hints off"), the journal mode, the quick grid size and columns,
the resource tube style, the editor mode switch and "restore the default profile". Every change is an existing
settings command (window.set_setting / session_settings: settings_set, hints_reset, profile_set, profile_reset) or
the Session editor mode; nothing here touches the character (D25).
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QPushButton, QScrollArea, QSpinBox, QVBoxLayout,
                               QWidget)

from wp.app import ui_data
from wp.i18n import i18n
from wp.ui.shell_data import SHELL

CLASSIC = "classic"
COMBO_CHARS = 10                       # a combo box shows about this many characters (it never widens the tab)
JOURNAL_MODES = ("short", "full")
STYLES = ("glass", "flat")


def _int_range(key):
    return ui_data.setting_range(key)


def _field_range(field):
    return ui_data.profile_field_range(CLASSIC, field)


class SettingsPage(QWidget):
    def __init__(self, block):
        super().__init__()
        self.block, self.session, self._tr, self._busy = block, None, None, False
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        area = QScrollArea()
        area.setWidgetResizable(True)
        inner = QWidget()
        self.form = QFormLayout(inner)
        self.form.setRowWrapPolicy(QFormLayout.WrapLongRows)     # a narrow tab: the field goes under its label
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        area.setWidget(inner)
        outer.addWidget(area, 1)
        self.w = {}
        self.w["language"] = self._combo(i18n.LANGS, lambda v: self.set("language", v))
        self.w["theme"] = self._combo((), self.choose_theme)
        self.w["theme_follow_system"] = self._check(lambda on: self.set("theme_follow_system", on))
        self.w["theme_editor"] = self._button(self.open_theme_editor)          # package 35 P3
        fams = ("",) + tuple(QFontDatabase.families())
        self.w["font_family"] = self._combo(fams, lambda v: self.set("font_family", v))
        self.w["font_family_numbers"] = self._combo(fams, lambda v: self.set("font_family_numbers", v))
        self.w["font_size"] = self._spin(_int_range("font_size"), lambda v: self.set("font_size", v))
        self.w["ui_scale"] = self._combo(tuple(str(x) for x in SHELL["scales"]),
                                         lambda v: self.set("ui_scale", float(v)))
        self.w["hints_off"] = self._check(lambda on: self.set("hints_off", on))
        self.w["hints_reset"] = self._button(lambda: self.run("hints_reset"))
        self.w["journal_mode"] = self._combo(JOURNAL_MODES, lambda v: self.set("journal_mode", v))
        self.w["quick_cells"] = self._spin(_field_range("quick_cells"), lambda v: self.profile(quick_cells=v))
        self.w["quick_columns"] = self._spin(_field_range("quick_columns"), lambda v: self.profile(quick_columns=v))
        self.w["resource_style"] = self._combo(STYLES, lambda v: self.set("resource_style", v))
        self.w["editor_mode"] = self._check(self.editor)
        self.w["layout_editor"] = self._button(self.open_layout_editor)        # package 35 P5
        self.w["profile_reset"] = self._button(lambda: self.run("profile_reset", mode=CLASSIC,
                                                                pid=self.session.profile(CLASSIC).get("id")))
        self.labels = {}
        for key, widget in self.w.items():
            self.form.addRow(key, widget)
            self.labels[key] = self.form.labelForField(widget)

    # ------------------------------------------------------------ widgets
    def _combo(self, values, fn):
        c = QComboBox()
        c.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        c.setMinimumContentsLength(COMBO_CHARS)
        for v in values:
            c.addItem(v or "-", v)
        c.activated.connect(lambda i, c=c: None if self._busy else fn(c.itemData(i)))
        return c

    def _check(self, fn):
        b = QCheckBox()
        b.toggled.connect(lambda on: None if self._busy else fn(bool(on)))
        return b

    def _spin(self, rng, fn):
        s = QSpinBox()
        s.setRange(*rng)
        s.editingFinished.connect(lambda s=s: None if self._busy else fn(int(s.value())))
        return s

    def _button(self, fn):
        b = QPushButton()
        b.setObjectName("small")
        b.clicked.connect(lambda _=False: fn())
        return b

    # ------------------------------------------------------------ commands (settings only)
    def set(self, key, value):
        return self.block.win.set_setting(key, value)

    def run(self, command, **params):
        return self.block.win.session_settings(command, **params)

    def profile(self, **fields):
        return self.run("profile_set", mode=CLASSIC, pid=self.session.profile(CLASSIC).get("id"), **fields)

    def choose_theme(self, tid):
        return self.block.win.choose_theme(tid)

    def open_theme_editor(self):
        from wp.ui.theme_editor import open_editor
        return open_editor(self.block.win)

    def open_layout_editor(self):
        from wp.ui.layout_editor import open_layout_editor
        return open_layout_editor(self.block.win)

    def editor(self, on):
        self.session.set_editor_mode(bool(on))

    # ------------------------------------------------------------ show
    def retranslate(self, tr):
        self._tr = tr
        for key, lab in self.labels.items():
            if lab is not None:
                lab.setText(tr("settings_tab." + key))
        self.w["hints_reset"].setText(tr("settings_tab.hints_reset_button"))
        self.w["theme_editor"].setText(tr("settings_tab.theme_editor_button"))
        self.w["layout_editor"].setText(tr("settings_tab.layout_editor_button"))
        for combo, prefix in ((self.w["language"], "lang."), (self.w["journal_mode"], "journal.mode."),
                              (self.w["resource_style"], "settings_tab.style.")):
            for i in range(combo.count()):
                combo.setItemText(i, tr(prefix + combo.itemData(i)))
        self.w["profile_reset"].setText(tr("settings_tab.profile_reset_button"))
        self._show()

    def refresh(self, session):
        self.session = session
        self._show()

    def _pick(self, combo, value):
        i = combo.findData(value)
        combo.setCurrentIndex(max(0, i))

    def _show(self):
        if self._tr is None or self.session is None:
            return
        s, w = self.session, self.w
        self._busy = True
        try:
            tv = s.themes_view()
            w["theme"].clear()
            for tid, name, _layer, _warn in tv["themes"]:
                w["theme"].addItem(name or tid, tid)
            self._pick(w["theme"], s.setting("theme"))
            for key in ("language", "font_family", "font_family_numbers", "journal_mode", "resource_style"):
                self._pick(w[key], s.setting(key))
            self._pick(w["ui_scale"], str(float(s.setting("ui_scale"))))
            w["theme_follow_system"].setChecked(bool(s.setting("theme_follow_system")))
            w["hints_off"].setChecked(bool(s.setting("hints_off")))
            w["font_size"].setValue(int(s.setting("font_size")))
            prof = s.profile(CLASSIC)
            w["quick_cells"].setValue(int(prof.get("quick_cells") or 0))
            w["quick_columns"].setValue(int(prof.get("quick_columns") or 0))
            w["editor_mode"].setChecked(bool(s.editor_mode))
        finally:
            self._busy = False
