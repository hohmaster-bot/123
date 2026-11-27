"""The statuses, favourites and reminders blocks of the Classic window (package 34 part 2, Phase 5 step 5;
UI_WISHES "Classic screen v2" point 8).

StatusesBlock: the buffs / statuses / injuries of the statuses view (container entries) with the filter All / Active /
Favorites (combat_logic.filter_entries); each row: the name (a click opens its effects in the Sources dialog), the
duration / charges text, an On / Off button (activate_status / remove_status) and a star (set_status_favorite).
FavoritesBlock: the favourite statuses and abilities (statuses view "favorites"); a click on an ability star removes
it (set_favorite on=False). RemindersBlock: the standing reminders of the character and the one-shot reminders of
this Session (Session.reminders_view; a one-shot one has a dismiss button: Session.dismiss_note).
Every change is a Session command; the blocks read only views (D25).
"""
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from wp.i18n import i18n
from wp.ui import combat_logic as cl
from wp.ui.blocks import Block
from wp.ui.sources_dialog import open_sources

STATUS = "status"


MANUAL = "manual:"


def manual_conditions(session, sid):
    """The texts of the manual conditions of a status's effects (package 36, decision 7)."""
    st = next((s for s in session.character.statuses if s.sid == sid), None) if session.character else None
    out = []
    for e in (st.effects if st is not None else ()):
        if e.condition.startswith(MANUAL) and e.condition[len(MANUAL):] not in out:
            out.append(e.condition[len(MANUAL):])
    return out


def _clear(lay):
    while lay.count():
        it = lay.takeAt(0)
        if it.widget() is not None:          # hidden and unparented first: a removed widget never paints again
            w = it.widget()
            w.hide()
            w.setParent(None)
            w.deleteLater()
        elif it.layout() is not None:
            _clear(it.layout())


class _Scroll(Block):
    """A block with a scrolling list area under the title (rows rebuilt on refresh)."""

    def __init__(self, pid, item, shell, vertical=True, inline=False):
        super().__init__(pid, item, shell)
        self.area = QScrollArea()
        self.area.setWidgetResizable(True)
        self.area.setObjectName("list_area")
        self.inner = QWidget()
        self.inner.setObjectName("list_inner")
        self.list = QVBoxLayout(self.inner) if vertical else QHBoxLayout(self.inner)
        self.list.setContentsMargins(0, 0, 0, 0)
        self.area.setWidget(self.inner)
        if inline:                     # a low block: the title and the list on one line (package 34)
            self.box.removeWidget(self.title)
            line = QHBoxLayout()
            line.addWidget(self.title)
            line.addWidget(self.area, 1)
            self.box.addLayout(line, 1)
        else:
            self.box.addWidget(self.area, 1)
        self.message = QLabel()
        self.message.setObjectName("message")
        self.message.hide()
        self.box.addWidget(self.message)
        self._tr, self.session = None, None

    def retranslate(self, tr):
        super().retranslate(tr)
        self._tr = tr
        self._show()

    def refresh(self, session):
        super().refresh(session)
        self.session = session
        self._read()
        self._show()

    def _read(self):
        pass

    def _show(self):
        pass

    def run(self, command, **params):
        r = self.session.dispatch(command, **params)
        if not r.ok:
            text = i18n.text_for(r, self.win.lang() if self.win is not None else i18n.BASE)
            self.message.setText(text)
            if self.win is not None:
                self.win.messages.append(text)
        else:
            self.message.setText("")
        self.message.setVisible(bool(self.message.text()))
        return r


class StatusesBlock(_Scroll):
    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell)
        self.mode = cl.ALL
        self.box.removeWidget(self.title)
        bar = QHBoxLayout()
        bar.addWidget(self.title)
        self.filters = {}
        for m in cl.MODES:
            b = QPushButton()
            b.setObjectName("small")
            b.setCheckable(True)
            b.setProperty("mode", m)
            b.clicked.connect(self._filter_clicked)    # a bound method, no lambda: no cycle kept past a rebuild
            self.filters[m] = b
            bar.addWidget(b)
        bar.addStretch(1)
        self.box.insertLayout(0, bar)
        self.entries, self.rows = (), {}

    def _filter_clicked(self):
        return self.set_mode(self.sender().property("mode"))

    def set_mode(self, mode):
        self.mode = mode
        self._show()

    def _read(self):
        if self.session.character is not None:
            self.entries = tuple(self.session.view("statuses")["container"].entries)

    def shown(self):
        return [e.eid for e in cl.filter_entries(self.entries, self.mode)]

    def _show(self):
        if self._tr is None:
            return
        tr = self._tr
        for m, b in self.filters.items():
            b.setText(tr("statuses.filter." + m))
            b.setChecked(m == self.mode)
        _clear(self.list)
        self.rows = {}
        for e in cl.filter_entries(self.entries, self.mode):
            row = QHBoxLayout()
            name = QPushButton(e.name or e.eid)
            name.setObjectName("link")
            name.clicked.connect(lambda _=False, sid=e.eid: self.open_effects(sid))
            key, values = cl.entry_text(e)
            info = QLabel(tr(key, values=values) + (" %d/%d" % tuple(e.charges) if e.charges else ""))
            info.setObjectName("muted")
            row.addWidget(name)
            row.addWidget(info, 1)
            widgets = {"name": name, "info": info}
            if e.kind == STATUS:
                on = QPushButton(tr("statuses.on") if not e.active else tr("statuses.end"))
                on.setObjectName("small")
                on.clicked.connect(lambda _=False, sid=e.eid, a=e.active: self.toggle(sid, a))
                star = QPushButton(tr("statuses.star_on") if e.favorite else tr("statuses.star_off"))
                star.setObjectName("fav_on" if e.favorite else "fav_off")
                star.clicked.connect(lambda _=False, sid=e.eid, f=e.favorite: self.favorite(sid, not f))
                row.addWidget(on)
                row.addWidget(star)
                widgets.update(on=on, star=star)
                for text in manual_conditions(self.session, e.eid):      # package 36: the manual condition box
                    box = QCheckBox(text)
                    box.setChecked(text in self.session.character.manual_conditions)
                    box.toggled.connect(lambda on, t=text: self.run("set_manual_condition", text=t, on=bool(on)))
                    row.addWidget(box)
                    widgets.setdefault("conditions", {})[text] = box
            if e.kind == STATUS and self.session is not None and self.session.character is not None:
                from wp.ui import tab_logic as tlg            # package 37: the status links on hover
                win = self.win
                danger = self.session.theme(win.system_dark() if win is not None else None)["colors"]["danger"]
                name.setToolTip(tlg.link_tooltip(self.session.view("links"), "status:" + e.eid, tr, danger))
            self.rows[e.eid] = widgets
            self.list.addLayout(row)
        self.list.addStretch(1)

    def toggle(self, sid, active):
        return self.run("remove_status" if active else "activate_status", sid=sid)

    def favorite(self, sid, value):
        return self.run("set_status_favorite", sid=sid, value=bool(value))

    def open_effects(self, sid):
        if self.win is None or self.session.character is None:
            return None
        if not any(s.sid == sid for s in self.session.character.statuses):
            return None                # an injury: no effects view yet
        return open_sources(self.win, "status:" + sid)


