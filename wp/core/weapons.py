"""Weapon proficiency (mastery): RULES/weapons.md, combat.md "Crit" / "Lucky attack".

Levels 0-12. Cost of +1 grade = (30 + 5X) * difficulty * scale, X = number of OTHER
weapons at level 8+. Combat basics: 50/100/150 for scale 1/2/3, +(5 - difficulty)
grades, never stacking: the weapon gets the MAX basics bump over itself and all
its ancestors (a weapon lists its parents; a variety may sit in several groups).
Bonus picks: specialist slots 5-7, expert 8-11, master 12, with repeat limits.
Mastery bonuses add as FLAT to AC (parry), attack, damage and change the FINAL
durability and HP of the item.
"""
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from wp.rules_data import rules as rd

# rule numbers that were inline literals (package 20: data, wp/rules_data/constants.json)
BASICS_COST = rd.ref("weapons.basics_cost")   # combat basics for scale 1 / 2 / 3
BASICS_RAISE_BASE = rd.ref("weapons.basics_raise_base")   # combat basics raise = this - difficulty
GRADE_COST_BASE = rd.ref("weapons.grade_cost_base")   # grade cost = (base + per_expert * X) * difficulty * scale
GRADE_COST_PER_EXPERT = rd.ref("weapons.grade_cost_per_expert")   # grade cost per OTHER group at expert+
REPEAT_SECOND = rd.ref("weapons.repeat_second")   # second pick of the same bonus
REPEAT_THIRD = rd.ref("weapons.repeat_third")   # third pick of the same bonus
DAMAGE_PICK = rd.ref("weapons.damage_pick")   # damage per 'damage +3' pick
RANGE_PICK_FT = rd.ref("weapons.range_pick_ft")   # range per 'range +10 ft' pick
DURABILITY_SPEC_PCT = rd.ref("weapons.durability_specialist_pct")   # hardness per specialist pick
DURABILITY_EXPERT_PCT = rd.ref("weapons.durability_expert_pct")   # hardness per expert pick
D20 = rd.ref("dice.d20_faces")   # the d20 (crit base range 20+)
KEEN_MULTIPLIER = rd.ref("weapons.keen_multiplier")   # keen multiplies the BASE crit range

MAX_LEVEL = rd.ref("weapons.max_level")
LEVEL_NAMES = {
    0: "none", 1: "Novice", 2: "Apprentice", 3: "Amateur", 4: "Skilled",
    5: "Specialist I", 6: "Specialist II", 7: "Specialist III",
    8: "Expert I", 9: "Expert II", 10: "Expert III", 11: "Expert IV", 12: "Master",
}
EXPERT_LEVEL = rd.ref("weapons.expert_level")

SPEC, EXPERT, MASTER = "specialist", "expert", "master"
SPEC_SLOTS = rd.ref("weapons.specialist_slots")
EXPERT_SLOTS = rd.ref("weapons.expert_slots")
MASTER_SLOT = rd.ref("weapons.master_slot")

# bonus id -> tier (weapons.md "Bonuses by tier")
BONUS_TIER = {
    "parry_1": SPEC, "durability_30": SPEC, "attack_1": SPEC, "crit_1": SPEC,
    "range_10": SPEC, "balance_regen_1": SPEC,
    "hp_1": EXPERT, "durability_70": EXPERT, "damage_3": EXPERT, "ignore_vulnerability": EXPERT,
    "ignore_cover_20": EXPERT, "lucky_1": EXPERT, "parry_ranged": EXPERT,
    "reroll_d20": MASTER, "no_attack_tag": MASTER, "restore_balance": MASTER,
}

QUALIFIED = rd.ref("weapons.qualified_penalty")
ONE_BELOW_PENALTY = rd.ref("weapons.one_below_penalty")
NOT_QUALIFIED_PENALTY = rd.ref("weapons.not_qualified_penalty")
LUCKY_BASE = rd.ref("weapons.lucky_base")
LUCKY_MASTERY_MAX = rd.ref("weapons.lucky_mastery_max")
MIN_THRESHOLD = rd.ref("weapons.min_threshold")


