"""Derived values, computed on read, never stored (D6, D18).

Rules: RULES/rest.md (BP, balance), RULES/resources.md (pain from HP),
RULES/defense.md (morale), RULES/gear.md (load thresholds).
"""

# Load: thresholds are stored in L (1 B = 10 L). Base light 0-5.9 B, heavy to 10.9 B.
LIGHT_MAX_BASE_L = 59
HEAVY_MAX_BASE_L = 109
L_PER_B = 10

MORALE_MIN = -10
MORALE_MAX = 10

PAIN_HP_STEP = 3

LOAD_LIGHT = "light"
LOAD_HEAVY = "heavy"
LOAD_OVER = "overload"


def ability_mod(score):
    """Pathfinder ability modifier: floor((score - 10) / 2)."""
    return (int(score) - 10) // 2


def bp_cap(max_hp):
    """BP cap = ceil(max HP / 4). rest.md: 11->3, 15->4, 19->5, 20->5, 21->6."""
    max_hp = int(max_hp)
    if max_hp <= 0:
        return 0
    return -(-max_hp // 4)


def balance_max(armor_bonus, bp_current, bonuses=0):
    """Balance max = worn armor bonus + CURRENT BP + bonuses (race, class, other).

    armor_bonus must be the worn armor bonus only: parry gives no balance.
    Spending BP lowers balance max (rest.md note). No clamp: RULES give none.
    """
    return int(armor_bonus) + int(bp_current) + int(bonuses)


def balance_regen(level, con_mod, other=0):
    """Balance restored per zero-initiative tick: level + Con mod + other, min 1."""
    return max(1, int(level) + int(con_mod) + int(other))


def pain_from_hp(hp):
    """Temp pain from negative HP: floor(-hp / 3) when hp < 0, else 0."""
    hp = int(hp)
    if hp >= 0:
        return 0
    return (-hp) // PAIN_HP_STEP


def morale_bonus(scale, combat_active=True):
    """Morale bonus = trunc(scale / 2), scale clamped to -10..10.

    Morale counts only while combat is active (defense.md).
    """
    if not combat_active:
        return 0
    scale = max(MORALE_MIN, min(MORALE_MAX, int(scale)))
    # int() truncates toward zero; // would floor (-3 // 2 == -2, wrong).
    return int(scale / 2)


def load_thresholds_l(str_mod):
    """(light max, heavy max) in L. Both shift by Str MODIFIER, 1 B per point."""
    shift = int(str_mod) * L_PER_B
    return LIGHT_MAX_BASE_L + shift, HEAVY_MAX_BASE_L + shift


def load_status(weight_l, str_mod):
    """'light' up to light max, 'heavy' up to heavy max, else 'overload'."""
    light, heavy = load_thresholds_l(str_mod)
    if weight_l <= light:
        return LOAD_LIGHT
    if weight_l <= heavy:
        return LOAD_HEAVY
    return LOAD_OVER
