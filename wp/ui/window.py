"""The Classic main window shell (package 32, D32; UI_WISHES "Classic screen v2").

Regions from the classic layout profile (session.profile("classic")): each visible panel item goes to the region of
its dock (top = the experience strip, left / center / right = the three columns, bottom = the bottom strip); inside
a region the items are ordered by position y, then x; items of the center with the same y share a row. Blocks keep
their saved sizes (sizeHint) and their registry minimum. The whole area scrolls when the window is too small.

Rules (D25): the window reads only session.view(...) / settings / theme and changes the character only through
session.dispatch (here: nothing yet besides the files); app settings through session.settings(...). It subscribes to
the Session: a command result refreshes the blocks whose views are in its topics ("all" = every block); the topic
"settings" re-applies the theme, the language and the scale LIVE. The window geometry is the app setting
window_classic (saved on close, restored on open). The first-run hint shows until "Understood!" (hint_dismiss).
"""
import json

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFontDatabase, QGuiApplication, QPainter, QPixmap
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QScrollArea,
                               QStyle, QStyleOption, QVBoxLayout, QWidget)

from wp.app.session import EDITOR_TOPICS, SETTINGS_TOPICS
from wp.i18n import i18n
from wp.theme import qss
from wp.app import ui_data
from wp.ui import blocks, menus
from wp.ui import theme_logic as thl
from wp.ui.files_ui import Files
from wp.ui.shell_data import SHELL

ALL = "all"
ADAPT_STEPS = ("normal", "gaps", "captions", "details")   # then the scroll (UI_WISHES point 12)
GAP_DIVISOR = 2                        # the small window halves the gaps (UI, not a rule)
EXPAND_GAPS = 4                        # gaps kept around an expanded tab (UI, not a rule)
TABS = "tabs"


class HintBar(QFrame):
    def __init__(self, win, hint_id):
        super().__init__()
        self.setObjectName("hint")
        self.hint_id = hint_id
        row = QHBoxLayout(self)
        self.text = QLabel()
        self.text.setWordWrap(True)
        self.button = QPushButton()
        self.button.clicked.connect(lambda: win.session_settings("hint_dismiss", hint_id=hint_id))
        row.addWidget(self.text, 1)
        row.addWidget(self.button)

    def retranslate(self, tr):
        self.text.setText(tr("hint." + self.hint_id))
        self.button.setText(tr("hint.understood"))


class Backdrop(QWidget):
    """The central area: the theme background, or the own background picture (package 35 P3) scaled to cover, with a
    black dimming of alpha dim_alpha(background_dim). No picture by default."""

    def __init__(self):
        super().__init__()
        self.setObjectName("central")
        self.pixmap, self.alpha, self.path = None, 0, ""

    def set_picture(self, path, alpha):
        if path != self.path:
            pm = QPixmap(path) if path else None
            self.pixmap = pm if pm is not None and not pm.isNull() else None
            self.path = path
        self.alpha = int(alpha)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
        if self.pixmap is not None:
            scaled = self.pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            p.drawPixmap(0, 0, scaled)
            p.fillRect(self.rect(), QColor(0, 0, 0, self.alpha))
        p.end()


