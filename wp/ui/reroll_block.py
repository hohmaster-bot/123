"""The Rerolls block (package 38, owner decision 7; RULES/buffs.md "Rerolls").

One row per reroll grant of the character (view "rerolls": name, source, left / max): the button spends one
(spend_reroll; journal, undo); a grant whose rule is "manual" also has a restore button (restore_reroll). The program
never rolls: the block only counts. A layout block (panels.json "rerolls"), default in the right column under the
combat tab; the layout editor moves, resizes or hides it like any block.
"""
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from wp.ui.status_blocks import _Scroll, _clear

MANUAL = "manual"


class RerollsBlock(_Scroll):
    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell)
        self.reads = tuple(self.reads) + ("rerolls",)
        self.rows = ()
        self.widgets = {}

    def _read(self):
        self.rows = self.session.view("rerolls") if self.session.character is not None else ()

    def _show(self):
        if self._tr is None:
            return
        tr = self._tr
        _clear(self.list)
        self.widgets = {}
        for ref, _src, source, name, left, top, rule in self.rows:
            row = QWidget()
            hl = QHBoxLayout(row)
            hl.setContentsMargins(0, 0, 0, 0)
            lab = QLabel(tr("rerolls.row", name=name, source=source, left=left, max=top,
                            rule=tr("rerolls.rule." + rule)))
            lab.setWordWrap(True)
            hl.addWidget(lab, 1)
            use = QPushButton(tr("rerolls.use"))
            use.setObjectName("small")
            use.setEnabled(left > 0)
            use.clicked.connect(lambda _=False, r=ref: self.run("spend_reroll", ref=r))
            hl.addWidget(use)
            w = {"text": lab, "use": use}
            if rule == MANUAL:
                back = QPushButton(tr("rerolls.restore"))
                back.setObjectName("small")
                back.clicked.connect(lambda _=False, r=ref: self.run("restore_reroll", ref=r))
                hl.addWidget(back)
                w["restore"] = back
            self.widgets[ref] = w
            self.list.addWidget(row)
        if not self.rows:
            lab = QLabel(tr("rerolls.empty"))
            lab.setObjectName("muted")
            self.list.addWidget(lab)
        self.list.addStretch(1)