class FavoritesBlock(_Scroll):
    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell, vertical=False, inline=True)
        self.favs, self.names = {"statuses": (), "abilities": ()}, {}

    def _read(self):
        if self.session.character is not None:
            self.favs = dict(self.session.view("statuses")["favorites"])
            self.names = {s.sid: s.name for s in self.session.character.statuses}

    def _show(self):
        if self._tr is None:
            return
        _clear(self.list)
        self.chips = []
        for sid in self.favs.get("statuses", ()):
            chip = QLabel(self.names.get(sid, sid))
            chip.setObjectName("fav_chip")
            self.list.addWidget(chip)
            self.chips.append(chip.text())
        for key in self.favs.get("abilities", ()):
            kind, _, oid = key.partition(":")
            b = QPushButton(oid + " " + self._tr("statuses.star_on"))
            b.setObjectName("small")
            b.clicked.connect(lambda _=False, k=kind, o=oid: self.run("set_favorite", kind=k, oid=o, on=False))
            self.list.addWidget(b)
            self.chips.append(oid)
        if not self.chips:
            empty = QLabel(self._tr("favorites.empty"))
            empty.setObjectName("muted")
            self.list.addWidget(empty)
        self.list.addStretch(1)


def action_label(tr, action, target, amount):
    """The button text of a trigger action; a run_command with its own text key trigger.command.<name> uses it."""
    if action == "run_command":
        key = "trigger.command." + str(target)
        own = tr(key, amount=amount, target=target)
        if own != key:
            return own
    return tr("trigger.action." + action, target=target, amount=amount)


class RemindersBlock(_Scroll):
    def __init__(self, pid, item, shell):
        super().__init__(pid, item, shell, inline=True)
        self.reads = tuple(self.reads) + ("reminders", "statuses")
        self.data = {"standing": (), "notes": (), "triggers": ()}
        self.trigger_rows = {}

    def _read(self):
        if self.session.character is not None:
            self.data = self.session.reminders_view()

    def texts(self):
        tr = self._tr
        return [tr(k, values=tuple(v)) for k, v in self.data["standing"] + self.data["notes"]]

    def _show(self):
        if self._tr is None:
            return
        tr = self._tr
        _clear(self.list)
        for k, v in self.data["standing"]:
            lab = QLabel(tr(k, values=tuple(v)))
            lab.setWordWrap(True)
            self.list.addWidget(lab)
        for i, (k, v) in enumerate(self.data["notes"]):
            row = QHBoxLayout()
            lab = QLabel(tr(k, values=tuple(v)))
            lab.setWordWrap(True)
            x = QPushButton(tr("reminders.dismiss"))
            x.setObjectName("small")
            x.clicked.connect(lambda _=False, i=i: self.session.dismiss_note(i))
            row.addWidget(lab, 1)
            row.addWidget(x)
            self.list.addLayout(row)
        self.trigger_rows = {}
        for nid, _src, text, action, target, amount, _handled in self.data.get("triggers", ()):
            row = QWidget()                    # a trigger reminder: text, the optional action button, Handled
            hl = QHBoxLayout(row)
            hl.setContentsMargins(0, 0, 0, 0)
            lab = QLabel(tr(text, amount=amount, target=target))    # a text key (package 38) or a plain text
            lab.setWordWrap(True)
            hl.addWidget(lab, 1)
            widgets = {"text": lab}
            if action:
                b = QPushButton(action_label(tr, action, target, amount))
                b.setObjectName("small")
                b.clicked.connect(lambda _=False, n=nid: self.run("run_trigger_action", nid=n))
                hl.addWidget(b)
                widgets["action"] = b
            done = QPushButton(tr("trigger.handled"))
            done.setObjectName("small")
            done.clicked.connect(lambda _=False, n=nid: self.run("set_trigger_handled", nid=n, handled=True))
            hl.addWidget(done)
            widgets["handled"] = done
            self.trigger_rows[nid] = widgets
            self.list.addWidget(row)
        if not (self.data["standing"] or self.data["notes"] or self.data.get("triggers")):
            lab = QLabel(tr("reminders.empty"))
            lab.setObjectName("muted")
            self.list.addWidget(lab)
        self.list.addStretch(1)
