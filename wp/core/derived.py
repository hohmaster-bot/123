"""Derived values, computed on read, never stored (D6, D18).

Rules: RULES/rest.md (BP, balance), RULES/resources.md (pain from HP),
RULES/defense.md (morale), RULES/gear.md (load thresholds).
"""
from wp.rules_data import rules as rd

# rule numbers that were inline literals (package 20: data, wp/rules_data/constants.json)
ABILITY_MOD_BASE = rd.ref("ability.mod_base")   # modifier = (score - base) // divisor
ABILITY_MOD_DIVISOR = rd.ref("ability.mod_divisor")   # modifier divisor
BP_CAP_DIVISOR = rd.ref("bp.cap_divisor")   # BP cap = ceil(max HP / this)
MORALE_DIVISOR = rd.ref("morale.divisor")   # morale bonus = trunc(scale / this)

# Load: thresholds are stored in L (1 B = 10 L). Base light 0-5.9 B, heavy to 10.9 B.
LIGHT_MAX_BASE_L = rd.ref("load.light_max_l")
HEAVY_MAX_BASE_L = rd.ref("load.heavy_max_l")
L_PER_B = rd.ref("load.l_per_b")

MORALE_MIN = rd.ref("morale.scale_min")
MORALE_MAX = rd.ref("morale.scale_max")

PAIN_HP_STEP = rd.ref("pain.hp_step")

LOAD_LIGHT = "light"
LOAD_HEAVY = "heavy"
LOAD_OVER = "overload"


def ability_mod(score):
    """Pathfinder ability modifier: floor((score - 10) / 2)."""
    return (int(score) - ABILITY_MOD_BASE) // ABILITY_MOD_DIVISOR


def bp_cap(max_hp):
    """BP cap = ceil(max HP / 4). rest.md: 11->3, 15->4, 19->5, 20->5, 21->6."""
    max_hp = int(max_hp)
    if max_hp <= 0:
        return 0
    return -(-max_hp // BP_CAP_DIVISOR)


def bp_cap_from_hp(hp_pool):
    """BP cap for an HP pool: always from MAX HP, never from current HP."""
    return bp_cap(hp_pool.max)


def balance_max(armor_bonus, bp_current, bonuses=0):
    """Balance max = worn armor bonus + CURRENT BP + bonuses (race, class, other).

    armor_bonus must be the worn armor bonus only: parry gives no balance.
    Spending BP lowers balance max (rest.md note). Never below 0 (owner).
    """
    return max(0, int(armor_bonus) + int(bp_current) + int(bonuses))


def balance_regen(level, con_mod, other=0):
    """Balance restored per zero-initiative tick: level + Con mod + other, min 1."""
    return max(1, int(level) + int(con_mod) + int(other))


def pain_from_hp(hp):
    """Temp pain from negative HP: floor(-hp / 3) when hp < 0, else 0."""
    hp = int(hp)
    if hp >= 0:
        return 0
    return (-hp) // PAIN_HP_STEP


# Size (combat.md "Size and speed", package 11 C): small / medium / large only.
SIZES = ("small", "medium", "large")
SIZE_MOD = rd.ref("size.attack_ac")  # attack and AC
SIZE_CMB = rd.ref("size.cmb_cmd")  # CMB and CMD (opposite sign)
BASE_SPEED_FT = rd.ref("speed.base_ft")
OVERLOAD_SPEED_FT = rd.ref("speed.encumbrance_ft")  # gear.md: overload -10 ft


def size_mod(size):
    return rd.value(SIZE_MOD)[size]


def size_cmb(size):
    return rd.value(SIZE_CMB)[size]


def armor_slowdown(penalty_ft, reduction=0):
    """Armor slowdown after reductions, never below 0 (gear.md, package 12)."""
    return max(0, int(penalty_ft) - max(0, int(reduction)))


def speed(base_ft, bonus_ft=0, overloaded=False, slowdown_ft=0):
    """Speed in feet = base + typed bonuses (target "speed") - armor slowdown, overload -10 ft."""
    return int(base_ft) + int(bonus_ft) - int(slowdown_ft) + (OVERLOAD_SPEED_FT if overloaded else 0)


def morale_bonus(scale, combat_active=True):
    """Morale bonus = trunc(scale / 2), scale clamped to -10..10.

    Morale counts only while combat is active (defense.md).
    """
    if not combat_active:
        return 0
    scale = max(MORALE_MIN, min(MORALE_MAX, int(scale)))
    # int() truncates toward zero; // would floor (-3 // 2 == -2, wrong).
    return int(scale / MORALE_DIVISOR)


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
