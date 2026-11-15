# character.py — модель персонажа v12
# v12: ranged/thrown оружие, диапазон, JSON-каталоги,
#      required_level, штраф невладения −4

import json
import math
import os
import re
import sys
import uuid
try:
    from modifiers import (
        BONUS_TYPES, BONUS_TYPES_FLAT, BONUS_TYPES_ROLL, BONUS_TYPES_CMD,
        AC_TOUCH_TYPES as _AC_TOUCH_TYPES_SET, AC_FLAT_TYPES, AC_PARRY_TYPES,
        AC_FULL_TYPES, AC_TYPES_NON_STACK as _AC_NON_STACK_LIST,
        apply_bonus_type, size_mod as _size_mod, size_mod_attack,
        apply_effects_defaults,
    )
except ImportError:
    from DND.modifiers import (
        BONUS_TYPES, BONUS_TYPES_FLAT, BONUS_TYPES_ROLL, BONUS_TYPES_CMD,
        AC_TOUCH_TYPES as _AC_TOUCH_TYPES_SET, AC_FLAT_TYPES, AC_PARRY_TYPES,
        AC_FULL_TYPES, AC_TYPES_NON_STACK as _AC_NON_STACK_LIST,
        apply_bonus_type, size_mod as _size_mod, size_mod_attack,
        apply_effects_defaults,
    )

if getattr(sys, "frozen", False):
    _exe = os.path.abspath(sys.argv[0])
    if _exe.lower().endswith(".exe") and os.path.isfile(_exe):
        BASE_DIR = os.path.dirname(_exe)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARACTERS_DIR = os.path.join(BASE_DIR, "characters")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
CATALOGS_DIR = os.path.join(BASE_DIR, "catalogs")

WEAPON_LEVELS = [
    "Не владеет", "Новичок", "Ученик", "Любитель", "Опытный",
    "Специалист I", "Специалист II", "Специалист III",
    "Эксперт I", "Эксперт II", "Эксперт III", "Эксперт IV", "Мастер",
]
ARMOR_LEVELS = ["None", "Light", "Medium", "Heavy"]
SHIELD_LEVELS = ["None", "Light", "Heavy", "Tower"]

# ============ БОНУСЫ ВЛАДЕНИЯ ОРУЖИЕМ ============
WEAPON_BONUS_CATALOG = {
    "spec_parry_1": {
        "name": "Парирование +1", "type": "spec", "max_stacks": 3,
        "desc": "Увеличение парирования на 1.",
    },
    "spec_hardness_30": {
        "name": "Прочность +30%", "type": "spec", "max_stacks": 3,
        "desc": "Повышение прочности оружия на 30%.",
    },
    "spec_attack_1": {
        "name": "Атака +1", "type": "spec", "max_stacks": 3,
        "desc": "Бонус квалификации к атакам на 1.",
    },
    "spec_crit_range": {
        "name": "Крит +1", "type": "spec", "max_stacks": 3,
        "desc": "Расширение критического диапазона на 1.",
    },
    "spec_range_10": {
        "name": "Дальность +10 фт", "type": "spec", "max_stacks": 3,
        "desc": "Увеличение дальности атаки на 10 фт.",
    },
    "spec_balance_1": {
        "name": "Баланс +1/ход", "type": "spec", "max_stacks": 3,
        "desc": "Восстановление баланса +1/ход.",
    },
    "expert_hp_1": {
        "name": "HP оружия +1", "type": "expert", "max_stacks": 2,
        "desc": "Повышение HP оружия на 1.",
    },
    "expert_hardness_70": {
        "name": "Прочность +70%", "type": "expert", "max_stacks": 2,
        "desc": "Повышение прочности оружия на 70% (складывается со spec).",
    },
    "expert_damage_3": {
        "name": "Урон +3", "type": "expert", "max_stacks": 2,
        "desc": "Бонус к урону +3.",
    },
    "expert_ignore_vuln": {
        "name": "Игнор первой уязвимости", "type": "expert",
        "max_stacks": 2,
        "desc": "Игнорирование первой уязвимости в бою.",
    },
    "expert_ignore_cover": {
        "name": "Игнор 20% укрытия", "type": "expert",
        "max_stacks": 2,
        "desc": "Игнорирование 20% укрытия.",
    },
    "expert_lucky_1": {
        "name": "Счастливая атака +1", "type": "expert",
        "max_stacks": 2,
        "desc": "Бонус к счастливым атакам +1.",
    },
    "expert_parry_range": {
        "name": "Парир. дальней атаки", "type": "expert",
        "max_stacks": 2,
        "desc": "Первую дальнюю атаку в раунд можно парировать.",
    },
    "master_reroll": {
        "name": "Переброс d20", "type": "master", "max_stacks": 1,
        "desc": "Переброс одного d20 с этим оружием.",
    },
    "master_no_attack_tag": {
        "name": "Атака без тега [атака]", "type": "master",
        "max_stacks": 1,
        "desc": "Одна атака в ход не получает тега [атака].",
    },
    "master_full_balance": {
        "name": "Полный баланс 1/бой", "type": "master",
        "max_stacks": 1,
        "desc": "Раз за бой свободным действием восстановить весь баланс.",
    },
}

WEAPON_BONUS_SLOTS = [
    (5, "Спец I"), (6, "Спец II"), (7, "Спец III"),
    (8, "Эксперт I"), (9, "Эксперт II"), (10, "Эксперт III"),
    (11, "Эксперт IV"), (12, "Мастер"),
]


def allowed_bonus_types_for_slot(slot_level):
    if slot_level < 5:
        return []
    if slot_level <= 7:
        return ["spec"]
    if slot_level <= 11:
        return ["expert", "spec"]
    return ["master", "expert", "spec"]


def weapon_available_slots(level):
    return sum(1 for lvl, _ in WEAPON_BONUS_SLOTS if lvl <= level)


ARMOR_DISPLAY = {
    "None":   "Не владеет броней",
    "Light":  "Легкая броня, парирование +2",
    "Medium": "Легкая и средняя броня, парирование +4",
    "Heavy":  "Все виды доспехов, парирование +6",
}
SHIELD_DISPLAY = {
    "None":   "Не владеет щитами",
    "Light":  "Легкие щиты",
    "Heavy":  "Легкие и тяжелые щиты",
    "Tower":  "Все щиты включая ростовые, парирование +2",
}
ARMOR_PARRYING = {"None": 0, "Light": 2, "Medium": 4, "Heavy": 6}
SHIELD_PARRYING = {"None": 0, "Light": 0, "Heavy": 0, "Tower": 2}

SIZES = ["Fine", "Diminutive", "Tiny", "Small", "Medium",
         "Large", "Huge", "Gargantuan", "Colossal"]
SIZE_AC = {"Fine": 8, "Diminutive": 4, "Tiny": 2, "Small": 1,
           "Medium": 0, "Large": -1, "Huge": -2,
           "Gargantuan": -4, "Colossal": -8}
SIZE_CMB = {"Fine": -8, "Diminutive": -4, "Tiny": -2, "Small": -1,
            "Medium": 0, "Large": 1, "Huge": 2,
            "Gargantuan": 4, "Colossal": 8}

SOURCE_ICONS = {"training": "T", "race": "R", "class": "C",
                "loot": "L", "quirk": "Q", "template": "Ш"}
SOURCE_NAMES = {"training": "Тренировки", "race": "Раса",
                "class": "Класс", "loot": "Лут", "quirk": "Квирк",
                "template": "Шаблон"}

# ============ ЗАКЛИНАНИЯ: константы (Задача C) ============

# Действия по времени сотворения (PF1).
# swift/immediate = 0 (не дают перегрузки).
CASTING_ACTIONS = {
    "swift": 0, "immediate": 0,
    "move": 1,
    "standard": 2,
    "full_round": 3,
    "one_round": 4,
}

# Таблица кругов: (мана, перегрузка, баланс).
SPELL_CIRCLE_TABLE = {
    0: {"mana": 0,  "overload": 4, "balance": 0},
    1: {"mana": 1,  "overload": 2, "balance": 1},
    2: {"mana": 3,  "overload": 2, "balance": 3},
    3: {"mana": 5,  "overload": 2, "balance": 5},
    4: {"mana": 7,  "overload": 2, "balance": 7},
    5: {"mana": 9,  "overload": 2, "balance": 9},
    6: {"mana": 11, "overload": 2, "balance": 11},
    7: {"mana": 13, "overload": 2, "balance": 13},
    8: {"mana": 15, "overload": 2, "balance": 15},
    9: {"mana": 17, "overload": 2, "balance": 17},
}

SPELL_ATTACK_SUFFIX = {
    "": "",
    "ranged": " (Ranged)",
    "ranged_touch": " (Ranged touch)",
    "melee": " (Melee)",
    "melee_finesse": " (MeleeF)",
}

SPELL_AOE_NAMES = {
    "": "", "burst": "всплеск", "cone": "конус",
    "cylinder": "цилиндр", "emanation": "эманация",
    "line": "линия", "sphere": "сфера", "spread": "распространение",
}

SKILL_TIERS = ["normal", "advanced", "specialized"]
SKILL_TIER_NAMES = {"normal": "обычный",
                    "advanced": "продвинутый",
                    "specialized": "специализированный"}

PAIN_MAX = 8
PAIN_HP_STEP = 3
SAVE_STATS = {"fort": "con", "ref": "dex", "will": "wis"}
BAB_MAP = {"full": "good", "3/4": "medium", "1/2": "poor"}

# T-BONUS-TYPES-2 (v18.4): источники правды — в modifiers.py.
# Здесь — алиасы для обратной совместимости (внешние импорты).
AC_TYPES_NON_STACK = ["armor", "shield", "natural", "deflection",
                       "insight", "morale", "competence", "luck",
                       "circumstance"]
AC_TYPE_DODGE = "dodge"
AC_TOUCH_TYPES = ["deflection", "dodge", "insight", "morale",
                   "competence", "luck", "circumstance"]
AC_TYPE_NAMES = {
    "armor": "Доспех", "shield": "Щит", "natural": "Натуральный",
    "deflection": "Отражение", "dodge": "Уклонение (складывается)",
    "insight": "Предвидение", "morale": "Мораль",
    "competence": "Компетентность", "luck": "Удача",
    "circumstance": "Обстоятельства",
}

# SIT_ALL_TARGETS удалено: `all` запрещён (CONTRACT §4).
VALID_SIT_TARGETS = {
    "attack", "damage", "save", "skill", "ac",
    "speed", "speed_mult",
    "str", "dex", "con", "int", "wis", "cha",
    "fort", "ref", "will",
    "lucky", "hp_temp",
    # T44: восстановление ресурсов (тик и разово)
    "restore_hp", "restore_mana", "restore_spirit",
    "restore_balance", "restore_resource",
    # T45: кровотечение (урон на тике)
    "self_damage_per_tick",
    # Задача B: CMB / CMD / инициатива как ситуативные цели
    "cmb", "cmd", "initiative",
    # T-MAX-STATS (v18.5)
    "max_hp", "max_mana", "max_balance", "max_spirit",
    "max_resource", "max_pain_threshold",
}

INJURY_SEVERITIES = {
    "light":  {"name": "Лёгкая травма",  "cost": 2,  "heal_rating": 3},
    "medium": {"name": "Средняя травма", "cost": 5,  "heal_rating": 2},
    "heavy":  {"name": "Тяжёлая травма", "cost": 12, "heal_rating": 1},
}

LOCATIONS = ["equipped", "unload", "bag", "base"]
LOCATION_NAMES = {
    "equipped": "Кукла", "unload": "Разгрузка",
    "bag": "Сумка", "base": "База",
}

EQUIP_SLOTS = [
    "armor", "belt", "body", "chest", "eyes", "gloves", "head",
    "neck", "ring1", "ring2", "back", "shoulders", "legs", "feet",
    "weapon_main", "weapon_off", "shield", "companion", "pet",
    "modifier", "tools_craft", "tools_travel", "components",
    "holy_symbol", "unload",
]
SLOT_NAMES = {
    "armor": "Броня / Одежда", "belt": "Пояс", "body": "Тело",
    "chest": "Грудь", "eyes": "Глаза", "gloves": "Перчатки",
    "head": "Голова", "neck": "Шея", "ring1": "Кольцо 1",
    "ring2": "Кольцо 2", "back": "Спина", "shoulders": "Плечи",
    "legs": "Ноги", "feet": "Ступни", "weapon_main": "Оружие (осн.)",
    "weapon_off": "Оружие (втор.)", "shield": "Щит",
    "companion": "Спутник", "pet": "Питомец",
    "modifier": "Модификатор",
    "tools_craft": "Инструменты ремесленные",
    "tools_travel": "Инструменты походные",
    "components": "Магические компоненты",
    "holy_symbol": "Предмет поклонения",
    "unload": "Разгрузка (расширение)",
}
CATEGORY_TO_SLOTS = {
    "armor": ["armor"], "shield": ["shield"],
    "weapon": ["weapon_main", "weapon_off"],
    "belt": ["belt"], "body": ["body"], "chest": ["chest"],
    "eyes": ["eyes"], "gloves": ["gloves"], "head": ["head"],
    "neck": ["neck"], "ring": ["ring1", "ring2"], "back": ["back"],
    "shoulders": ["shoulders"], "legs": ["legs"], "feet": ["feet"],
    "companion": ["companion"], "pet": ["pet"],
    "modifier": ["modifier"], "tools_craft": ["tools_craft"],
    "tools_travel": ["tools_travel"], "components": ["components"],
    "holy_symbol": ["holy_symbol"], "unload": ["unload"],
    "consumable": [], "misc": [],
}
ITEM_CATEGORIES = [
    "armor", "shield", "weapon", "belt", "body", "chest", "eyes",
    "gloves", "head", "neck", "ring", "back", "shoulders", "legs",
    "feet", "companion", "pet", "modifier", "tools_craft",
    "tools_travel", "components", "holy_symbol", "unload",
    "consumable", "misc",
]
SLOT_ALIASES = {"helmet": "head", "cloak": "back",
                "boots": "feet", "amulet": "neck"}
ARMOR_TYPE_ORDER = {"None": 0, "Light": 1, "Medium": 2,
                    "Heavy": 3, "Tower": 3}

# ============ КАТАЛОГИ (загружаются из catalogs/*.json) ============

WEAPON_GROUP_CATALOG = []   # [{name, scale, difficulty, maneuvers, weapons}]
ARMOR_CATALOG = []          # [item_dict, ...]
SHIELD_CATALOG = []         # [item_dict, ...]
# K2c: новые каталоги
WEAPON_ITEM_CATALOG = []
FEATS_CATALOG = []
TEMPLATES_CATALOG = []
SKILLS_CATALOG = []
RACE_ABILITIES_CATALOG = []
CLASS_ABILITIES_CATALOG = []
SPELLS_CATALOG = []
BUFFS_CATALOG = []
CUSTOM_CATALOG = []

def load_catalogs(settings=None):
    """Загружает JSON-каталоги из catalogs/*.
    T-CAT: catalogs_enabled = ['<папка>/<файл>.json', ...] или ['<папка>'].
    catalogs_items_disabled = ['<папка>/<файл>#<имя>', ...].
    catalogs_mode = 'whitelist' | 'blacklist'.
    Если _enabled пуст — всё включено (обратная совместимость).
    """
    if settings is None:
        try:
            cfg_path = os.path.join(BASE_DIR, "config.json")
            with open(cfg_path, "r", encoding="utf-8") as f:
                _cfg = json.load(f)
            _last = _cfg.get("last_character", "")
            if _last:
                _p = os.path.join(CHARACTERS_DIR,
                                   f"{_last}.json")
                if os.path.exists(_p):
                    with open(_p, "r", encoding="utf-8") as f2:
                        _data = json.load(f2)
                    settings = _data.get("settings", {})
        except Exception:
            settings = {}
    _enabled = (settings or {}).get("catalogs_enabled", []) or []
    _items_disabled = (settings or {}).get(
        "catalogs_items_disabled", []) or []
    _mode = (settings or {}).get("catalogs_mode", "whitelist")

    def _allowed(sub, fname=None):
        """Фильтр по файлу ('sub/fname.json') и по папке (старое)."""
        if not _enabled:
            return True
        file_key = f"{sub}/{fname}" if fname else None
        folder_key = sub
        if _mode == "whitelist":
            return (folder_key in _enabled) or (
                file_key is not None and file_key in _enabled)
        return (folder_key not in _enabled) and (
            file_key is None or file_key not in _enabled)

    def _item_allowed(sub, fname, item):
        """Скрыт ли конкретный элемент (catalogs_items_disabled)."""
        if not _items_disabled:
            return True
        nm = (item.get("name") or "").strip()
        if not nm:
            return True
        key = f"{sub}/{fname}#{nm}"
        return key not in _items_disabled

    global WEAPON_GROUP_CATALOG, ARMOR_CATALOG, SHIELD_CATALOG
    global WEAPON_ITEM_CATALOG, FEATS_CATALOG
    global TEMPLATES_CATALOG, SKILLS_CATALOG
    global RACE_ABILITIES_CATALOG, CLASS_ABILITIES_CATALOG
    global SPELLS_CATALOG, BUFFS_CATALOG, CUSTOM_CATALOG
    WEAPON_GROUP_CATALOG = []
    ARMOR_CATALOG = []
    SHIELD_CATALOG = []
    WEAPON_ITEM_CATALOG = []
    FEATS_CATALOG = []
    TEMPLATES_CATALOG = []
    SKILLS_CATALOG = []
    RACE_ABILITIES_CATALOG = []
    CLASS_ABILITIES_CATALOG = []
    SPELLS_CATALOG = []
    BUFFS_CATALOG = []
    CUSTOM_CATALOG = []

    _simple_map = {
        "weapon_items": WEAPON_ITEM_CATALOG,
        "feats": FEATS_CATALOG,
        "templates": TEMPLATES_CATALOG,
        "skills": SKILLS_CATALOG,
        "race_abilities": RACE_ABILITIES_CATALOG,
        "class_abilities": CLASS_ABILITIES_CATALOG,
        "spells": SPELLS_CATALOG,
        "buffs": BUFFS_CATALOG,
        "custom": CUSTOM_CATALOG,
    }

    for subdir in CATALOG_SUBDIRS:
        folder = os.path.join(CATALOGS_DIR, subdir)
        if not os.path.isdir(folder):
            continue
        for fname in sorted(os.listdir(folder)):
            if not fname.endswith(".json"):
                continue
            if not _allowed(subdir, fname):
                continue
            path = os.path.join(folder, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"[catalog {fname}] {e}")
                continue
            if subdir == "weapons":
                for g in data.get("groups", []):
                    g.setdefault("pack", fname[:-5])
                    if _item_allowed(subdir, fname, g):
                        WEAPON_GROUP_CATALOG.append(g)
            elif subdir == "armor":
                for it in data.get("items", []):
                    it.setdefault("category", "armor")
                    it.setdefault("ac_type", "armor")
                    it.setdefault("pack", fname[:-5])
                    if _item_allowed(subdir, fname, it):
                        ARMOR_CATALOG.append(it)
            elif subdir == "shields":
                for it in data.get("items", []):
                    it.setdefault("category", "shield")
                    it.setdefault("ac_type", "shield")
                    it.setdefault("pack", fname[:-5])
                    if _item_allowed(subdir, fname, it):
                        SHIELD_CATALOG.append(it)
            elif subdir in _simple_map:
                target = _simple_map[subdir]
                for it in data.get("items", []):
                    if isinstance(it, dict):
                        it.setdefault("pack", fname[:-5])
                        if _item_allowed(subdir, fname, it):
                            target.append(it)



