# gui_alphabet.py — единый словарь названий целей (target) для GUI.
# Только для ОТОБРАЖЕНИЯ. Логика — в character.VALID_SIT_TARGETS.
# Правило: set(TARGET_NAMES) == character.VALID_SIT_TARGETS.
# Если это не так — assert упадёт при импорте (защита от рассинхрона).

from character import VALID_SIT_TARGETS, ITEM_CATEGORIES


TARGET_NAMES = {
    "attack": "атаки",
    "damage": "урон",
    "save": "спасбр",
    "skill": "навыки",
    "ac": "AC",
    "fort": "Fort",
    "ref": "Ref",
    "will": "Will",
    "speed": "скорость+",
    "speed_mult": "скорость×",
    "str": "СИЛ",
    "dex": "ЛОВ",
    "con": "ТЕЛ",
    "int": "ИНТ",
    "wis": "МДР",
    "cha": "ХАР",
    "lucky": "счастливая",
    "hp_temp": "врем. HP",
    "restore_hp": "восст. HP",
    "restore_mana": "восст. маны",
    "restore_spirit": "восст. духа",
    "restore_balance": "восст. баланса",
    "restore_resource": "восст. ресурса",
    "self_damage_per_tick": "урон/тик",
    "cmb": "CMB",
    "cmd": "CMD",
    "initiative": "инициатива",
    "max_hp": "макс HP",
    "max_mana": "макс мана",
    "max_balance": "макс баланс",
    "max_spirit": "макс дух",
    "max_resource": "макс ресурс",
    "max_pain_threshold": "макс БП",
}

# Защита от рассинхрона: словарь обязан совпадать с ядром логики.
assert set(TARGET_NAMES) == VALID_SIT_TARGETS, (
    "gui_alphabet.TARGET_NAMES рассинхронизирован с "
    "character.VALID_SIT_TARGETS.\n"
    f"Только в словаре: {set(TARGET_NAMES) - VALID_SIT_TARGETS}\n"
    f"Только в ядре:    {VALID_SIT_TARGETS - set(TARGET_NAMES)}"
)


# T-P2: единый словарь категорий предметов (только отображение).
# Используется в pdf_export, gui_inventory, gui_shop, gui_catalogs.
CATEGORY_NAMES = {
    "armor":        "Броня / Одежда",
    "shield":       "Щит",
    "weapon":       "Оружие",
    "belt":         "Пояс",
    "body":         "Тело",
    "chest":        "Грудь",
    "eyes":         "Глаза",
    "gloves":       "Перчатки",
    "head":         "Голова",
    "neck":         "Шея",
    "ring":         "Кольцо",
    "back":         "Спина",
    "shoulders":    "Плечи",
    "legs":         "Ноги",
    "feet":         "Ступни",
    "companion":    "Спутник",
    "pet":          "Питомец",
    "modifier":     "Модификатор",
    "tools_craft":  "Инструменты ремесленные",
    "tools_travel": "Инструменты походные",
    "components":   "Магические компоненты",
    "holy_symbol":  "Предмет поклонения",
    "unload":       "Разгрузка",
    "consumable":   "Расходник",
    "misc":         "Разное",
}
# Защита от рассинхрона: категории обязаны совпадать с ядром.
assert set(CATEGORY_NAMES) == set(ITEM_CATEGORIES), (
    "gui_alphabet.CATEGORY_NAMES рассинхронизирован с "
    "character.ITEM_CATEGORIES.\n"
    f"Только в словаре: {set(CATEGORY_NAMES) - set(ITEM_CATEGORIES)}\n"
    f"Только в ядре:    {set(ITEM_CATEGORIES) - set(CATEGORY_NAMES)}"
)

# T-BONUS-TYPES-2 (v18.4): русские подписи типов бонусов (только отображение).
BONUS_TYPE_NAMES = {
    "flat":         "Без типа",
    "alchemical":   "Алхимический",
    "armor":        "Доспех",
    "circumstance": "Обстоятельства",
    "competence":   "Компетентность",
    "deflection":   "Отражение",
    "dodge":        "Уклонение",
    "enhancement":  "Усиление",
    "inherent":     "Врождённый",
    "insight":      "Предвидение",
    "luck":         "Удача",
    "morale":       "Мораль",
    "natural":      "Натуральный",
    "profane":      "Нечестивый",
    "racial":       "Расовый",
    "resistance":   "Сопротивление",
    "sacred":       "Священный",
    "shield":       "Щит",
    "size":         "Размер",
    "trait":        "Черта",
}
# Защита от рассинхрона с modifiers.BONUS_TYPES.
try:
    from modifiers import BONUS_TYPES as _BONUS_TYPES
except ImportError:
    from DND.modifiers import BONUS_TYPES as _BONUS_TYPES
assert set(BONUS_TYPE_NAMES) == set(_BONUS_TYPES), (
    "gui_alphabet.BONUS_TYPE_NAMES рассинхронизирован с "
    "modifiers.BONUS_TYPES.\n"
    f"Только в словаре: {set(BONUS_TYPE_NAMES) - set(_BONUS_TYPES)}\n"
    f"Только в ядре:    {set(_BONUS_TYPES) - set(BONUS_TYPE_NAMES)}"
)