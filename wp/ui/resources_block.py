"""The RESOURCES block of the Classic window (package 33, Phase 5 step 2; UI_WISHES "Classic screen v2" points 3-6).

Top to bottom: HP, balance, spirit, mana (order: data/resources.json), then the class pools (the first three large,
the rest compact in their own scroll area; app settings pool_order / pools_large). Each row: the label (mana: the
overload chip), the value "cur / max" (over the max in the warning colour, never clamped), the horizontal tube
(wp/ui/tube.py) and the buttons under it. A click on a tube opens the value EDITOR (a correction: "+N" / "-N" /
a number -> adjust_value / set_value; HP: a second field = set_temp_hp). The mechanics are buttons: HP Take damage
(amount + damage type -> take_damage) and Heal (restore), balance Damage to balance (damage_to_balance), spirit /
mana / pools -1 / +1 (adjust_value), mana overload - / + (adjust_value overload); the player's own buttons = the app
quick buttons of group "resource:<id>" (Session.run_quick). Refusals, warnings and reminders show as their i18n text
in the message line under the block (never blocking, no traceback).
Reads only session.view("resources") and the app settings; changes the character only through the Session (D25).
"""
import io
import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from wp.i18n import i18n
from wp.ui import dialogs
from wp.ui import tube_logic as tl
from wp.ui.blocks import Block
from wp.ui.tube import Tube

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "resources.json")
POOL = "pool"
HP = "hp"
MANA = "mana"
OVERLOAD = "overload"
STEP = 1                               # the -1 / +1 buttons
ROW_GAP = 2                            # px between the label, the tube and the buttons of one row


def load(path=DATA):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


RES = load()


def _repolish(w, name):
    if w.objectName() != name:
        w.setObjectName(name)
        w.style().unpolish(w)
        w.style().polish(w)


class Row(QWidget):
    """One resource: label (+ chip), value text, tube, buttons."""

    def __init__(self, block, rid, kind, name="", compact=False):
        super().__init__()
        self.block, self.rid, self.kind, self.name, self.compact = block, rid, kind, name, compact
        self.data = {"current": 0, "max": 0, "over_max": False}
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(ROW_GAP)
        top = QHBoxLayout()
        self.label = QLabel(self)
        self.chip = QLabel(self)
        self.chip.setObjectName("chip")
        self.chip.setVisible(rid == MANA)
        self.value = QLabel(self)
        self.value.setObjectName("value")
        self.value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top.addWidget(self.label)
        top.addWidget(self.chip)
        top.addStretch(1)
        top.addWidget(self.value)
        self.tube = Tube(rid, RES["tokens"].get(kind, POOL))
        self.tube.clicked.connect(block.open_editor)
        self.buttons = QHBoxLayout()
        if compact:                    # one line: name, thin bar with the number, -1 / +1, own buttons
            self.buttons.addWidget(self.label)
            self.buttons.addWidget(self.tube, 1)
        self.button_widgets = {}
        for b in RES["buttons"].get(kind, ()):
            w = QPushButton(self)
            w.setObjectName("small")
            w.clicked.connect(lambda _=False, b=b: block.press(self.rid, b))
            self.button_widgets[b] = w
            self.buttons.addWidget(w)
        self.custom = {}
        self.buttons.addStretch(1)
        if compact:
            lay.addLayout(self.buttons)
            self.value.hide()
            self.chip.hide()
        else:
            lay.addLayout(top)
            lay.addWidget(self.tube)
            lay.addLayout(self.buttons)

    def set_custom(self, buttons, session):
        for bid in [b for b in self.custom if b not in dict(buttons)]:
            self.custom.pop(bid).deleteLater()
        for bid, label in buttons:
            if bid not in self.custom:
                w = QPushButton(self)
                w.setObjectName("small")
                w.clicked.connect(lambda _=False, bid=bid: self.block.quick(bid))
                self.custom[bid] = w
                self.buttons.insertWidget(self.buttons.count() - 1, w)
            self.custom[bid].setText(label)

    def show_data(self, data, tr, overload=0, temp=0, step=0, temp_step=0):
        self.data = dict(data)
        cur, mx = int(data["current"]), int(data["max"])
        self.label.setText(self.name or tr("resource." + self.rid))
        self.value.setText("%d / %d" % (cur, mx))
        _repolish(self.value, "over_max" if tl.over_max(cur, mx) else "value")
        if self.rid == MANA:
            self.chip.setText(tr("resources.overload", n=int(overload)))
        self.tube.set_values(cur, mx, temp, step, temp_step)
        for b, w in self.button_widgets.items():
            w.setText(tr("resources.button." + b))


