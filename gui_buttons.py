# gui_buttons.py — кнопки левого меню (Задача R / T-SPLIT)
import tkinter as tk
import gui_editors
import gui_skills
import gui_spells
import gui_stub
import gui_training
import gui_inventory
import gui_shop
import gui_templates
import gui_wiki

DEFAULT_VISIBLE_BUTTONS = {
    "Переименовать": True, "Музыка": True, "Ссылка": True,
    "Инвентарь": True, "Каталог": True, "Шаблоны": True,
    "Вики": True, "Драйвы": True, "CMB/CMD-моды": True,
    "Линзы": True, "Раса": True, "Класс": True, "Черты": True,
    "Квирки": True, "Навыки": True, "Атаки": True,
    "Спасброски": True, "Редактирование": True, "Заклинания": True,
    "Восстановление": True, "Настройки": True, "Сохранить": True,
    "Выход": True,
}

FORCED_VISIBLE_BUTTONS = {"Настройки"}

# Кнопки, которые показывают содержимое в чарнике (центре).
# Клик по такой кнопке при закрытом центре (режим split) — открывает центр.
# Кнопки, которых тут нет, открывают своё окно (Toplevel/диалог) — центр не трогают.
CENTER_BUTTONS = {
    "Раса", "Класс", "Черты", "Квирки", "Навыки",
    "Атаки", "Спасброски", "CMB/CMD-моды",
    "Редактирование", "Заклинания",
    "Восстановление", "Настройки", "Инвентарь", "Каталог",
    "Вики", "Шаблоны",
}


def buttons_list(app):
    return [
        ("✏ Переименовать", app._rename_character, "Переименовать"),
        ("", None, None),
        ("▶ Музыка", app._play_music, "Музыка"),
        ("🔗 Ссылка", app._set_music, "Ссылка"),
        ("", None, None),
        ("🎒 Инвентарь", app._open_inventory, "Инвентарь"),
        ("📦 Каталог", app._open_catalogs, "Каталог"),
        ("📜 Шаблоны", app._edit_templates, "Шаблоны"),
        ("📚 Вики", app._edit_wiki, "Вики"),
        ("", None, None),
        ("🌀 Драйвы / Квесты", lambda: gui_stub.edit_drives(app), "Драйвы"),
        ("🔍 Линзы", lambda: gui_stub.edit_lenses(app), "Линзы"),
        ("", None, None),
        ("Раса", lambda: gui_editors.edit_race(app), "Раса"),
        ("Класс", lambda: gui_editors.edit_class(app), "Класс"),
        ("Черты и Стойки", lambda: gui_editors.edit_feats(app), "Черты"),
        ("🏛 Квирки/Дворы/Квесты", lambda: gui_stub.edit_courts(app), "Квирки"),
        ("Навыки", lambda: gui_skills.edit_skills(app), "Навыки"),
        ("Атаки", lambda: gui_editors.edit_attacks(app), "Атаки"),
        ("Спасброски", lambda: gui_editors.edit_saves(app), "Спасброски"),
        ("CMB/CMD-моды", lambda: gui_editors.edit_cmb_mods(app), "CMB/CMD-моды"),
        ("", None, None),
        ("Редактирование", lambda: gui_training.edit_training(app), "Редактирование"),
        ("Заклинания", lambda: gui_spells.edit_spells(app), "Заклинания"),
        ("🛏 Восстановление", app._rest_dialog, "Восстановление"),
        ("Настройки", lambda: gui_editors.edit_settings(app), "Настройки"),
        ("", None, None),
        ("Сохранить", lambda: app._save(), "Сохранить"),
        ("", None, None),
        ("🚪 Выход", app._on_close, "Выход"),
    ]


def is_visible(app, key):
    if not app.c:
        return True
    if key in FORCED_VISIBLE_BUTTONS:
        return True
    vb = app.c.settings.get("visible_buttons", {})
    if key in vb:
        return vb[key]
    return DEFAULT_VISIBLE_BUTTONS.get(key, True)


def rebuild_side_buttons(app):
    """Перерисовывает кнопки левого меню с учётом visible_buttons."""
    for w in app.buttons_inner.winfo_children():
        w.destroy()
    for text, cmd, key in buttons_list(app):
        if cmd is None:
            tk.Frame(app.buttons_inner, height=6, bg="#1a1a1a").pack(fill="x")
        else:
            if app.c and not is_visible(app, key):
                continue
            tk.Button(app.buttons_inner, text=text, command=cmd,
                      anchor="w", font=("Segoe UI", 10),
                      relief="flat", bg="#3a3a3a", fg="white",
                      activebackground="#555",
                      activeforeground="white"
                      ).pack(fill="x", padx=4, pady=1)