class MainWindow(QMainWindow):
    def __init__(self, session, quiet=False, system_dark=None):
        super().__init__()
        self.session, self.shell = session, SHELL
        self.quiet = quiet                 # tests: messages are recorded, questions get self.answer
        self.answer = False
        self.messages = []
        self.qss = ""
        self._system_dark = system_dark    # tests set it; None = ask Qt
        self.files = Files(self)
        self.blocks = {}
        self.expanded = None               # a tab expanded to the full screen (package 35 P4)
        self.hint = HintBar(self, SHELL["hint"])
        self._build_regions()
        menus.build(self)
        self.statusBar()
        session.subscribe(self.on_topics)
        hints = QGuiApplication.styleHints()
        if hasattr(hints, "colorSchemeChanged"):
            hints.colorSchemeChanged.connect(lambda *_: self.apply_settings())
        self.restore_geometry()
        self.apply_settings()
        self.refresh_all()

    # ------------------------------------------------------------ layout from the profile
    def panels_signature(self):
        return json.dumps([dict(i) for i in self.session.profile("classic").get("panels", ())], sort_keys=True)

    def rebuild(self):
        """The layout editor changed the profile panels (package 35 P5): the regions are built again from it."""
        self.expanded = None
        self.blocks = {}
        old = self.takeCentralWidget()     # deleted later: no widget dies inside the signal that rebuilt it
        self._build_regions()
        if old is not None:
            old.hide()
            old.deleteLater()
        self.apply_settings()
        self.refresh_all()
        self.retranslate()

    def _build_regions(self):
        reg = SHELL["regions"]
        self.built = self.panels_signature()
        items = [i for i in self.session.profile("classic").get("panels", ()) if i.get("visible", True)]
        by_dock = {}
        for it in sorted(items, key=lambda i: (tuple(i.get("position") or (0, 0))[::-1], i.get("tab_order", 0))):
            by_dock.setdefault(it.get("dock", reg["center"]), []).append(it)
        self.central = Backdrop()
        self.outer = QVBoxLayout(self.central)
        self.outer.addWidget(self.hint)
        self.layouts = [self.outer]
        self.regions, self.region_of, self.rows = {}, {}, {}
        self.regions[reg["top"]] = self._strip(by_dock.get(reg["top"], ()))
        middle = QHBoxLayout()
        self.layouts.append(middle)
        for dock in (reg["left"], reg["center"], reg["right"]):
            col = QVBoxLayout()
            self.layouts.append(col)
            self.regions[dock] = col
            rows = {}
            for it in by_dock.get(dock, ()):
                y = (tuple(it.get("position") or (0, 0)) + (0, 0))[1] if dock == reg["center"] else len(rows)
                rows.setdefault(y, []).append(it)
            self.rows[dock] = [[i.get("id", i.get("panel")) for i in rows[y]] for y in sorted(rows)]
            for y in sorted(rows):
                row = QHBoxLayout()
                self.layouts.append(row)
                for it in rows[y]:
                    row.addWidget(self._block(it))
                row.addStretch(1)
                col.addLayout(row)
            col.addStretch(1)
            middle.addLayout(col, 1 if dock == reg["center"] else 0)
        self.outer.addLayout(middle, 1)
        self.regions[reg["bottom"]] = self._strip(by_dock.get(reg["bottom"], ()))
        scroll = self.scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(self.central)
        self.setCentralWidget(scroll)

    def _strip(self, items):
        row = QHBoxLayout()
        self.layouts.append(row)
        for it in items:
            row.addWidget(self._block(it))
        self.outer.addLayout(row)
        return row

    def _block(self, item):
        b = blocks.make(item.get("panel", ""), item, SHELL)
        b.attach(self)
        self.blocks[item.get("id", item.get("panel"))] = b
        self.region_of[item.get("id", item.get("panel"))] = item.get("dock", SHELL["regions"]["center"])
        return b

    # ------------------------------------------------------------ settings: theme, language, scale (live)
    def tr(self, key, **params):
        return i18n.t(key, self.lang(), **params)

    def lang(self):
        lg = self.session.setting("language")
        return lg if lg in i18n.LANGS else i18n.BASE

    def system_dark(self):
        if self._system_dark is not None:
            return self._system_dark
        scheme = QGuiApplication.styleHints().colorScheme() if hasattr(QGuiApplication.styleHints(),
                                                                         "colorScheme") else None
        if scheme == Qt.ColorScheme.Dark:
            return True
        if scheme == Qt.ColorScheme.Light:
            return False
        return None

    def fonts(self, theme):
        """The app font settings (package 33): family, numbers family, base size; not installed -> fallback."""
        s = self.session
        return qss.fonts(theme, s.setting("font_family"), s.setting("font_family_numbers"), s.setting("font_size"),
                         QFontDatabase.families(), QFontDatabase.systemFont(QFontDatabase.GeneralFont).family())

    def apply_settings(self):
        theme = self.session.theme(self.system_dark())
        scale = float(self.session.setting("ui_scale"))
        fonts = self.fonts(theme)
        self.qss = qss.build_qss(theme, scale, fonts=fonts) + self.background(theme)
        self.setStyleSheet(self.qss)
        self.gap = int(qss.scaled(theme, scale)["spacing"])
        colors = qss.scaled(theme, scale, fonts=fonts)
        for b in self.blocks.values():
            b.apply_look(colors, scale, self.session)
        self.retranslate()
        self.adapt()

    def background(self, theme):
        """The own background picture (app settings background_image / background_dim / background_readable; package
        35 P3): painted by the central Backdrop; the readable overlay = extra QSS behind the blocks. "" = none."""
        s = self.session
        path = ui_data.background_path(s)
        shown = bool(path)
        self.central.set_picture(path, thl.dim_alpha(s.setting("background_dim")))
        self.background_shown = shown
        return thl.background_qss(theme, bool(s.setting("background_readable"))) if shown else ""

    # ------------------------------------------------------------ small window (UI_WISHES point 12, package 34)
    def _apply_level(self, level):
        """0 = normal; 1 = smaller gaps; 2 = + no block captions; 3 = + no details (small notes); then scroll.
        Never written to the layout profile (D31)."""
        lv_gaps, lv_captions, lv_details = (ADAPT_STEPS.index(k) for k in ADAPT_STEPS[1:])
        gap = self.gap if level < lv_gaps else max(1, self.gap // GAP_DIVISOR)
        for lay in self.layouts:
            lay.setSpacing(gap)
        self.outer.setContentsMargins(gap, gap, gap, gap)
        for b in self.blocks.values():
            b.set_gap(gap)
            b.set_compact(level >= lv_captions, level >= lv_details)
        self.adapt_level = level

    def adapt(self):
        have = self.scroll.viewport().size()
        for level in range(len(ADAPT_STEPS)):
            self._apply_level(level)
            need = self.central.minimumSizeHint()
            if need.width() <= have.width() and need.height() <= have.height():
                return level
        return self.adapt_level            # the last step: the area scrolls

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "gap"):
            QTimer.singleShot(0, self.adapt)       # after the scroll area took its new size

    # ------------------------------------------------------------ expand a tab to the full screen (UI_WISHES 9, pkg 35)
    def expand_block(self, bid):
        """bid = a block id: every other block except the tab bar is hidden for a while and the block takes the
        visible area; None = back to the layout. Never written to the profile (D31)."""
        prev = self.expanded
        if prev is not None and prev in self.blocks:
            self.blocks[prev].setFixedSize(self.blocks[prev].saved)
        for k, b in self.blocks.items():
            b.setVisible(bid is None or k in (bid, TABS))
        if bid is not None and bid in self.blocks:
            have = self.scroll.viewport().size()
            tabs = self.blocks[TABS].height() if TABS in self.blocks else 0
            b = self.blocks[bid]
            b.setFixedSize(max(b.saved.width(), have.width() - EXPAND_GAPS * self.gap),
                           max(b.saved.height(), have.height() - tabs - EXPAND_GAPS * self.gap))
        self.expanded = bid
        return bid

    def retranslate(self):
        tr = self.tr
        self.setWindowTitle(tr("shell.title", name=self.session.name or "-"))
        menus.retranslate(self, tr)
        self.hint.retranslate(tr)
        self.hint.setVisible(self.session.hint_visible(self.hint.hint_id))
        for b in self.blocks.values():
            b.retranslate(tr)

    def session_settings(self, command, **params):
        r = self.session.settings(command, **params)
        if not r.ok:
            self.refusal(r)
        return r

    def set_setting(self, key, value):
        return self.session_settings("settings_set", key=key, value=value)

    def choose_theme(self, tid):
        if self.session.setting("theme_follow_system"):
            self.set_setting("theme_follow_system", False)
        return self.set_setting("theme", tid)

    # ------------------------------------------------------------ the Session subscription (D25)
    def on_topics(self, topics):
        if tuple(topics) == SETTINGS_TOPICS:
            if self.panels_signature() != self.built:     # the layout editor / a profile reset (package 35 P5)
                self.rebuild()
            else:
                self.apply_settings()
            return
        if tuple(topics) == EDITOR_TOPICS:     # the editor mode switched (package 34)
            self.refresh_all()
            self.retranslate()
            return
        for b in self.blocks.values():
            if ALL in topics or set(b.reads) & set(topics):
                b.refresh(self.session)
        if topics and getattr(self, "sources", None) is not None:     # ANY_TOPIC_VIEWS (package 34)
            self.sources.reload()

    def refresh_all(self):
        editing = bool(self.session.editor_mode)
        for b in self.blocks.values():
            if b.property("editing") != editing:      # editor mode: block borders (token block_border_edit)
                b.setProperty("editing", editing)
                b.style().unpolish(b)
                b.style().polish(b)
            b.refresh(self.session)

    def character_changed(self):
        self.refresh_all()
        self.retranslate()

    # ------------------------------------------------------------ messages (never a traceback)
    def message(self, text):
        self.messages.append(text)
        if not self.quiet:
            QMessageBox.warning(self, self.tr("shell.error"), text)

    def refusal(self, err):
        self.message(i18n.text_for(err, self.lang()))

    def ask(self, text):
        self.messages.append(text)
        if self.quiet:
            return self.answer
        return QMessageBox.question(self, self.tr("shell.error"), text) == QMessageBox.Yes

    def info(self, title, text):
        """A message box (level-up reminders); tests record the text."""
        self.messages.append(text)
        if not self.quiet:
            QMessageBox.information(self, title, text)

    def status(self, text):
        self.statusBar().showMessage(text)

    # ------------------------------------------------------------ geometry
    def restore_geometry(self):
        x, y, w, h = [int(v) for v in self.session.setting("window_classic")]
        self.setGeometry(x, y, w, h)

    def closeEvent(self, event):
        g = self.geometry()
        self.set_setting("window_classic", [g.x(), g.y(), g.width(), g.height()])
        try:
            self.session.close()           # saves unsaved changes (backups first)
        except Exception as e:             # noqa: BLE001 - a failed save is shown, the window still closes
            self.refusal(e)
        super().closeEvent(event)
