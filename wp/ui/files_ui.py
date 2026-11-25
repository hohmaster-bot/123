"""Character files of the window shell (package 32): new demo, open, save, save as; through the Session only
(wp/app/files.py rules: backups before every save, atomic writes, a damaged file offers the newest valid backup).
The file dialogs (QFileDialog) are not covered by the tests; open_path / save_as_path are.
Every refusal is shown as its i18n text (window.message), never as a Python traceback."""
import os

from PySide6.QtWidgets import QFileDialog

from wp.app.session import CommandError
from wp.ui import demo

EXT = ".json"


class Files(object):
    def __init__(self, win):
        self.win = win
        self.session = win.session

    def _folder(self):
        return os.path.normcase(os.path.abspath(self.session.characters_dir))

    def _keep_changes(self):
        if self.session.character is not None and self.session.dirty_since is not None:
            self.session.save()

    def _done(self, name):
        self.win.set_setting("last_character", name)
        self.win.character_changed()

    def _refused(self, err):
        self.win.refusal(err)
        return False

    # ------------------------------------------------------------ actions
    def new_demo(self):
        try:
            self._keep_changes()
            name = demo.build(self.session)
        except CommandError as e:
            return self._refused(e)
        self._done(name)
        return True

    def open_name(self, name):
        try:
            self._keep_changes()
            self.session.open(name)
        except CommandError as e:
            backup = e.params.get("backup") if e.reason == "file_corrupt" else None
            if e.reason == "file_corrupt" and backup and self.win.ask(
                    self.win.tr("reason.file_corrupt", values=e.params.get("values", (name,))) + "\n\n" +
                    self.win.tr("shell.restore_backup", backup=backup)):
                try:
                    self.session.restore_backup(name)
                except CommandError as e2:
                    return self._refused(e2)
            else:
                return self._refused(e)
        self._done(name)
        return True

    def open_path(self, path):
        name, ext = os.path.splitext(os.path.basename(path))
        if os.path.normcase(os.path.dirname(os.path.abspath(path))) != self._folder():
            try:
                self.session.import_file(path, name)
            except CommandError as e:
                return self._refused(e)
        return self.open_name(name)

    def save(self):
        try:
            self.session.save()
        except CommandError as e:
            return self._refused(e)
        self.win.status(self.win.tr("shell.saved", name=self.session.name))
        return True

    def save_as_path(self, path):
        """Into the characters folder: a new character file (opened); elsewhere: an exported copy."""
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            if os.path.normcase(os.path.dirname(os.path.abspath(path))) == self._folder():
                self.session.new(name, character=self.session.character)
            else:
                self.session.save()
                self.session.export(self.session.name, path)
                self.win.status(self.win.tr("shell.saved", name=path))
                return True
        except CommandError as e:
            return self._refused(e)
        self._done(name)
        return True

    # ------------------------------------------------------------ dialogs (by hand)
    def open_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self.win, self.win.tr("menu.open"), self.session.characters_dir,
                                              self.win.tr("shell.file_filter"))
        return self.open_path(path) if path else False

    def save_as_dialog(self):
        if self.session.character is None:
            return False
        start = os.path.join(self.session.characters_dir, self.session.name + EXT)
        path, _ = QFileDialog.getSaveFileName(self.win, self.win.tr("menu.save_as"), start,
                                              self.win.tr("shell.file_filter"))
        return self.save_as_path(path) if path else False
