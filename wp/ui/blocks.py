"""Blocks of the Classic window shell (package 32, UI_WISHES "Classic screen v2"). A block is a frame with its
translated title; it reads only session.view(...) and changes the character only through the Session. Real data:
the experience strip (training.experience; the level-up button, package 33), the identity block (sheet: name, class,
level) and the resources block (wp/ui/resources_block.py, package 33); every other block is a placeholder naming the
views it will read (wp/panels registry.reads).

make(pid, item, shell) -> the block of a layout item; block.reads = the views it shows (refresh on their topics);
block.retranslate(tr), block.refresh(session); block.sizeHint() = the saved size of the layout item.
"""
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QPushButton, QSizePolicy, QVBoxLayout

from wp.panels import registry

PCT_MAX = 100                          # the progress bar runs 0..100 (progress_pct of the experience view)
NEWLINE = chr(10)                      # one reminder per line in the message box
SHELL_ROLL_MAX = 1000                  # the roll spin box upper end (the core refuses a roll above the die)


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
        self.win = None

    def attach(self, win):
        self.win = win

    def set_compact(self, no_caption, no_details):
        """Small window (package 34): hide the caption, then the details (small notes); the size never changes."""
        self.title.setVisible(not no_caption)
        for w in self.findChildren(QLabel):
            if w.objectName() == "muted" and w is not self.title:
                w.setVisible(not no_details)

    def apply_look(self, colors, scale, session):
        """Theme colours and the scale after a settings change (blocks that paint use them)."""

    def base_size(self):
        """The size the layout asks for (the saved one; a few blocks compute their own height)."""
        return self.saved

    def fit_content(self):
        """Package 36 P1.5 (owner: "I changed the font and the layout drifted"): after a font / scale change the block
        is at least as large as its content needs (the saved size stays the lower bound; nothing is saved)."""
        lay = self.layout()
        if lay is None:
            return
        lay.invalidate()
        need, base = lay.minimumSize(), self.base_size()
        if self.strip:
            self.setFixedHeight(max(base.height(), need.height()))
            self.setMinimumWidth(max(int(self.entry["min_size"][0]), need.width()))
        else:
            self.setFixedSize(max(base.width(), need.width()), max(base.height(), need.height()))
        self.updateGeometry()

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
    """The glass bar (progress_pct), the total, the goal (always exp.level_cost, package 33), the "Level up" button
    (enabled at can_level_up: asks "Raise the level?", then the hit-die roll, runs level_up and shows the reminders)
    and the "Experience log" button (opens in a later step)."""

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
        self.level_button = QPushButton()
        self.level_button.setEnabled(False)
        self.level_button.clicked.connect(self.level_up)
        self.box.addWidget(self.bar, 1)
        self.box.addWidget(self.total)
        self.box.addWidget(self.goal)
        self.box.addWidget(self.level_button)
        self.box.addWidget(self.log_button)
        self.dialog = None
        self.session = None
        self._tr = None
        self._xp = None

    def retranslate(self, tr):
        super().retranslate(tr)
        self._tr = tr
        self.log_button.setText(tr("xp.log"))
        self.level_button.setText(tr("levelup.button"))
        self._show()

    def refresh(self, session):
        super().refresh(session)
        self.session = session
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
        self.level_button.setEnabled(bool(xp.get("can_level_up")))

    def level_up(self):
        """Ask, then the roll dialog; the command runs on OK (window.ask / window.info; tests answer for the user)."""
        from wp.ui import dialogs
        win, tr = self.win, self._tr
        if win is None or self.session is None or not win.ask(tr("levelup.ask")):
            return None
        dlg = dialogs.RollDialog(win, tr, SHELL_ROLL_MAX)
        dlg.accepted.connect(lambda: self.apply_level_up(dlg.value()))
        self.dialog = dlg
        if not win.quiet:
            dlg.open()
        return dlg

    def apply_level_up(self, roll):
        win, tr = self.win, self._tr
        r = self.session.dispatch("level_up", hp_roll=int(roll))
        if not r.ok:
            win.refusal(r)
            return r
        lines = [tr(k, values=tuple(v)) for k, v in dict(r.info).get("reminders", ())]
        lines += [tr("warning." + w) for w in dict(r.info).get("warnings", ())]
        win.info(tr("levelup.done", level=dict(r.info).get("level")), NEWLINE.join(lines))
        return r


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
    if pid == "resources":
        from wp.ui.resources_block import ResourcesBlock      # imports Block from here
        return ResourcesBlock(pid, item, shell)
    if pid in ("statuses", "favorites", "reminders"):
        from wp.ui import status_blocks as stb               # package 34 part 2
        return {"statuses": stb.StatusesBlock, "favorites": stb.FavoritesBlock,
                "reminders": stb.RemindersBlock}[pid](pid, item, shell)
    if pid == "rerolls":
        from wp.ui.reroll_block import RerollsBlock           # package 38
        return RerollsBlock(pid, item, shell)
    if pid in ("tabs", "combat"):
        from wp.ui import combat_tab as ct
        return (ct.TabsBlock if pid == "tabs" else ct.CombatBlock)(pid, item, shell)
    if pid == "bottom_strip":
        from wp.ui.bottom_strip import BottomStrip            # package 35 P2
        return BottomStrip(pid, item, shell)
    if pid in ("parameters", "ac_block"):
        from wp.ui import screen_blocks as sb                 # package 34
        return (sb.ParametersBlock if pid == "parameters" else sb.AcBlock)(pid, item, shell)
    return TYPES.get(pid, Placeholder)(pid, item, shell)
