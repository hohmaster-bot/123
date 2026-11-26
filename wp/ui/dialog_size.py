"""Dialogs scale to their content (owner review 4, package 35 P1): a dialog takes the size of its content
(adjustSize / sizeHint, no fixed frames), or the size the owner dragged it to (the app setting dialog_sizes, one entry
per dialog id), never larger than the screen. The size is remembered when the dialog closes and its size differs
from the fitted one (window.set_setting: a settings command, D22). Pure numbers: dialog_logic.fit_size."""
from PySide6.QtGui import QGuiApplication

from wp.ui import dialog_logic as dl

SETTING = "dialog_sizes"


def window_of(parent):
    """The main window of a parent widget (the window itself or a block with .win)."""
    if parent is None:
        return None
    if hasattr(parent, "session") and hasattr(parent, "set_setting"):
        return parent
    return getattr(parent, "win", None)


class SizedDialog:
    """Mix into a QDialog: call setup_size(parent, dialog_id) at the end of __init__."""

    def setup_size(self, parent, dialog_id):
        self._size_win, self.dialog_id, self.fitted = window_of(parent), dialog_id, None
        self.fit()

    def saved_size(self):
        win = self._size_win
        if win is None:
            return None
        return dict(win.session.setting(SETTING) or {}).get(self.dialog_id)

    def fit(self):
        self.adjustSize()
        hint = self.sizeHint()
        screen = self.screen() or QGuiApplication.primaryScreen()
        avail = screen.availableGeometry()
        w, h = dl.fit_size((hint.width(), hint.height()), self.saved_size(), (avail.width(), avail.height()))
        self.resize(w, h)
        self.fitted = (self.width(), self.height())
        return self.fitted

    def remember(self):
        win = self._size_win
        now = (self.width(), self.height())
        if win is None or self.fitted is None or now == self.fitted:
            return False
        sizes = dict(win.session.setting(SETTING) or {})
        sizes[self.dialog_id] = list(now)
        self.fitted = now
        return bool(win.set_setting(SETTING, sizes).ok)

    def done(self, result):
        self.remember()
        super().done(result)
