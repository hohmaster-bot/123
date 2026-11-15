
import sys
import ctypes

from PySide6.QtCore import Qt, QPoint, QTimer, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)


# ---------------------------------------------------------
# WINDOWS DIAGNOSTICS
# ---------------------------------------------------------

def print_window_info(widget):
    hwnd = int(widget.winId())

    user32 = ctypes.windll.user32
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_TOPMOST = 0x00000008

    style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

    print("\n========== WINDOW DIAGNOSTICS ==========")
    print(f"HWND:        {hex(hwnd)}")
    print(f"EXSTYLE:     {hex(style)}")
    print(f"LAYERED:     {bool(style & WS_EX_LAYERED)}")
    print(f"TRANSPARENT: {bool(style & WS_EX_TRANSPARENT)}")
    print(f"TOPMOST:     {bool(style & WS_EX_TOPMOST)}")
    print("========================================\n")


# ---------------------------------------------------------
# DRAGGABLE CHIP
# ---------------------------------------------------------

class Chip(QFrame):
    action = Signal(str, str)

    def __init__(self, chip_id, title, value, parent=None):
        super().__init__(parent)

        self.chip_id = chip_id
        self.drag_offset = QPoint()
        self.dragging = False

        self.setObjectName("chip")
        self.setFixedSize(230, 145)

        self.setStyleSheet("""
            QFrame#chip {
                background-color: rgba(30, 34, 45, 245);
                border: 1px solid rgba(130, 150, 190, 180);
                border-radius: 12px;
            }

            QLabel {
                color: white;
                background: transparent;
                border: none;
            }

            QPushButton {
                color: white;
                background-color: #424e68;
                border: none;
                border-radius: 6px;
                padding: 7px 12px;
            }

            QPushButton:hover {
                background-color: #61769e;
            }

            QPushButton:pressed {
                background-color: #29364f;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 9, 12, 10)
        layout.setSpacing(7)

        # Header
        self.header = QLabel(title)
        self.header.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #b9d5ff;
        """)
        self.header.setCursor(Qt.CursorShape.SizeAllCursor)
        layout.addWidget(self.header)

        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)
        layout.addWidget(self.value_label)

        # Buttons
        buttons = QHBoxLayout()

        self.minus_button = QPushButton("-")
        self.plus_button = QPushButton("+")
        self.action_button = QPushButton("Команда")

        buttons.addWidget(self.minus_button)
        buttons.addWidget(self.plus_button)
        layout.addLayout(buttons)

        layout.addWidget(self.action_button)

        self.minus_button.clicked.connect(
            lambda: self.action.emit(self.chip_id, "minus")
        )

        self.plus_button.clicked.connect(
            lambda: self.action.emit(self.chip_id, "plus")
        )

        self.action_button.clicked.connect(
            lambda: self.action.emit(self.chip_id, "command")
        )

    def set_data(self, title=None, value=None):
        if title is not None:
            self.header.setText(str(title))

        if value is not None:
            self.value_label.setText(str(value))

    # Drag only by header
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.header.geometry().contains(event.position().toPoint()):
                self.dragging = True
                self.drag_offset = (
                    event.globalPosition().toPoint()
                    - self.pos()
                )
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            new_position = (
                event.globalPosition().toPoint()
                - self.drag_offset
            )
            self.move(new_position)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        super().mouseReleaseEvent(event)


# ---------------------------------------------------------
# MAIN OVERLAY
# ---------------------------------------------------------

class Overlay(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        # Transparent window background
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            True
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_NoSystemBackground,
            True
        )

        # Do not set WA_TransparentForMouseEvents!
        # We need buttons to receive mouse input.

        screen = QApplication.primaryScreen()
        self.setGeometry(screen.geometry())

        self.chips = {}

        self.create_chips()

    def create_chips(self):
        positions = [
            ("chip1", "Первый чип", "100", 100, 100),
            ("chip2", "Второй чип", "250", 380, 180),
            ("chip3", "Третий чип", "500", 680, 300),
        ]

        for chip_id, title, value, x, y in positions:
            chip = Chip(chip_id, title, value, self)

            chip.move(x, y)
            chip.action.connect(self.handle_action)

            self.chips[chip_id] = chip
            chip.show()

    # Python-side action handling
    def handle_action(self, chip_id, command):
        print(f"ACTION: {chip_id} -> {command}")

        chip = self.chips[chip_id]

        try:
            value = int(chip.value_label.text())
        except ValueError:
            value = 0

        if command == "plus":
            value += 1

        elif command == "minus":
            value -= 1

        elif command == "command":
            print(f"Команда выполнена для {chip_id}")

        chip.set_data(value=value)

    # External Python programs can call this
    def update_chip(self, chip_id, title=None, value=None):
        if chip_id in self.chips:
            self.chips[chip_id].set_data(title, value)

    def closeEvent(self, event):
        print("Overlay closed.")
        event.accept()


# ---------------------------------------------------------
# START
# ---------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)

    overlay = Overlay()
    overlay.show()

    QTimer.singleShot(
        500,
        lambda: print_window_info(overlay)
    )

    print("Overlay started.")
    print("ESC is not configured yet.")
    print("Close with Alt+F4.")

    sys.exit(app.exec())
