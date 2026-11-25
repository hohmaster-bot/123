"""The right column: the tab bar and the COMBAT tab (package 34 part 2, Phase 5 step 5; UI_WISHES "Classic screen v2"
point 9).

TabsBlock: a tab bar with every planned tab (data/screen_blocks.json "tabs" or the layout item's own "tabs"); only
Combat has content now, any other tab shows an empty placeholder with its name in the combat block (no fake content).
CombatBlock: combat on / off (start_combat / end_combat), End of turn (tick), End of cycle (end_cycle), the round;
actions as numbered one-colour squares (a click spends 1: the core spends the SMALLEST free number first; spent ones
grey) and Restore (restore_actions); the reaction squares (spend_reaction / restore_reactions); the attacks list
(statuses view "active": a click = use_attack); the quick-access grid (Session.quick_view: profile quick_cells 4-16,
quick_columns; a click = Session.run_quick). Every control is an existing Session command (D25).
"""
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QTabBar, QVBoxLayout, \
    QWidget

from wp.i18n import i18n
from wp.ui import combat_logic as cl
from wp.ui.blocks import Block
from wp.ui.screen_blocks import SB
from wp.ui.status_blocks import _clear

COMBAT = "combat"
STEP = 1                               # a square click spends one action / reaction


class TabsBlock(Block):
    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell)
        self.tabs = cl.tab_list(item, SB["tabs"])
        self.bar = QTabBar()
        self.bar.setUsesScrollButtons(True)
        self.bar.setExpanding(False)
        for _ in self.tabs:
            self.bar.addTab("")
        self.bar.currentChanged.connect(self.choose)
        self.box.addWidget(self.bar)
        self.box.addStretch(1)

    def choose(self, index):
        if self.win is not None and COMBAT in self.win.blocks:
            self.win.blocks[COMBAT].show_tab(self.tabs[index])

    def retranslate(self, tr):
        super().retranslate(tr)
        for i, t in enumerate(self.tabs):
            self.bar.setTabText(i, tr("tab." + t))


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
        for key in ("combat", "turn", "cycle"):
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
        self.reads = tuple(self.reads) + ("statuses", "attacks", "sheet", "resources")
        self._tr, self.session, self.combat, self.active, self.quick = None, None, None, None, None
        self.squares, self.reaction_squares, self.quick_cells = [], [], []

    # ------------------------------------------------------------ tabs
    def show_tab(self, tab):
        self.tab = tab
        self._show()

    def retranslate(self, tr):
        super().retranslate(tr)
        self._tr = tr
        self._show()

    def refresh(self, session):
        super().refresh(session)
        self.session = session
        if session.character is not None:
            self.combat = session.view("combat")
            self.active = session.view("statuses")["active"]
            self.quick = session.quick_view("classic")
        self._show()

    def apply_look(self, colors, scale, session):
        """A settings change (quick buttons, profile quick fields) re-reads the quick grid."""
        if session.character is not None and self.combat is not None:
            self.session = session
            self.quick = session.quick_view("classic")
            self._show()

    # ------------------------------------------------------------ show
    def _show(self):
        if self._tr is None:
            return
        tr = self._tr
        if self.tab not in SB["implemented_tabs"]:
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
        self.buttons["turn"].setText(tr("combat.turn"))
        self.buttons["cycle"].setText(tr("combat.cycle"))
        self.round.setText(tr("combat.round", n=c["round"]) if c["in_combat"] else tr("combat.out"))
        self.actions_label.setText(tr("combat.actions"))
        self.reactions_label.setText(tr("combat.reactions"))
        self.squares = self._squares(self.actions_row, c["action_squares"], "action", "spend_actions",
                                     "restore_actions")
        self.reaction_squares = self._squares(self.reactions_row, c["reaction_squares"], "reaction",
                                              "spend_reaction", "restore_reactions")
        self.attacks_title.setText(tr("combat.attacks"))
        _clear(self.attacks)
        for a in getattr(self.active, "attacks", ()):
            b = QPushButton("%s %+d (%s)" % (a.weapon or a.record, a.to_hit, a.damage))
            b.setObjectName("small")
            b.clicked.connect(lambda _=False, rid=a.record: self.run("use_attack", rid=rid))
            self.attacks.addWidget(b)
        self._quick_grid()

    def _squares(self, row, squares, kind, spend, restore):
        _clear(row)
        out = []
        for n, spent in squares:
            b = QPushButton(str(n))
            b.setObjectName("%s_spent" % kind if spent else "%s_square" % kind)
            b.setEnabled(not spent)
            b.clicked.connect(lambda _=False: self.run(spend, n=STEP))
            row.addWidget(b)
            out.append(b)
        r = QPushButton(self._tr("combat.restore"))
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

    def quick_press(self, bid):
        return self._result(self.session.run_quick(bid))

    def press(self, key):
        if key == "combat":
            return self.run("end_combat" if self.combat["in_combat"] else "start_combat")
        return self.run("tick" if key == "turn" else "end_cycle")
