
    
  
        self.action_button.clicked.connect(self.on_action)
        buttons.addWidget(self.action_button)

        self.close_button = QPushButton("×")
        self.close_button.setFixedWidth(32)
        self.close_button.clicked.connect(self.close)
        buttons.addWidget(self.close_button)
        outer.addLayout(buttons)

        self.setStyleSheet("""
            QFrame#chip {
                background-color: rgba(27, 34, 47, 242);
                border: 1px solid rgba(130, 165, 210, 210);
                border-radius: 12px;
            }
            QPushButton {
                color: white;
                background: #365d91;
                border: 0;
                border-radius: 6px;
                padding: 7px 10px;
            }
            QPushButton:hover { background: #4779b8; }
            QPushButton:pressed { background: #24446d; }
        """)
        self.move(*position)
        self.adjustSize()

    def on_action(self):
        self.content.setText(self.content.text() + "\nКнопка нажата — Python обработал событие.")

    def begin_drag(self, global_pos):
        self.drag_offset = global_pos - self.mapToGlobal(QPoint(0, 0))
        self.raise_()

    def drag_to(self, global_pos):
        if self.drag_offset is not None:
            self.move(global_pos - self.drag_offset)

    def end_drag(self):
        self.drag_offset = None


class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python transparent overlay test")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        # Test on the primary monitor first. The window is one surface;
        # all chips are ordinary child widgets, not separate top-level windows.
        screen = QGuiApplication.primaryScreen()
        self.setGeometry(screen.geometry())

        self.chip_a = Chip(
            "ЧИП A",
            "Это один общий overlay. Перетаскивай за верхнюю полоску.",
            (80, 100),
            self,
        )
        self.chip_b = Chip(
            "ЧИП B",
            "Кнопки вызывают обычные Python-обработчики.",
            (420, 220),
            self,
        )
        self.chip_c = Chip(
            "ЧИП C",
            "Пустая прозрачная область вокруг чипов должна пропускать клики в игру.",
            (180, 470),
            self,
        )

        # A visible close control so the overlay can be dismissed even
        # after focus has moved to the application underneath.
        self.close_all = QPushButton("Закрыть overlay", self)
        self.close_all.setGeometry(20, 20, 150, 34)
        self.close_all.setStyleSheet("""
            QPushButton {
                color: white; background: #8b3434; border: 1px solid #d98b8b;
                border-radius: 7px; padding: 5px 10px;
            }
            QPushButton:hover { background: #ad4545; }
        """)
        self.close_all.clicked.connect(QApplication.quit)

        self.show()

    def paintEvent(self, event):
        # Deliberately paint nothing: the unused area remains fully transparent.
        pass


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Overlay hit-test test")
    overlay = Overlay()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

