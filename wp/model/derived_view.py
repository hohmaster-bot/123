"""All derived values of a Character in one place (D6, D18).

Everything is computed on read from base values through wp.core.*; nothing here
is stored back into the character.
"""
from wp.core import ac as acm
from wp.core import bonuses as bo
from wp.core import derived as dv
from wp.core import effects as ef
from wp.core import pain as pn
from wp.core import skills as sk
from wp.core import training as tr
from wp.core import weapons as wpn
from wp.core.damage import Pool
from wp.model import records as rec


# ----------------------------------------------------------------- abilities

def ability_current(ch, name):
    return ch.ability(name).current


def ability_mod(ch, name):
    """Modifier from the CURRENT score (stats.md)."""
    return dv.ability_mod(ability_current(ch, name))


# --------------------------------------------------------------- HP, BP, bal

def hp_max(ch):
    """Sum of hit-die results + Con mod per level + bonus, at least 1."""
    return max(1, sum(ch.hp_rolls) + ability_mod(ch, "con") * ch.level + ch.hp_bonus)


def hp_pool(ch):
    return Pool(ch.hp_current, hp_max(ch))


def bp_max(ch):
    return dv.bp_cap(hp_max(ch)) + ch.bp_bonus


def bp_pool(ch):
    return Pool(ch.bp_current, bp_max(ch))


def _equipped(ch):
    """Worn on the doll (armor, rings...)."""
    return [it for it in ch.items if it.equipped]


def _in_hands(ch):
    """Held in the hands slot (weapon, shield, special item)."""
    return [it for it in ch.items if it.in_hands]


def hands_used(ch):
    return sum(it.hands for it in _in_hands(ch))


def armor_bonus(ch):
    return max([it.armor for it in _equipped(ch)] or [0])


def shield_bonus(ch):
    """Shield bonus counts only while the shield is held in a hand (gear.md)."""
    return max([it.shield for it in _in_hands(ch)] or [0])


BALANCE_SHIELDS = ("heavy", "tower")


def shield_balance_bonus(ch):
    """Heavy and tower shields add their shield bonus to the balance max while held in a hand
    (training.md [OWNER, Q28])."""
    return max([it.shield for it in _in_hands(ch) if it.shield_type in BALANCE_SHIELDS] or [0])


def balance_max_base(ch):
    """Worn armor bonus + CURRENT BP + temporary BP (e.g. narrative) + heavy/tower shield in hand
    + bonuses (rest.md, training.md); parry gives none."""
    return dv.balance_max(armor_bonus(ch), ch.bp_current + ch.temp_bp,
                          ch.balance_bonus + shield_balance_bonus(ch))


def balance_max(ch):
    """In combat the cap drops by 1 per hit that reached the balance (owner homerule);
    out of combat it is the normal value."""
    if not ch.in_combat:
        return balance_max_base(ch)
    return max(0, balance_max_base(ch) - ch.balance_cap_hits)


def balance_pool(ch):
    return Pool(ch.balance_current, balance_max(ch))


def balance_regen(ch):
    """Level + Con mod + other (incl. passive group bonus 'balance regen +1' from the
    primary attack records and Unarmed combat), min 1."""
    other = ch.balance_regen_bonus + rec.passive(ch, "balance_regen")
    return dv.balance_regen(ch.level, ability_mod(ch, "con"), other)


SPIRIT_BASE = 5
SPIRIT_PER_CHA = 5


def spirit_max(ch):
    """5 + 5 * Cha mod, never below 0, then bonuses/penalties by source; the total is never below 0."""
    base = max(0, SPIRIT_BASE + SPIRIT_PER_CHA * ability_mod(ch, "cha"))
    return max(0, base + sum(v for _, v in ch.spirit_bonuses))


def spirit_pool(ch):
    return Pool(ch.spirit_current, spirit_max(ch))


ATTENTION_DRIVE_LEVEL = 4


def attention_per_cycle(ch):
    """1 + levels reached that are multiples of 3 + 1 per drive at level 4+ (narrative.md)."""
    return 1 + ch.level // 3 + sum(1 for v in ch.drives.values() if v >= ATTENTION_DRIVE_LEVEL)


