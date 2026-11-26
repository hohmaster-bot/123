"""Own windows of the top menus "Settings" and "Catalog" (package 36 P1.3; owner: these are top menus next to View and
Help, not tabs of the right column). A PageWindow hosts one tab page (tab_settings.SettingsPage,
tab_pages2.CatalogsPage) and gives it the host API the pages use (win, item, run, step); it is a non-blocking dialog
that takes the size of its content or the size the owner dragged it to (SizedDialog). The main window refreshes the
open page windows on every Session topic and after a settings change.
"""
import importlib

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from wp.i18n import i18n
from wp.ui.dialog_size import SizedDialog

PAGES = {"settings": ("wp.ui.tab_settings", "SettingsPage"), "catalogs": ("wp.ui.tab_pages2", "CatalogsPage")}


class PageWindow(SizedDialog, QDialog):
    def __init__(self, win, page_id):
        super().__init__(win)
        self.win, self.session, self.page_id = win, win.session, page_id
        self.item, self.pid = {"id": "window:" + page_id}, page_id
        lay = QVBoxLayout(self)
        mod, cls = PAGES[page_id]
        self.page = getattr(importlib.import_module(mod), cls)(self)
        if getattr(self.page, "expand_button", None) is not None:
            self.page.expand_button.hide()     # an own window has nothing to expand over
        lay.addWidget(self.page, 1)
        self.message = QLabel()
        self.message.setObjectName("message")
        self.message.setWordWrap(True)
        self.message.hide()
        lay.addWidget(self.message)
        self.retranslate(win.tr)
        self.refresh(win.session)
        self.setup_size(win, "page:" + page_id)

    def retranslate(self, tr):
        self.setWindowTitle(tr("menu." + self.page_id))
        self.page.retranslate(tr)

    def refresh(self, session):
        self.page.refresh(session)

    def _result(self, r):
        text = "" if r.ok else i18n.text_for(r, self.win.lang())
        if text:
            self.win.messages.append(text)
        self.message.setText(text)
        self.message.setVisible(bool(text))
        return r

    def run(self, command, **params):
        return self._result(self.session.dispatch(command, **params))

    def step(self, result):
        return self._result(result)


def open_page(win, page_id):
    """Open (or bring back) the own window of a top menu page; tests (quiet) get it without showing it."""
    pw = win.page_windows.get(page_id)
    if pw is None:
        pw = PageWindow(win, page_id)
        win.page_windows[page_id] = pw
    else:
        pw.refresh(win.session)
    if not win.quiet:
        pw.show()
        pw.raise_()
    return pw
