"""Overlay spike (package 28 C): a small always-on-top window over a browser / VTT. NOT part of wp, no Session,
no character files; stub numbers in memory only. Run: python tools\\overlay_spike.py (needs PySide6).

- Frameless, always on top, semi-transparent; drag by the title strip; resize by the corner grip.
- Opacity slider. Ctrl+Alt+O: click-through on / off (the mouse goes to the window underneath).
  Ctrl+Alt+H: hide / show. Both are global hotkeys (Windows RegisterHotKey via ctypes); elsewhere they are
  skipped with a message and the buttons in the window do the same.
- Position, size and opacity are saved to overlay_spike.json next to this script.
"""
import json
import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton, QSizeGrip, QSlider, QVBoxLayout,
                               QWidget)

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "overlay_spike.json")
WINDOWS = sys.platform == "win32"
WM_HOTKEY = 0x0312
MOD_ALT, MOD_CONTROL, MOD_NOREPEAT = 0x1, 0x2, 0x4000
HOTKEYS = {1: ord("O"), 2: ord("H")}          # 1 = click-through, 2 = hide / show
GWL_EXSTYLE, WS_EX_LAYERED, WS_EX_TRANSPARENT = -20, 0x80000, 0x20
DEFAULT = {"x": 200, "y": 200, "w": 260, "h": 230, "opacity": 85}


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
        self.title = QLabel("WipeFinder overlay (drag here)")
        self.title.setStyleSheet("background: #34404c; padding: 3px;")
        box.addWidget(self.title)
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
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = int(self.winId())
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED
            style = style | WS_EX_TRANSPARENT if self.click_through else style & ~WS_EX_TRANSPARENT
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        else:
            self.setWindowFlag(Qt.WindowTransparentForInput, self.click_through)
            self.show()
        self.info.setText("click-through ON (Ctrl+Alt+O to turn off)" if self.click_through else "")

    def toggle_visible(self):
        self.setVisible(not self.isVisible())

    def register_hotkeys(self):
        if not WINDOWS:
            print("global hotkeys need Windows: skipped (use the buttons)")
            return
        import ctypes
        hwnd = int(self.winId())
        for hid, vk in HOTKEYS.items():
            if not ctypes.windll.user32.RegisterHotKey(hwnd, hid, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, vk):
                print("hotkey %d could not be registered (taken by another program?)" % hid)

    def nativeEvent(self, event_type, message):
        if WINDOWS and event_type == b"windows_generic_MSG":
            import ctypes.wintypes
            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == WM_HOTKEY:
                (self.toggle_click_through if msg.wParam == 1 else self.toggle_visible)()
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
        if WINDOWS:
            import ctypes
            for hid in HOTKEYS:
                ctypes.windll.user32.UnregisterHotKey(int(self.winId()), hid)
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
        ok = w.hp_label.text() == "HP 24 / 30"
        w.close()
        print("smoke: %s" % ("ok" if ok else "FAILED"))
        return 0 if ok else 1
    return app.exec()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