def natives(ch):
    return sum(1 for lang in ch.languages if lang.native)


def temp_hp_total(ch):
    """Temp HP 'until the end of combat' + temp HP held by statuses with their own duration."""
    return ch.temp_hp + sum(s.temp_hp_left for s in ch.statuses)


def comfort_max(ch):
    return tr.comfort_max(ch.level, ch.comfort_bonus)


def comfort_pool(ch):
    return Pool(ch.comfort_current, comfort_max(ch))


# ---------------------------------------------------------------------- load

def carried_weight_l(ch):
    return sum(it.weight_l for it in ch.items if it.carried)


def load_status(ch):
    return dv.load_status(carried_weight_l(ch), ability_mod(ch, "str"))


def overloaded(ch):
    return load_status(ch) == dv.LOAD_OVER


# ---------------------------------------------------------------------- pain

def pain_total(ch):
    return pn.total_pain(ch.pain, ch.hp_current)


def pain_penalty(ch):
    return pn.penalty(pain_total(ch), ch.pain_profile)


def is_dead(ch):
    return pn.is_dead(pain_total(ch), ch.pain_profile)


# --------------------------------------------------------------- bonuses, AC

def morale_bonus(ch):
    return dv.morale_bonus(ch.morale_scale, ch.in_combat)


def context(ch):
    """Values effects may read (buffs.md): the current overload."""
    return {ef.OVERLOAD: ch.overload}


def item_effects(ch):
    """Exactly one tab acts per worn or held item (D17). A weapon's own attack/damage
    effects belong to its attack records (attack_view), not to every roll."""
    out = []
    for it in _equipped(ch) + [i for i in _in_hands(ch) if not i.equipped]:
        for e in (it.effects_on if it.activated else it.effects_off):
            b = e.as_bonus(it.name, context(ch))
            if it.groups and b.target in (bo.ATTACK, bo.DAMAGE):
                continue
            out.append(b)
    return out


def all_bonuses(ch):
    """Typed bonuses from statuses, items, morale and pain."""
    out = list(ef.bonuses_from(ch.statuses, ch.in_combat, context(ch)))
    out += item_effects(ch)
    out.append(bo.morale(morale_bonus(ch)))
    out.append(pn.penalty_bonus(pain_total(ch), ch.pain_profile))
    return tuple(out)


def total(ch, target, weapon=None, skill=None):
    return bo.total(all_bonuses(ch), target, weapon, skill)


def ac_input(ch):
    eq = _equipped(ch)
    caps = [it.max_dex for it in eq if it.max_dex is not None]
    # parry = armor proficiency + odd levels (training.md) + weapon mastery picks (weapons.md)
    parry = acm.base_parry(ch.armor_grade, ch.level) + rec.passive(ch, "parry")
    return acm.AcInput(dex_mod=ability_mod(ch, "dex"), armor=armor_bonus(ch), parry=parry,
                       natural=max([it.natural for it in eq] or [0]),
                       shield=shield_bonus(ch),
                       size_mod=ch.size_mod, max_dex=min(caps) if caps else None,
                       overloaded=overloaded(ch),
                       bonuses=tuple(b for b in all_bonuses(ch) if b.target == bo.AC))


def ac(ch, mode=acm.FRONT, from_shield_side=False):
    return acm.ac(ac_input(ch), mode, from_shield_side)


# -------------------------------------------------------------------- skills

def skill(ch, name):
    for s in ch.skills:
        if s.name == name:
            return s
    raise KeyError("no skill %r" % (name,))


def armor_skill_penalty(ch):
    """Penalty of worn armor to Str/Dex skills (gear.md 'Armor'): sum of worn items' penalties."""
    return sum(min(0, it.skill_penalty) for it in _equipped(ch))


def skill_bonus(ch, name):
    s = skill(ch, name)
    return sk.roll_bonus(s, ch.level, ability_mod(ch, s.stat), total(ch, bo.SKILL, skill=s.name),
                         armor_skill_penalty(ch))


# ------------------------------------------------------------------- weapons

def weapon_level(ch, wid):
    return wpn.level(ch.weapon_catalog(), wid)
