"""Skills: tiers, roll bonus, training costs (RULES/skills.md, D19).

Tiers are data: NORMAL, ADVANCED (+3 to the roll), SPECIALIZED (from advanced only).
Roll bonus = ranks + key stat mod + bonuses + armor penalty (+3 if advanced/specialized).
Costs ("rank" = the NEW rank):
  normal +1 rank 20 * rank, advanced 15 * rank (both: ranks <= level),
  specialized: ranks up to level are free/automatic, above level 10 * rank.
  make advanced: 40 + 20 * other advanced; make specialized: 200 + 50 * other specialized.
Free advanced/specialized skills still count as "other".
"""
from dataclasses import dataclass
from wp.rules_data import rules as rd

# rule numbers that were inline literals (package 20: data, wp/rules_data/constants.json)
PROMOTE_BASE = rd.ref("skills.promote_base")   # make advanced = base + per_other * others
PROMOTE_PER_OTHER = rd.ref("skills.promote_per_other")   # per OTHER advanced or specialized skill
SPECIALIZE_BASE = rd.ref("skills.specialize_base")   # make specialized = base + per_other * others
SPECIALIZE_PER_OTHER = rd.ref("skills.specialize_per_other")   # per OTHER specialized skill

NORMAL = "normal"
ADVANCED = "advanced"
SPECIALIZED = "specialized"
TIERS = (NORMAL, ADVANCED, SPECIALIZED)

ADVANCED_ROLL_BONUS = rd.ref("skills.advanced_roll_bonus")
RANK_PRICE = rd.ref("skills.rank_price")


@dataclass(frozen=True)
class Skill:
    name: str                 # stable id; for a family: "<template>:<sub-name>"
    stat: str                 # key stat: str, dex, con, int, wis, cha
    tier: str = NORMAL
    ranks: int = 0            # bought ranks
    armor_penalty_applies: bool = False
    template: str = ""        # catalog template id (skills_list.md)
    sub: str = ""             # sub-skill name for a param family ("kuznets", "air"...)

    def __post_init__(self):
        if self.tier not in TIERS:
            raise ValueError("unknown tier: %r" % (self.tier,))


def effective_ranks(skill, level):
    """Specialized: ranks auto rise to level (floor = level). Others: bought ranks."""
    if skill.tier == SPECIALIZED:
        return max(skill.ranks, int(level))
    return skill.ranks


def roll_bonus(skill, level, stat_mod, bonuses=0, armor_penalty=0):
    """ranks + key stat mod + bonuses + armor penalty (if it applies) + 3 if advanced."""
    b = effective_ranks(skill, level) + int(stat_mod) + int(bonuses)
    if skill.armor_penalty_applies:
        b += int(armor_penalty)
    if skill.tier in (ADVANCED, SPECIALIZED):
        b += ADVANCED_ROLL_BONUS
    return b


def rank_step_cost(tier, new_rank, level):
    """Cost of buying one rank up to new_rank."""
    new_rank, level = int(new_rank), int(level)
    if new_rank < 1:
        raise ValueError("new rank must be >= 1")
    if tier in (NORMAL, ADVANCED) and new_rank > level:
        raise ValueError("normal/advanced skill ranks cannot exceed character level")
    if tier == SPECIALIZED and new_rank <= level:
        return 0
    return RANK_PRICE[tier] * new_rank


def ranks_cost(tier, old_rank, new_rank, level):
    """Total cost from old_rank to new_rank."""
    return sum(rank_step_cost(tier, r, level) for r in range(int(old_rank) + 1, int(new_rank) + 1))


def _count(skills, tiers, exclude):
    return sum(1 for s in skills if s.tier in tiers and s.name != exclude)


def promote_cost(skills, name):
    """Make a skill advanced: 40 + 20 per OTHER advanced skill (specialized ones are advanced too)."""
    return PROMOTE_BASE + PROMOTE_PER_OTHER * _count(skills, (ADVANCED, SPECIALIZED), name)


def specialize_cost(skills, name):
    """Make an advanced skill specialized: 200 + 50 per OTHER specialized skill."""
    return SPECIALIZE_BASE + SPECIALIZE_PER_OTHER * _count(skills, (SPECIALIZED,), name)


def tier_cost(skills, name, to_tier):
    """Cost to raise a skill's tier (normal -> specialized = both steps)."""
    skill = next((s for s in skills if s.name == name), None)
    if skill is None:
        raise ValueError("skill not found: %r" % (name,))
    order = TIERS.index
    if order(to_tier) < order(skill.tier):
        raise ValueError("lowering a tier is not a purchase")
    cost = 0
    if skill.tier == NORMAL and order(to_tier) >= order(ADVANCED):
        cost += promote_cost(skills, name)
    if to_tier == SPECIALIZED and skill.tier != SPECIALIZED:
        cost += specialize_cost(skills, name)
    return cost
