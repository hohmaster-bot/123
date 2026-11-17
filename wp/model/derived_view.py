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
    return [it for it in ch.items if it.equipped]


def armor_bonus(ch):
    return max([it.armor for it in _equipped(ch)] or [0])


def balance_max(ch):
    """Worn armor bonus + CURRENT BP + bonuses (rest.md); parry gives none."""
    return dv.balance_max(armor_bonus(ch), ch.bp_current, ch.balance_bonus)


def balance_pool(ch):
    return Pool(ch.balance_current, balance_max(ch))


def _weapon_picks(ch):
    return [p for e in ch.weapons for p in e.picks]


def balance_regen(ch):
    """Level + Con mod + other (incl. weapon mastery 'balance regen +1'), min 1."""
    other = ch.balance_regen_bonus + wpn.mastery_flat(_weapon_picks(ch))["balance_regen"]
    return dv.balance_regen(ch.level, ability_mod(ch, "con"), other)


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
    """Exactly one tab acts per equipped item (D17)."""
    out = []
    for it in _equipped(ch):
        for e in (it.effects_on if it.activated else it.effects_off):
            out.append(e.as_bonus(it.name, context(ch)))
    return out


def all_bonuses(ch):
    """Typed bonuses from statuses, items, morale and pain."""
    out = list(ef.bonuses_from(ch.statuses, ch.in_combat, context(ch)))
    out += item_effects(ch)
    out.append(bo.morale(morale_bonus(ch)))
    out.append(pn.penalty_bonus(pain_total(ch), ch.pain_profile))
    return tuple(out)


def total(ch, target, weapon=None):
    return bo.total(all_bonuses(ch), target, weapon)


def ac_input(ch):
    eq = _equipped(ch)
    caps = [it.max_dex for it in eq if it.max_dex is not None]
    parry = wpn.mastery_flat(_weapon_picks(ch))["parry"]
    return acm.AcInput(dex_mod=ability_mod(ch, "dex"), armor=armor_bonus(ch), parry=parry,
                       natural=max([it.natural for it in eq] or [0]),
                       shield=max([it.shield for it in eq] or [0]),
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


def skill_bonus(ch, name, armor_penalty=0):
    s = skill(ch, name)
    return sk.roll_bonus(s, ch.level, ability_mod(ch, s.stat), total(ch, bo.SKILL), armor_penalty)


# ------------------------------------------------------------------- weapons

def weapon_level(ch, wid):
    return wpn.level(ch.weapon_catalog(), wid)
