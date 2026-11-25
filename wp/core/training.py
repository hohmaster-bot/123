"""Training purchases (RULES/training.md, progression.md, gear.md base, resources.md comfort).

Only source = training spends training points; race/class/loot/quirk/template never do.
"""
from wp.core.derived import ability_mod
from wp.rules_data import rules as rd

# rule numbers that were inline literals (package 20: data, wp/rules_data/constants.json)
BASE_MAX_PER_LEVEL = rd.ref("training.base_max_per_level")   # max base slots = this * level
COMFORT_MAX_BASE = rd.ref("training.comfort_max_base")   # comfort max = base + per_level * level
COMFORT_MAX_PER_LEVEL = rd.ref("training.comfort_max_per_level")   # comfort max per level
COMFORT_RATE_BASE = rd.ref("training.comfort_rate_base")   # 1 comfort = base + per_level * level training
COMFORT_RATE_PER_LEVEL = rd.ref("training.comfort_rate_per_level")   # comfort rate per level
ATTENTION_COMFORT_MIN = rd.ref("training.attention_comfort_min")   # attention option 2: at least this
ATTENTION_COMFORT_DIVISOR = rd.ref("training.attention_comfort_divisor")   # attention option 2: Dex mod divided by
TENTHS = rd.ref("training.tenths_per_point")   # tenths in one base point

TRAINING = "training"

START_TRAINING = rd.ref("training.start")
ABILITY_STEP = rd.ref("training.ability_step")
SHIELD_GRADE_COST = rd.ref("training.shield_grade_cost")
ARMOR_GRADE_COST = rd.ref("training.armor_grade_cost")
SHIELD_GRADES = ("none", "light", "heavy", "tower")
ARMOR_GRADES = ("none", "light", "medium", "heavy")
BASE_SLOT_COST = rd.ref("training.base_slot_cost")
HP_POINT_COST = rd.ref("training.hp_point_cost")  # max HP +1 (hit-die HP, up to die * level)
BASE_START = rd.ref("training.base_start")
LANG_NON_NATIVE = rd.ref("training.language_non_native")
LANG_NATIVE_CHEAP = rd.ref("training.language_native_cheap")
LANG_NATIVE_EXPENSIVE = rd.ref("training.language_native_expensive")
# package 15 (training.md "Other purchases", progression.md, spells.md): the rule constants of the purchase commands
LEVEL_UP_PER_LEVEL = rd.ref("training.level_up_per_level")  # training at level-up = 100 * new level
REACTION_STEP = rd.ref("training.reaction_step")  # +1 reaction = 200 * the new number of reactions
SEED_COST = rd.ref("training.seed_cost")  # new seed
SPROUT_COST = rd.ref("training.sprout_cost")  # sprout a seed
ATTENTION_COURSE_COST = rd.ref("training.attention_course_cost")  # attention course +1
MANEUVER_COST = rd.ref("training.maneuver_cost")  # new combat maneuver
QUALIFICATION_STEP = rd.ref("training.qualification_step")  # item qualification = 50 * N
PROFESSIONALISM_COST = rd.ref("training.professionalism_cost")
PROFESSIONALISM_SKILLS = rd.ref("training.professionalism_skills")  # class skill points 8+ / 6+ / 4+ / 2+ -> specialized skills
SPELL_BASE = rd.ref("training.spell_base")  # new spell = 20 + 10 * circle^2
SPELL_PER_CIRCLE_SQ = rd.ref("training.spell_per_circle_sq")
SPELL_DISCOUNT_DIVISOR = rd.ref("training.spell_discount_divisor")  # book / teacher / scroll classes: half price
MASTERY_BASE = rd.ref("training.mastery_base")  # spell upgrade = 25 * (1 + circle^2)
MASTERY_SLOTS = rd.ref("training.mastery_slots")  # three upgrade slots per spell


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
    return BASE_MAX_PER_LEVEL * int(level)


