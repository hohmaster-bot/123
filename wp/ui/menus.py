"""The menu bar of the Classic window shell (package 32): Character (New demo character, Open, Save, Save as, Exit),
View (Theme: the theme list + follow the system; Language RU / EN; Scale; Editor mode, package 34), Help (show hints
again).
Every choice goes through the Session: character files through wp/app/files.py rules (window.files), app settings
through session.settings(...). build(win) makes the actions once; retranslate(win, tr) renames them and rebuilds the
theme list (own themes may appear)."""
from PySide6.QtGui import QAction, QActionGroup

PERCENT = 100                          # the label of a scale: 1.25 -> "125 %"
LANGS = ("ru", "en")


def _act(win, menu, key, slot, checkable=False):
    a = QAction(win)
    a.setCheckable(checkable)
    a.triggered.connect(slot)
    menu.addAction(a)
    win.actions[key] = a
    return a


def build(win):
    bar = win.menuBar()
    win.actions, win.menus = {}, {}
    m = win.menus["character"] = bar.addMenu("")
    _act(win, m, "new_demo", lambda: win.files.new_demo())
    _act(win, m, "open", lambda: win.files.open_dialog())
    _act(win, m, "save", lambda: win.files.save())
    _act(win, m, "save_as", lambda: win.files.save_as_dialog())
    m.addSeparator()
    _act(win, m, "exit", win.close)
    v = win.menus["view"] = bar.addMenu("")
    win.menus["theme"] = v.addMenu("")
    win.theme_group = None
    win.menus["language"] = v.addMenu("")
    group = QActionGroup(win)
    for lang in LANGS:
        a = _act(win, win.menus["language"], "lang." + lang, lambda _=False, lg=lang: win.set_setting("language", lg),
                 True)
        group.addAction(a)
    win.menus["scale"] = v.addMenu("")
    group = QActionGroup(win)
    for s in win.shell["scales"]:
        a = _act(win, win.menus["scale"], "scale.%s" % s, lambda _=False, sc=s: win.set_setting("ui_scale", sc), True)
        a.setText("%d %%" % round(s * PERCENT))
        group.addAction(a)
    v.addSeparator()
    _act(win, v, "theme_editor", lambda: __import__("wp.ui.theme_editor", fromlist=["open_editor"]).open_editor(win))
    _act(win, v, "editor", lambda on: win.session.set_editor_mode(bool(on)), True)   # package 34
    _act(win, v, "layout_editor", lambda: __import__("wp.ui.layout_editor", fromlist=["x"]).open_layout_editor(win))
    for key, page in (("settings", "settings"), ("catalog", "catalogs")):     # package 36 P1.3: top menus
        a = QAction(win)
        a.triggered.connect(lambda _=False, pg=page: __import__("wp.ui.page_window", fromlist=["x"]).open_page(win, pg))
        bar.addAction(a)
        win.actions["top." + key] = a
    h = win.menus["help"] = bar.addMenu("")
    _act(win, h, "hints_reset", lambda: win.session_settings("hints_reset"))


def _theme_menu(win, tr):
    menu = win.menus["theme"]
    menu.clear()
    group = QActionGroup(win)
    view = win.session.themes_view(win.system_dark())
    follow = bool(win.session.setting("theme_follow_system"))
    for tid, name, _layer, _warn in view["themes"]:
        a = QAction(win)
        a.setCheckable(True)
        a.setText(tr("theme." + tid) if tr("theme." + tid) != "theme." + tid else (name or tid))
        a.setChecked(tid == view["active"] and not follow)
        a.triggered.connect(lambda _=False, t=tid: win.choose_theme(t))
        group.addAction(a)
        menu.addAction(a)
        win.actions["theme." + tid] = a
    menu.addSeparator()
    a = QAction(win)
    a.setCheckable(True)
    a.setChecked(follow)
    a.setText(tr("menu.theme_follow_system"))
    a.triggered.connect(lambda on: win.set_setting("theme_follow_system", bool(on)))
    menu.addAction(a)
    win.actions["theme_follow_system"] = a
    win.theme_group = group


def retranslate(win, tr):
    for key in ("character", "view", "theme", "language", "scale", "help"):
        win.menus[key].setTitle(tr("menu." + key))
    win.actions["editor"].setChecked(bool(getattr(win.session, "editor_mode", False)))
    win.actions["top.settings"].setText(tr("menu.settings"))
    win.actions["top.catalog"].setText(tr("menu.catalog"))
    for key in ("new_demo", "open", "save", "save_as", "exit", "hints_reset", "editor", "theme_editor",
                "layout_editor"):
        win.actions[key].setText(tr("menu." + key))
    lang = win.session.setting("language")
    for lg in LANGS:
        win.actions["lang." + lg].setText(tr("lang." + lg))
        win.actions["lang." + lg].setChecked(lg == lang)
    scale = float(win.session.setting("ui_scale"))
    for s in win.shell["scales"]:
        win.actions["scale.%s" % s].setChecked(float(s) == scale)   # the setting holds one of these values
    win.actions["layout_editor"].setEnabled(bool(getattr(win.session, "editor_mode", False)))   # package 35 P5
    win.actions["save"].setEnabled(win.session.character is not None)
    win.actions["save_as"].setEnabled(win.session.character is not None)
    _theme_menu(win, tr)