@dataclass(frozen=True)
class Weapon:
    name: str
    scale: int = 1               # 1 named weapon, 2 variety, 3 group
    difficulty: int = 1
    grades: int = 0              # grades bought with training (not basics)
    basics: bool = False         # combat basics bought on this node
    parents: Tuple[str, ...] = ()
    required_level: int = 0      # qualification level of the weapon
    basic: bool = False          # group "Basic/simple": no qualification, cannot be trained


@dataclass(frozen=True)
class Pick:
    slot: int                    # 5..12
    bonus: str
    used: int = 0                # once-per-combat picks (COUNTER_PICKS): 1 = spent this combat (package 17)


# Mastery picks that are a "once per combat" ability: usage charges max 1, recharge at the end of combat (package 17)
COUNTER_PICKS = ("reroll_d20", "restore_balance", "parry_ranged")


# ------------------------------------------------------------ levels / cost

def level_name(level):
    return LEVEL_NAMES[int(level)]


def ancestors(catalog, name):
    """All ancestors of a weapon (parents, their parents...), no duplicates."""
    seen, todo, out = {name}, list(catalog[name].parents), []
    while todo:
        p = todo.pop(0)
        if p in seen or p not in catalog:
            continue
        seen.add(p)
        out.append(p)
        todo.extend(catalog[p].parents)
    return tuple(out)


def basics_bump(difficulty):
    """Combat basics raise by (5 - difficulty) grades (difficulty 1 -> +4)."""
    return max(0, BASICS_RAISE_BASE - int(difficulty))


def basics_cost(scale):
    return BASICS_COST[int(scale) - 1]


def effective_basics(catalog, name):
    """MAX basics bump over the weapon and all ancestors, never a sum."""
    nodes = (name,) + ancestors(catalog, name)
    return max([basics_bump(catalog[n].difficulty) for n in nodes if catalog[n].basics] or [0])


def level(catalog, name):
    """Effective level = own bought grades + max basics bump over ancestors, capped at 12."""
    return min(MAX_LEVEL, catalog[name].grades + effective_basics(catalog, name))


def grade_cost(catalog, name):
    """Cost of +1 grade: (30 + 5X) * difficulty * scale, X = OTHER weapons at 8+."""
    w = catalog[name]
    x = sum(1 for n in catalog if n != name and level(catalog, n) >= EXPERT_LEVEL)
    return (GRADE_COST_BASE + GRADE_COST_PER_EXPERT * x) * w.difficulty * w.scale


def qualification_penalty(weapon_level, required_level):
    """0 if qualified, -2 one level below, -4 further below (no free attacks)."""
    gap = int(required_level) - int(weapon_level)
    if gap <= 0:
        return QUALIFIED
    if gap == 1:
        return ONE_BELOW_PENALTY
    return NOT_QUALIFIED_PENALTY


# ------------------------------------------------------------------ picks

def slot_tier(slot):
    if slot in SPEC_SLOTS:
        return SPEC
    if slot in EXPERT_SLOTS:
        return EXPERT
    if slot == MASTER_SLOT:
        return MASTER
    raise ValueError("no bonus slot at level %r" % (slot,))


_ALLOWED_LISTS = {SPEC: (SPEC,), EXPERT: (EXPERT, SPEC), MASTER: (MASTER, EXPERT, SPEC)}


def _repeat_ok(tier, ordinal, slot):
    """Repeat limits: specialist 2nd from expert level, 3rd at master;
    expert 2nd at master; master once."""
    if ordinal == 1:
        return True
    if tier == SPEC:
        return (ordinal == REPEAT_SECOND and slot >= EXPERT_LEVEL) or (ordinal == REPEAT_THIRD and slot == MASTER_SLOT)
    if tier == EXPERT:
        return ordinal == REPEAT_SECOND and slot == MASTER_SLOT
    return False


