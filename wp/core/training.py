"""Training purchases (RULES/training.md, progression.md, gear.md base, resources.md comfort).

Only source = training spends training points; race/class/loot/quirk/template never do.
"""
from wp.core.derived import ability_mod

TRAINING = "training"

START_TRAINING = 1000
ABILITY_STEP = 150
SHIELD_GRADE_COST = 100
ARMOR_GRADE_COST = 250
SHIELD_GRADES = ("none", "light", "heavy", "tower")
ARMOR_GRADES = ("none", "light", "medium", "heavy")
BASE_SLOT_COST = 100
HP_POINT_COST = 50          # max HP +1 (hit-die HP, up to die * level)
BASE_START = 5
LANG_NON_NATIVE = 30
LANG_NATIVE_CHEAP = 50
LANG_NATIVE_EXPENSIVE = 100


def pay(available, cost, source=TRAINING):
    """New training balance. Non-training sources never spend points."""
    cost = int(cost)
    if source != TRAINING or cost <= 0:
        return available
    if cost > available:
        raise ValueError("not enough training: need %d, have %d" % (cost, available))
    return available - cost


# ---------------------------------------------------------------- abilities

def price_score(base, race_bonus=0):
    """Score used for pricing = base + race bonus (items, quirks do not count)."""
    return int(base) + int(race_bonus)


def ability_step_cost(base, race_bonus=0):
    """Cost of +1 = 150 * max(1, NEW modifier)."""
    return ABILITY_STEP * max(1, ability_mod(price_score(base, race_bonus) + 1))


def ability_cost(base, race_bonus, steps):
    """Cost of several +1 steps in a row."""
    total = 0
    for i in range(int(steps)):
        total += ability_step_cost(int(base) + i, race_bonus)
    return total


# ---------------------------------------------------------------- languages

def native_language_cost(natives, int_mod):
    """First native free; cheap (50) while natives < Int MODIFIER, else 100."""
    if natives <= 0:
        return 0
    return LANG_NATIVE_CHEAP if natives < int(int_mod) else LANG_NATIVE_EXPENSIVE


def language_cost(native, natives=0, int_mod=0, projects=1):
    """Non-native: 30 * number of projects (steps) from the nearest native language (training.md)."""
    if native:
        return native_language_cost(natives, int_mod)
    if int(projects) < 1:
        raise ValueError("projects from the nearest native language must be >= 1")
    return LANG_NON_NATIVE * int(projects)


# ------------------------------------------------------------ armor, shield

def grade_cost(grades, current, step_cost):
    """Cost of the next grade; ValueError at max."""
    i = grades.index(current)
    if i >= len(grades) - 1:
        raise ValueError("already at max grade")
    return step_cost


def shield_grade_cost(current):
    return grade_cost(SHIELD_GRADES, current, SHIELD_GRADE_COST)


def armor_grade_cost(current):
    return grade_cost(ARMOR_GRADES, current, ARMOR_GRADE_COST)


# --------------------------------------------------------------------- base

def base_max(level):
    return 10 * int(level)


def base_slot_cost(slots, level):
    """100 per slot; start 5, max 10 * level."""
    if slots >= base_max(level):
        raise ValueError("base is at max (%d)" % base_max(level))
    return BASE_SLOT_COST


# ------------------------------------------------------------ training gain

def level_up_training(new_level):
    """Training gained at level-up = 100 * new level."""
    return 100 * int(new_level)


def comfort_max(level, bonus=0):
    """Comfort max = 5 + 5 * level, modifiable by class/race/items."""
    return 5 + 5 * int(level) + int(bonus)


def comfort_rate(level, bonus=0):
    """1 comfort = 5 + 5 * level training (training.md); item/class bonuses change it."""
    return 5 + 5 * int(level) + int(bonus)


def comfort_to_training(points, level, bonus=0):
    """Training for spent comfort."""
    return int(points) * comfort_rate(level, bonus)


# --------------------------------------------------------- attention course

def _tenths(x):
    return round(float(x), 1)


def attention_comfort_equivalent(dex_mod):
    """Option 2: training as if spending comfort = Dex mod / 2, min 1, tenths."""
    return max(1.0, _tenths(int(dex_mod) / 2.0))


def attention_base_points(attention, int_mod):
    """Option 4: 0.2 * Int mod base points per attention, min 0.4; fractions kept."""
    per = max(0.4, _tenths(0.2 * int(int_mod)))
    return _tenths(per * int(attention))


def professionalism_ok(new_level, char_level):
    """Professionalism level cannot exceed character level."""
    return int(new_level) <= int(char_level)