CATALOG_SUBDIRS = [
    "weapons", "armor", "shields",
    "weapon_items", "feats", "templates",
    "skills", "race_abilities", "class_abilities",
    "spells", "buffs", "custom",
]


def ensure_dirs():
    for folder in (BASE_DIR, CHARACTERS_DIR, EXPORTS_DIR, CATALOGS_DIR):
        os.makedirs(folder, exist_ok=True)
    for sub in CATALOG_SUBDIRS:
        folder = os.path.join(CATALOGS_DIR, sub)
        os.makedirs(folder, exist_ok=True)
        custom_path = os.path.join(folder, "custom.json")
        if not os.path.exists(custom_path):
            try:
                with open(custom_path, "w", encoding="utf-8") as f:
                    if sub == "weapons":
                        json.dump({"groups": []}, f,
                                  ensure_ascii=False, indent=2)
                    else:
                        json.dump({"items": []}, f,
                                  ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[ensure_dirs custom {sub}] {e}")
    try:
        load_catalogs()
    except Exception as e:
        print(f"[load_catalogs] {e}")


# ============ ХЕЛПЕРЫ ============

def _new_save():
    return {"base": 0, "mods": []}


def _new_mana():
    return {
        "current": 0, "enabled": False, "class_max": 0,
        "bonus_sources": [{"name": "", "value": 0},
                           {"name": "", "value": 0}],
    }


def _new_downtime():
    return {
        "gold":   {"name": "Золото",  "amount": 0},
        "silver": {"name": "Серебро", "amount": 0},
        "copper": {"name": "Медь",    "amount": 0},
        "rates":  {"gold_to_silver": 100, "silver_to_copper": 100},
        "time_points": {"current": 0, "max": 0},
    }


def _make_item(**kwargs):
    item = {
        "id": str(uuid.uuid4()),
        "name": "", "category": "misc", "location": "bag",
        "slot": None, "order": 0, "qty": 1, "desc": "",
        "icon_b64": "",
        "weight": 0, "weight_type": "mass",
        "armor_type": None, "ac_bonus": 0, "ac_type": "armor",
        "ac_max_dex": None,
        "skill_penalty": 0, "speed_penalty": 0,
        "arcane_failure": 0, "mana_penalty": 0,
        "unprof_penalty": -2,
        # оружие
        "damage": "", "damage_sml": "", "damage_med": "",
        "crit_threshold": 20, "crit_mult": 2,
        "lucky_threshold": 20,
        "weapon_group": "",
        "attack_bonus": 0, "damage_bonus": 0,
        "finesse": False, "two_handed": False,
        "ranged": False, "thrown": False, "range_ft": 0,
        "required_level": 0,
        "damage_type": "", "hands": "",
        # заряды
        "uses": False, "uses_max": 0, "uses_current": 0,
        "show_on_panel": False,
        "tick_mode": "none", "tick_on_initiative": False,
        "cooldown_rounds": 0, "cooldown_current": 0,
        # HP / прочность
        "hp": 0, "max_hp": 0, "hardness": 0,
        # пассивные бонусы
        "passive_bonuses": [],
        # активация
        "activatable": False, "activation_cost_spirit": 0,
        "activation_effects": [], "activation_duration": 0,
        "activated": False,
        # база
        "base_slots": 1, "gray": False,
        "enchants": [],
        "unload_bonus": 0,
        # цена (для каталога/магазина)
        "price": 0,
    }
    item.update(kwargs)
    return item


def catalog_item_to_make_item_args(cat_item, category_hint=None):
    """Конвертирует запись JSON-каталога в kwargs для _make_item."""
    damage_med = cat_item.get("damage_med",
                                cat_item.get("damage", ""))
    return {
        "name": cat_item.get("name", "Без названия"),
        "category": cat_item.get("category",
                                   category_hint or "misc"),
        "desc": cat_item.get("desc", ""),
        "price": cat_item.get("price", 0),
        "armor_type": cat_item.get("armor_type"),
        "ac_bonus": cat_item.get("ac_bonus", 0),
        "ac_type": cat_item.get("ac_type", "armor"),
        "ac_max_dex": cat_item.get("ac_max_dex"),
        "skill_penalty": cat_item.get("skill_penalty", 0),
        "speed_penalty": cat_item.get("speed_penalty", 0),
        "arcane_failure": cat_item.get("arcane_failure", 0),
        "weight": cat_item.get("weight", 0),
        "weight_type": cat_item.get("weight_type", "mass"),
        "hardness": cat_item.get("hardness", 0),
        "hp": cat_item.get("hp", 0),
        "max_hp": cat_item.get("hp", 0),
        "damage": damage_med,
        "damage_sml": cat_item.get("damage_sml", ""),
        "damage_med": cat_item.get("damage_med", ""),
        "damage_type": cat_item.get("damage_type", ""),
        "crit_threshold": cat_item.get("crit_threshold", 20),
        "crit_mult": cat_item.get("crit_mult", 2),
        "weapon_group": cat_item.get("weapon_group", ""),
        "ranged": cat_item.get("ranged", False),
        "thrown": cat_item.get("thrown", False),
        "range_ft": cat_item.get("range_ft", 0),
        "required_level": cat_item.get("required_level", 0),
        "finesse": cat_item.get("finesse", False),
        "two_handed": cat_item.get("two_handed", False),
        "hands": cat_item.get("hands", ""),
    }


def _skill_expected_value(c, name):
    skill = None
    for s in c.skills:
        if s["name"] == name:
            skill = s
            break
    if not skill:
        return 0
    tier = skill.get("tier", "normal")
    level = c.level
    rank = skill.get("rank", 0)
    other_adv = sum(1 for s in c.skills
                    if s["name"] != name
                    and s.get("tier") in ("advanced", "specialized"))
    other_spec = sum(1 for s in c.skills
                     if s["name"] != name
                     and s.get("tier") == "specialized")
    cost = 0
    if tier == "advanced":
        cost += 40 + 20 * other_adv
    elif tier == "specialized":
        cost += (40 + 20 * other_adv) + (200 + 50 * other_spec)
    if tier == "normal":
        cost += 20 * rank * (rank + 1) // 2
    elif tier == "advanced":
        cost += 15 * rank * (rank + 1) // 2
    else:
        if rank > level:
            cost += 10 * (rank * (rank + 1) // 2
                          - level * (level + 1) // 2)
    return cost

def spell_display_name(spell):
    """Название заклинания с суффиксом по attack_type."""
    base = (spell.get("name") or "").strip()
    at = (spell.get("attack_type") or "").strip()
    return base + SPELL_ATTACK_SUFFIX.get(at, "")


def spell_overload_auto(spell):
    """Авто-перегрузка по casting_time и mana_cost."""
    ct = (spell.get("casting_time") or "standard").strip()
    actions = CASTING_ACTIONS.get(ct, 2)
    mana = int(spell.get("mana_cost", 0) or 0)
    mult = 2 if mana == 0 else 1
    return actions * mult

# ============ ДРАЙВЫ ============
DRIVE_KEYS = [
    ("idealism",  "Идеализм"),
    ("growth",    "Рост"),
    ("knowledge", "Знание"),
    ("autonomy",  "Автономия"),
    ("pleasure",  "Удовольствие"),
    ("material",  "Материальное"),
    ("triumph",   "Триумф"),
    ("success",   "Успех"),
    ("society",   "Общество"),
    ("decadence", "Декаданс"),
]

DRIVE_LEVEL_NAMES = {
    0: "низкая", 1: "средняя", 2: "высокая",
    3: "очень высокая", 4: "экстремальная", 5: "мания",
}

COURT_TIERS = ["I", "II", "III", "IV", "V"]


# ============ КЛАСС CHARACTER ============

class Character:
    def __init__(self, name="Без имени"):
        self.name = name
        self.xp = 0
        self.xp_threshold = 1000
        self.portrait = ""
        self.portrait_b64 = ""
        self.background_image = ""
        self.background_b64 = ""
        self.music_url = ""

        self.char_class = {
            "name": "", "level": 1, "hp_die": 8, "hp_rolls": [],
            "abilities": [], "has_spellbook": False,
            "spell_discount_extra": 0,
            "bab_type": "good", "good_saves": [],
        }
        self.race = {"name": "", "type": "", "speed": 30,
                      "abilities": []}
        self.abilities = {"str": 10, "dex": 10, "con": 10,
                          "int": 10, "wis": 10, "cha": 10}
        self.ability_damage = {"str": 0, "dex": 0, "con": 0,
                                "int": 0, "wis": 0, "cha": 0}

        self.combat = {
            "hp_current": 0, "hp_bought": 0, "hp_temp": 0,
            "ac": 10, "initiative": 0, "speed": 30,
            "bab": 0, "cmb": 0, "cmd": 10, "size": "Medium",
            "saves": {"fort": _new_save(), "ref": _new_save(),
                       "will": _new_save()},
        }
        self.equipment = {"armor_ac": 0, "shield_ac": 0,
                          "add_shield_ac_to_balance": False}
        self.natural_armor = 0
        self.ac_bonus = 0
        self.ac_misc = 0
        self.cmb_mods = []
        self.cmd_mods = []

        self.items = {}
        self.downtime = _new_downtime()
        self.bag_dropped = False

        self.pain_threshold = {"current": 0, "max": 0}
        self.pain_threshold_bonus = 0
        self.pain_extra = 0
        self.pain_extra_temp = 0
        self.pain_max = PAIN_MAX
        self.regen_modifier = ""
        self.ignore_pain = False
        self.overload = 0
        self.overload_enabled = False
        self.auto_balance_on_tick = True
        self.balance = {"current": 0, "max": 0}
        self.balance_bonus = 0
        self.balance_restore_bonus = 0
        self.spirit = {"current": 0, "max": 0}
        self.spirit_bonus = 0
        self.hp_bonus = 0
        self.mana = _new_mana()

        self.injury_points = 0
        self.injuries = []
        self.morale = 0
        self.ignore_negative_morale = False
        self.situational_bonuses = []
        self.reactions = 1
        self.reactions_invested = 0
        # T-STANCE (v18): имя активной стойки (feats[] с is_stance) или None
        self.active_stance = None
        # T-LOG (v18): журнал трат (append-only, max 20)
        self.action_log = []

        self.proficiencies = {"armor": "None", "shields": "None",
                               "weapons": []}
        self.armor_invested = 0
        self.shield_invested = 0

        self.training = {"available": 1000, "spent": 0,
                          "purchases": []}
        self.skills = []
        self.feats = []
        self.quirks = []
        self.attacks = []
        self.class_resources = []
        self.spell_slots = {}
        self.spell_slots_enabled = False
        self.base = {"slots_max": 5, "contents": []}
        self.base_invested = 0
        self.comfort = {"current": 0, "max": 10}
        self.attention = {"current": 0, "max": 1}
        self.languages = []
        self.spells = []
        self.seeds = []
        self.templates = []
        self.wiki_links = []
        self.drives = {k: 0 for k, _ in DRIVE_KEYS}
        self.drive_principles = []
        self.courts = []
        self.court_quests = []
        self.lenses = []
        self.settings = {
            "show_mana": False, "show_class_points": False,
            "show_spell_slots": False, "show_spell_list": False,
            "hide_portrait": False, "show_rest_short": True,
            "show_rest_long": True, "show_bp_chip": True,
            "show_attention_chip": False, "show_comfort_chip": True,
            "show_time_chip": False, "ui_layout": [],
            "hide_hints": False,
            "hp_regen_per_tick": 0,
            # T-ALPHA (v18): 10..90
            "alpha_menu": 90,
            "alpha_center": 90,
            "alpha_chips": 90,
            "alpha_log": 90,
            "alpha_chip_buttons": 90,
            # T-STANCE (v18)
            "stance_chips": [],
            "catalogs_enabled": [],
            "catalogs_mode": "whitelist",
            "window_open_mode": "menu",
            "pin_editor_to_menu": True,
            "close_prev_window": False,
            "hotkeys": {
                "damage": "u", "heal": "h",
                "restore_balance": "b", "pain_up": "p",
                "pain_down": "P", "morale_up": "m",
                "morale_down": "M", "comfort_spend": "c",
                "temp_hp": "t",
            },
        }
        self.notes = ""
        self.recompute_derived()

    @property
    def level(self):
        return self.char_class.get("level", 1)

    def effective_ability(self, ab):
        base = self.abilities.get(ab, 10)
        dmg = self.ability_damage.get(ab, 0)
        return max(0, base - dmg)

    def ability_modifier(self, ab):
        total = (self.effective_ability(ab)
                 + self.situational_bonus(ab))
        return (total - 10) // 2

    def con_mod(self):
        return self.ability_modifier("con")

    def cha_mod(self):
        return self.ability_modifier("cha")

    def hp_rolls_total(self):
        return sum(self.char_class.get("hp_rolls", []))

    def hp_die_total(self):
        return self.char_class.get("hp_die", 8) * self.level

    def hp_max_cap(self):
        return (self.hp_die_total() + self.con_mod() * self.level
                + self.hp_bonus)

    def hp_max_from_rolls(self):
        return (self.hp_rolls_total() + self.con_mod() * self.level
                + self.hp_bonus)

    def hp_max_actual(self):
        base = self.hp_max_from_rolls() + self.combat["hp_bought"]
        return max(1, base + self.situational_bonus("max_hp"))

    def hp_bought_available(self):
        return max(0, self.hp_max_cap() - self.hp_max_actual())

    def spirit_max(self):
        base = 5 + 5 * self.cha_mod() + self.spirit_bonus
        return max(0, base + self.situational_bonus("max_spirit"))

    def armor_parrying(self):
        return ARMOR_PARRYING.get(self.proficiencies["armor"], 0)

    def shield_parrying(self):
        return SHIELD_PARRYING.get(self.proficiencies["shields"], 0)

    def parrying_bonus_from_level(self):
        return max(0, (self.level - 1) // 2)

    def total_parrying(self):
        base = (self.armor_parrying() + self.shield_parrying()
                + self.parrying_bonus_from_level())
        for it in self.items.values():
            if it["location"] != "equipped":
                continue
            if it.get("slot") not in ("weapon_main", "weapon_off"):
                continue
            w_name = ((it.get("weapon_group") or "").strip()
                      or it.get("name", ""))
            w = self.weapon_by_name(w_name)
            if w:
                base += self.weapon_parry_bonus(w)
        return base

    def shield_part_for_balance(self):
        if not self.equipment.get("add_shield_ac_to_balance", True):
            return 0
        if self.proficiencies["shields"] in ("Heavy", "Tower"):
            return self.shield_ac_from_equipped()
        return 0

    def bab_base(self):
        lvl = self.level
        t = self.char_class.get("bab_type", "good")
        if t == "medium":
            return (3 * lvl) // 4
        if t == "poor":
            return lvl // 2
        return lvl

    def add_item(self, **kwargs):
        item = _make_item(**kwargs)
        while item["id"] in self.items:
            item["id"] = str(uuid.uuid4())
        self.items[item["id"]] = item
        self._sync_item_bonuses()
        return item

    def remove_item(self, item_id):
        if item_id in self.items:
            self._sync_item_bonuses()
            return self.items.pop(item_id)
        return None

    def get_item(self, item_id):
        return self.items.get(item_id)

    def items_by_location(self, location):
        lst = [it for it in self.items.values()
               if it["location"] == location]
        lst.sort(key=lambda x: (x.get("order", 0),
                                  x.get("name", "")))
        return lst

    def equipped_in_slot(self, slot):
        for item in self.items.values():
            if (item["location"] == "equipped"
                    and item.get("slot") == slot):
                return item
        return None

    def _default_slot(self, item):
        cat = item.get("category", "misc")
        slots = CATEGORY_TO_SLOTS.get(cat, [])
        for s in slots:
            if self.equipped_in_slot(s) is None:
                return s
        return slots[0] if slots else None

    def move_item(self, item_id, to_location, to_slot=None):
        item = self.items.get(item_id)
        if not item:
            raise ValueError("Предмет не найден")
        if to_location not in LOCATIONS:
            raise ValueError(f"Неизвестная локация: {to_location}")
        if to_location == "equipped":
            if to_slot is None:
                to_slot = self._default_slot(item)
            if to_slot not in EQUIP_SLOTS:
                raise ValueError(f"Неизвестный слот: {to_slot}")
            occupied = self.equipped_in_slot(to_slot)
            if occupied and occupied["id"] != item_id:
                occupied["location"] = "bag"
                occupied["slot"] = None
            item["slot"] = to_slot
        else:
            item["slot"] = None
        item["location"] = to_location
        self._sync_item_bonuses()

    def equip_item(self, item_id, slot=None):
        self.move_item(item_id, "equipped", slot)

    def unequip_item(self, item_id):
        self.move_item(item_id, "bag")

    # ============ АТАКИ ИЗ ПРЕДМЕТОВ ============

    def _item_bonus(self, item_id, target):
        item = self.items.get(item_id)
        if not item:
            return 0
        total = 0
        if target == "attack":
            total += item.get("attack_bonus", 0)
        elif target == "damage":
            total += item.get("damage_bonus", 0)
        for e in item.get("enchants", []):
            if e.get("target") == target:
                total += e.get("value", 0)
        return total

    def _proficiency_for_item(self, item):
        """Ищет группу владения для предмета по weapon_group или name."""
        if not item:
            return None
        cand = (item.get("weapon_group") or "").strip()
        if cand:
            w = self.weapon_by_name(cand)
            if w:
                return cand
        name = (item.get("name") or "").strip()
        if name and self.weapon_by_name(name):
            return name
        return None

    def attack_from_item(self, item_id, name=None, stat="str",
                         use_bab=True, proficiency=None):
        """Создаёт атаку из надетого оружия.
        ranged → hit=DEX, dmg без мода стата.
        thrown → hit=DEX, dmg с модом STR.
        finesse → hit=DEX, dmg=STR.
        Обычное → hit=stat, dmg=stat."""
        item = self.items.get(item_id)
        if not item:
            raise ValueError("Предмет не найден")
        if item.get("category") != "weapon":
            raise ValueError("Предмет не оружие")
        if any(a.get("from_item") == item_id
                for a in self.attacks):
            raise ValueError("Атака из этого оружия уже есть")

        finesse = bool(item.get("finesse"))
        two_handed = bool(item.get("two_handed"))
        ranged = bool(item.get("ranged"))
        thrown = bool(item.get("thrown"))

        # Попадание
        if ranged or thrown or finesse:
            hit_stat = "dex"
        else:
            hit_stat = stat or "str"

        # Урон
        if finesse or ranged or thrown:
            dmg_stat = "str"
        else:
            dmg_stat = stat or "str"

        # Множитель
        if two_handed:
            dmg_mult = 1.5
        elif item.get("slot") == "weapon_off":
            dmg_mult = 0.5
        else:
            dmg_mult = 1.0

        # ranged не добавляет мод стата к урону (только кубик + бонусы)
        damage_stat_auto = not ranged

        atk = {
            "name": name or item.get("name", "Оружие"),
            "use_bab": use_bab,
            "stat": hit_stat,
            "damage_stat": dmg_stat,
            "damage_mult": dmg_mult,
            "damage_stat_auto": damage_stat_auto,
            "finesse": finesse,
            "two_handed": two_handed,
            "ranged": ranged,
            "thrown": thrown,
            "extra_bonus": 0,
            "manual_bonus": 0,
            "damage_dice": item.get("damage", ""),
            "crit_threshold": item.get("crit_threshold", 20),
            "crit_mult": item.get("crit_mult", 2),
            "lucky_threshold": item.get("lucky_threshold", 20),
            "desc": "",
            "source": item.get("source", "training"),
            "is_maneuver": False,
            "from_item": item_id,
            "proficiency": "",
            "master_ability": False,
            "master_ability_id": "",
            "show_on_panel": False,
            "uses": False,
            "uses_max": 0,
            "uses_current": 0,
            "tick_on_initiative": False,
            "tick_mode": "none",
            "cooldown_rounds": 0,
            "cooldown_current": 0,
            "order": len(self.attacks),
        }
        if proficiency is None:
            proficiency = self._proficiency_for_item(item)
        if proficiency:
            atk["proficiency"] = proficiency
        self.attacks.append(atk)
        return atk

    def attack_damage_bonus(self, a):
        total = 0
        if a.get("damage_stat_auto", True):
            ds = a.get("damage_stat") or a.get("stat") or "str"
            dm = float(a.get("damage_mult", 1.0))
            mod = self.ability_modifier(ds)
            total += int(math.floor(mod * dm))
        iid = a.get("from_item")
        if iid:
            total += self._item_bonus(iid, "damage")
        total += (self.pain_penalty() + self.morale_bonus()
                  + self.situational_bonus("damage"))
        w = self.weapon_by_name(a.get("proficiency"))
        if w:
            total += self.weapon_damage_bonus(w)
        return total

    def attack_crit(self, a):
        ct = a.get("crit_threshold", 20)
        cm = a.get("crit_mult", 2)
        iid = a.get("from_item")
        if iid:
            it = self.items.get(iid)
            if it:
                ct = it.get("crit_threshold", ct)
                cm = it.get("crit_mult", cm)
        w = self.weapon_by_name(a.get("proficiency"))
        if w:
            ct = max(2, ct - self.weapon_crit_reduction(w))
        return ct, cm

    def attack_lucky(self, a):
        """Порог счастливой атаки ('20+x', где x — сумма бонусов).
        Возвращает (порог, разбивка_по_источникам).
        Порог уменьшается бонусами, но не ниже 2."""
        base = int(a.get("lucky_threshold", 20) or 20)
        parts = []

        # 1) Бонусы владения expert_lucky_1 (по профишенси атаки)
        w = self.weapon_by_name(a.get("proficiency"))
        if w:
            wl = self.weapon_bonus_count(w, "expert_lucky_1")
            if wl:
                base -= wl
                parts.append(f"владение −{wl}")

        # 2) Ситуативные эффекты (включают пассивки предмета через
        # _sync_item_bonuses, зачарования и абилки классов)
        for b in self.situational_bonuses:
            for e in b.get("effects", []):
                if e.get("target") == "lucky":
                    v = self._eval_effect_value(e.get("value", 0))
                    if v:
                        base -= v
                        parts.append(f"{b.get('name', '?')} −{v}")

        base = max(2, base)
        return base, parts

    def attack_range(self, a):
        """Диапазон атаки в фт (0 если не ranged/thrown)."""
        iid = a.get("from_item")
        base = 0
        if iid:
            it = self.items.get(iid)
            if it:
                base = int(it.get("range_ft", 0) or 0)
        if not base:
            return 0
        w = self.weapon_by_name(a.get("proficiency"))
        if w:
            base += self.weapon_range_bonus(w)
        return base

    # ============ БОНУСЫ ВЛАДЕНИЯ ОРУЖИЕМ ============

    def weapon_by_name(self, name):
        if not name:
            return None
        for w in self.proficiencies.get("weapons", []):
            if w.get("name") == name:
                return w
        return None

    def weapon_bonuses_by_slot(self, w):
        result = {}
        if not w:
            return result
        for entry in w.get("bonuses", []):
            slot = entry.get("slot")
            bid = entry.get("id")
            if bid in WEAPON_BONUS_CATALOG:
                result[slot] = bid
        return result

    def weapon_bonus_count(self, w, bonus_id):
        if not w:
            return 0
        return sum(1 for e in w.get("bonuses", [])
                   if e.get("id") == bonus_id)

    def weapon_attack_bonus(self, w):
        return self.weapon_bonus_count(w, "spec_attack_1")

    def weapon_damage_bonus(self, w):
        return 3 * self.weapon_bonus_count(w, "expert_damage_3")

    def weapon_crit_reduction(self, w):
        return self.weapon_bonus_count(w, "spec_crit_range")

    def weapon_parry_bonus(self, w):
        return self.weapon_bonus_count(w, "spec_parry_1")

    def weapon_hp_bonus(self, w):
        return self.weapon_bonus_count(w, "expert_hp_1")

    def weapon_hardness_multiplier(self, w):
        if not w:
            return 1.0
        spec = self.weapon_bonus_count(w, "spec_hardness_30")
        exp = self.weapon_bonus_count(w, "expert_hardness_70")
        return 1.0 + 0.3 * spec + 0.7 * exp

    # ===== РЕАЛЬНЫЕ HP/ПРОЧНОСТЬ ПРЕДМЕТА (база + бонусы владения) =====

    def _item_prof_weapon(self, item):
        """Ищет proficiency оружия для предмета по weapon_group или name."""
        if not item:
            return None
        w_name = ((item.get("weapon_group") or "").strip()
                  or item.get("name", ""))
        return self.weapon_by_name(w_name) if w_name else None

    def item_hp_actual(self, item):
        """Текущий HP предмета с бонусами владения (expert_hp_1)."""
        if not item:
            return 0
        base = int(item.get("hp", 0) or 0)
        if base <= 0:
            return 0
        w = self._item_prof_weapon(item)
        if not w:
            return base
        return base + self.weapon_hp_bonus(w)

    def item_max_hp_actual(self, item):
        """Максимум HP предмета с бонусами владения (expert_hp_1)."""
        if not item:
            return 0
        base = int(item.get("max_hp", 0) or 0)
        if base <= 0:
            return 0
        w = self._item_prof_weapon(item)
        if not w:
            return base
        return base + self.weapon_hp_bonus(w)

    def item_hardness_actual(self, item):
        """Прочность предмета с бонусами владения (spec+expert)."""
        if not item:
            return 0
        base = int(item.get("hardness", 0) or 0)
        if base <= 0:
            return 0
        w = self._item_prof_weapon(item)
        if not w:
            return base
        mult = self.weapon_hardness_multiplier(w)
        return int(round(base * mult))

    def item_hp_breakdown(self, item):
        """Список строк-пояснений по HP/прочности (для tooltip).
        Возвращает [] если бонусов нет."""
        if not item:
            return []
        w = self._item_prof_weapon(item)
        if not w:
            return []
        lines = []
        hp_bonus = self.weapon_hp_bonus(w)
        if hp_bonus:
            st = self.weapon_bonus_count(w, "expert_hp_1")
            lines.append(f"HP оружия +{hp_bonus} (Эксперт HP ×{st})")
        spec = self.weapon_bonus_count(w, "spec_hardness_30")
        exp = self.weapon_bonus_count(w, "expert_hardness_70")
        if spec or exp:
            mult = self.weapon_hardness_multiplier(w)
            parts = []
            if spec:
                parts.append(f"Спец +30% ×{spec}")
            if exp:
                parts.append(f"Эксперт +70% ×{exp}")
            lines.append(f"Прочность ×{mult:.2f} ({', '.join(parts)})")
        return lines

    def weapon_range_bonus(self, w):
        return 10 * self.weapon_bonus_count(w, "spec_range_10")

    def weapon_balance_restore_bonus(self, w):
        return self.weapon_bonus_count(w, "spec_balance_1")

    # ============ АКТИВАЦИЯ ПРЕДМЕТОВ ============

    def _sync_item_bonuses(self):
        self.situational_bonuses = [
            b for b in self.situational_bonuses
            if "from_item" not in b
        ]
        for item in self.items.values():
            if item["location"] != "equipped":
                continue
            for bon in item.get("passive_bonuses", []):
                self.situational_bonuses.append({
                    "name": item.get("name", "?"),
                    "desc": "",
                    "effects": [{
                        "target": bon.get("target", "all"),
                        "value": bon.get("value", 0),
                        "bonus_type": bon.get("bonus_type", "flat") or "flat",
                    }],
                    "duration_rounds": 0,
                    "duration_current": 0,
                    "charges_max": 0,
                    "charges_current": 0,
                    "tick_on_initiative": False,
                    "from_item": item["id"],
                })

    def activate_item(self, item_id):
        item = self.items.get(item_id)
        if not item:
            raise ValueError("Предмет не найден")
        if not item.get("activatable"):
            raise ValueError("Предмет не активируется")
        if item.get("activated"):
            raise ValueError("Уже активирован")
        cost = item.get("activation_cost_spirit", 0)
        if cost > 0:
            if self.spirit["current"] < cost:
                raise ValueError(
                    f"Не хватает духа: нужно {cost}, "
                    f"есть {self.spirit['current']}")
            self.spirit["current"] -= cost
        item["activated"] = True
        dur = item.get("activation_duration", 0)
        for bon in item.get("activation_effects", []):
            self.situational_bonuses.append({
                "name": f"{item.get('name','?')} ✨",
                "desc": "",
                "effects": [{
                    "target": bon.get("target", "all"),
                    "value": bon.get("value", 0),
                }],
                "duration_rounds": dur,
                "duration_current": dur,
                "charges_max": 0,
                "charges_current": 0,
                "tick_on_initiative": dur > 0,
                "from_item_activation": item["id"],
            })
        return cost

    def deactivate_item(self, item_id):
        item = self.items.get(item_id)
        if item:
            item["activated"] = False
        self.situational_bonuses = [
            b for b in self.situational_bonuses
            if b.get("from_item_activation") != item_id
        ]

    def activate_buff(self, idx):
        """T34: переактивация бафа за заряд.
        Сбрасывает duration_current на duration_rounds,
        тратит 1 заряд. Возвращает True, если удалось."""
        if not (0 <= idx < len(self.situational_bonuses)):
            return False
        b = self.situational_bonuses[idx]
        if int(b.get("charges_max", 0) or 0) <= 0:
            return False
        cur = int(b.get("charges_current", 0) or 0)
        if cur <= 0:
            return False
        b["charges_current"] = cur - 1
        rounds = int(b.get("duration_rounds", 0) or 0)
        if rounds > 0:
            b["duration_current"] = rounds
        # T42: применить разовые эффекты.
        on_act = b.get("on_activate_effects") or []
        if on_act:
            self._apply_effect_values(on_act)
        return True

    def trigger_buff(self, idx):
        """T42: активировать баф/дебаф.
        - если есть заряды: списать 1 (activate_buff).
        - если зарядов нет: просто применить on_activate_effects.
        Сбрасывает duration_current на duration_rounds (если rounds>0).
        Возвращает True, если что-то произошло."""
        if not (0 <= idx < len(self.situational_bonuses)):
            return False
        b = self.situational_bonuses[idx]
        cm = int(b.get("charges_max", 0) or 0)
        if cm > 0:
            return self.activate_buff(idx)
        # без зарядов
        rounds = int(b.get("duration_rounds", 0) or 0)
        if rounds > 0:
            b["duration_current"] = rounds
        on_act = b.get("on_activate_effects") or []
        if on_act:
            self._apply_effect_values(on_act)
        return True

    def activate_ability_buff(self, source, idx):
        """T47/T48: активировать класс-баф (is_buff) как ситуативный.
        source: 'class' | 'race'. idx: индекс в abilities.
        Тратит 1 заряд (если есть), сбрасывает duration,
        применяет on_activate_effects, добавляет в situational_bonuses."""
        if source == "class":
            abils = self.char_class.get("abilities", [])
        elif source == "race":
            abils = self.race.get("abilities", [])
        else:
            return False
        if not (0 <= idx < len(abils)):
            return False
        a = abils[idx]
        if not a.get("is_buff"):
            return False
        # Трата заряда
        cm = int(a.get("charges_max", 0) or 0)
        cc = int(a.get("charges_current", 0) or 0)
        if cm > 0:
            if cc <= 0:
                return False
            a["charges_current"] = cc - 1
        # Новая запись в situational_bonuses
        rounds = int(a.get("duration_rounds", 0) or 0)
        new_b = {
            "name": a.get("name", "?"),
            "desc": a.get("desc", ""),
            "duration_rounds": rounds,
            "duration_current": rounds,
            "charges_max": 0,
            "charges_current": 0,
            "tick_on_initiative": rounds > 0,
            "blocks": [],
            "effects": [dict(e) for e in a.get("effects", [])],
            "on_activate_effects": [
                dict(e) for e in a.get("on_activate_effects", [])],
            "from_ability": source,
            "from_ability_idx": idx,
        }
        self.situational_bonuses.append(new_b)
        # Разовые эффекты
        on_act = a.get("on_activate_effects") or []
        if on_act:
            self._apply_effect_values(on_act)
        return True

    def activate_feat_buff(self, feat_idx):
        """T-EFFECTS-UI: активировать черту/стойку как ситуативный баф.
        Копирует feats[feat_idx] → situational_bonuses.
        Тратит 1 заряд (если charges_max > 0), сбрасывает duration,
        применяет on_activate_effects.
        Возвращает True, если удалось."""
        if not (0 <= feat_idx < len(self.feats)):
            return False
        f = self.feats[feat_idx]
        if not isinstance(f, dict):
            return False
        if not f.get("is_buff"):
            return False
        # Трата заряда
        cm = int(f.get("charges_max", 0) or 0)
        cc = int(f.get("charges_current", 0) or 0)
        if cm > 0:
            if cc <= 0:
                return False
            f["charges_current"] = cc - 1
        # Новая запись в situational_bonuses
        rounds = int(f.get("duration_rounds", 0) or 0)
        new_b = {
            "name": f.get("name", "?"),
            "desc": f.get("desc", ""),
            "duration_rounds": rounds,
            "duration_current": rounds,
            "charges_max": 0,
            "charges_current": 0,
            "tick_on_initiative": rounds > 0,
            "permanent": bool(f.get("permanent", False)),
            "keep_at_zero": bool(f.get("keep_at_zero", False)),
            "allow_toggle": bool(f.get("allow_toggle", True)),
            "enabled": True,
            "blocks": list(f.get("blocks", [])),
            "effects": [dict(e) for e in f.get("effects", [])],
            "on_activate_effects": [
                dict(e) for e in f.get("on_activate_effects", [])],
            "from_feat": feat_idx,
        }
        self.situational_bonuses.append(new_b)
        # Разовые эффекты
        on_act = f.get("on_activate_effects") or []
        if on_act:
            self._apply_effect_values(on_act)
        return True

    def activate_injury_buff(self, injury_idx):
        """T-EFFECTS-UI: активировать травму как ситуативный баф.
        Копирует injuries[injury_idx] → situational_bonuses.
        Аналогично activate_feat_buff, но для травм.
        Возвращает True, если удалось."""
        if not (0 <= injury_idx < len(self.injuries)):
            return False
        inj = self.injuries[injury_idx]
        if not isinstance(inj, dict):
            return False
        if not inj.get("is_buff"):
            return False
        # Трата заряда
        cm = int(inj.get("charges_max", 0) or 0)
        cc = int(inj.get("charges_current", 0) or 0)
        if cm > 0:
            if cc <= 0:
                return False
            inj["charges_current"] = cc - 1
        # Новая запись в situational_bonuses
        rounds = int(inj.get("duration_rounds", 0) or 0)
        new_b = {
            "name": inj.get("name", "?"),
            "desc": inj.get("desc", ""),
            "duration_rounds": rounds,
            "duration_current": rounds,
            "charges_max": 0,
            "charges_current": 0,
            "tick_on_initiative": rounds > 0,
            "permanent": bool(inj.get("permanent", False)),
            "keep_at_zero": bool(inj.get("keep_at_zero", False)),
            "allow_toggle": bool(inj.get("allow_toggle", True)),
            "enabled": True,
            "blocks": list(inj.get("blocks", [])),
            "effects": [dict(e) for e in inj.get("effects", [])],
            "on_activate_effects": [
                dict(e) for e in inj.get("on_activate_effects", [])],
            "from_injury": injury_idx,
        }
        self.situational_bonuses.append(new_b)
        # Разовые эффекты
        on_act = inj.get("on_activate_effects") or []
        if on_act:
            self._apply_effect_values(on_act)
        return True


    # ============ ВЕС / НАГРУЗКА ============

    def _item_weight_L(self, item):
        wt = item.get("weight_type", "mass")
        w = float(item.get("weight", 0) or 0)
        qty = int(item.get("qty", 1) or 1)
        if wt == "-":
            return 0
        if wt == "L":
            return w * qty
        if wt == "mass":
            return w * 10 * qty
        return 0

    def total_weight_L(self):
        total = 0
        for item in self.items.values():
            loc = item["location"]
            if loc == "base":
                continue
            if loc == "bag" and self.bag_dropped:
                continue
            total += self._item_weight_L(item)
        return total

    def unload_capacity_L(self):
        total = 10
        for item in self._equipped_items():
            if item.get("category") == "unload":
                total += int(item.get("unload_bonus", 0) or 0)
        return total

    def max_weight_light(self):
        return (5 + self.ability_modifier("str")) * 10 + 9

    def max_weight_loaded(self):
        return (10 + self.ability_modifier("str")) * 10 + 9

    def weight_status(self):
        w = self.total_weight_L()
        if w <= self.max_weight_light():
            return "light"
        if w <= self.max_weight_loaded():
            return "loaded"
        return "over"

    def total_weight_display(self):
        w = self.total_weight_L()
        bulks = int(w // 10)
        rest_L = round(w - bulks * 10, 1)
        if rest_L == int(rest_L):
            rest_L = int(rest_L)
        return f"{bulks} балк {rest_L}L"

    # ============ AC ИЗ ПРЕДМЕТОВ ============

    def _ac_items_max(self, ac_type):
        mx = 0
        for item in self._equipped_items():
            if item.get("ac_type") == ac_type:
                val = item.get("ac_bonus", 0) or 0
                mx = max(mx, val)
        return mx

    def _ac_items_sum(self, ac_type):
        total = 0
        for item in self._equipped_items():
            if item.get("ac_type") == ac_type:
                total += item.get("ac_bonus", 0) or 0
        return total

    def _ac_manual(self, ac_type):
        if ac_type == "armor":
            return self.equipment.get("armor_ac", 0) or 0
        if ac_type == "shield":
            return self.equipment.get("shield_ac", 0) or 0
        if ac_type == "natural":
            return self.natural_armor or 0
        if ac_type == "deflection":
            return self.ac_bonus or 0
        return 0

    def _ac_type_max(self, ac_type):
        return max(self._ac_items_max(ac_type),
                    self._ac_manual(ac_type))

    # T-BONUS-TYPES-2 (v18.4): ac_bonus_total удалён.
    # Используйте _ac_type_max() (предметы) + _ac_situational_by_type() (эффекты).

    def armor_bonus(self):
        return self._ac_type_max("armor")

    def shield_bonus(self):
        return self._ac_type_max("shield")

    def natural_bonus(self):
        return self._ac_type_max("natural")

    def deflection_bonus(self):
        return self._ac_type_max("deflection")

    def armor_ac_from_equipped(self):
        return self.armor_bonus()

    def shield_ac_from_equipped(self):
        return self.shield_bonus()

    def ac_max_dex_cap(self):
        caps = []
        for item in self.items.values():
            if item["location"] != "equipped":
                continue
            cap = item.get("ac_max_dex")
            if cap is not None:
                caps.append(cap)
        if not caps:
            return None
        return min(caps)

    def dex_bonus_for_ac(self):
        """DEX-бонус уклонения. dex_mod + dodge ≤ ac_max_dex (сумма)."""
        dex = self.ability_modifier("dex")
        # dodge-бонусы (складываются с dex)
        dodge = 0
        for b in self.situational_bonuses:
            for e in b.get("effects", []):
                if e.get("target") != "ac":
                    continue
                if (e.get("bonus_type") or "flat") == "dodge":
                    dodge += self._eval_effect_value(e.get("value", 0))
        for e in self.stance_effects():
            if e.get("target") != "ac":
                continue
            if (e.get("bonus_type") or "flat") == "dodge":
                dodge += self._eval_effect_value(e.get("value", 0))
        for f in self.feats:
            for e in f.get("effects", []):
                if e.get("target") != "ac":
                    continue
                if (e.get("bonus_type") or "flat") == "dodge":
                    dodge += self._eval_effect_value(e.get("value", 0))
        total = dex + dodge
        cap = self.ac_max_dex_cap()
        if cap is not None:
            total = min(total, cap)
        if self.weight_status() in ("loaded", "over"):
            total = min(total, 2)
        return total
    
    # ============ ВЛАДЕНИЕ / ШТРАФЫ ============

    def _is_unproficient(self, item):
        at = item.get("armor_type")
        if not at or at == "None":
            return False
        cat = item.get("category")
        if cat == "armor":
            my = self.proficiencies.get("armor", "None")
        elif cat == "shield":
            my = self.proficiencies.get("shields", "None")
        else:
            return False
        return (ARMOR_TYPE_ORDER.get(my, 0)
                < ARMOR_TYPE_ORDER.get(at, 0))

    def _equipped_items(self):
        return [it for it in self.items.values()
                if it["location"] == "equipped"]

    def unprof_attack_penalty(self):
        total = 0
        for item in self._equipped_items():
            if self._is_unproficient(item):
                total += item.get("unprof_penalty", -2)
        return total

    def weapon_unprof_penalty_for_attack(self, a):
        """-4 если владение оружием < required_level предмета."""
        iid = a.get("from_item")
        if not iid:
            return 0
        item = self.items.get(iid)
        if not item:
            return 0
        req = int(item.get("required_level", 0) or 0)
        if req <= 0:
            return 0
        prof_name = a.get("proficiency") or self._proficiency_for_item(item)
        w = self.weapon_by_name(prof_name) if prof_name else None
        lvl = int((w or {}).get("level", 0) or 0)
        if lvl < req:
            return -4
        return 0

    def unprof_skill_penalty(self, stat):
        if stat not in ("str", "dex"):
            return 0
        total = 0
        for item in self._equipped_items():
            if self._is_unproficient(item):
                total += item.get("unprof_penalty", -2)
        return total

    def equipped_skill_penalty(self, stat):
        if stat not in ("str", "dex"):
            return 0
        total = 0
        for item in self._equipped_items():
            total -= abs(item.get("skill_penalty", 0) or 0)
        if self.weight_status() in ("loaded", "over"):
            total -= 2
        return total

    def equipped_speed_penalty(self):
        total = 0
        for item in self._equipped_items():
            total += item.get("speed_penalty", 0)
        return total

    # ---------- РАЗМЕР / CMB / CMD ----------

    def size_mod_ac(self):
        return SIZE_AC.get(self.combat.get("size", "Medium"), 0)

    def size_mod_cmb(self):
        return SIZE_CMB.get(self.combat.get("size", "Medium"), 0)

    def cmb_mods_sum(self):
        return sum(m.get("value", 0) for m in self.cmb_mods)

    def cmd_mods_sum(self):
        return sum(m.get("value", 0) for m in self.cmd_mods)

    def cmb_total(self):
        return (self.bab_base()
                + self.ability_modifier("str")
                + self.size_mod_cmb()
                + self.cmb_mods_sum()
                + self.pain_penalty()
                + self.morale_bonus()
                + self.situational_bonus("cmb"))

    def cmd_total(self):
        return (10
                + self.bab_base()
                + self.ability_modifier("str")
                + self.ability_modifier("dex")
                + self.size_mod_cmb()
                + self.cmd_mods_sum()
                + self.pain_penalty()
                + self.morale_bonus()
                + self.situational_bonus("cmd"))

    def initiative_total(self):
        """Инициатива = ЛОВ + ситуативка (вкл. черты) + боль/мораль + ручной бонус."""
        return self.initiative_breakdown()["total"]

    def initiative_breakdown(self):
        """Возвращает словарь с разбивкой инициативы (для чарника)."""
        dex = self.ability_modifier("dex")
        pain = self.pain_penalty()
        morale = self.morale_bonus()
        manual = int(self.combat.get("initiative", 0) or 0)
        
        parts = [f"ЛОВ {dex:+d}"]
        total = dex + pain + morale + manual
        
        if pain: parts.append(f"боль {pain:+d}")
        if morale: parts.append(f"мораль {morale:+d}")
        if manual: parts.append(f"ручной {manual:+d}")

        # 1. Бафы (Ситуативно)
        for b in self.situational_bonuses:
            for e in b.get("effects", []):
                if e.get("target") == "initiative":
                    v = self._eval_effect_value(e.get("value", 0))
                    if v:
                        nm = b.get("name", "Баф")
                        parts.append(f"{nm} {v:+d}")
                        total += v

        # 2. Стойки
        for e in self.stance_effects():
            if e.get("target") == "initiative":
                v = self._eval_effect_value(e.get("value", 0))
                if v:
                    st_name = self.active_stance or "Стойка"
                    for f in self.feats:
                        if f.get("is_stance") and f.get("name") == st_name:
                            st_name = f.get("display_name") or st_name
                            break
                    parts.append(f"{st_name} {v:+d}")
                    total += v

        # 3. Черты (постоянные)
        for f in self.feats:
            if f.get("is_stance"): continue
            for e in f.get("effects", []):
                if e.get("target") == "initiative":
                    v = self._eval_effect_value(e.get("value", 0))
                    if v:
                        nm = f.get("display_name") or f.get("name", "Черта")
                        parts.append(f"{nm} {v:+d}")
                        total += v

        return {"total": total, "parts": parts}

    # ===== T-STANCE (v18) =====
    def feats_for_ui(self):
        """Черты для обычного редактора (без стоек)."""
        return [f for f in self.feats if not f.get("is_stance")]

    def stances(self):
        """Все стойки-черты (feats с is_stance=true)."""
        return [f for f in self.feats if f.get("is_stance")]

    def stance_effects(self, name=None):
        """Эффекты активной (или указанной) стойки. None/'' → []."""
        target = name if name is not None else self.active_stance
        if not target:
            return []
        for f in self.feats:
            if f.get("is_stance") and f.get("name") == target:
                return f.get("stance_effects", []) or []
        return []

    def stance_blocks(self, name=None):
        """Блокировки активной (или указанной) стойки."""
        target = name if name is not None else self.active_stance
        if not target:
            return []
        for f in self.feats:
            if f.get("is_stance") and f.get("name") == target:
                return f.get("stance_blocks", []) or []
        return []

    def set_active_stance(self, name):
        """name=None → 'Обычная'. True, если имя найдено (или None)."""
        if name is None or name == "":
            self.active_stance = None
            return True
        for f in self.feats:
            if f.get("is_stance") and f.get("name") == name:
                self.active_stance = name
                return True
        return False

    # ===== T-LOG (v18) =====
    def log_action(self, kind, summary, before=None, after=None, rev=True):
        """Добавить запись в action_log (append-only, max 20)."""
        import datetime
        self.action_log.append({
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            "kind": kind,
            "summary": summary,
            "before": before or {},
            "after": after or {},
            "rev": bool(rev),
        })
        if len(self.action_log) > 20:
            self.action_log = self.action_log[-20:]

    def revert_action(self, idx):
        """Откатить запись action_log[idx] (применить before обратно)."""
        if not (0 <= idx < len(self.action_log)):
            return False
        entry = self.action_log[idx]
        if not entry.get("rev", True):
            return False
        before = entry.get("before") or {}
        for key, val in before.items():
            if key == "injury_points":
                self.injury_points = val
            elif key == "overload":
                self.overload = val
            elif key == "overload_enabled":
                self.overload_enabled = bool(val)
            elif key == "mana_current":
                self.mana["current"] = val
            elif key == "balance_current":
                self.balance["current"] = val
            elif key == "hp_current":
                self.combat["hp_current"] = val
            elif key == "hp_temp":
                self.combat["hp_temp"] = val
            elif key == "spirit_current":
                self.spirit["current"] = val
            elif key.startswith("slot_"):
                c = key.split("_", 1)[1]
                if c in self.spell_slots:
                    self.spell_slots[c]["current"] = val
            elif key.startswith("ability_uses_"):
                i = int(key.rsplit("_", 1)[-1])
                abils = self.char_class.get("abilities", [])
                if 0 <= i < len(abils):
                    abils[i]["uses_current"] = val
            elif key.startswith("race_uses_"):
                i = int(key.rsplit("_", 1)[-1])
                abils = self.race.get("abilities", [])
                if 0 <= i < len(abils):
                    abils[i]["uses_current"] = val
            elif key == "training_available":
                self.training["available"] = val
            elif key == "training_spent":
                self.training["spent"] = val
        self.action_log.pop(idx)
        return True

    def lens_status(self, lens):
        """'closed' | 'failed' | ''."""
        cur = int(lens.get("current", 0) or 0)
        mx = int(lens.get("max", 0) or 0)
        if mx > 0 and cur >= mx:
            return "closed"
        if mx > 0 and cur <= 0:
            return "failed"
        return ""

    # ---------- 4 ТИПА AC ----------

    def _ac_situational_by_type(self, for_touch=False, for_flat=False,
                                 for_parry=False):
        """Собирает ВСЕ бонусы AC (из бафов, стоек, черт) через барабан.

        T-BONUS-TYPES-2 (v18.4):
          - flat/'' → сумма;
          - dodge → сумма;
          - остальные → «побеждает больший по модулю», равны → 0.
          - allowed-фильтр: touch / flat / parry.
        """
        bonuses = []

        def collect(effects):
            if self.is_target_denied("ac"):
                return
            for e in effects:
                if not isinstance(e, dict):
                    continue
                if e.get("target") != "ac":
                    continue
                btype = e.get("bonus_type", "flat") or "flat"
                if btype == "dodge":
                    # dodge уже учтён в dex_bonus_for_ac (с cap ac_max_dex)
                    continue
                v = self._eval_effect_value(e.get("value", 0))
                bonuses.append({
                    "value": v,
                    "type": btype,
                })
                
        # 1. Ситуативные бафы
        for b in self.situational_bonuses:
            collect(b.get("effects", []))
        # 2. Стойки
        collect(self.stance_effects())
        # 3. Постоянные черты
        for f in self.feats:
            collect(f.get("effects", []))

        denied = set()
        for t in list(AC_FULL_TYPES):
            if self.is_bonus_denied(t):
                denied.add(t)
        if for_touch:
            allowed = _AC_TOUCH_TYPES_SET
        elif for_flat:
            allowed = AC_FLAT_TYPES
        elif for_parry:
            allowed = AC_PARRY_TYPES
        else:
            allowed = AC_FULL_TYPES
        return apply_bonus_type(bonuses, allowed=allowed, denied=denied)
    
    def ac_full(self):
        dex = self.dex_bonus_for_ac()
        return (10
                + dex
                + self.size_mod_ac()
                + self._ac_type_max("armor")
                + self._ac_type_max("shield")
                + self._ac_type_max("natural")
                + self.ac_misc
                + self._ac_situational_by_type())

    def ac_touch(self):
        dex = self.dex_bonus_for_ac()
        return (10
                + dex
                + self.size_mod_ac()
                + self.ac_misc
                + self._ac_situational_by_type(for_touch=True))

    def ac_flat(self):
        return (10
                + self.size_mod_ac()
                + self._ac_type_max("armor")
                + self._ac_type_max("shield")
                + self._ac_type_max("natural")
                + self.ac_misc
                + self._ac_situational_by_type(for_flat=True))

    def ac_parry(self):
        dex = self.dex_bonus_for_ac()
        return (10
                + self.total_parrying()
                + dex
                + self.size_mod_ac()
                + self._ac_type_max("shield")
                + self._ac_type_max("natural")
                + self.ac_misc
                + self._ac_situational_by_type(for_parry=True))

    def ac_total(self):
        return self.ac_full()

    # ---------- БОЛЬ / МОРАЛЬ / СИТУАТИВКА ----------

    def pain_from_hp(self):
        hp = self.combat["hp_current"]
        return 0 if hp >= 0 else (-hp) // PAIN_HP_STEP

    def pain_level(self):
        return (self.pain_from_hp() + self.pain_extra
                + self.pain_extra_temp)

    def pain_penalty(self):
        if self.ignore_pain:
            return 0
        return -self.pain_level()

    def add_pain(self, n):
        self.pain_extra = max(0, self.pain_extra + n)

    def add_temp_pain(self, n):
        self.pain_extra_temp = max(0, self.pain_extra_temp + n)

    def clear_temp_pain(self):
        self.pain_extra_temp = 0

    def is_dead(self):
        return self.pain_level() >= self.pain_max

    def morale_bonus(self):
        b = self.morale // 2
        if self.ignore_negative_morale and b < 0:
            return 0
        return b

    def situational_bonus(self, target, skill_name=None):
        total = 0
        denied = self.is_target_denied(target)
        for b in self.situational_bonuses:
            for e in b.get("effects", []):
                t = e.get("target", "")
                if t != target:
                    continue
                if denied:
                    continue
                # T40: значение может быть формулой ('2*lvl').
                v = self._eval_effect_value(e.get("value", 0))
                if t == "skill":
                    sname = (e.get("skill_name") or "").strip()
                    if sname:
                        if skill_name is None or sname != skill_name:
                            continue
                total += v
        # T-STANCE (v18): активная стойка — те же target, что у бафов.
        # permanent-эффект: применяется, пока active_stance указывает на неё.
        for e in self.stance_effects():
            if not isinstance(e, dict):
                continue
            t = e.get("target", "")
            if t != target:
                continue
            if denied:
                continue
            v = self._eval_effect_value(e.get("value", 0))
            if t == "skill":
                sname = (e.get("skill_name") or "").strip()
                if sname:
                    if skill_name is None or sname != skill_name:
                        continue
            total += v

        # T-FEAT-EFFECTS: постоянные эффекты из обычных черт (не стоек)
        for f in self.feats:
            if f.get("is_stance"):
                continue # у стоек своя логика через active_stance
            for e in f.get("effects", []):
                if not isinstance(e, dict):
                    continue
                t = e.get("target", "")
                if t != target:
                    continue
                if denied:
                    continue
                v = self._eval_effect_value(e.get("value", 0))
                if t == "skill":
                    sname = (e.get("skill_name") or "").strip()
                    if sname:
                        if skill_name is None or sname != skill_name:
                            continue
                total += v
        return total
    
    def speed_multiplier(self):
        mult = 1.0
        for b in self.situational_bonuses:
            for e in b.get("effects", []):
                if e.get("target") == "speed_mult":
                    # T40: value может быть формулой.
                    v = self._eval_effect_value(e.get("value", 100))
                    mult *= v / 100.0
        return mult

    def speed_total(self):
        """T-BONUS-TYPES-2: speed_mult [DEPRECATED], не применяется."""
        base = (self.race.get("speed", 30)
                + self.situational_bonus("speed"))
        penalty = self.equipped_speed_penalty()
        ws = self.weight_status()
        if ws in ("loaded", "over"):
            penalty += 10
        return max(0, int(base - penalty))

    def _eval_effect_value(self, value, dice_rolls=None):
        """T40/T40b: вычислить value эффекта.
        - число → int.
        - строка → безопасный парсер выражений (ast, без eval):
          числа, + - * /, скобки, lvl/level, X_mod, NdX, dX.
        Возвращает int. Не падает: при ошибке → 0."""
        import ast
        import random
        if isinstance(value, (int, float)):
            return int(value)
        if not isinstance(value, str):
            return 0
        s = value.strip().lower().replace(" ", "")
        if not s:
            return 0

        stat_map = {"str", "dex", "con", "int", "wis", "cha"}

        def _roll_die(die_str, n=1):
            try:
                sides = int(die_str[1:])
            except Exception:
                return 0
            if sides < 2:
                return 0
            total = 0
            for _ in range(max(0, int(n))):
                if dice_rolls is not None:
                    if die_str not in dice_rolls:
                        dice_rolls[die_str] = random.randint(1, sides)
                    total += dice_rolls[die_str]
                else:
                    total += random.randint(1, sides)
            return total

        # Быстрый путь: число, lvl, X_mod
        try:
            return int(s)
        except ValueError:
            pass
        if s in ("lvl", "level"):
            return int(self.level)
        if s in [f"{k}_mod" for k in stat_map]:
            return int(self.ability_modifier(s[:-4]))

        # Преобразуем токены NdX → число (броски), _mod → int
        def _pre(match):
            token = match.group(0)
            if token.endswith("_mod"):
                key = token[:-4]
                return str(int(self.ability_modifier(key)))
            m2 = re.fullmatch(r"(\d*)d(\d+)", token)
            if m2:
                n = int(m2.group(1) or 1)
                die = f"d{m2.group(2)}"
                return str(_roll_die(die, n))
            return token

        tokens_re = re.compile(r"(\d*)d(\d+)|(str|dex|con|int|wis|cha)_mod")
        prepared = tokens_re.sub(_pre, s)
        # Заменяем lvl/level на число уровня
        prepared = re.sub(r"\blvl\b|\blevel\b",
                          str(int(self.level)), prepared)

        # Парсим AST (безопасно, без eval)
        try:
            tree = ast.parse(prepared, mode="eval")
        except Exception:
            return 0

        def _eval_node(node):
            if isinstance(node, ast.Expression):
                return _eval_node(node.body)
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return int(node.value)
                return 0
            if isinstance(node, ast.Num):  # legacy
                return int(node.n)
            if isinstance(node, ast.UnaryOp):
                v = _eval_node(node.operand)
                if isinstance(node.op, ast.USub):
                    return -v
                if isinstance(node.op, ast.UAdd):
                    return v
                return 0
            if isinstance(node, ast.BinOp):
                l = _eval_node(node.left)
                r = _eval_node(node.right)
                if isinstance(node.op, ast.Add):
                    return l + r
                if isinstance(node.op, ast.Sub):
                    return l - r
                if isinstance(node.op, ast.Mult):
                    return l * r
                if isinstance(node.op, ast.Div):
                    return int(l / r) if r else 0
                if isinstance(node.op, ast.FloorDiv):
                    return l // r if r else 0
                return 0
            return 0

        try:
            return int(_eval_node(tree))
        except Exception:
            return 0

    def _apply_effect_values(self, effects, report=None, source_name=""):
        """T42+T44: применяет список эффектов 'restore_*' к персонажу.
        effects — список dict(target, value[, resource_name]).
        report — если list, туда пишем строки отчёта.
        Возвращает список строк-отчётов (для тика)."""
        out = []
        for e in effects or []:
            if not isinstance(e, dict):
                continue
            t = e.get("target", "")
            if t.startswith("restore_") and self.is_resource_denied(t):
                continue
            v_raw = e.get("value", 0)
            v = self._eval_effect_value(v_raw)
            if v == 0:
                continue
            if t == "restore_hp":
                before = self.combat["hp_current"]
                self.combat["hp_current"] = min(
                    self.hp_max_actual(), before + v)
                got = self.combat["hp_current"] - before
                if got:
                    out.append(f"HP +{got}")
            elif t == "restore_mana":
                if not self.mana.get("enabled"):
                    continue
                before = self.mana["current"]
                self.mana["current"] = min(
                    self.mana["max"], before + v)
                got = self.mana["current"] - before
                if got:
                    out.append(f"Мана +{got}")
            elif t == "restore_spirit":
                before = self.spirit["current"]
                self.spirit["current"] = min(
                    self.spirit["max"], before + v)
                got = self.spirit["current"] - before
                if got:
                    out.append(f"Дух +{got}")
            elif t == "restore_balance":
                before = self.balance["current"]
                self.balance["current"] = min(
                    self.balance["max"], before + v)
                got = self.balance["current"] - before
                if got:
                    out.append(f"Баланс +{got}")
            elif t == "restore_resource":
                rname = (e.get("resource_name") or "").strip()
                if not rname:
                    continue
                for r in self.class_resources:
                    if r.get("name") == rname:
                        before = r.get("current", 0)
                        mx = r.get("max", 0)
                        r["current"] = min(mx, before + v)
                        got = r["current"] - before
                        if got:
                            out.append(f"{rname} +{got}")
                        break
        if report is not None:
            report.extend(out)
        return out


    def tick_initiative(self, apply_balance=None):
        if apply_balance is None:
            apply_balance = getattr(self, "auto_balance_on_tick", True)
        report = []

        # 1) Бафы: длительность / заряды
        # Правила (см. CONTRACT §4, GLOSSARY §7):
        #  - permanent == True  → не тикает, не удаляется.
        #  - tick_on_initiative False → не тикает.
        #  - duration_rounds > 0: duration_current -= 1 (мин. 0).
        #  - duration_current == 0 и keep_at_zero == False
        #    и settings.buff_delete_on_zero → удалить на СЛЕД. тике
        #    (здесь: уже 0 → удаляем сразу при повторном тике).
        #  - duration_rounds == 0 и permanent == False:
        #    «без потолка» — тик всё равно идёт, но не удаляется
        #    автоматически (как если бы keep_at_zero == True).
        delete_on_zero = bool(
            self.settings.get("buff_delete_on_zero", False))
        new_list = []
        expired = []
        for b in self.situational_bonuses:
            if b.get("permanent", False):
                new_list.append(b)
                continue
            if not b.get("tick_on_initiative", False):
                new_list.append(b)
                continue
            rounds_max = int(b.get("duration_rounds", 0) or 0)
            cur = int(b.get("duration_current", 0) or 0)
            # «Без потолка» = rounds_max == 0 → не удаляем автоматически
            auto_delete_ok = (rounds_max > 0
                              and not b.get("keep_at_zero", False)
                              and delete_on_zero)
            if cur > 0:
                cur -= 1
                b["duration_current"] = cur
            # T34.1: тик зарядов (только если charges_tick_mode != none)
            ctm = b.get("charges_tick_mode", "none")
            if ctm == "decrement":
                cc = int(b.get("charges_current", 0) or 0)
                if cc > 0:
                    b["charges_current"] = cc - 1
                    report.append(
                        f"{b.get('name', '?')}: заряд −1 "
                        f"({b['charges_current']}/"
                        f"{b.get('charges_max', 0)})")
            elif ctm == "increment":
                cc = int(b.get("charges_current", 0) or 0)
                cm = int(b.get("charges_max", 0) or 0)
                if cm > 0 and cc < cm:
                    b["charges_current"] = cc + 1
                    report.append(
                        f"{b.get('name', '?')}: заряд +1 "
                        f"({b['charges_current']}/{cm})")
            if auto_delete_ok and cur <= 0:
                if "from_item_activation" in b:
                    item = self.items.get(
                        b["from_item_activation"])
                    if item:
                        item["activated"] = False
                expired.append(b.get("name", "?"))
                continue
            new_list.append(b)
        self.situational_bonuses = new_list
        for n in expired:
            report.append(f"Закончился баф: {n}")

        # T45: restore_* и self_damage_per_tick вынесены из блока
        # «1) Бафы» и применяются в конце тика (см. ниже).

        # 2) Кулдауны

        holders = [
            self.char_class.get("abilities", []),
            self.race.get("abilities", []),
            list(self.items.values()),
            self.attacks,
        ]
        for holder in holders:
            for e in holder:
                if not isinstance(e, dict):
                    continue
                if e.get("cooldown_rounds", 0) > 0:
                    cur = e.get("cooldown_current", 0)
                    if cur > 0:
                        e["cooldown_current"] = max(0, cur - 1)
                        if e["cooldown_current"] == 0:
                            report.append(
                                f"Готово: {e.get('name', '?')}")

        # 3) Тик зарядов
        for holder in holders:
            for e in holder:
                if not isinstance(e, dict):
                    continue
                mode = e.get("tick_mode", "none")
                if mode == "restore" and e.get("uses"):
                    mx = e.get("uses_max", 0)
                    if mx > 0:
                        before = e.get("uses_current", 0)
                        e["uses_current"] = mx
                        if before < mx:
                            report.append(
                                f"{e.get('name', '?')}: заряды "
                                f"восстановлены ({mx}/{mx})")
                elif mode == "decrease" and e.get("uses"):
                    if e.get("uses_current", 0) > 0:
                        e["uses_current"] = max(
                            0, e["uses_current"] - 1)
                        report.append(
                            f"{e.get('name', '?')}: −1 заряд "
                            f"({e['uses_current']}/"
                            f"{e.get('uses_max', 0)})")

        for a in self.attacks:
            if (a.get("tick_on_initiative") and a.get("uses")
                    and not a.get("tick_mode")):
                a["uses_current"] = a.get("uses_max", 0)

        # 4) Травмы
        for inj in self.injuries:
            if not isinstance(inj, dict):
                continue
            if inj.get("tick_on_initiative") and inj.get("uses"):
                inj["uses_current"] = max(
                    0, inj.get("uses_current", 0) - 1)

        # 5) Перегрузка
        if getattr(self, "overload_enabled", False):
            if self.overload > 0:
                self.overload -= 1
                report.append(
                    f"⛓ Перегрузка −1 (осталось {self.overload})")

        # 6) Баланс
        if apply_balance:
            blockers = []
            if self.is_blocked("balance_restore"):
                blockers.append("баф")
            if (getattr(self, "overload_enabled", False)
                    and self.overload > 0):
                blockers.append(f"перегрузка {self.overload}")
            if blockers:
                report.append(
                    f"Баланс: заблокировано ({', '.join(blockers)})")
            else:
                # Бонус +1 баланс/ход от spec_balance_1
                # (складывается по всем надетым оружиям владения)
                weapon_balance_bonus = 0
                for it in self._equipped_items():
                    if it.get("slot") not in ("weapon_main",
                                                "weapon_off"):
                        continue
                    w_name = ((it.get("weapon_group") or "").strip()
                              or it.get("name", ""))
                    w = (self.weapon_by_name(w_name)
                         if w_name else None)
                    if w:
                        weapon_balance_bonus += (
                            self.weapon_balance_restore_bonus(w))

                before = self.balance["current"]
                restore = max(
                    1, self.level + self.con_mod()
                    + self.balance_restore_bonus
                    + weapon_balance_bonus)
                # T45: НЕ обрезаем до max — даём «запас» для урона.
                self.balance["current"] = before + restore
                gained = self.balance["current"] - before
                if gained:
                    report.append(f"Баланс +{gained}")

        # 7) T45: кровотечение (self_damage_per_tick).
        # Урон идёт через take_damage → HP + баланс + ОТ.
        total_self_dmg = 0
        for b in self.situational_bonuses:
            dmgs = []
            for e in b.get("effects", []):
                if (isinstance(e, dict)
                        and e.get("target") == "self_damage_per_tick"):
                    dmgs.append(e)
            if not dmgs:
                continue
            dmg_sum = sum(self._eval_effect_value(e.get("value", 0))
                          for e in dmgs)
            if dmg_sum <= 0:
                continue
            total_self_dmg += dmg_sum
            r = self.take_damage(dmg_sum)
            parts = [f"−{dmg_sum} HP"]
            if r.get("balance_loss"):
                parts.append(f"баланс −{r['balance_loss']}")
            if r.get("injury"):
                parts.append(f"ОТ +{r['injury']}")
            report.append(
                f"{b.get('name', '?')}: " + ", ".join(parts))
        if total_self_dmg > 0 and self.is_dead():
            report.append("💀 ПЕРСОНАЖ МЁРТВ (кровотечение)")

        # T45: после урона — обрезать переполнение баланса до max.
        self.balance["current"] = min(self.balance["current"], self.balance["max"])

        # 8) T45: restore_* — в самом конце, после урона.
        for b in self.situational_bonuses:
            restores = [e for e in b.get("effects", [])
                        if isinstance(e, dict)
                        and str(e.get("target", "")).startswith("restore_")]
            if restores:
                got = self._apply_effect_values(restores)
                for line in got:
                    report.append(f"{b.get('name', '?')}: {line}")

        # 9) T41: HP-реген за тик
        regen = int(self.settings.get("hp_regen_per_tick", 0) or 0)
        if regen > 0:
            before = self.combat["hp_current"]
            cap = self.hp_max_actual()
            self.combat["hp_current"] = min(cap, before + regen)
            got = self.combat["hp_current"] - before
            if got:
                report.append(f"HP-реген +{got}")

        return report

    def is_blocked(self, action):
        """T-EFFECTS-UI: блокировки с префиксами do:*."""
        for b in self.situational_bonuses:
            for blk in b.get("blocks", []):
                if (blk.startswith("do:") and blk[3:] == action) or blk == action:
                    return True
        for blk in self.stance_blocks():
            if (blk.startswith("do:") and blk[3:] == action) or blk == action:
                return True
        return False

    def is_bonus_denied(self, bonus_type):
        """T-EFFECTS-UI: запрещён ли тип бонуса."""
        for b in self.situational_bonuses:
            for blk in b.get("blocks", []):
                if blk.startswith("bonus:") and blk[6:] == bonus_type:
                    return True
        for blk in self.stance_blocks():
            if blk.startswith("bonus:") and blk[6:] == bonus_type:
                return True
        return False

    def is_resource_denied(self, resource):
        """T-EFFECTS-UI: запрещено ли восстановление ресурса."""
        for b in self.situational_bonuses:
            for blk in b.get("blocks", []):
                if blk.startswith("res:") and blk[4:] == resource:
                    return True
        for blk in self.stance_blocks():
            if blk.startswith("res:") and blk[4:] == resource:
                return True
        return False

    def is_target_denied(self, target):
        """T-EFFECTS-UI: запрещён ли бонус к этой цели (deny:*)."""
        for b in self.situational_bonuses:
            for blk in b.get("blocks", []):
                if blk == f"deny:{target}":
                    return True
        for blk in self.stance_blocks():
            if blk == f"deny:{target}":
                return True
        return False
    
    # ---------- ПРОИЗВОДНЫЕ ----------

    def damage_modifier(self):
        return (self.pain_penalty() + self.morale_bonus()
                + self.situational_bonus("damage"))

    def attack_bonus(self, a):
        base = 0
        if a.get("use_bab"):
            stat = a.get("stat")
            mod = self.ability_modifier(stat) if stat else 0
            base = (self.bab_base() + mod
                    + a.get("extra_bonus", 0))
        else:
            base = a.get("manual_bonus", 0)
        iid = a.get("from_item")
        if iid:
            base += self._item_bonus(iid, "attack")
        w = self.weapon_by_name(a.get("proficiency"))
        if w:
            base += self.weapon_attack_bonus(w)
        return (base + self.pain_penalty() + self.morale_bonus()
                + self.situational_bonus("attack")
                + self.unprof_attack_penalty()
                + self.weapon_unprof_penalty_for_attack(a)
                + size_mod_attack(self.combat.get("size", "Medium")))

    def save_auto_base(self, key):
        good = self.char_class.get("good_saves", [])
        lvl = self.level
        if key in good:
            return 2 + lvl // 2
        return lvl // 3

    def save_ability_mod(self, key):
        return self.ability_modifier(SAVE_STATS.get(key, "con"))

    def save_mods(self, key):
        s = self.combat["saves"].get(key, _new_save())
        return s.get("mods", [])

    def save_mods_sum(self, key):
        return sum(m.get("value", 0) for m in self.save_mods(key))

    def save_total(self, key):
        return (self.save_auto_base(key)
                + self.save_ability_mod(key)
                + self.save_mods_sum(key)
                + self.pain_penalty() + self.morale_bonus()
                + self.situational_bonus("save")
                + self.situational_bonus(key))

    def save_breakdown(self, key):
        auto = self.save_auto_base(key)
        ab = self.save_ability_mod(key)
        mods = self.save_mods(key)
        m_sum = sum(m.get("value", 0) for m in mods)
        pen = (self.pain_penalty() + self.morale_bonus()
               + self.situational_bonus("save")
               + self.situational_bonus(key))
        return {"auto": auto, "ability": ab,
                "ability_stat": SAVE_STATS.get(key, "con").upper(),
                "mods": mods, "mods_sum": m_sum,
                "penalty": pen,
                "total": auto + ab + m_sum + pen}

    def skill_bonus(self, skill):
        tier = skill.get("tier", "normal")
        tier_bonus = {"normal": 0, "advanced": 3,
                      "specialized": 6}.get(tier, 0)
        stat = skill.get("stat", "int")
        mods_sum = sum(m.get("value", 0)
                       for m in skill.get("mods", []))
        return (skill.get("rank", 0)
                + self.ability_modifier(stat)
                + self.pain_penalty() + self.morale_bonus()
                + self.situational_bonus("skill", skill.get("name"))
                + mods_sum
                + tier_bonus
                + self.unprof_skill_penalty(stat)
                + self.equipped_skill_penalty(stat))

    def mana_max_calc(self):
        total = int(self.mana.get("class_max", 0) or 0)
        for b in self.mana.get("bonus_sources", []):
            total += int(b.get("value", 0) or 0)
        return max(0, total + self.situational_bonus("max_mana"))

    def mana_detail(self):
        out = []
        cl = int(self.mana.get("class_max", 0) or 0)
        if cl:
            out.append(("за класс", cl))
        for i, b in enumerate(self.mana.get("bonus_sources", [])):
            v = int(b.get("value", 0) or 0)
            if v:
                nm = (b.get("name") or "").strip() or f"источник {i+1}"
                out.append((nm, v))
        return out

    def attention_per_cycle(self):
        base = 1 + self.level // 3
        drive_bonus = sum(1 for v in self.drives.values()
                          if v >= 4)
        return base + drive_bonus

    def drives_total(self):
        return sum(self.drives.values())

    def drives_at_crazy(self):
        return [k for k, v in self.drives.items() if v >= 5]

    def principles_for(self, drive_key):
        return [p for p in self.drive_principles
                if p.get("drive_key") == drive_key]

    def recompute_derived(self):
        hp_max = self.hp_max_actual()
        self.combat["hp_current"] = min(self.combat["hp_current"], hp_max)
        pain_base = (math.ceil(hp_max / 4) + self.pain_threshold_bonus)
        self.pain_threshold["max"] = max(
            1, pain_base + self.situational_bonus("max_pain_threshold"))
        self.balance["max"] = max(0,
            self.pain_threshold["max"]
            + self.armor_ac_from_equipped()
            + self.shield_part_for_balance()
            + self.balance_bonus
            + self.situational_bonus("max_balance"))
        self.spirit["max"] = self.spirit_max()
        self.mana["max"] = self.mana_max_calc()
        
        max_res = self.situational_bonus("max_resource")
        for r in self.class_resources:
            if max_res:
                r["max"] = max(0, int(r.get("max", 0)) + max_res)
        self.mana["current"] = min(self.mana["current"], self.mana["max"])
        self.mana["current"] = max(self.mana["current"], 0)
        for field in (self.pain_threshold, self.balance, self.spirit):
            field["current"] = min(field["current"], field["max"])

    def recompute_skills_invested(self):
        expected = {}
        for s in self.skills:
            expected[s["name"]] = _skill_expected_value(self, s["name"])
        for s in self.skills:
            old = s.get("invested", 0)
            new = expected.get(s["name"], 0)
            if old > new:
                diff = old - new
                self.training["available"] += diff
                self.training["spent"] = max(
                    0, self.training["spent"] - diff)
                s["invested"] = new

    def embed_images(self):
        import base64
        import io
        try:
            from PIL import Image
        except Exception:
            return

        def _encode(path, max_side=1200):
            try:
                if not path or not os.path.exists(path):
                    return ""
                img = Image.open(path)
                has_alpha = img.mode in ("RGBA", "LA", "P")
                img = img.convert("RGBA" if has_alpha else "RGB")
                if img.width > max_side or img.height > max_side:
                    img.thumbnail((max_side, max_side), Image.LANCZOS)
                buf = io.BytesIO()
                if has_alpha:
                    img.save(buf, format="PNG", optimize=True)
                else:
                    img.save(buf, format="JPEG", quality=85)
                return base64.b64encode(buf.getvalue()).decode("ascii")
            except Exception as e:
                print(f"[embed] {e}")
                return ""

        if self.portrait and not self.portrait_b64:
            self.portrait_b64 = _encode(self.portrait)
        if self.background_image and not self.background_b64:
            self.background_b64 = _encode(self.background_image)

    def add_xp(self, n):
        self.xp = max(0, self.xp + n)
        return self.xp

    def init_defaults(self):
        self.char_class["level"] = 1
        hp_die = self.char_class.get("hp_die", 8)
        self.char_class["hp_rolls"] = [hp_die]
        if not any(s.get("name") == "Восприятие" for s in self.skills):
            self.skills.append({
                "name": "Восприятие", "stat": "wis",
                "tier": "normal", "rank": 0,
                "source": "training", "invested": 0,
                "mods": [],
            })
        self.recompute_derived()

    def start_session(self):
        self.recompute_derived()
        self.pain_threshold["current"] = self.pain_threshold["max"]
        self.balance["current"] = self.balance["max"]
        self.spirit["current"] = self.spirit["max"]
        self.mana["current"] = self.mana["max"]
        self.pain_extra_temp = 0
        for lvl, s in self.spell_slots.items():
            s["current"] = s["max"]
        for r in self.class_resources:
            r["current"] = r["max"]
        for a in self.char_class.get("abilities", []):
            if isinstance(a, dict) and a.get("uses"):
                a["uses_current"] = a.get("uses_max", 0)
        for a in self.race.get("abilities", []):
            if isinstance(a, dict) and a.get("uses"):
                a["uses_current"] = a.get("uses_max", 0)
        for s in self.skills:
            if s.get("tier") == "specialized":
                s["used_this_session"] = False

    # ============ ЗАКЛИНАНИЯ (Задача C) ============

    def spell_range_text(self, spell):
        """Текст дистанции заклинания (число + ' фт' или текст)."""
        rt = (spell.get("range_type") or "long").strip()
        if rt == "short":
            val = 25 + 5 * (self.level // 2)
            return f"{val} фт"
        if rt == "medium":
            val = 100 + 10 * self.level
            return f"{val} фт"
        if rt == "long":
            val = 400 + 40 * self.level
            return f"{val} фт"
        # custom
        raw = spell.get("range_custom", 0)
        if isinstance(raw, str):
            v = self._eval_effect_value(raw)
            if v:
                return f"{v} фт"
            return raw or "—"
        if raw:
            return f"{int(raw)} фт"
        return "—"

    def spell_can_cast(self, spell):
        """Можно ли скастовать (True/False)."""
        mana_cost = int(spell.get("mana_cost", 0) or 0)
        slot_circle = int(spell.get("slot_circle", spell.get("circle", 0)) or 0)
        if mana_cost > 0:
            if not self.mana.get("enabled"):
                return False
            return self.mana.get("current", 0) >= mana_cost
        # без маны — тратит слот
        if not self.spell_slots_enabled:
            return True
        s = self.spell_slots.get(str(slot_circle))
        if not s:
            return False
        return s.get("current", 0) > 0

    def cast_spell(self, spell_idx):
        """Скастовать заклинание. Возвращает dict-отчёт."""
        if not (0 <= spell_idx < len(self.spells)):
            return {"ok": False, "msg": "Заклинание не найдено"}
        sp = self.spells[spell_idx]
        if not self.spell_can_cast(sp):
            return {"ok": False, "msg": "Недостаточно маны или слотов"}
        mana_cost = int(sp.get("mana_cost", 0) or 0)
        slot_circle = int(sp.get("slot_circle", sp.get("circle", 0)) or 0)
        # Трата маны ИЛИ слота
        if mana_cost > 0:
            self.mana["current"] = max(0, self.mana.get("current", 0) - mana_cost)
        else:
            if self.spell_slots_enabled:
                s = self.spell_slots.get(str(slot_circle))
                if s and s.get("current", 0) > 0:
                    s["current"] -= 1
        # Перегрузка
        ov = int(sp.get("overload", 0) or 0)
        if ov > 0:
            self.overload += ov
            self.overload_enabled = True
        # Баланс (с проверкой на ОТ, как в take_damage)
        bal_cost = int(sp.get("balance_cost", 0) or 0)
        injury = 0
        if bal_cost > 0:
            bal = self.balance.get("current", 0)
            if bal >= bal_cost:
                self.balance["current"] = bal - bal_cost
            else:
                diff = bal_cost - bal
                self.balance["current"] = 0
                self.injury_points += diff
                injury = diff
        # Концентрация: если баланс получил ОТ — нужен бросок.
        # КС = 10 + 2×ОТ. Если ОТ = 0 — проверка не нужна.
        concentration_ks = (10 + 2 * injury) if injury > 0 else 0
        return {"ok": True, "mana": mana_cost, "slot": slot_circle,
                "overload": ov, "balance": bal_cost,
                "injury": injury,
                "concentration_ks": concentration_ks}

    def apply_regen_modifier(self, base_hp):
        s = (self.regen_modifier or "").strip().lower()
        if not s:
            return base_hp
        s = (s.replace(" ", "")
              .replace("х", "x").replace("×", "x").replace("*", "x"))
        try:
            mult = 1.0
            for m in re.finditer(r'x(\d+(?:\.\d+)?)', s):
                mult *= float(m.group(1))
            add = 0.0
            s_clean = re.sub(r'x(\d+(?:\.\d+)?)', '', s)
            for m in re.finditer(r'([+-]?)(\d+(?:\.\d+)?)', s_clean):
                sign = -1 if m.group(1) == "-" else 1
                add += sign * float(m.group(2))
            result = int(base_hp * mult + add)
            return max(0, result)
        except Exception:
            return base_hp

    def short_rest(self):
        base_hp = 2 + self.level
        heal = self.apply_regen_modifier(base_hp)
        before_hp = self.combat["hp_current"]
        self.combat["hp_current"] = min(
            self.hp_max_actual(), before_hp + heal)
        got_hp = self.combat["hp_current"] - before_hp
        before_bp = self.pain_threshold["current"]
        self.pain_threshold["current"] = min(
            self.pain_threshold["max"], before_bp + 1)
        got_bp = self.pain_threshold["current"] - before_bp
        return {"hp": got_hp, "bp": got_bp,
                "hp_base": base_hp, "hp_final": heal}

    def long_rest(self):
        self.recompute_derived()
        self.combat["hp_current"] = self.hp_max_actual()
        self.combat["hp_temp"] = 0
        self.pain_threshold["current"] = self.pain_threshold["max"]
        self.balance["current"] = self.balance["max"]
        self.spirit["current"] = self.spirit["max"]
        if self.mana.get("enabled"):
            self.mana["current"] = self.mana["max"]
        for lvl, s in self.spell_slots.items():
            s["current"] = s["max"]
        for r in self.class_resources:
            r["current"] = r["max"]
        for a in self.char_class.get("abilities", []):
            if isinstance(a, dict) and a.get("uses"):
                a["uses_current"] = a.get("uses_max", 0)
        for a in self.race.get("abilities", []):
            if isinstance(a, dict) and a.get("uses"):
                a["uses_current"] = a.get("uses_max", 0)
        self.injury_points = 0
        for ab in self.ability_damage:
            self.ability_damage[ab] = 0
        for s in self.skills:
            if s.get("tier") == "specialized":
                s["used_this_session"] = False
        for item in self.items.values():
            if item.get("activated"):
                item["activated"] = False
        self.situational_bonuses = [
            b for b in self.situational_bonuses
            if "from_item_activation" not in b
        ]
        # T34: заряды восстанавливаются на долгом отдыхе.
        for b in self.situational_bonuses:
            if int(b.get("charges_max", 0) or 0) > 0:
                b["charges_current"] = int(b["charges_max"])
        self.recompute_derived()

    def take_damage(self, amount):
        if amount <= 0:
            return {"hp_loss": 0, "temp_loss": 0, "balance_loss": 0,
                    "injury": 0, "pain": self.pain_level(),
                    "hp_current": self.combat["hp_current"],
                    "hp_temp": self.combat.get("hp_temp", 0)}
        temp = self.combat.get("hp_temp", 0)
        temp_loss = min(amount, temp)
        self.combat["hp_temp"] = temp - temp_loss
        remaining = amount - temp_loss
        hp_loss = remaining
        self.combat["hp_current"] -= remaining
        bal_loss = min(remaining, self.balance["current"])
        self.balance["current"] -= bal_loss
        injury = remaining - bal_loss
        self.injury_points += injury
        return {"hp_loss": hp_loss, "temp_loss": temp_loss,
                "balance_loss": bal_loss, "injury": injury,
                "pain": self.pain_level(),
                "hp_current": self.combat["hp_current"],
                "hp_temp": self.combat["hp_temp"]}

    def set_temp_hp(self, amount):
        self.combat["hp_temp"] = max(0, amount)

    def lose_balance(self, amount):
        if amount <= 0:
            return 0
        actual = min(amount, self.balance["current"])
        self.balance["current"] -= actual
        return actual

    def zero_initiative(self):
        restore = max(1, self.level + self.con_mod()
                      + self.balance_restore_bonus)
        before = self.balance["current"]
        self.balance["current"] = min(
            self.balance["max"], self.balance["current"] + restore)
        return self.balance["current"] - before

    def restore_hp(self, amount):
        if amount <= 0:
            return 0
        before = self.combat["hp_current"]
        self.combat["hp_current"] = min(
            self.hp_max_actual(), before + amount)
        return self.combat["hp_current"] - before

    def restore_balance(self, amount):
        if amount <= 0:
            return 0
        before = self.balance["current"]
        self.balance["current"] = min(
            self.balance["max"], before + amount)
        return self.balance["current"] - before

    def restore_bp(self, amount):
        if amount <= 0:
            return 0
        before = self.pain_threshold["current"]
        self.pain_threshold["current"] = min(
            self.pain_threshold["max"], before + amount)
        return self.pain_threshold["current"] - before

    def clear_injury(self, amount=None):
        if amount is None:
            self.injury_points = 0
        else:
            self.injury_points = max(0, self.injury_points - amount)

    def spend_mana(self, n=1):
        if not self.mana.get("enabled"):
            return 0
        actual = min(n, self.mana["current"])
        self.mana["current"] -= actual
        return actual

    def restore_mana(self, n=1):
        if not self.mana.get("enabled"):
            return 0
        before = self.mana["current"]
        self.mana["current"] = min(self.mana["max"], before + n)
        return self.mana["current"] - before

    def spend_slot(self, circle):
        s = self.spell_slots.get(str(circle))
        if not s or s["current"] <= 0:
            return False
        s["current"] -= 1
        return True

    def restore_slot(self, circle):
        s = self.spell_slots.get(str(circle))
        if not s or s["current"] >= s["max"]:
            return False
        s["current"] += 1
        return True

    def spend_resource(self, index):
        if index < 0 or index >= len(self.class_resources):
            return False
        r = self.class_resources[index]
        if r["current"] <= 0:
            return False
        r["current"] -= 1
        return True

    def restore_resource(self, index):
        if index < 0 or index >= len(self.class_resources):
            return False
        r = self.class_resources[index]
        if r["current"] >= r["max"]:
            return False
        r["current"] += 1
        return True

    def use_ability(self, index):
        abils = self.char_class.get("abilities", [])
        if index < 0 or index >= len(abils):
            return False
        a = abils[index]
        if not a.get("uses") or a.get("uses_current", 0) <= 0:
            return False
        if a.get("cooldown_current", 0) > 0:
            return False
        a["uses_current"] -= 1
        if a.get("cooldown_rounds", 0) > 0:
            a["cooldown_current"] = a["cooldown_rounds"]
        return True

    def restore_ability(self, index):
        abils = self.char_class.get("abilities", [])
        if index < 0 or index >= len(abils):
            return False
        a = abils[index]
        if not a.get("uses"):
            return False
        if a.get("uses_current", 0) >= a.get("uses_max", 0):
            return False
        a["uses_current"] += 1
        return True

    def use_race_ability(self, index):
        abils = self.race.get("abilities", [])
        if index < 0 or index >= len(abils):
            return False
        a = abils[index]
        if not a.get("uses") or a.get("uses_current", 0) <= 0:
            return False
        if a.get("cooldown_current", 0) > 0:
            return False
        a["uses_current"] -= 1
        if a.get("cooldown_rounds", 0) > 0:
            a["cooldown_current"] = a["cooldown_rounds"]
        return True

    def restore_race_ability(self, index):
        abils = self.race.get("abilities", [])
        if index < 0 or index >= len(abils):
            return False
        a = abils[index]
        if not a.get("uses"):
            return False
        if a.get("uses_current", 0) >= a.get("uses_max", 0):
            return False
        a["uses_current"] += 1
        return True

    def to_dict(self):
        return {
            "name": self.name,
            "class_display":
                f"{self.char_class['name']} {self.level}".strip(),
            "hp": f"{self.combat['hp_current']}/{self.hp_max_actual()}",
            "ac": self.combat["ac"],
            "parrying": self.total_parrying(),
            "bab": self.bab_base(),
            "pain_threshold":
                f"{self.pain_threshold['current']}/{self.pain_threshold['max']}",
            "balance": f"{self.balance['current']}/{self.balance['max']}",
            "spirit": f"{self.spirit['current']}/{self.spirit['max']}",
            "mana": f"{self.mana['current']}/{self.mana['max']}",
            "injury_points": self.injury_points,
            "morale": self.morale,
            "situational_bonuses": self.situational_bonuses,
            "ignore_pain": self.ignore_pain,
            "ignore_negative_morale": self.ignore_negative_morale,
            "overload": self.overload,
            "overload_enabled": self.overload_enabled,
            "auto_balance_on_tick": self.auto_balance_on_tick,
            "save_fort": self.save_total("fort"),
            "save_ref": self.save_total("ref"),
            "save_will": self.save_total("will"),
            "xp": self.xp, "xp_threshold": self.xp_threshold,
            "portrait": self.portrait,
            "portrait_b64": self.portrait_b64,
            "background_image": self.background_image,
            "background_b64": self.background_b64,
            "music_url": self.music_url,
            "char_class": self.char_class,
            "race": self.race,
            "abilities": self.abilities,
            "ability_damage": self.ability_damage,
            "combat": self.combat,
            "equipment": self.equipment,
            "natural_armor": self.natural_armor,
            "ac_bonus": self.ac_bonus,
            "ac_misc": self.ac_misc,
            "cmb_mods": self.cmb_mods,
            "cmd_mods": self.cmd_mods,
            "items": self.items,
            "downtime": self.downtime,
            "bag_dropped": self.bag_dropped,
            "_pain_threshold_data": self.pain_threshold,
            "pain_threshold_bonus": self.pain_threshold_bonus,
            "pain_extra": self.pain_extra,
            "pain_extra_temp": self.pain_extra_temp,
            "pain_max": self.pain_max,
            "regen_modifier": self.regen_modifier,
            "_balance_data": self.balance,
            "balance_bonus": self.balance_bonus,
            "balance_restore_bonus": self.balance_restore_bonus,
            "spirit_bonus": self.spirit_bonus,
            "hp_bonus": self.hp_bonus,
            "_spirit_data": self.spirit,
            "_mana_data": self.mana,
            "injuries": self.injuries,
            "reactions": self.reactions,
            "reactions_invested": self.reactions_invested,
            "active_stance": self.active_stance,
            "action_log": self.action_log,
            "proficiencies": self.proficiencies,
            "armor_invested": self.armor_invested,
            "shield_invested": self.shield_invested,
            "training": self.training,
            "skills": self.skills,
            "feats": self.feats,
            "quirks": self.quirks,
            "attacks": self.attacks,
            "class_resources": self.class_resources,
            "spell_slots": self.spell_slots,
            "spell_slots_enabled": self.spell_slots_enabled,
            "base": self.base,
            "base_invested": self.base_invested,
            "comfort": self.comfort,
            "attention": self.attention,
            "languages": self.languages,
            "spells": self.spells,
            "seeds": self.seeds,
            "templates": self.templates,
            "wiki_links": self.wiki_links,
            "drives": self.drives,
            "drive_principles": self.drive_principles,
            "courts": self.courts,
            "court_quests": self.court_quests,
            "lenses": self.lenses,
            "settings": self.settings,
            "notes": self.notes,
            "_hp_max_cap": self.hp_max_cap(),
        }

    def save(self, path):
        self.recompute_derived()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        c = cls(data.get("name", "Без имени"))
        summary = {"name", "class_display", "hp", "ac", "parrying",
                   "bab", "pain_threshold", "balance", "spirit", "mana",
                   "save_fort", "save_ref", "save_will",
                   "hp_from_rolls", "injury_points"}
        dp = data.pop("_pain_threshold_data", None)
        db = data.pop("_balance_data", None)
        ds = data.pop("_spirit_data", None)
        dm = data.pop("_mana_data", None)
        for k, v in data.items():
            if k in summary or k.startswith("_"):
                continue
            setattr(c, k, v)
        if dp: c.pain_threshold = dp
        if db: c.balance = db
        if ds: c.spirit = ds
        if dm: c.mana = dm

        if not isinstance(c.mana, dict):
            c.mana = _new_mana()
        old_max = c.mana.pop("max", 0)
        old_per = c.mana.pop("per_level", 0)
        old_bonus = c.mana.pop("bonus", 0)
        c.mana.setdefault("current", 0)
        c.mana.setdefault("enabled", bool(old_max > 0))
        if "class_max" not in c.mana:
            if old_per:
                c.mana["class_max"] = c.level * old_per
            elif old_max:
                c.mana["class_max"] = old_max
            else:
                c.mana["class_max"] = 0
        if not isinstance(c.mana.get("bonus_sources"), list):
            c.mana["bonus_sources"] = []
        if old_bonus:
            bs = c.mana["bonus_sources"]
            while len(bs) < 2:
                bs.append({"name": "", "value": 0})
            if not bs[0].get("value"):
                bs[0]["name"] = "старый бонус"
                bs[0]["value"] = old_bonus
        while len(c.mana["bonus_sources"]) < 2:
            c.mana["bonus_sources"].append({"name": "", "value": 0})
        for b in c.mana["bonus_sources"]:
            b.setdefault("name", "")
            b.setdefault("value", 0)

        if "hp_temp" not in c.combat:
            c.combat["hp_temp"] = 0
        if not hasattr(c, "spell_slots_enabled"):
            c.spell_slots_enabled = bool(c.spell_slots)

        if not isinstance(c.equipment, dict):
            c.equipment = {"armor_ac": 0, "shield_ac": 0}
        c.equipment.setdefault("armor_ac", 0)
        c.equipment.setdefault("shield_ac", 0)
        c.equipment.setdefault("add_shield_ac_to_balance", False)

        for key in ("fort", "ref", "will"):
            s = c.combat["saves"].get(key)
            if isinstance(s, (int, float)):
                c.combat["saves"][key] = {"base": 0, "mods": [
                    {"source": "старый base", "value": int(s)}]}
            elif s is None:
                c.combat["saves"][key] = _new_save()
            else:
                old_base = s.get("base", 0)
                if old_base != 0:
                    s.setdefault("mods", []).append(
                        {"source": "старый base",
                         "value": int(old_base)})
                    s["base"] = 0
                s.setdefault("mods", [])

        if not isinstance(getattr(c, "settings", None), dict):
            c.settings = {}
        for k in ("show_mana", "show_class_points",
                  "show_spell_slots", "show_spell_list",
                  "hide_portrait"):
            c.settings.setdefault(k, False)
        for k in ("show_rest_short", "show_rest_long", "show_bp_chip",
                  "show_comfort_chip"):
            c.settings.setdefault(k, True)
        for k in ("show_attention_chip", "show_time_chip"):
            c.settings.setdefault(k, False)
        c.settings.setdefault("hide_hints", False)
        c.settings.setdefault("hp_regen_per_tick", 0)
        # T-ALPHA (v18)
        for _ak in ("alpha_menu", "alpha_center", "alpha_chips",
                    "alpha_log", "alpha_chip_buttons"):
            c.settings.setdefault(_ak, 90)
            try:
                c.settings[_ak] = max(10, min(90, int(c.settings[_ak])))
            except Exception:
                c.settings[_ak] = 90
        # T-STANCE (v18)
        if not isinstance(c.settings.get("stance_chips"), list):
            c.settings["stance_chips"] = []
        c.settings.setdefault("stance_chips", [])
        if not hasattr(c, "active_stance"):
            c.active_stance = None
        if not isinstance(c.active_stance, (str, type(None))):
            c.active_stance = None
        if not isinstance(getattr(c, "action_log", None), list):
            c.action_log = []
        # обрезка action_log до 20
        c.action_log = [e for e in c.action_log
                        if isinstance(e, dict)][-20:]
        if not isinstance(c.settings.get("catalogs_enabled"), list):
            c.settings["catalogs_enabled"] = []
        if c.settings.get("catalogs_mode") not in ("blacklist",
                                                    "whitelist"):
            c.settings["catalogs_mode"] = "blacklist"
        c.settings.setdefault("ui_layout", [])
        c.settings.setdefault("window_open_mode", "menu")
        c.settings.setdefault("pin_editor_to_menu", True)
        c.settings.setdefault("close_prev_window", False)
        c.settings.setdefault("hotkeys", {
            "damage": "u", "heal": "h", "restore_balance": "b",
            "pain_up": "p", "pain_down": "P",
            "morale_up": "m", "morale_down": "M",
            "comfort_spend": "c", "temp_hp": "t",
        })

        for attr, default in [("quirks", []), ("attacks", []),
                               ("class_resources", []),
                               ("spell_slots", {}), ("spells", []),
                               ("languages", []), ("skills", []),
                               ("feats", []), ("injuries", []),
                               ("seeds", []), ("templates", []),
                               ("wiki_links", []),
                               ("drive_principles", []),
                               ("court_quests", []),
                               ("lenses", [])]:
            if not hasattr(c, attr) or not isinstance(
                    getattr(c, attr), type(default)):
                setattr(c, attr, default)
        # Задача L: нормализация линз
        c.lenses = [ln for ln in c.lenses if isinstance(ln, dict)]
        for ln in c.lenses:
            ln.setdefault("name", "")
            ln.setdefault("desc", "")
            ln.setdefault("current", 0)
            ln.setdefault("max", 0)
            ln.setdefault("show_on_panel", False)
            ln.pop("done", None)

        # ===== Миграция драйвов =====
        if not isinstance(c.drives, dict):
            old_drives = c.drives if isinstance(c.drives, list) else []
            c.drives = {k: 0 for k, _ in DRIVE_KEYS}
            for old in old_drives:
                if not isinstance(old, dict):
                    continue
                lvl = old.get("level", 0)
                old_name = (old.get("name") or "").lower()
                for k, ru in DRIVE_KEYS:
                    if ru.lower() in old_name or old_name in ru.lower():
                        c.drives[k] = min(5, max(0, lvl))
                        break
        else:
            for k, _ in DRIVE_KEYS:
                c.drives.setdefault(k, 0)
                try:
                    c.drives[k] = min(5, max(0, int(c.drives[k])))
                except Exception:
                    c.drives[k] = 0

        # ===== Миграция дворов =====
        new_courts = []
        new_quests = []
        for old in getattr(c, "courts", []):
            if not isinstance(old, dict):
                continue
            name = old.get("name", "")
            if not name:
                continue
            if "reputation" not in old and "tier" not in old:
                new_courts.append({
                    "name": name, "reputation": 0, "tier": "I",
                })
                for q in old.get("quests", []):
                    if isinstance(q, str) and q.strip():
                        new_quests.append({
                            "name": q.strip(), "court": name,
                            "desc": "", "show_on_panel": False,
                        })
                    elif isinstance(q, dict):
                        new_quests.append({
                            "name": q.get("name", "?"),
                            "court": name,
                            "desc": q.get("desc", ""),
                            "show_on_panel": q.get(
                                "show_on_panel", False),
                        })
            else:
                new_courts.append({
                    "name": name,
                    "reputation": int(old.get("reputation", 0)),
                    "tier": old.get("tier", "I")
                            if old.get("tier") in COURT_TIERS
                            else "I",
                })
        c.courts = new_courts
        existing_quests = list(getattr(c, "court_quests", []) or [])
        for nq in new_quests:
            if not any(eq.get("name") == nq["name"]
                       and eq.get("court") == nq["court"]
                       for eq in existing_quests):
                existing_quests.append(nq)
        c.court_quests = existing_quests

        # ===== Миграция items =====
        if not isinstance(getattr(c, "items", None), dict):
            c.items = {}
        for it in c.items.values():
            if not isinstance(it, dict):
                continue
            slot = it.get("slot")
            if slot in SLOT_ALIASES:
                it["slot"] = SLOT_ALIASES[slot]
            it.setdefault("unload_bonus", 0)
            it.setdefault("enchants", [])
            it.setdefault("icon_b64", "")
            it.setdefault("base_slots", 1)
            it.setdefault("gray", False)
            it.setdefault("hardness", 0)
            it.setdefault("ac_type", "armor")
            it.setdefault("uses", False)
            it.setdefault("uses_max", 0)
            it.setdefault("uses_current", 0)
            it.setdefault("show_on_panel", False)
            it.setdefault("activatable", False)
            it.setdefault("activation_cost_spirit", 0)
            it.setdefault("activation_effects", [])
            it.setdefault("activation_duration", 0)
            it.setdefault("activated", False)
            it.setdefault("passive_bonuses", [])
            it.setdefault("attack_bonus", 0)
            it.setdefault("damage_bonus", 0)
            it.setdefault("crit_threshold", 20)
            it.setdefault("crit_mult", 2)
            it.setdefault("damage", "")
            it.setdefault("damage_sml", "")
            it.setdefault("damage_med", "")
            it.setdefault("damage_type", "")
            it.setdefault("hands", "")
            it.setdefault("weapon_group", "")
            it.setdefault("finesse", False)
            it.setdefault("two_handed", False)
            it.setdefault("ranged", False)
            it.setdefault("thrown", False)
            it.setdefault("range_ft", 0)
            it.setdefault("required_level", 0)
            it.setdefault("tick_mode", "none")
            it.setdefault("tick_on_initiative", False)
            it.setdefault("cooldown_rounds", 0)
            it.setdefault("cooldown_current", 0)
            it.setdefault("price", 0)
            old_str = it.pop("str_penalty", 0) or 0
            old_dex = it.pop("dex_penalty", 0) or 0
            if "skill_penalty" not in it:
                it["skill_penalty"] = min(old_str, old_dex)
        if not c.items:
            if c.equipment.get("armor_ac", 0) > 0:
                it = _make_item(
                    name="Старая броня", category="armor",
                    ac_bonus=c.equipment["armor_ac"],
                    ac_type="armor",
                    location="equipped", slot="armor",
                    weight=0, weight_type="-",
                )
                c.items[it["id"]] = it
                c.equipment["armor_ac"] = 0
            if c.equipment.get("shield_ac", 0) > 0:
                it = _make_item(
                    name="Старый щит", category="shield",
                    ac_bonus=c.equipment["shield_ac"],
                    ac_type="shield",
                    location="equipped", slot="shield",
                    weight=0, weight_type="-",
                )
                c.items[it["id"]] = it
                c.equipment["shield_ac"] = 0

        # ===== Миграция downtime =====
        if not isinstance(getattr(c, "downtime", None), dict):
            c.downtime = _new_downtime()
        c.downtime.setdefault("gold",
                               {"name": "Золото", "amount": 0})
        c.downtime.setdefault("silver",
                               {"name": "Серебро", "amount": 0})
        c.downtime.setdefault("copper",
                               {"name": "Медь", "amount": 0})
        c.downtime.setdefault("rates",
                               {"gold_to_silver": 100,
                                "silver_to_copper": 100})
        c.downtime.setdefault("time_points",
                               {"current": 0, "max": 0})

        if not isinstance(getattr(c, "bag_dropped", False), bool):
            c.bag_dropped = False

        # ===== Миграция травм =====
        new_injuries = []
        for inj in getattr(c, "injuries", []):
            if not isinstance(inj, dict):
                continue
            inj.setdefault("name", "Травма")
            inj.setdefault("desc", "")
            sev = inj.get("severity", "custom")
            if isinstance(sev, int):
                if sev >= 12:
                    sev = "heavy"
                elif sev >= 5:
                    sev = "medium"
                elif sev >= 2:
                    sev = "light"
                else:
                    sev = "custom"
            if sev not in ("light", "medium", "heavy", "custom"):
                sev = "custom"
            inj["severity"] = sev
            inj.setdefault("heal_rating",
                            {"light": 3, "medium": 2,
                             "heavy": 1, "custom": 1}.get(sev, 1))
            new_injuries.append(inj)
        c.injuries = new_injuries

        if not isinstance(getattr(c, "ability_damage", None), dict):
            c.ability_damage = {"str": 0, "dex": 0, "con": 0,
                                 "int": 0, "wis": 0, "cha": 0}
        for ab in ("str", "dex", "con", "int", "wis", "cha"):
            c.ability_damage.setdefault(ab, 0)
            if not isinstance(c.ability_damage[ab], int):
                c.ability_damage[ab] = 0
            c.ability_damage[ab] = max(
                0, min(c.ability_damage[ab], c.abilities.get(ab, 10)))

        for attr in ("pain_extra", "pain_extra_temp", "balance_bonus",
                     "balance_restore_bonus", "spirit_bonus",
                     "hp_bonus", "natural_armor", "ac_bonus", "ac_misc"):
            if not isinstance(getattr(c, attr, 0), int):
                setattr(c, attr, 0)
        if not isinstance(getattr(c, "pain_max", PAIN_MAX), int):
            c.pain_max = PAIN_MAX
        if c.pain_max < 1:
            c.pain_max = PAIN_MAX
        if not isinstance(getattr(c, "regen_modifier", ""), str):
            c.regen_modifier = ""
        if not isinstance(getattr(c, "attention", None), dict):
            c.attention = {"current": 0, "max": 1}
        c.attention.setdefault("current", 0)
        c.attention.setdefault("max", 1)
        if not isinstance(getattr(c, "ignore_pain", False), bool):
            c.ignore_pain = False
        if not isinstance(getattr(c, "ignore_negative_morale", False),
                          bool):
            c.ignore_negative_morale = False
        if not isinstance(getattr(c, "overload", 0), int):
            c.overload = 0
        c.overload = max(c.overload, 0)
        if not isinstance(getattr(c, "overload_enabled", False), bool):
            c.overload_enabled = False
        if not isinstance(getattr(c, "auto_balance_on_tick", True), bool):
            c.auto_balance_on_tick = True

        if not isinstance(getattr(c, "portrait_b64", ""), str):
            c.portrait_b64 = ""
        if not isinstance(getattr(c, "background_b64", ""), str):
            c.background_b64 = ""

        if not isinstance(getattr(c, "cmb_mods", None), list):
            c.cmb_mods = []
        if not isinstance(getattr(c, "cmd_mods", None), list):
            c.cmd_mods = []
        for lst in (c.cmb_mods, c.cmd_mods):
            for m in lst:
                if isinstance(m, dict):
                    m.setdefault("source", "?")
                    m.setdefault("value", 0)

        if not isinstance(getattr(c, "situational_bonuses", None),
                          list):
            c.situational_bonuses = []
        clean = []
        for b in c.situational_bonuses:
            if not isinstance(b, dict):
                continue
            b.setdefault("name", "?")
            b.setdefault("desc", "")
            b.setdefault("duration_rounds", 0)
            b.setdefault("duration_current", 0)
            b.setdefault("charges_max", 0)
            b.setdefault("charges_current", 0)
            # T34: заряды не должны превышать max.
            _cm = int(b.get("charges_max", 0) or 0)
            _cc = int(b.get("charges_current", 0) or 0)
            if _cm > 0 and _cc > _cm:
                b["charges_current"] = _cm
            b.setdefault("tick_on_initiative", False)
            b.setdefault("charges_tick_mode", "none")
            b.setdefault("blocks", [])
            # T42: разовые эффекты при активации.
            if not isinstance(b.get("on_activate_effects"), list):
                b["on_activate_effects"] = []
            for e in b["on_activate_effects"]:
                if not isinstance(e, dict):
                    continue
                e.setdefault("target", "restore_hp")
                e.setdefault("value", 0)
                if e["target"] not in VALID_SIT_TARGETS:
                    e["target"] = "restore_hp"
            if "effects" not in b:
                old_t = b.pop("target", "all")
                old_v = b.pop("value", 0)
                b["effects"] = [{"target": old_t, "value": old_v}]
            if not isinstance(b["effects"], list):
                b["effects"] = []
            for e in b["effects"]:
                if not isinstance(e, dict):
                    continue
                e.setdefault("target", "ac")
                e.setdefault("value", 0)
                if e["target"] not in VALID_SIT_TARGETS:
                    e["target"] = "ac"
            clean.append(b)
        c.situational_bonuses = clean

        c.char_class.setdefault("bab_type", "good")
        c.char_class["bab_type"] = BAB_MAP.get(
            c.char_class["bab_type"], c.char_class["bab_type"])
        if c.char_class["bab_type"] not in ("good", "medium", "poor"):
            c.char_class["bab_type"] = "good"
        if not isinstance(c.char_class.get("good_saves"), list):
            c.char_class["good_saves"] = []
        c.char_class["good_saves"] = [
            k for k in c.char_class["good_saves"]
            if k in ("fort", "ref", "will")]

        if not isinstance(c.char_class.get("abilities"), list):
            c.char_class["abilities"] = []
        for a in c.char_class["abilities"]:
            if not isinstance(a, dict):
                continue
            a.setdefault("uses", False)
            a.setdefault("uses_current", 0)
            a.setdefault("uses_max", 0)
            a.setdefault("show_on_panel", True)
            a.setdefault("tick_mode", "none")
            a.setdefault("cooldown_rounds", 0)
            a.setdefault("cooldown_current", 0)

        if not isinstance(c.race.get("abilities"), list):
            c.race["abilities"] = []
        for a in c.race["abilities"]:
            if not isinstance(a, dict):
                continue
            a.setdefault("uses", False)
            a.setdefault("uses_current", 0)
            a.setdefault("uses_max", 0)
            a.setdefault("show_on_panel", True)
            a.setdefault("tick_mode", "none")
            a.setdefault("cooldown_rounds", 0)
            a.setdefault("cooldown_current", 0)
            # T-EFFECTS-UI: единый шаблон
            if not isinstance(a.get("effects"), list):
                a["effects"] = []
            if not isinstance(a.get("on_activate_effects"), list):
                a["on_activate_effects"] = []
            a.setdefault("duration_rounds", 0)
            a.setdefault("duration_current", 0)
            a.setdefault("charges_max", 0)
            a.setdefault("charges_current", 0)
            a.setdefault("charges_tick_mode", "none")
            a.setdefault("tick_on_initiative", True)
            a.setdefault("permanent", True)
            a.setdefault("keep_at_zero", True)
            a.setdefault("is_buff", True)
            a.setdefault("allow_toggle", True)
            a.setdefault("enabled", True)
            a.setdefault("blocks", [])
            a.setdefault("is_stance", True)

        for s in c.skills:
            if not isinstance(s, dict):
                continue
            s.setdefault("stat", "int")
            s.setdefault("rank", 0)
            s.setdefault("tier", "normal")
            s.setdefault("invested", 0)
            if not isinstance(s.get("mods"), list):
                s["mods"] = []

        for f in c.feats:
            if isinstance(f, dict):
                f.pop("effect", None)
                f.setdefault("display_name", "")
                f.setdefault("is_stance", False)
                if not isinstance(f.get("stance_effects"), list):
                    f["stance_effects"] = []
                if not isinstance(f.get("stance_blocks"), list):
                    f["stance_blocks"] = []
                if not isinstance(f.get("effects"), list):
                    f["effects"] = []

        for w in c.proficiencies.get("weapons", []):
            if isinstance(w, dict):
                w.setdefault("desc", "")
                w.setdefault("difficulty", 1)
                w.setdefault("scale", 1)
                w.setdefault("level", 0)
                w.setdefault("basics", False)
                w.setdefault("bump_applied", 0)
                w.setdefault("basics_invested", 0)
                w.setdefault("bonuses", [])
                w.setdefault("source", "training")
                w.setdefault("invested", 0)
                if not w["difficulty"]:
                    w["difficulty"] = 1
                if not w["scale"]:
                    w["scale"] = 1

        new_quirks = []
        for q in c.quirks:
            if not isinstance(q, dict):
                continue
            if "seed" not in q:
                new_quirks.append({
                    "seed": "", "court": "", "focus": "",
                    "name": q.get("name", ""),
                    "desc": q.get("desc", ""),
                    "source": q.get("source", "quirk")})
            else:
                q.setdefault("court", "")
                q.setdefault("focus", "")
                q.setdefault("name", "")
                q.setdefault("desc", "")
                q.setdefault("source", "quirk")
                new_quirks.append(q)
        c.quirks = new_quirks

        new_attacks = []
        for idx, a in enumerate(c.attacks):
            if not isinstance(a, dict):
                continue
            if "use_bab" not in a:
                new_attacks.append({
                    "name": a.get("name", "?"),
                    "use_bab": False, "stat": None,
                    "damage_stat": None, "damage_mult": 1.0,
                    "damage_stat_auto": False,
                    "finesse": False, "two_handed": False,
                    "ranged": False, "thrown": False,
                    "extra_bonus": 0,
                    "manual_bonus": a.get("bonus", 0),
                    "damage_dice": a.get("damage", ""),
                    "crit_threshold": 20, "crit_mult": 2,
                    "desc": a.get("desc", ""),
                    "source": a.get("source", "training"),
                    "is_maneuver": False,
                    "from_item": None,
                    "proficiency": "",
                    "master_ability": False,
                    "master_ability_id": "",
                    "show_on_panel": False,
                    "uses": False,
                    "uses_max": 0,
                    "uses_current": 0,
                    "tick_on_initiative": False,
                    "tick_mode": "none",
                    "cooldown_rounds": 0,
                    "cooldown_current": 0,
                    "order": idx})
            else:
                use_bab = bool(a.get("use_bab", False))
                a.setdefault("stat", None)
                a.setdefault("damage_stat",
                              (a.get("stat") or "str")
                              if use_bab else None)
                a.setdefault("damage_mult", 1.0)
                a.setdefault("damage_stat_auto", use_bab)
                a.setdefault("finesse", False)
                a.setdefault("two_handed", False)
                a.setdefault("ranged", False)
                a.setdefault("thrown", False)
                a.setdefault("extra_bonus", 0)
                a.setdefault("manual_bonus", 0)
                a.setdefault("damage_dice", "")
                a.setdefault("crit_threshold", 20)
                a.setdefault("crit_mult", 2)
                a.setdefault("source", "training")
                a.setdefault("is_maneuver", False)
                a.setdefault("from_item", None)
                a.setdefault("proficiency", "")
                a.setdefault("master_ability", False)
                a.setdefault("master_ability_id", "")
                a.setdefault("show_on_panel", False)
                a.setdefault("uses", False)
                a.setdefault("uses_max", 0)
                a.setdefault("uses_current", 0)
                a.setdefault("tick_on_initiative", False)
                a.setdefault("tick_mode", "none")
                a.setdefault("cooldown_rounds", 0)
                a.setdefault("cooldown_current", 0)
                a.setdefault("order", idx)
                new_attacks.append(a)
        c.attacks = new_attacks

        for s in c.spells:
            if not isinstance(s, dict):
                continue
            if "masteries" not in s:
                s["masteries"] = []
            old_level = s.get("mastery_level", 0)
            if old_level > 0 and not s["masteries"]:
                for _ in range(old_level):
                    s["masteries"].append({
                        "name": "(старое мастерство)",
                        "desc": "", "stars": 1, "invested": 0,
                        "source": s.get("source", "training")})
            s["mastery_level"] = sum(
                m.get("stars", 1) for m in s["masteries"])
            s["mastery"] = s["mastery_level"] > 0
            s.setdefault("mastery_invested", sum(
                m.get("invested", 0) for m in s["masteries"]))

        # T-EFFECTS-UI: единый шаблон для feats / injuries / abilities.
        for _coll in (c.feats, c.injuries,
                      c.char_class.get("abilities", []),
                      c.race.get("abilities", [])):
            for _obj in _coll:
                apply_effects_defaults(_obj)
        # T-EFFECTS-UI: единый шаблон для feats / injuries / abilities.
        for _coll in (c.feats, c.injuries,
                      c.char_class.get("abilities", []),
                      c.race.get("abilities", [])):
            for _obj in _coll:
                apply_effects_defaults(_obj)
        c._sync_item_bonuses()
        c.recompute_derived()
        return c


if __name__ == "__main__":
    ensure_dirs()
    g = Character("Тест")
    g.char_class = {"name": "Воин", "level": 5, "hp_die": 10,
                    "hp_rolls": [10, 7, 8, 6, 9], "abilities": [],
                    "has_spellbook": False, "spell_discount_extra": 0,
                    "bab_type": "good", "good_saves": ["fort"]}
    g.abilities = {"str": 16, "dex": 14, "con": 12,
                   "int": 10, "wis": 12, "cha": 10}
    g.proficiencies["armor"] = "Medium"
    g.proficiencies["shields"] = "Tower"
    g.init_defaults()

    print("=== Тест v12 ===")
    print(f"Каталогов оружия: {len(WEAPON_GROUP_CATALOG)}")
    print(f"Каталогов брони: {len(ARMOR_CATALOG)}")
    print(f"Каталогов щитов: {len(SHIELD_CATALOG)}")

    # Броня
    g.add_item(name="Кольчуга", category="armor",
                location="equipped", slot="armor",
                armor_type="Medium", ac_bonus=6, ac_max_dex=2,
                weight=2, weight_type="mass", speed_penalty=5)
    print(f"AC full: {g.ac_full()}")

    # Обычный меч
    sword = g.add_item(
        name="Длинный меч", category="weapon",
        location="equipped", slot="weapon_main",
        damage="1d8", crit_threshold=19, crit_mult=2,
        attack_bonus=0, damage_bonus=0,
        weight=1, weight_type="mass")
    atk = g.attack_from_item(sword["id"], name="Длинный меч")
    print(f"Атака мечом: {g.attack_bonus(atk):+d}, "
          f"урон мод: {g.attack_damage_bonus(atk):+d}")

    # Двуручный меч (×1.5)
    greatsword = g.add_item(
        name="Двуручный меч", category="weapon",
        location="bag", slot=None,
        damage="2d6", two_handed=True,
        weight=2, weight_type="mass")
    atk2 = g.attack_from_item(greatsword["id"])
    print(f"Атака двуручником: мод {g.attack_damage_bonus(atk2):+d} "
          f"(СИЛ 16 = +3 ×1.5 = +4)")

    # Лук (ranged) — без мода стата к урону
    bow = g.add_item(
        name="Короткий лук", category="weapon",
        location="equipped", slot="weapon_main",
        damage="1d6", ranged=True, range_ft=60,
        two_handed=True, required_level=3)
    atk3 = g.attack_from_item(bow["id"])
    print(f"Атака луком: урон мод {g.attack_damage_bonus(atk3)} "
          f"(должно 0), range {g.attack_range(atk3)}")

    # Метательный нож (thrown) — с модом СИЛ
    dagger = g.add_item(
        name="Метательный нож", category="weapon",
        location="bag", slot=None,
        damage="1d4", thrown=True, range_ft=20,
        finesse=True, required_level=3)
    atk4 = g.attack_from_item(dagger["id"])
    print(f"Атака ножом (thrown): урон мод "
          f"{g.attack_damage_bonus(atk4)}, range {g.attack_range(atk4)}")

    print("\n=== OK ===")