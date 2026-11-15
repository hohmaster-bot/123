# gui_menu.py — меню-бар (T-SPLIT).
# MENU_SPEC — чистые данные (JSON-совместимые): action — строка, имя метода App.
# Кнопки ✖ (выход) и — (свернуть в трей) — ВНЕ спеки, всегда справа, всегда видимы.
#
# Хранение пользовательских настроек (план, пока не активно):
#   config.json["menu_spec"]  — сохранённый спек (если есть, перекрывает MENU_SPEC);
#   save_menu_spec(spec)      — сохранить спек (зовёт UI-редактор меню, не build_menu);
#   reset_menu_spec()         — сбросить на дефолт.
# Позже: отдельная папка DND/настройки/ для переносимых наборов (см. TECH.md v15).

import tkinter as tk

from gui_app_config import load_app_config, save_app_config


# ---- Данные меню. Никаких лямбд и методов — только строки. ----
MENU_SPEC = {
    "_version": 1,
    "menus": [
        {
            "key": "file",
            "title": "Файл",
            "items": [
                {"type": "command", "title": "Создать нового...",      "action": "_new_character"},
                {"type": "command", "title": "Открыть из characters/...", "action": "_open_character"},
                {"type": "command", "title": "📁 Открыть папку",         "action": "_open_characters_folder"},
                {"type": "command", "title": "✏ Переименовать...",       "action": "_rename_character"},
                {"type": "command", "title": "Сохранить",               "action": "_save"},
                {"type": "separator"},
                {"type": "command", "title": "📥 Импортировать .wp...", "action": "_import_character"},
                {"type": "command", "title": "🌐 Импорт по URL...",      "action": "_import_character_url"},
                {"type": "command", "title": "📤 Экспортировать .wp...", "action": "_export_character"},
                {"type": "command", "title": "📄 Экспорт в PDF...",      "action": "_export_pdf"},
            ],
        },
        {
            "key": "view",
            "title": "Вид",
            "items": [
                {"type": "check", "title": "Источники записей",          "key": "show_sources"},
                {"type": "check", "title": "[прием] у атак",             "key": "show_maneuver"},
                {"type": "check", "title": "[основы] у оружия",          "key": "show_basics"},
                {"type": "check", "title": "[маст. N/3]",                "key": "show_mastery"},
                {"type": "check", "title": "[тир] у навыков",            "key": "show_tier"},
                {"type": "check", "title": "Разбивка спасбросков",       "key": "show_saves_breakdown"},
                {"type": "check", "title": "[⏱/⚡] у бафов",             "key": "show_buffs_tags"},
                {"type": "check", "title": "[игнор] у боли/морали",      "key": "show_ignore_marks"},
            ],
        },
        {
            "key": "tools",
            "title": "Инструменты",
            "items": [
                {"type": "command", "title": "📋 Скопировать лист", "action": "_copy_sheet"},
            ],
        },
        {
            "key": "editors",
            "title": "Редакторы",
            "items": [
                {"type": "command", "title": "🗂 Открыть окно «Редакторы»", "action": "_open_editors_window"},
            ],
        },
    ],
}


def _resolve_spec(app, spec):
    """Вернуть спек: аргумент → app._menu_spec → config.json['menu_spec'] → MENU_SPEC."""
    if spec is not None:
        return spec
    saved = getattr(app, "_menu_spec", None)
    if saved:
        return saved
    cfg = load_app_config()
    saved = cfg.get("menu_spec")
    if saved:
        return saved
    return MENU_SPEC


def _safe_version(spec):
    try:
        return int(spec.get("_version", 0) or 0)
    except Exception:
        return 0


