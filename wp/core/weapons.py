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

MAX_LEVEL = 12
LEVEL_NAMES = {
    0: "none", 1: "Novice", 2: "Apprentice", 3: "Amateur", 4: "Skilled",
    5: "Specialist I", 6: "Specialist II", 7: "Specialist III",
    8: "Expert I", 9: "Expert II", 10: "Expert III", 11: "Expert IV", 12: "Master",
}
EXPERT_LEVEL = 8
BASICS_COST = {1: 50, 2: 100, 3: 150}

SPEC, EXPERT, MASTER = "specialist", "expert", "master"
SPEC_SLOTS = (5, 6, 7)
EXPERT_SLOTS = (8, 9, 10, 11)
MASTER_SLOT = 12

# bonus id -> tier (weapons.md "Bonuses by tier")
BONUS_TIER = {
    "parry_1": SPEC, "durability_30": SPEC, "attack_1": SPEC, "crit_1": SPEC,
    "range_10": SPEC, "balance_regen_1": SPEC,
    "hp_1": EXPERT, "durability_70": EXPERT, "damage_3": EXPERT, "ignore_vulnerability": EXPERT,
    "ignore_cover_20": EXPERT, "lucky_1": EXPERT, "parry_ranged": EXPERT,
    "reroll_d20": MASTER, "no_attack_tag": MASTER, "restore_balance": MASTER,
}

QUALIFIED = 0
ONE_BELOW_PENALTY = -2
NOT_QUALIFIED_PENALTY = -4
LUCKY_BASE = 20
LUCKY_MASTERY_MAX = 3
MIN_THRESHOLD = 2


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
    return max(0, 5 - int(difficulty))


def basics_cost(scale):
    return BASICS_COST[int(scale)]


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
    return (30 + 5 * x) * w.difficulty * w.scale


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
        return (ordinal == 2 and slot >= EXPERT_LEVEL) or (ordinal == 3 and slot == MASTER_SLOT)
    if tier == EXPERT:
        return ordinal == 2 and slot == MASTER_SLOT
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
        "damage": 3 * count(picks, "damage_3"),
        "range_ft": 10 * count(picks, "range_10"),
        "balance_regen": count(picks, "balance_regen_1"),
    }


def durability_percent(picks):
    """Specialist +30%, expert +70% per pick; they stack."""
    return 30 * count(picks, "durability_30") + 70 * count(picks, "durability_70")


def final_durability(base, picks):
    """Final durability from the item's base value; rounded down."""
    return int(base) * (100 + durability_percent(picks)) // 100


def final_hp(base, picks):
    """Final item HP: +1 per expert 'weapon HP +1' pick."""
    return int(base) + count(picks, "hp_1")


# --------------------------------------------------------- crit and lucky

def crit_threshold(base_threshold=20, keen=False, picks=(), feat_widen=0):
    """Lowest d20 that threatens a crit. Keen doubles the BASE range; each
    'crit +1' pick and feat_widen widen it by 1. Never below 2."""
    size = 21 - int(base_threshold)
    if keen:
        size *= 2
    size += count(picks, "crit_1") + int(feat_widen)
    return max(MIN_THRESHOLD, 21 - size)


def lucky_threshold(picks=(), enchant=0, extra=0):
    """Lucky attack die: base 20, -1 per mastery pick (max 3), -enchant level,
    -extra (class/race/feat for this weapon). No other bonuses. Never below 2."""
    mastery = min(LUCKY_MASTERY_MAX, count(picks, "lucky_1"))
    return max(MIN_THRESHOLD, LUCKY_BASE - mastery - int(enchant) - int(extra))
