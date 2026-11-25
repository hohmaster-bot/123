"""Overlay spike (package 28 C): a small always-on-top window over a browser / VTT. NOT part of wp, no Session,
no character files; stub numbers in memory only. Run: python tools\\overlay_spike.py (needs PySide6).

- Frameless, always on top, semi-transparent; drag by the title strip; resize by the corner grip.
- Opacity slider. Ctrl+Alt+O: click-through on / off (the mouse goes to the window underneath).
  Ctrl+Alt+H: hide / show. Both are global hotkeys (Windows RegisterHotKey via ctypes); elsewhere they are
  skipped with a message and the buttons in the window do the same.
- Position, size and opacity are saved to overlay_spike.json next to this script.
- [package 32] A tray icon: green = the overlay is shown, grey = hidden; an orange corner = click-through is on; the
  tooltip says the same; its menu: Show / Hide, Click-through on / off, Exit. A close button (x) in the title strip;
  Esc closes too; Ctrl+Alt+Q (global) exits.
"""
import json
import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMenu, QPushButton, QSizeGrip, QSlider,
                               QSystemTrayIcon, QVBoxLayout, QWidget)

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "overlay_spike.json")
WINDOWS = sys.platform == "win32"
WM_HOTKEY = 0x0312
MOD_ALT, MOD_CONTROL, MOD_NOREPEAT = 0x1, 0x2, 0x4000
HOTKEYS = {1: ord("O"), 2: ord("H"), 3: ord("Q")}   # 1 = click-through, 2 = hide / show, 3 = exit
GWL_EXSTYLE, WS_EX_LAYERED, WS_EX_TRANSPARENT = -20, 0x80000, 0x20
DEFAULT = {"x": 200, "y": 200, "w": 260, "h": 230, "opacity": 85}
ICON = 32
SHOWN, HIDDEN, THROUGH = "#3cb371", "#808080", "#ff9900"   # tray icon colours: shown, hidden, click-through badge


def tray_pixmap(visible, click_through):
    """The tray icon: a green (shown) or grey (hidden) disc; an orange corner square when click-through is on."""
    pm = QPixmap(ICON, ICON)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(SHOWN if visible else HIDDEN))
    p.setPen(Qt.NoPen)
    p.drawEllipse(2, 2, ICON - 4, ICON - 4)
    if click_through:
        p.setBrush(QColor(THROUGH))
        p.drawRect(ICON // 2, ICON // 2, ICON // 2, ICON // 2)
    p.end()
    return pm


def tray_tooltip(visible, click_through):
    return "WipeFinder overlay: %s, click-through %s" % ("shown" if visible else "hidden",
                                                          "ON" if click_through else "off")


def user32():
    """user32 with typed arguments: a window handle is a pointer (64-bit); untyped ctypes overflows (package 32 fix)."""
    import ctypes
    from ctypes import wintypes
    u = ctypes.windll.user32
    if not getattr(u, "_wp_typed", False):
        u.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint, ctypes.c_uint]
        u.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
        u.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
        u.GetWindowLongW.restype = ctypes.c_long
        u.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
        u.SetWindowLongW.restype = ctypes.c_long
        u._wp_typed = True
    return u


def load_state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return dict(DEFAULT, **json.load(f))
    except (OSError, ValueError):
        return dict(DEFAULT)


