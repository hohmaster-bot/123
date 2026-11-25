"""Blocks of the Classic window shell (package 32, UI_WISHES "Classic screen v2"). A block is a frame with its
translated title; it reads only session.view(...) and never changes the character. Two blocks show real data:
the experience strip (training.experience) and the identity block (sheet: name, class, level); every other block is
a placeholder naming the views it will read (wp/panels registry.reads).

make(pid, item, shell) -> the block of a layout item; block.reads = the views it shows (refresh on their topics);
block.retranslate(tr), block.refresh(session); block.sizeHint() = the saved size of the layout item.
"""
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QPushButton, QSizePolicy, QVBoxLayout

from wp.panels import registry

PCT_MAX = 100                          # the progress bar runs 0..100 (progress_pct of the experience view)


class Block(QFrame):
    def __init__(self, pid, item, shell):
        super().__init__()
        self.pid, self.item, self.entry = pid, dict(item), registry.get(pid)
        self.reads = registry.reads(pid)
        self.strip = item.get("dock") in shell["strips"]
        self.setObjectName("strip" if self.strip else "block")
        self.saved = QSize(*[int(v) for v in item.get("size") or self.entry["defaults"]["classic"]["size"]])
        if self.strip:                 # a strip takes the whole width; its height is the saved one
            self.setMinimumWidth(int(self.entry["min_size"][0]))
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.setFixedHeight(self.saved.height())
        else:                          # a column block keeps its saved size (small windows scroll for now)
            self.setFixedSize(self.saved)
        self.title = QLabel()
        self.title.setObjectName("block_title")
        self.box = QHBoxLayout(self) if self.strip else QVBoxLayout(self)
        self.box.addWidget(self.title)
        self.refreshed = 0             # how many times the block re-read its views (tests)

    def sizeHint(self):
        return self.saved

    def set_gap(self, gap):
        self.box.setContentsMargins(gap, gap, gap, gap)
        self.box.setSpacing(gap)

    def retranslate(self, tr):
        self.title.setText(tr(self.entry["title"]))

    def refresh(self, session):
        self.refreshed += 1


class Placeholder(Block):
    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell)
        self.note = QLabel()
        self.note.setObjectName("muted")
        self.note.setWordWrap(True)
        self.box.addWidget(self.note)
        self.box.addStretch(1)

    def retranslate(self, tr):
        super().retranslate(tr)
        views = ", ".join(self.reads) or "-"
        self.note.setText("%s; %s" % (tr("shell.placeholder"), tr("shell.reads", views=views)))


class ExperienceStrip(Block):
    """The glass bar (progress_pct), the total, the goal and the "Experience log" button (opens in a later step)."""

    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell)
        self.bar = QProgressBar()
        self.bar.setObjectName("xp")
        self.bar.setRange(0, PCT_MAX)
        self.bar.setTextVisible(True)
        self.total = QLabel()
        self.total.setObjectName("big")
        self.goal = QLabel()
        self.log_button = QPushButton()
        self.log_button.setEnabled(False)
        self.box.addWidget(self.bar, 1)
        self.box.addWidget(self.total)
        self.box.addWidget(self.goal)
        self.box.addWidget(self.log_button)
        self._tr = None
        self._xp = None

    def retranslate(self, tr):
        super().retranslate(tr)
        self._tr = tr
        self.log_button.setText(tr("xp.log"))
        self._show()

    def refresh(self, session):
        super().refresh(session)
        self._xp = dict(session.view("training")["experience"]) if session.character is not None else None
        self._show()

    def _show(self):
        if self._tr is None or self._xp is None:
            return
        xp, tr = self._xp, self._tr
        pct = xp.get("progress_pct")
        self.bar.setValue(int(pct) if pct is not None else 0)
        self.bar.setFormat("%d%%" % int(pct) if pct is not None else "")
        self.total.setText(tr("xp.total", total=xp["total"]))
        goal = xp.get("next_level_at")
        self.goal.setText(tr("xp.goal", goal=goal) if goal else tr("xp.no_goal"))


class IdentityBlock(Block):
    """The portrait (a placeholder frame for now), the name, the class and the level (sheet view)."""

    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell)
        row = QHBoxLayout()
        self.portrait = QLabel()
        self.portrait.setObjectName("portrait")
        self.portrait.setAlignment(Qt.AlignCenter)
        self.portrait.setFixedSize(QSize(*shell["portrait"]))
        col = QVBoxLayout()
        self.name = QLabel()
        self.name.setObjectName("big")
        self.klass = QLabel()
        self.level = QLabel()
        for w in (self.name, self.klass, self.level):
            col.addWidget(w)
        col.addStretch(1)
        row.addWidget(self.portrait)
        row.addLayout(col, 1)
        self.box.addLayout(row)
        self.box.addStretch(1)
        self._tr = None
        self._sheet = None

    def retranslate(self, tr):
        super().retranslate(tr)
        self._tr = tr
        self.portrait.setText(tr("identity.portrait"))
        self._show()

    def refresh(self, session):
        super().refresh(session)
        self._sheet = session.view("sheet") if session.character is not None else None
        self._show()

    def _show(self):
        if self._tr is None or self._sheet is None:
            return
        sh, tr = self._sheet, self._tr
        self.name.setText(sh.get("name", ""))
        info = sh.get("class")
        self.klass.setText(getattr(info, "name", "") or sh.get("class_id") or tr("identity.no_class"))
        self.level.setText(tr("identity.level", level=sh["level"]))


TYPES = {"experience_strip": ExperienceStrip, "identity": IdentityBlock}


def make(pid, item, shell):
    return TYPES.get(pid, Placeholder)(pid, item, shell)