def validate_picks(weapon_level, picks):
    """Raise ValueError if the picks break weapons.md rules."""
    used = set()
    counts = {}
    for p in sorted(picks, key=lambda q: q.slot):
        if p.slot in used:
            raise ValueError("slot %d already used" % p.slot)
        if p.slot > weapon_level:
            raise ValueError("slot %d needs weapon level %d" % (p.slot, p.slot))
        if p.bonus not in BONUS_TIER:
            raise ValueError("unknown bonus: %r" % (p.bonus,))
        st, bt = slot_tier(p.slot), BONUS_TIER[p.bonus]
        if bt not in _ALLOWED_LISTS[st]:
            raise ValueError("%s bonus cannot go to a %s slot" % (bt, st))
        if st != SPEC and not all(s in used for s in SPEC_SLOTS):
            raise ValueError("expert/master picks need 3 specialist picks first")
        counts[p.bonus] = counts.get(p.bonus, 0) + 1
        if not _repeat_ok(bt, counts[p.bonus], p.slot):
            raise ValueError("%s picked too often for slot %d" % (p.bonus, p.slot))
        used.add(p.slot)
    return True


def count(picks, bonus):
    return sum(1 for p in picks if p.bonus == bonus)


# ------------------------------------------------- mastery in final numbers

def mastery_flat(picks):
    """FLAT bonuses from picks: parry (AC), attack, damage, range, balance regen."""
    return {
        "parry": count(picks, "parry_1"),
        "attack": count(picks, "attack_1"),
        "damage": DAMAGE_PICK * count(picks, "damage_3"),
        "range_ft": RANGE_PICK_FT * count(picks, "range_10"),
        "balance_regen": count(picks, "balance_regen_1"),
    }


def durability_percent(picks):
    """Specialist +30%, expert +70% per pick; they stack."""
    return DURABILITY_SPEC_PCT * count(picks, "durability_30") + DURABILITY_EXPERT_PCT * count(picks, "durability_70")


ITEM_HP = "item_hp"                # ItemBonus kinds: effect targets on items (package 17, Q125)
ITEM_HARDNESS = "item_hardness"


@dataclass(frozen=True)
class ItemBonus:
    """An effect bonus to one item's HP or hardness, passed together with the mastery picks (not a pick)."""
    bonus: str
    value: int


def _effect(picks, kind):
    return sum(p.value for p in picks if isinstance(p, ItemBonus) and p.bonus == kind)


def final_durability(base, picks):
    """Final durability from the item's base value; rounded down; then + effects "item_hardness" (never below 0)."""
    return max(0, int(base) * (100 + durability_percent(picks)) // 100 + _effect(picks, ITEM_HARDNESS))


def final_hp(base, picks):
    """Final item HP: +1 per expert 'weapon HP +1' pick + effects "item_hp" (package 17)."""
    return int(base) + count(picks, "hp_1") + _effect(picks, ITEM_HP)


# --------------------------------------------------------- crit and lucky

def crit_threshold(base_threshold=None, keen=False, picks=(), feat_widen=0):
    """Lowest d20 that threatens a crit. Keen doubles the BASE range; each
    'crit +1' pick and feat_widen widen it by 1. Never below 2."""
    faces = int(D20) + 1
    size = faces - int(D20 if base_threshold is None else base_threshold)
    if keen:
        size *= int(KEEN_MULTIPLIER)
    size += count(picks, "crit_1") + int(feat_widen)
    return max(int(MIN_THRESHOLD), faces - size)


def lucky_threshold(picks=(), enchant=0, extra=0):
    """Lucky attack die: base 20, -1 per mastery pick (max 3), -enchant level,
    -extra (class/race/feat for this weapon). No other bonuses. Never below 2."""
    mastery = min(int(LUCKY_MASTERY_MAX), count(picks, "lucky_1"))
    return max(int(MIN_THRESHOLD), LUCKY_BASE - mastery - int(enchant) - int(extra))
