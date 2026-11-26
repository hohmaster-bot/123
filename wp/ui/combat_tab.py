"""The right column: the tab bar and the COMBAT tab (package 34 part 2, Phase 5 step 5; UI_WISHES "Classic screen v2"
point 9).

TabsBlock: a tab bar with every planned tab (data/screen_blocks.json "tabs" or the layout item's own "tabs"); only
Combat has content now, any other tab shows an empty placeholder with its name in the combat block (no fake content).
Package 35 P1 (owner review 5): the tabs WRAP onto further rows when the block is narrow and back when it is wide (no
scroll, no clipping; dialog_logic.flow_rows); the profile field tab_rows (> 0) pins the number of rows (editor mode:
View > Editor mode, then the pin buttons of the block); the block height follows the rows; the saved layout is never
rewritten by a resize.
CombatBlock: combat on / off (start_combat / end_combat), Zero initiative (tick: pressed when every character has
acted and the circle ends; not tied to the character's own turn; package 35), End of cycle (end_cycle), the round;
actions as numbered one-colour squares (a click on a free one spends 1: the core spends the SMALLEST free number
first; spent ones grey; a click on a spent one returns one: return_action, package 35) and Restore = restore all
(restore_actions); the reaction squares (spend_reaction / return_reaction / restore_reactions); the attacks list
(statuses view "active": a click = use_attack); the quick-access grid (Session.quick_view: profile quick_cells 4-16,
quick_columns; a click = Session.run_quick). Every control is an existing Session command (D25).
"""
import importlib

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from wp.i18n import i18n
from wp.ui import combat_logic as cl
from wp.ui import dialog_logic as dl
from wp.ui.blocks import Block
from wp.ui.screen_blocks import SB
from wp.ui.status_blocks import _clear

COMBAT = "combat"
PAGE_TOPICS = ("log", "items", "training", "injuries", "notebook", "rest", "skills", "combat", "defense")  # pages
PAGES = {"journal": ("wp.ui.tab_journal", "JournalPage"), "settings": ("wp.ui.tab_settings", "SettingsPage"),
         "injuries": ("wp.ui.tab_pages", "InjuriesPage"), "drives": ("wp.ui.tab_pages", "DrivesPage"),
         "rest": ("wp.ui.tab_pages", "RestPage"), "inventory": ("wp.ui.tab_pages2", "InventoryPage"),
         "training": ("wp.ui.tab_pages2", "TrainingPage"), "skills": ("wp.ui.tab_pages2", "SkillsPage"),
         "feats": ("wp.ui.tab_pages2", "FeatsPage"), "catalogs": ("wp.ui.tab_pages2", "CatalogsPage"),
         "narrative": ("wp.ui.tab_narrative", "NarrativePage"), "race": ("wp.ui.tab_race", "RacePage")}
STEP = 1                               # a square click spends / returns one action / reaction
BUTTONS = ("combat", "zero", "cycle")  # package 35: "zero" = Zero initiative (the tick), no "end of turn"


class TabFlow(QWidget):
    """Checkable tab buttons laid out in rows (the API of a tab bar: count, tabText, setCurrentIndex)."""
    currentChanged = Signal(int)

    def __init__(self, on_height=None):
        super().__init__()
        self.buttons, self.pinned, self.gap, self.current = [], 0, 0, 0
        self.on_height = on_height
        self.row_list = []

    def addTab(self, text):
        b = QPushButton(text, self)
        b.setObjectName("tab")
        b.setCheckable(True)
        b.clicked.connect(lambda _=False, i=len(self.buttons): self.setCurrentIndex(i))
        self.buttons.append(b)
        self.relayout()

    def count(self):
        return len(self.buttons)

    def tabText(self, i):
        return self.buttons[i].text()

    def setTabText(self, i, text):
        self.buttons[i].setText(text)
        self.relayout()

    def currentIndex(self):
        return self.current

    def setCurrentIndex(self, i):
        changed = i != self.current
        self.current = i
        for k, b in enumerate(self.buttons):
            b.setChecked(k == i)
        if changed:
            self.currentChanged.emit(i)

    def set_pinned(self, rows):
        self.pinned = int(rows or 0)
        self.relayout()

    def set_gap(self, gap):
        self.gap = gap
        self.relayout()

    def rows_for(self, width):
        if self.pinned:
            return dl.pinned_rows(len(self.buttons), self.pinned)
        return dl.flow_rows([b.sizeHint().width() for b in self.buttons], width, self.gap)

    def heightForWidth(self, width):
        rows = self.rows_for(width)
        hs = [max(self.buttons[i].sizeHint().height() for i in r) for r in rows]
        return sum(hs) + self.gap * max(0, len(rows) - 1)

    def hasHeightForWidth(self):
        return True

    def relayout(self):
        rows = self.row_list = self.rows_for(max(1, self.width()))
        y = 0
        for r in rows:
            x, h = 0, max(self.buttons[i].sizeHint().height() for i in r)
            for i in r:
                w = self.buttons[i].sizeHint().width()
                self.buttons[i].setGeometry(x, y, w, h)
                x += w + self.gap
            y += h + self.gap
        need = max(0, y - self.gap)
        self.setMinimumHeight(need)
        if self.on_height is not None:
            self.on_height(need)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.relayout()


