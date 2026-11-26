"""Small dialogs of the resources block and the experience strip (package 33). They only collect numbers and text;
the block turns them into Session commands (D25). Every dialog is non-blocking: open() shows it, the accepted signal
runs the block's apply function. In tests (window.quiet) the dialog is built but not shown: the test fills the fields
and calls accept().

EditPopup: the tube value editor ("+N" / "-N" / a number; for HP a second field = temporary HP).
AmountDialog: an amount (and optionally a damage type) for Take damage / Heal / Damage to balance.
RollDialog: the hit-die roll of a level-up (spin box, minimum 1).
Package 35: every dialog takes the size of its content or the size the owner dragged it to, never larger than the
screen (dialog_size.SizedDialog; ids edit / amount / level_up).
"""
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QSpinBox,
                               QVBoxLayout)

from wp.ui.dialog_size import SizedDialog


class _Base(SizedDialog, QDialog):
    def __init__(self, parent, title, tr):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.tr_ = tr
        self.form = QFormLayout()
        lay = QVBoxLayout(self)
        lay.addLayout(self.form)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setText(tr("dialog.ok"))
        self.buttons.button(QDialogButtonBox.Cancel).setText(tr("dialog.cancel"))
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        lay.addWidget(self.buttons)


class EditPopup(_Base):
    def __init__(self, parent, tr, title, current_text, with_temp=False, temp_text=""):
        super().__init__(parent, title, tr)
        self.hint = QLabel(tr("resources.edit_hint"))
        self.hint.setObjectName("muted")
        self.hint.setWordWrap(True)
        self.form.addRow(self.hint)
        self.value = QLineEdit()
        self.value.setPlaceholderText(current_text)
        self.form.addRow(tr("resources.edit_value"), self.value)
        self.temp = None
        if with_temp:
            self.temp = QLineEdit()
            self.temp.setPlaceholderText(temp_text)
            self.form.addRow(tr("resources.edit_temp"), self.temp)
        self.setup_size(parent, "edit")

    def texts(self):
        return self.value.text().strip(), (self.temp.text().strip() if self.temp is not None else "")


class AmountDialog(_Base):
    def __init__(self, parent, tr, title, maximum, types=()):
        super().__init__(parent, title, tr)
        self.amount = QSpinBox()
        self.amount.setRange(0, int(maximum))
        self.form.addRow(tr("resources.amount"), self.amount)
        self.kind = None
        if types:
            self.kind = QComboBox()
            for t in types:
                self.kind.addItem(tr("damage." + t), t)
            self.form.addRow(tr("resources.damage_type"), self.kind)
        self.setup_size(parent, "amount")

    def values(self):
        return int(self.amount.value()), (self.kind.currentData() if self.kind is not None else None)


class RollDialog(_Base):
    def __init__(self, parent, tr, maximum):
        super().__init__(parent, tr("levelup.title"), tr)
        self.roll = QSpinBox()
        self.roll.setRange(1, int(maximum))
        self.roll.setValue(1)
        self.form.addRow(tr("levelup.roll"), self.roll)
        self.setup_size(parent, "level_up")

    def value(self):
        return int(self.roll.value())
