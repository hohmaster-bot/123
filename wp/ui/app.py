"""Start of the Classic window shell (package 32, D32): python run_wp.py [--data DIR].

The data folder (default: <home>/WipeFinder) holds characters/ (the character files, backups, trash) and settings/
(app settings, own themes, catalogs). On start the last character (app setting last_character) is opened; without
one (or when it cannot be opened) the demo character is opened or built (wp/ui/demo.py). An unexpected error is
shown as a short i18n text and printed to the console, never as a traceback in the window."""
import os
import sys
import traceback

from wp.app.session import Session
from wp.ui import demo
from wp.ui.shell_data import SHELL

DATA_ARG = "--data"


def data_dirs(argv, home=None):
    base = os.path.join(home or os.path.expanduser("~"), SHELL["data_folder"])
    if DATA_ARG in argv[:-1]:
        base = argv[argv.index(DATA_ARG) + 1]
    return os.path.join(base, SHELL["characters_folder"]), os.path.join(base, SHELL["settings_folder"])


def start_character(win):
    """Open the last character, else the demo (built when it does not exist yet). Returns the opened name."""
    s = win.session
    names = s.list_characters()
    last = s.setting("last_character")
    if last and last in names and win.files.open_name(last):
        return s.name
    base = demo.load()["name"]
    if base in names and win.files.open_name(base):
        return s.name
    win.files.new_demo()
    return s.name


def _hook(win):
    def hook(kind, value, tb):
        traceback.print_exception(kind, value, tb)
        try:
            win.message(win.tr("shell.unexpected"))
        except Exception:              # noqa: BLE001 - the hook itself must never raise
            pass
    return hook


def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    from PySide6.QtWidgets import QApplication
    from wp.ui.window import MainWindow
    app = QApplication(argv)
    chars, user = data_dirs(argv)
    for d in (chars, user):
        os.makedirs(d, exist_ok=True)
    session = Session(chars, user)
    win = MainWindow(session)
    sys.excepthook = _hook(win)
    start_character(win)
    win.show()
    return app.exec()