class TabsBlock(Block):
    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell)
        self.tabs = cl.tab_list(item, SB["tabs"])
        self.bar = TabFlow(self.fit_height)
        for _ in self.tabs:
            self.bar.addTab("")
        self.bar.setCurrentIndex(0)
        self.bar.currentChanged.connect(self.choose)
        self.box.addWidget(self.bar, 1)
        self.pin_row = QWidget()                 # editor mode only: pin the rows (profile field tab_rows)
        pr = QHBoxLayout(self.pin_row)
        pr.setContentsMargins(0, 0, 0, 0)
        self.pin_buttons = {}
        for key in ("pin", "fewer", "more"):
            b = QPushButton()
            b.setObjectName("small")
            b.clicked.connect(lambda _=False, k=key: self.pin(k))
            self.pin_buttons[key] = b
            pr.addWidget(b)
        pr.addStretch(1)
        self.pin_row.hide()
        self.box.addWidget(self.pin_row)
        self.session = None

    def fit_height(self, flow_height):
        """The block height follows the rows of tabs (the width is the layout's; nothing is saved)."""
        m = self.box.contentsMargins()
        title = self.title.sizeHint().height() if not self.title.isHidden() else 0
        row = getattr(self, "pin_row", None)
        pin = (row.sizeHint().height() + self.box.spacing()) if row is not None and not row.isHidden() else 0
        self.flow_height = m.top() + m.bottom() + title + self.box.spacing() + flow_height + pin
        self.setFixedHeight(self.flow_height)
        self.updateGeometry()

    def base_size(self):
        from PySide6.QtCore import QSize
        return QSize(self.saved.width(), getattr(self, "flow_height", self.saved.height()))

    def fit_content(self):
        self.bar.relayout()                    # the rows follow the new font; the height follows the rows
        self.setFixedWidth(max(self.saved.width(), self.minimumSizeHint().width()))

    def set_compact(self, no_caption, no_details):
        super().set_compact(no_caption, no_details)
        self.bar.relayout()

    def rows(self):
        return len(self.bar.row_list)

    def pin(self, key):
        """Editor mode: pin the current number of rows / one row fewer / more; pin again = automatic (0)."""
        if self.session is None or self.win is None:
            return None
        prof = self.session.profile("classic")
        now = int(prof.get("tab_rows", 0) or 0)
        if key == "pin":
            rows = 0 if now else self.rows()
        else:
            rows = max(1, (now or self.rows()) + (1 if key == "more" else -1))
        return self.win.session_settings("profile_set", mode="classic", pid=prof.get("id"), tab_rows=rows)

    def set_gap(self, gap):
        super().set_gap(gap)
        self.bar.set_gap(gap)

    def refresh(self, session):
        super().refresh(session)
        self.session = session
        self.pin_row.setVisible(bool(session.editor_mode))
        self.bar.set_pinned(session.profile("classic").get("tab_rows", 0))

    def apply_look(self, colors, scale, session):
        self.session = session
        self.bar.set_pinned(session.profile("classic").get("tab_rows", 0))

    def select(self, tab):
        """Show one tab by its id (the bottom strip's Journal button)."""
        if tab in self.tabs:
            self.bar.setCurrentIndex(self.tabs.index(tab))
            if self.win is not None and COMBAT in self.win.blocks:
                self.win.blocks[COMBAT].show_tab(tab)
        return tab in self.tabs

    def choose(self, index):
        if self.win is not None and COMBAT in self.win.blocks:
            self.win.blocks[COMBAT].show_tab(self.tabs[index])

    def retranslate(self, tr):
        super().retranslate(tr)
        for i, t in enumerate(self.tabs):
            self.bar.setTabText(i, tr("tab." + t))
        pinned = bool(self.session is not None and self.session.profile("classic").get("tab_rows", 0))
        self.pin_buttons["pin"].setText(tr("tabs.auto") if pinned else tr("tabs.pin"))
        self.pin_buttons["fewer"].setText(tr("tabs.fewer"))
        self.pin_buttons["more"].setText(tr("tabs.more"))