def base_slot_cost(slots, level):
    """100 per slot; start 5, max 10 * level."""
    if slots >= base_max(level):
        raise ValueError("base is at max (%d)" % base_max(level))
    return BASE_SLOT_COST


# ------------------------------------------------------------ training gain

def level_up_training(new_level):
    """Training gained at level-up = 100 * new level."""
    return LEVEL_UP_PER_LEVEL * int(new_level)


def comfort_max(level, bonus=0):
    """Comfort max = 5 + 5 * level, modifiable by class/race/items."""
    return COMFORT_MAX_BASE + COMFORT_MAX_PER_LEVEL * int(level) + int(bonus)


def comfort_rate(level, bonus=0):
    """1 comfort = 5 + 5 * level training (training.md); item/class bonuses change it."""
    return COMFORT_RATE_BASE + COMFORT_RATE_PER_LEVEL * int(level) + int(bonus)


def comfort_to_training(points, level, bonus=0):
    """Training for spent comfort."""
    return int(points) * comfort_rate(level, bonus)


# --------------------------------------------------------- attention course

def _tenths(x):
    return round(float(x), 1)


def attention_comfort_equivalent(dex_mod):
    """Option 2: training as if spending comfort = Dex mod / 2, min 1, tenths."""
    return max(float(ATTENTION_COMFORT_MIN), _tenths(int(dex_mod) / float(ATTENTION_COMFORT_DIVISOR)))


def attention_base_points(attention, int_mod):
    """Option 4: 0.2 * Int mod base points per attention, min 0.4; fractions kept."""
    per = max(BASE_POINT_TENTHS_MIN / TENTHS, _tenths(BASE_POINT_TENTHS_PER_INT / TENTHS * int(int_mod)))
    return _tenths(per * int(attention))


BASE_POINT_TENTHS_PER_INT = rd.ref("training.base_point_tenths_per_int")  # option 4: 0.2 * Int mod per attention = 2 tenths per Int mod
BASE_POINT_TENTHS_MIN = rd.ref("training.base_point_tenths_min")  # minimum 0.4 per attention


def attention_base_tenths(attention, int_mod):
    """Option 4 in TENTHS of a base point (integers, fractions never lost): per attention max(4, 2 * Int mod)."""
    return max(BASE_POINT_TENTHS_MIN, BASE_POINT_TENTHS_PER_INT * int(int_mod)) * int(attention)


def professionalism_ok(new_level, char_level):
    """Professionalism level cannot exceed character level."""
    return int(new_level) <= int(char_level)


# ------------------------------------------------------------ package 15 prices

def reaction_cost(current):
    """+1 reaction = 200 * the NEW number of reactions (1 reaction -> the 2nd costs 400)."""
    return REACTION_STEP * (int(current) + 1)


def qualification_cost(n):
    """Item qualification = 50 * N (N = the number written on the item)."""
    return QUALIFICATION_STEP * int(n)


SPELL_MIN_PRICE = rd.ref("training.spell_min_price")


def spell_cost(circle, discount=False, minus=0):
    """New spell = 20 + 10 * circle^2; book / teacher / scroll classes pay half, rounded down (circle 2 -> 60, 30);
    then minus `minus` (effects "spell_price_discount", package 16 G5); never below 1."""
    c = int(circle)
    cost = SPELL_BASE + SPELL_PER_CIRCLE_SQ * c * c
    cost = cost // SPELL_DISCOUNT_DIVISOR if discount else cost
    return max(int(SPELL_MIN_PRICE), cost - max(0, int(minus)))


def mastery_cost(circle):
    """One spell upgrade = 25 * (1 + circle^2) (circle 2 -> 125)."""
    c = int(circle)
    return MASTERY_BASE * (1 + c * c)


def professionalism_skills(class_skill_points):
    """How many class skills become specialized: 2+ -> 1, 4+ -> 2, 6+ -> 3, 8+ -> 4; below 2 -> 0."""
    for need, n in PROFESSIONALISM_SKILLS:
        if int(class_skill_points) >= need:
            return n
    return 0