class Overlay(QWidget):
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.state = load_state()
        self.hp = [25, 30]
        self.click_through = False
        self._drag = None
        self.setGeometry(self.state["x"], self.state["y"], self.state["w"], self.state["h"])
        self.setStyleSheet("QWidget { background: #202830; color: #e8e8e8; font-size: 12px; }"
                           "QPushButton { background: #34404c; border: 1px solid #50606c; padding: 2px 6px; }")
        box = QVBoxLayout(self)
        box.setContentsMargins(6, 4, 6, 4)
        top = QHBoxLayout()
        self.title = QLabel("WipeFinder overlay (drag here)")
        self.title.setStyleSheet("background: #34404c; padding: 3px;")
        self.close_button = QPushButton("x")
        self.close_button.setToolTip("Close the overlay (Esc, Ctrl+Alt+Q)")
        self.close_button.setFixedWidth(24)
        self.close_button.clicked.connect(self.quit)
        top.addWidget(self.title, 1)
        top.addWidget(self.close_button)
        box.addLayout(top)
        self.hp_label = QLabel()
        box.addWidget(self.hp_label)
        for text in ("Balance 3 / 5", "Mana 12 / 20", "Status: Haste (3)", "Status: Bleeding (2)"):
            box.addWidget(QLabel(text))
        row = QHBoxLayout()
        for text, delta in (("HP -1", -1), ("HP +1", 1)):
            b = QPushButton(text)
            b.clicked.connect(lambda _=False, d=delta: self.change_hp(d))
            row.addWidget(b)
        box.addLayout(row)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(20, 100)
        self.slider.setValue(int(self.state["opacity"]))
        self.slider.valueChanged.connect(self.set_opacity)
        box.addWidget(QLabel("Opacity"))
        box.addWidget(self.slider)
        row2 = QHBoxLayout()
        ct = QPushButton("Click-through (Ctrl+Alt+O)")
        ct.clicked.connect(self.toggle_click_through)
        row2.addWidget(ct)
        row2.addWidget(QSizeGrip(self), 0, Qt.AlignBottom | Qt.AlignRight)
        box.addLayout(row2)
        self.info = QLabel("")
        box.addWidget(self.info)
        self.set_opacity(self.slider.value())
        self.change_hp(0)
        self.tray = None
        self.make_tray()

    # ------------------------------------------------------------ tray icon (package 32)
    def make_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("no system tray here: the tray icon is skipped")
            return
        self.tray = QSystemTrayIcon(self)
        menu = QMenu()
        self.act_show = QAction("Hide", menu)
        self.act_show.triggered.connect(self.toggle_visible)
        self.act_through = QAction("Click-through on", menu)
        self.act_through.triggered.connect(self.toggle_click_through)
        act_exit = QAction("Exit", menu)
        act_exit.triggered.connect(self.quit)
        for a in (self.act_show, self.act_through, act_exit):
            menu.addAction(a)
        self.tray_menu = menu
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.toggle_visible()
                                    if reason == QSystemTrayIcon.Trigger else None)
        self.update_tray()
        self.tray.show()

    def update_tray(self):
        visible = self.isVisible()
        if self.tray is None:
            return
        self.tray.setIcon(QIcon(tray_pixmap(visible, self.click_through)))
        self.tray.setToolTip(tray_tooltip(visible, self.click_through))
        self.act_show.setText("Hide" if visible else "Show")
        self.act_through.setText("Click-through off" if self.click_through else "Click-through on")

    def quit(self):
        self.close()
        QApplication.instance().quit()

    # ------------------------------------------------------------ stub data
    def change_hp(self, delta):
        self.hp[0] = max(-self.hp[1], min(self.hp[1], self.hp[0] + delta))
        self.hp_label.setText("HP %d / %d" % tuple(self.hp))

    def set_opacity(self, value):
        self.setWindowOpacity(value / 100.0)
        self.state["opacity"] = value

    # ------------------------------------------------------------ click-through and hide
    def toggle_click_through(self):
        self.click_through = not self.click_through
        if WINDOWS:
            u = user32()
            hwnd = int(self.winId())
            style = u.GetWindowLongW(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED
            style = style | WS_EX_TRANSPARENT if self.click_through else style & ~WS_EX_TRANSPARENT
            u.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        else:
            self.setWindowFlag(Qt.WindowTransparentForInput, self.click_through)
            self.show()
        self.info.setText("click-through ON (Ctrl+Alt+O to turn off)" if self.click_through else "")
        self.update_tray()

    def toggle_visible(self):
        self.setVisible(not self.isVisible())
        self.update_tray()

    def register_hotkeys(self):
        if not WINDOWS:
            print("global hotkeys need Windows: skipped (use the buttons)")
            return
        hwnd = int(self.winId())
        for hid, vk in HOTKEYS.items():
            if not user32().RegisterHotKey(hwnd, hid, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, vk):
                print("hotkey %d could not be registered (taken by another program?)" % hid)

    def nativeEvent(self, event_type, message):
        if WINDOWS and event_type == b"windows_generic_MSG":
            import ctypes.wintypes
            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == WM_HOTKEY:
                {1: self.toggle_click_through, 2: self.toggle_visible, 3: self.quit}.get(msg.wParam, lambda: None)()
                return True, 0
        return super().nativeEvent(event_type, message)

    # ------------------------------------------------------------ drag by the title strip, save on close
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.title.geometry().contains(e.position().toPoint()):
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag is not None:
            self.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        self._drag = None
        self.save_state()

    def save_state(self):
        g = self.geometry()
        self.state.update(x=g.x(), y=g.y(), w=g.width(), h=g.height())
        try:
            with open(STATE, "w", encoding="utf-8") as f:
                json.dump(self.state, f)
        except OSError as err:
            print("could not save %s: %s" % (STATE, err))

    def closeEvent(self, e):
        self.save_state()
        if self.tray is not None:
            self.tray.hide()
        if WINDOWS:
            for hid in HOTKEYS:
                user32().UnregisterHotKey(int(self.winId()), hid)
        super().closeEvent(e)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


def main(argv):
    app = QApplication(argv)
    w = Overlay()
    w.show()
    w.register_hotkeys()
    if "--smoke" in argv:                  # start, draw, toggle, close (a self-check without a person)
        w.change_hp(-1)
        w.toggle_click_through()
        w.toggle_click_through()
        w.toggle_visible()
        w.toggle_visible()
        app.processEvents()
        tips = (tray_tooltip(True, False), tray_tooltip(False, True))
        ok = (w.hp_label.text() == "HP 24 / 30" and tips == ("WipeFinder overlay: shown, click-through off",
                                                              "WipeFinder overlay: hidden, click-through ON")
              and not tray_pixmap(True, True).isNull() and w.close_button.text() == "x")
        w.close()
        print("smoke: %s" % ("ok" if ok else "FAILED"))
        return 0 if ok else 1
    return app.exec()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
