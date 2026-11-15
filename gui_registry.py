# gui_registry.py — реестр редакторов (Задача R).
# Меню "Редакторы" в gui.py строится из EDITORS.
# Группы: Предметы / Развитие / Бой / Магия / Мир / Настройки.


EDITORS = [
    # (key, title, group, callable(app))
    ("inventory", "🎒 Инвентарь", "Предметы",
     lambda app: __import__("gui_inventory").open_inventory(app)),
    ("shop", "📦 Каталог", "Предметы",
     lambda app: __import__("gui_shop").open_shop(app)),

    ("race", "Раса", "Развитие",
     lambda app: __import__("gui_editors").edit_race(app)),
    ("class", "Класс", "Развитие",
     lambda app: __import__("gui_editors").edit_class(app)),
    ("feats", "Черты и Стойки", "Развитие",
     lambda app: __import__("gui_editors").edit_feats(app)),
    ("skills", "Навыки", "Развитие",
     lambda app: __import__("gui_skills").edit_skills(app)),
    ("training", "Редактирование", "Развитие",
     lambda app: __import__("gui_training").edit_training(app)),

    ("attacks", "Атаки", "Бой",
     lambda app: __import__("gui_editors").edit_attacks(app)),
    ("saves", "Спасброски", "Бой",
     lambda app: __import__("gui_editors").edit_saves(app)),
    ("cmbcmd", "CMB/CMD-моды", "Бой",
     lambda app: __import__("gui_editors").edit_cmb_mods(app)),
    ("rest", "🛏 Восстановление", "Бой",
     lambda app: __import__("gui_rest").rest_dialog(app)),

    ("spells", "Заклинания", "Магия",
     lambda app: __import__("gui_spells").edit_spells(app)),

    ("drives", "🌀 Драйвы / Квесты", "Мир",
     lambda app: __import__("gui_stub").edit_drives(app)),
    ("courts", "🏛 Квирки/Дворы/Квесты", "Мир",
     lambda app: __import__("gui_stub").edit_courts(app)),
    ("lenses", "🔍 Линзы", "Мир",
     lambda app: __import__("gui_stub").edit_lenses(app)),
    ("templates", "📜 Шаблоны", "Мир",
     lambda app: __import__("gui_templates").edit_templates(app)),
    ("wiki", "📚 Вики", "Мир",
     lambda app: __import__("gui_wiki").edit_wiki(app)),

    ("settings", "Настройки", "Настройки",
     lambda app: __import__("gui_editors").edit_settings(app)),
]


def groups():
    """Список групп в порядке появления."""
    seen = []
    for _, _, g, _ in EDITORS:
        if g not in seen:
            seen.append(g)
    return seen


def by_group(group):
    return [e for e in EDITORS if e[2] == group]


def get(key):
    for e in EDITORS:
        if e[0] == key:
            return e
    return None