class ResourcesBlock(Block):
    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell)
        self.win = None
        self.session = None
        self._tr = None
        self.view = None
        self.rows = {}
        self.inner = QWidget()
        self.inner.setObjectName("resources_inner")
        self.main = QVBoxLayout(self.inner)
        self.main.setContentsMargins(0, 0, 0, 0)
        for rid in RES["order"]:
            self.rows[rid] = Row(self, rid, rid)
            self.main.addWidget(self.rows[rid])
        self.large = QVBoxLayout()
        self.main.addLayout(self.large)
        self.compact_box = QWidget()
        self.compact = QVBoxLayout(self.compact_box)
        self.compact.setContentsMargins(0, 0, 0, 0)
        self.compact_scroll = QScrollArea()
        self.compact_scroll.setWidgetResizable(True)
        self.compact_scroll.setWidget(self.compact_box)
        self.compact_scroll.setObjectName("compact_pools")
        self.main.addWidget(self.compact_scroll)
        self.main.addStretch(1)
        self.box.addWidget(self.inner, 1)
        self.message = QLabel()
        self.message.setObjectName("message")
        self.message.setWordWrap(True)
        self.box.addWidget(self.message)
        self.pool_ids = ((), ())
        self.dialog = None             # the last dialog opened (tests fill it)
        self.colors, self.scale = {}, 1.0

    # ------------------------------------------------------------ wiring
    def attach(self, win):
        self.win = win

    def tr(self, key, **params):
        return self._tr(key, **params) if self._tr else key

    def retranslate(self, tr):
        super().retranslate(tr)
        self._tr = tr
        self._show()

    def refresh(self, session):
        super().refresh(session)
        self.session = session
        self.view = session.view("resources") if session.character is not None else None
        self._show()

    def apply_look(self, colors, scale, session):
        """After a settings change: the look and the view again (own quick buttons are app settings)."""
        self.colors, self.scale, self.session = dict(colors), float(scale), session
        if session.character is not None:
            self.view = session.view("resources")
        self._show()

    # ------------------------------------------------------------ pools and the look
    def _pools(self):
        pools = tuple(self.view.get("pools", ()))
        s = self.session
        big, small = tl.split_pools(pools, s.setting("pool_order"), s.setting("pools_large"), RES["large_pools"])
        ids = (tuple(p[0] for p in big), tuple(p[0] for p in small))
        if ids != self.pool_ids:
            for rid in [r for r in self.rows if r.startswith(POOL + ":")]:
                self.rows.pop(rid).deleteLater()
            for pid, name, _ in big:
                self.rows[POOL + ":" + pid] = Row(self, POOL + ":" + pid, POOL, name)
                self.large.addWidget(self.rows[POOL + ":" + pid])
            for pid, name, _ in small:
                self.rows[POOL + ":" + pid] = Row(self, POOL + ":" + pid, POOL, name, compact=True)
                self.compact.addWidget(self.rows[POOL + ":" + pid])
            self.pool_ids = ids
        self.compact_scroll.setVisible(bool(small))
        return {POOL + ":" + pid: data for pid, _, data in pools}

    def tube_height(self, kind, n_rows):
        """The tube height in px and the mode: resource_size times the scale, shrunk to fit the block when the
        auto-switch is on (big -> medium -> thin bar with the number)."""
        s = self.session
        size = dict(s.setting("resource_size"))
        h = float((size.get(kind) or size.get(POOL))[1]) * self.scale
        w = float((size.get(kind) or size.get(POOL))[0]) * self.scale
        auto = bool(s.setting("resource_autoswitch"))
        if auto and n_rows:
            fit = (self.saved.height() - RES["block_overhead"] * self.scale) / n_rows - RES["row_overhead"] * self.scale
            h = min(h, fit)
        mode = tl.pick_mode(h / self.scale, auto, RES["modes"])
        if mode == "thin":
            h = max(h, RES["thin_min"] * self.scale)
        return w, h, mode

    def _show(self):
        if self._tr is None or self.view is None or self.session is None:
            return
        v, s, tr = self.view, self.session, self._tr
        pools = self._pools()
        style = s.setting("resource_style")
        seg = dict(s.setting("resource_segments"))
        buttons = dict(v.get("buttons", {}))
        n_rows = len(RES["order"]) + len(self.pool_ids[0])
        for rid, row in self.rows.items():
            kind = row.kind
            data = pools.get(rid) if kind == POOL else v[rid]
            if data is None:
                continue
            w, h, mode = self.tube_height(kind, 0 if row.compact else n_rows)
            if row.compact:
                mode = "thin"
            temp = v.get("temp_hp", 0) if rid == HP else 0
            row.tube.set_look(style, mode, self.colors, w, h)
            row.show_data(data, tr, v.get(OVERLOAD, 0), temp, seg.get(kind, seg.get(POOL, 0)),
                          seg.get("temp_hp", RES["temp_step"]))
            row.value.setVisible(mode != "thin" and not row.compact)
            row.set_custom(buttons.get(rid, ()), s)

    # ------------------------------------------------------------ commands (only through the Session)
    def say(self, text):
        self.message.setText(text)
        if self.win is not None:
            self.win.messages.append(text)

    def _result(self, r):
        lang = self.win.lang() if self.win is not None else i18n.BASE
        if not r.ok:
            self.say(i18n.text_for(r, lang))
            return r
        info = dict(r.info or {})
        lines = [self.tr(k, values=tuple(vals)) for k, vals in info.get("reminders", ())]
        lines += [self.tr("warning." + w) for w in info.get("warnings", ())]
        self.say("; ".join(lines))
        return r

    def run(self, command, **params):
        return self._result(self.session.dispatch(command, **params))

    def quick(self, bid):
        return self._result(self.session.run_quick(bid))

    def press(self, rid, button):
        if button in ("minus", "plus"):
            return self.run("adjust_value", resource=rid, delta=STEP if button == "plus" else -STEP)
        if button in ("overload_minus", "overload_plus"):
            return self.run("adjust_value", resource=OVERLOAD, delta=STEP if button == "overload_plus" else -STEP)
        types = tuple(self.view.get("damage_types", ())) if button == "take_damage" else ()
        dlg = dialogs.AmountDialog(self.win, self.tr, self.tr("resources.button." + button), RES["damage_max"], types)
        dlg.accepted.connect(lambda: self._amount(button, dlg))
        return self._open(dlg)

    def _amount(self, button, dlg):
        amount, dtype = dlg.values()
        if button == "take_damage":
            return self.run("take_damage", amount=amount, dtype=dtype)
        if button == "heal":
            return self.run("restore", resource=HP, amount=amount)
        return self.run("damage_to_balance", amount=amount)

    def open_editor(self, rid):
        row = self.rows[rid]
        cur = "%d / %d" % (int(row.data["current"]), int(row.data["max"]))
        temp = str(self.view.get("temp_hp", 0)) if rid == HP else ""
        dlg = dialogs.EditPopup(self.win, self.tr, row.label.text(), cur, rid == HP, temp)
        dlg.accepted.connect(lambda: self.apply_edit(rid, *dlg.texts()))
        return self._open(dlg)

    def apply_edit(self, rid, text, temp_text=""):
        """The editor's texts -> commands: the value field (if typed), then the temp HP field (a plain number)."""
        r = None
        try:
            if text:
                kind, n = tl.parse_edit(text)
                command, params = tl.edit_command(rid, kind, n, self.rows[rid].data["current"])
                r = self.run(command, **params)
                if not r.ok:
                    return r
            if temp_text:
                kind, n = tl.parse_edit(temp_text)
                if kind != tl.SET:
                    raise tl.EditError(temp_text)
                r = self.run("set_temp_hp", value=n)
        except tl.EditError as e:
            self.say(self.tr(e.key, text=e.text))
        return r

    def _open(self, dlg):
        self.dialog = dlg
        if self.win is None or not self.win.quiet:
            dlg.open()
        return dlg