def _build_one_menu(app, parent, menu_spec):
    """Построить один tk.Menu по описанию. Возвращает (menu, key)."""
    key = menu_spec.get("key", "")
    menu = tk.Menu(parent, tearoff=0)
    for item in menu_spec.get("items", []):
        it_type = item.get("type", "command")
        if it_type == "separator":
            menu.add_separator()
            continue
        if it_type == "command":
            name = item.get("action", "")
            cmd = getattr(app, name, None) if name else None
            if cmd is None:
                print(f"[menu] unknown action: {name!r} (menu={key!r})")
                continue
            menu.add_command(label=item.get("title", "?"), command=cmd)
            continue
        if it_type == "check":
            vkey = item.get("key", "")
            if not vkey:
                print(f"[menu] check without key (menu={key!r})")
                continue
            var = tk.BooleanVar(value=app._view_options.get(vkey, True))
            menu.add_checkbutton(
                label=item.get("title", "?"),
                variable=var,
                command=lambda k=vkey, v=var: app._toggle_view_opt(k, v),
            )
            continue
        print(f"[menu] unknown item type: {it_type!r} (menu={key!r})")
    return menu, key


def build_menu(app, spec=None, parent=None):
    """Построить меню-бар по спеку. ✖ и — добавляются ВНЕ спеки, справа.
    parent=None → app.root (classic); parent=<Toplevel> → меню-бар в этом окне (split)."""
    spec = _resolve_spec(app, spec)
    app._menu_spec = spec

    if _safe_version(spec) not in (0, 1):
        print(f"[menu] unsupported menu_spec version: {_safe_version(spec)}, using defaults")
        spec = MENU_SPEC
        app._menu_spec = spec

    root = parent if parent is not None else app.root
    menubar = tk.Frame(root, bg="#1a1a1a", pady=2, padx=5)
    menubar.pack(fill="x", side="top")
    app._menubar = menubar

    # Меню (leading): создаём tk.Menu и кнопки-открывашки.
    for menu_spec in spec.get("menus", []):
        menu, key = _build_one_menu(app, root, menu_spec)
        setattr(app, f"{key}_menu", menu)  # app.file_menu / app.view_menu / ...

        btn = tk.Button(menubar, text=menu_spec.get("title", "?"),
                        bg="#1a1a1a", fg="#ddd", relief="flat",
                        font=("Segoe UI", 9),
                        activebackground="#444", activeforeground="white")
        btn.pack(side="left", padx=2, pady=2)
        btn.bind("<Button-1>",
                 lambda e, m=menu, b=btn: (b.configure(relief="flat"),
                                           m.post(e.x_root, e.y_root + e.widget.winfo_height())))

    # Кнопки окна (trailing, ВНЕ спеки): ✖ и —, всегда видимы.
    # split: ✖ закрывает окно меню (вернуть — через трей), — в трей.
    # classic: ✖ выход, — в трей (как раньше).
    in_split = parent is not None
    if in_split:
        # Вызываем правильный метод скрытия, чтобы сплит знал об этом
        on_close = lambda: app._split._on_menu_close() if getattr(app, "_split", None) else parent.withdraw()
    else:
        on_close = app._on_close
    tk.Button(menubar, text="✖", command=on_close,
              bg="#1a1a1a", fg="#a33", relief="flat",
              font=("Segoe UI", 10, "bold"), width=2,
              activebackground="#a33", activeforeground="white"
              ).pack(side="right", padx=(0, 2), pady=2)
    tk.Button(menubar, text="—", command=app._hide_to_tray,
              bg="#1a1a1a", fg="#ddd", relief="flat",
              font=("Segoe UI", 10, "bold"), width=2,
              activebackground="#444", activeforeground="white"
              ).pack(side="right", padx=(0, 0), pady=2)


# ---- Сохранение пользовательских настроек меню (пока никто не зовёт). ----

def save_menu_spec(spec):
    """Сохранить спек меню в config.json. Зовёт UI-редактор, НЕ build_menu."""
    cfg = load_app_config()
    cfg["menu_spec"] = spec
    save_app_config(cfg)


def reset_menu_spec():
    """Сбросить сохранённый спек — build_menu снова возьмёт MENU_SPEC."""
    cfg = load_app_config()
    cfg.pop("menu_spec", None)
    save_app_config(cfg)