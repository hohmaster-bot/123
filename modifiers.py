# modifiers.py — единственный источник правды для барабанов бонусов.
# T-BONUS-TYPES-2 (v18.4)
#
# Правила:
#   - flat / ""  → складывается всегда.
#   - dodge      → складывается (как flat), ограничен ac_max_dex (см. character.dex_bonus_for_ac).
#   - остальные  → «побеждает больший по модулю» (bonus_max vs penalty_max), равны → 0.
#   - неизвестный тип → flat.
#
# ВАЖНО: это ЧИСТЫЕ функции. Никаких импортов из character.py (циклический импорт).
# character.py импортирует ОТСЮДА.

# 20 типов бонусов PF1.
BONUS_TYPES = {
    "flat", "alchemical", "armor", "circumstance", "competence",
    "deflection", "dodge", "enhancement", "inherent", "insight",
    "luck", "morale", "natural", "profane", "racial",
    "resistance", "sacred", "shield", "size", "trait",
}

# flat и пустая строка — одно и то же (складываются).
BONUS_TYPES_FLAT = {"flat", ""}

# «Барабан бросков»: атака, урон, спасброски, инициатива, навыки, CMB.
# Без armor/deflection/dodge/natural/shield.
BONUS_TYPES_ROLL = BONUS_TYPES - {
    "armor", "deflection", "dodge", "natural", "shield",
}

# «Барабан статичных защит» (CMD): без armor/shield/natural/resistance.
BONUS_TYPES_CMD = BONUS_TYPES - {
    "armor", "shield", "natural", "resistance",
}

# AC touch: только эти типы.
AC_TOUCH_TYPES = {
    "flat", "deflection", "dodge", "insight", "morale",
    "competence", "luck", "circumstance",
}

# AC flat-footed: все, кроме dodge (dodge теряется без dex).
AC_FLAT_TYPES = BONUS_TYPES - {"dodge"}

# AC parry: все, кроме armor (вместо armor — parrying).
AC_PARRY_TYPES = BONUS_TYPES - {"armor"}

# AC full: все 20.
AC_FULL_TYPES = set(BONUS_TYPES)

# Устаревший список (T-BONUS-TYPES v18.2). Оставлен для совместимости.
# character.py может использовать как алиас AC_FULL_TYPES.
AC_TYPES_NON_STACK = [
    "armor", "shield", "natural", "deflection",
    "insight", "morale", "competence", "luck", "circumstance",
]


def _normalize_type(btype):
    """Привести bonus_type к нижнему регистру; пусто/None → 'flat'."""
    if not btype:
        return "flat"
    t = str(btype).strip().lower()
    if t in BONUS_TYPES_FLAT:
        return "flat"
    if t not in BONUS_TYPES:
        return "flat"  # неизвестный → flat (A13)
    return t


def apply_bonus_type(bonuses, allowed=None, denied=None):
    """Универсальный барабан.

    bonuses: list[dict] — каждый {"value": int|float, "type": str}.
    allowed: set[str] | None — если задан, типы вне allowed игнорируются.

    Правила:
      flat/""  → сумма (складывается всегда).
      dodge    → сумма (складывается; cap на ac_max_dex — в character.py).
      остальные:
        bonus_max   = max(+) этого типа (0, если нет)
        penalty_max = max(|−|) этого типа (0, если нет)
        если bonus_max > penalty_max   → +bonus_max
        если penalty_max > bonus_max   → −penalty_max
        если равны                      → 0
        (то есть побеждает больший по модулю, равные — взаимоуничтожаются)

    Возвращает int.
    """
    flat_total = 0
    # Для каждого типа: (max_positive, max_abs_negative)
    groups = {}

    for b in bonuses or []:
        if not isinstance(b, dict):
            continue
        try:
            v = b.get("value", 0)
            v = float(v) if v is not None else 0.0
        except (TypeError, ValueError):
            v = 0.0
        t = _normalize_type(b.get("type", "flat"))
        if allowed is not None and t not in allowed:
            continue
        if denied is not None and t in denied:
            continue
        if t == "flat":
            flat_total += v
        elif t == "dodge":
            # dodge складывается (как flat), но ограничен ac_max_dex в character.py
            flat_total += v
        else:
            pos, neg = groups.get(t, (0.0, 0.0))
            if v >= 0:
                pos = max(pos, v)
            else:
                neg = max(neg, abs(v))
            groups[t] = (pos, neg)

    total = flat_total
    for t, (pos, neg) in groups.items():
        if pos > neg:
            total += pos
        elif neg > pos:
            total -= neg
        # равно → 0
    return int(total)


def size_mod(size):
    """Размер → модификатор CMB/CMD.
    Medium = 0; Large = +1; Huge = +2; Gargantuan = +4; Colossal = +8.
    Fine = −8; Diminutive = −4; Tiny = −2; Small = −1.

    Для атак знак ОБРАТНЫЙ (size_mod_attack = −size_mod).
    """
    order = ["Fine", "Diminutive", "Tiny", "Small", "Medium",
             "Large", "Huge", "Gargantuan", "Colossal"]
    values = {"Fine": -8, "Diminutive": -4, "Tiny": -2, "Small": -1,
              "Medium": 0, "Large": 1, "Huge": 2,
              "Gargantuan": 4, "Colossal": 8}
    return values.get(size, 0)


def size_mod_attack(size):
    """Модификатор атаки от размера (обратный CMB/CMD)."""
    return -size_mod(size)

# ============ T-EFFECTS-UI: единый шаблон ============

EFFECTS_DEFAULTS = {
    "effects": [],
    "on_activate_effects": [],
    "duration_rounds": 0,
    "duration_current": 0,
    "charges_max": 0,
    "charges_current": 0,
    "charges_tick_mode": "none",
    "cooldown_rounds": 0,
    "cooldown_current": 0,
    "tick_mode": "none",
    "tick_on_initiative": True,
    "permanent": True,
    "keep_at_zero": True,
    "is_buff": True,
    "show_on_panel": True,
    "allow_toggle": True,
    "enabled": True,
    "blocks": [],
    "is_stance": True,
}


def apply_effects_defaults(obj):
    """T-EFFECTS-UI: единый шаблон для feats / injuries / abilities.
    Мутирует obj (dict). Возвращает obj."""
    if not isinstance(obj, dict):
        return obj
    for key, default in EFFECTS_DEFAULTS.items():
        if key in ("effects", "on_activate_effects", "blocks"):
            if not isinstance(obj.get(key), list):
                obj[key] = list(default)
        else:
            obj.setdefault(key, default)
    return obj