class CombatBlock(Block):
    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell)
        self.stack = QStackedWidget()
        self.box.addWidget(self.stack, 1)
        self.page = QWidget()
        lay = QVBoxLayout(self.page)
        lay.setContentsMargins(0, 0, 0, 0)
        top = QHBoxLayout()
        self.buttons = {}
        for key in BUTTONS:
            b = QPushButton()
            b.setObjectName("small")
            b.clicked.connect(lambda _=False, k=key: self.press(k))
            self.buttons[key] = b
            top.addWidget(b)
        lay.addLayout(top)
        self.round = QLabel()
        self.round.setObjectName("muted")
        lay.addWidget(self.round)
        self.actions_row, self.reactions_row = QHBoxLayout(), QHBoxLayout()
        self.actions_label, self.reactions_label = QLabel(), QLabel()
        for label, row in ((self.actions_label, self.actions_row), (self.reactions_label, self.reactions_row)):
            line = QHBoxLayout()
            line.addWidget(label)
            line.addLayout(row)
            line.addStretch(1)
            lay.addLayout(line)
        self.attacks_title = QLabel()
        self.attacks_title.setObjectName("muted")
        lay.addWidget(self.attacks_title)
        self.attacks = QVBoxLayout()
        lay.addLayout(self.attacks)
        self.quick_title = QLabel()
        self.quick_title.setObjectName("muted")
        lay.addWidget(self.quick_title)
        self.grid = QGridLayout()
        lay.addLayout(self.grid)
        self.message = QLabel()
        self.message.setObjectName("message")
        self.message.setWordWrap(True)
        lay.addWidget(self.message)
        lay.addStretch(1)
        self.placeholder = QLabel()
        self.placeholder.setObjectName("muted")
        self.placeholder.setWordWrap(True)
        self.stack.addWidget(self.page)
        self.stack.addWidget(self.placeholder)
        self.tab = COMBAT
        self.pages = {}                      # the other implemented tabs (package 35): built on first use
        self.reads = tuple(self.reads) + ("statuses", "attacks", "sheet", "resources") + PAGE_TOPICS
        self._tr, self.session, self.combat, self.active, self.quick = None, None, None, None, None
        self.squares, self.reaction_squares, self.quick_cells = [], [], []

    # ------------------------------------------------------------ tabs
    def show_tab(self, tab):
        self.tab = tab
        if tab in PAGES and tab in SB["implemented_tabs"] and tab not in self.pages:
            mod, cls = PAGES[tab]
            page = getattr(importlib.import_module(mod), cls)(self)
            self.pages[tab] = page
            self.stack.addWidget(page)
            if self._tr is not None:
                page.retranslate(self._tr)
            if self.session is not None:
                page.refresh(self.session)
        self._show()

    def tab_page(self, tab):
        """The page of an implemented tab (built when first needed; tests)."""
        if tab not in self.pages:
            keep = self.tab
            self.show_tab(tab)
            self.show_tab(keep)
        return self.pages.get(tab)

    def retranslate(self, tr):
        super().retranslate(tr)
        self._tr = tr
        for page in self.pages.values():
            page.retranslate(tr)
        self._show()

    def refresh(self, session):
        super().refresh(session)
        self.session = session
        for page in self.pages.values():
            page.refresh(session)
        if session.character is not None:
            self.combat = session.view("combat")
            self.active = session.view("statuses")["active"]
            self.quick = session.quick_view("classic")
        self._show()

    def apply_look(self, colors, scale, session):
        """A settings change (quick buttons, profile quick fields) re-reads the quick grid and the pages."""
        for page in self.pages.values():
            page.refresh(session)
        if session.character is not None and self.combat is not None:
            self.session = session
            self.quick = session.quick_view("classic")
            self._show()

    # ------------------------------------------------------------ show
    def _show(self):
        if self._tr is None:
            return
        tr = self._tr
        if self.tab in self.pages:
            self.title.setText(tr("tab." + self.tab))
            self.stack.setCurrentWidget(self.pages[self.tab])
            return
        if self.tab not in SB["implemented_tabs"] or self.tab != COMBAT:
            self.title.setText(tr("tab." + self.tab))
            self.placeholder.setText(tr("tab.placeholder", name=tr("tab." + self.tab)))
            self.stack.setCurrentWidget(self.placeholder)
            return
        self.title.setText(tr(self.entry["title"]))
        self.stack.setCurrentWidget(self.page)
        if self.combat is None:
            return
        c = self.combat
        self.buttons["combat"].setText(tr("combat.end") if c["in_combat"] else tr("combat.start"))
        self.buttons["zero"].setText(tr("combat.zero"))
        self.buttons["zero"].setToolTip(tr("combat.zero_hint"))
        self.buttons["cycle"].setText(tr("combat.cycle"))
        self.round.setText(tr("combat.round", n=c["round"]) if c["in_combat"] else tr("combat.out"))
        self.actions_label.setText(tr("combat.actions"))
        self.reactions_label.setText(tr("combat.reactions"))
        self.squares = self._squares(self.actions_row, c["action_squares"], "action", "spend_actions",
                                     "return_action", "restore_actions")
        self.reaction_squares = self._squares(self.reactions_row, c["reaction_squares"], "reaction",
                                              "spend_reaction", "return_reaction", "restore_reactions")
        self.attacks_title.setText(tr("combat.attacks"))
        _clear(self.attacks)
        for a in getattr(self.active, "attacks", ()):
            b = QPushButton("%s %+d (%s)" % (a.weapon or a.record, a.to_hit, a.damage))
            b.setObjectName("small")
            b.clicked.connect(lambda _=False, rid=a.record: self.run("use_attack", rid=rid))
            self.attacks.addWidget(b)
        self._quick_grid()

    def _squares(self, row, squares, kind, spend, give_back, restore):
        _clear(row)
        out = []
        for n, spent in squares:
            b = QPushButton(str(n))
            b.setObjectName("%s_spent" % kind if spent else "%s_square" % kind)
            b.setProperty("spent", bool(spent))
            b.setToolTip(self._tr("combat.square_return" if spent else "combat.square_spend"))
            b.clicked.connect(lambda _=False, s=spent: self.run(give_back if s else spend, n=STEP))
            row.addWidget(b)
            out.append(b)
        r = QPushButton(self._tr("combat.restore"))
        r.setToolTip(self._tr("combat.restore_hint"))
        r.setObjectName("small")
        r.clicked.connect(lambda _=False: self.run(restore))
        row.addWidget(r)
        return out

    def _quick_grid(self):
        _clear(self.grid)
        q = SB["quick"]
        n, cols, _ = cl.grid_shape((self.quick or {}).get("cells") or q["default"], (self.quick or {}).get("columns"),
                                   q["lo"], q["hi"])
        buttons = list((self.quick or {}).get("buttons", ()))
        self.quick_title.setText(self._tr("combat.quick"))
        self.quick_cells = []
        for i in range(n):
            if i < len(buttons):
                bid, label, _cost = buttons[i]
                b = QPushButton(label)
                b.clicked.connect(lambda _=False, bid=bid: self.quick_press(bid))
            else:
                b = QPushButton("")
                b.setEnabled(False)
            b.setObjectName("quick_cell")
            self.grid.addWidget(b, i // cols, i % cols)
            self.quick_cells.append(b)

    # ------------------------------------------------------------ commands
    def _result(self, r):
        if not r.ok:
            text = i18n.text_for(r, self.win.lang() if self.win is not None else i18n.BASE)
            self.message.setText(text)
            if self.win is not None:
                self.win.messages.append(text)
        else:
            self.message.setText("")
        self.message.setVisible(bool(self.message.text()))
        return r

    def run(self, command, **params):
        return self._result(self.session.dispatch(command, **params))

    def step(self, result):
        """Undo / redo of the Journal tab: a refusal shows its text."""
        return self._result(result)

    def quick_press(self, bid):
        return self._result(self.session.run_quick(bid))

    def press(self, key):
        if key == "combat":
            return self.run("end_combat" if self.combat["in_combat"] else "start_combat")
        return self.run("tick" if key == "zero" else "end_cycle")
