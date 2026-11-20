"""All derived values of a Character in one place (D6, D18).

Everything is computed on read from base values through wp.core.*; nothing here
is stored back into the character.
"""
import math
from dataclasses import dataclass, replace
from fractions import Fraction

from wp.core import ac as acm
from wp.core import bonuses as bo
from wp.core import derived as dv
from wp.core import effects as ef
from wp.core import pain as pn
from wp.core import skills as sk
from wp.core import training as tr
from wp.core import weapons as wpn
from wp.core.damage import Pool
from wp.model import blocks as blk
from wp.model import items as itm
from wp.model import stance_view as stv
from wp.model import records as rec
from wp.model import sheet_targets as stg
from wp.model.body_view import (armor_slowdown, is_dead, morale_bonus, pain_penalty,  # noqa: F401
                                pain_profile, pain_total, size_cmb, size_mod, speed)
from wp.model.load_view import (WeightView, bag_weight_l, carried_weight_l, condition_tags,  # noqa: F401
                                in_bag, load_status, overloaded, weight_view)


# ----------------------------------------------------------------- abilities

def ability_current(ch, name):
    """Stored current score + effects with target "stat:<name>" (package 16 A2; typed bonuses, normal stacking)."""
    return ch.ability(name).current + stg.stat_bonus(ch, name)


def ability_max(ch, name):
    return ch.ability(name).score_max + stg.stat_bonus(ch, name)


def ability_mod(ch, name):
    """Modifier from the CURRENT score (stats.md); a positive one counts as 0 while a block_stat_bonus
    effect covers this stat (package 13 B)."""
    m = dv.ability_mod(ability_current(ch, name))
    return min(0, m) if m > 0 and blk.stat_blocked(ch, name) else m


# --------------------------------------------------------------- HP, BP, bal

def hit_die_hp(ch):
    """Hit-die HP: level 1 = the die max, later levels = the value entered at level up (and
    training HP), each roll at most the die (progression.md, training.md)."""
    return sum(ch.hp_rolls)


def hit_die_cap(ch):
    """Most hit-die HP possible: die * level (training HP cannot go above it)."""
    return ch.hit_die * ch.level


def hit_dice(ch):
    """Every hit die of the sheet: the class rolls (one per level) + one die per effect "extra_hit_dice" (templates,
    races, items...; its value = the HP of that die). No level cap on extra dice (package 16 G1)."""
    extra = [e.resolve(context(ch)) for _, e in blk.active_effects(ch) if e.target == stg.EXTRA_DICE]
    return tuple(ch.hp_rolls) + tuple(d for t in ch.templates for d in t.hit_dice) + tuple(int(v) for v in extra)


def hp_max(ch):
    """Sum over the hit dice of max(1, die HP + CURRENT Con mod) (package 16 G1, owner) + race bonus + other
    bonuses + effects "hp_max"; at least 1."""
    con = ability_mod(ch, "con")
    dice = sum(max(1, d + con) for d in hit_dice(ch))
    return max(1, dice + ch.hp_race + ch.hp_bonus + stg.value(ch, "hp_max"))


def hp_pool(ch):
    return Pool(ch.hp_current, hp_max(ch))


def bp_max(ch):
    return dv.bp_cap(hp_max(ch)) + ch.bp_bonus + stg.value(ch, "bp_max")


def bp_pool(ch):
    return Pool(ch.bp_current, bp_max(ch))


def picks(ch, it):
    """Mastery picks reaching this item (records.item_picks, package 8 R3)."""
    return rec.item_picks(ch, it)


def works(ch, it):
    return itm.works(it, picks(ch, it))


def _equipped(ch):
    """Worn on the doll (armor, rings...). An item at HP 0 or destroyed counts as taken off:
    no AC bonus, no armor skill penalty, no Dex cap, no tab (gear.md [OWNER pkg 7])."""
    return [it for it in ch.items if it.equipped and works(ch, it)]


def _in_hands(ch):
    """Held in the hands slot (weapon, shield, special item)."""
    return [it for it in ch.items if it.in_hands]


def hands_used(ch):
    return sum(it.hands for it in _in_hands(ch))


item_active = itm.item_active
enchant = itm.enchant
item_tab = itm.tab
item_durability = itm.durability
item_hp_max = itm.hp_max
item_hp_current = itm.hp_current
item_state = itm.state


@dataclass(frozen=True)
class ItemView:
    """Derived numbers of one item with the mastery picks that reach it (package 8, R3)."""
    iid: str
    state: str
    hp_current: int
    hp_max: int
    durability: int
    enchant: int
    masterwork: bool
    skill_penalty: int
    group: str                         # group whose picks count ("" = none)
    shield_proficient: bool = True     # kept name: True when the wearer is proficient (armor or shield)
    masterwork_active: bool = False
    masterwork_reason: str = ""        # items.MW_* id when masterwork is off ("" = active)
    touch_bonus: int = 0               # bonus to touch AC (worn armor)
    durable: bool = False              # at most 1 notch per attack
    spell_penalty_mana: int = 0
    spell_failure_pct: int = 0
    condition_tag: str = "none"        # display only (package 9 E)
    quantity: int = 1
    spent: bool = False                # consumable at quantity 0: grey, weight 0 (package 13 D)


def item_view(ch, iid):
    it = ch.item(iid)
    p = picks(ch, it)
    r = rec.item_record(ch, iid)
    mw = itm.masterwork_state(it, p)
    return ItemView(iid=iid, state=itm.state(it, p), hp_current=itm.hp_current(it, p),
                    hp_max=itm.hp_max(it, p), durability=itm.durability(it, p),
                    enchant=itm.enchant(it, p), masterwork=it.masterwork,
                    skill_penalty=itm.skill_penalty(it, p), group=r.group if r is not None else "",
                    shield_proficient=proficient(ch, it),
                    masterwork_active=mw[0], masterwork_reason=mw[1], touch_bonus=touch_value(it, p),
                    durable=itm.is_durable(it), spell_penalty_mana=it.spell_penalty_mana,
                    spell_failure_pct=it.spell_failure_pct, condition_tag=it.condition_tag, quantity=it.quantity, spent=itm.spent(it))


def _defense_value(it, base, p=()):
    """Armor / shield bonus of one item: base + enchantment while activated; broken -> half (down);
    HP 0 or destroyed -> 0 (gear.md)."""
    if base <= 0 or not itm.works(it, p):
        return 0
    v = base + enchant(it, p)
    return v // 2 if itm.broken(it, p) else v


def armor_value(it, p=()):
    return _defense_value(it, it.armor, p)


def touch_value(it, p=()):
    """Touch AC bonus of worn armor (package 9 H): like the armor bonus (0 at HP 0, broken halved
    down) but no enchantment (see OPEN_QUESTIONS)."""
    if it.touch_bonus <= 0 or not itm.works(it, p):
        return 0
    return it.touch_bonus // 2 if itm.broken(it, p) else it.touch_bonus


def touch_armor(ch):
    """Armor layer of the touch AC: worn armor's touch bonus (as type armor) + effects with target
    "touch_armor" (statuses, spells, items; package 10, Q46), stacked by the normal rules, >= 0."""
    item = max([touch_value(it, picks(ch, it)) for it in _equipped(ch)] or [0])
    effects = [b for b in all_bonuses(ch) if b.target == bo.TOUCH_ARMOR]
    return max(0, bo.stack([bo.Bonus(item, bo.ARMOR, bo.TOUCH_ARMOR, source="armor touch")] + effects))


def shield_value(it, p=()):
    return _defense_value(it, it.shield, p)


def armor_bonus(ch):
    return max([armor_value(it, picks(ch, it)) for it in _equipped(ch)] or [0])


def shield_bonus(ch):
    """Shield bonus counts only while the shield is held in a hand (gear.md)."""
    return max([shield_value(it, picks(ch, it)) for it in _in_hands(ch)] or [0])


# Shield proficiency (training.md, package 8 D1): grade rank 0 none, 1 light, 2 heavy, 3 tower.
SHIELD_RANK = {"none": 0, "light": 1, "heavy": 2, "tower": 3}
SHIELD_NEED = {"": 1, "light": 1, "heavy": 2, "tower": 3}
BALANCE_SHIELDS = ("heavy", "tower")


def shield_rank(ch):
    return SHIELD_RANK[ch.shield_grade]


def shield_proficient(ch, it):
    """True for a non-shield; a shield needs the grade of its type (light 1, heavy 2, tower 3)."""
    if not rec.is_shield(it):
        return True
    return shield_rank(ch) >= SHIELD_NEED.get(it.shield_type, 1)


# Armor proficiency (training.md): grade rank 0 none, 1 light, 2 medium, 3 heavy (package 9 B).
ARMOR_RANK = {"none": 0, "light": 1, "medium": 2, "heavy": 3}
ARMOR_NEED = {"": 1, "light": 1, "medium": 2, "heavy": 3}


def is_armor(it):
    return it.armor > 0 and not rec.is_shield(it)


def armor_proficient(ch, it):
    if not is_armor(it):
        return True
    return ARMOR_RANK[ch.armor_grade] >= ARMOR_NEED.get(it.armor_type, 1)


def proficient(ch, it):
    return shield_proficient(ch, it) and armor_proficient(ch, it)


def non_proficient_penalties(ch):
    """((iid, penalty), ...) of worn armor and held shields the character is not proficient in:
    their skill penalty goes ALSO to every attack roll (package 9 B)."""
    worn = [it for it in _equipped(ch) if is_armor(it) or rec.is_shield(it)]
    held = [it for it in _in_hands(ch) if not it.equipped and rec.is_shield(it) and works(ch, it)]
    return tuple((it.iid, itm.skill_penalty(it, picks(ch, it))) for it in worn + held if not proficient(ch, it))


def shield_balance_bonus(ch):
    """Heavy and tower shields add their shield bonus to the balance max while held in a hand,
    only with the proficiency grade of that type (heavy: rank 2, tower: rank 3); light never
    (training.md [OWNER, Q28, package 8 D1])."""
    return max([shield_value(it, picks(ch, it)) for it in _in_hands(ch)
                if it.shield_type in BALANCE_SHIELDS and shield_proficient(ch, it)] or [0])


def balance_max_base(ch):
    """Worn armor bonus + CURRENT BP (BP above max included: overcap, package 8 C)
    + heavy/tower shield in hand + bonuses (rest.md, training.md); parry gives none."""
    return dv.balance_max(armor_bonus(ch), ch.bp_current,
                          ch.balance_bonus + shield_balance_bonus(ch) + stg.value(ch, "balance_max"))


def balance_max(ch):
    """Out of combat: the normal value. In combat: the SNAPSHOT taken at start_combat (package 9 C;
    BP spent, armor on/off, Con or bonus changes do not move it) minus 1 per hit that reached the
    balance or HP (owner homerule). No snapshot (sheet built by hand): the live value."""
    if not ch.in_combat:
        return balance_max_base(ch)
    start = balance_max_base(ch) if ch.balance_cap_start is None else ch.balance_cap_start
    return max(0, start - ch.balance_cap_hits)


def balance_pool(ch):
    return Pool(ch.balance_current, balance_max(ch))


def balance_regen(ch):
    """Level + Con mod + other (incl. passive group bonus 'balance regen +1' from the
    primary attack records and Unarmed combat), min 1."""
    other = ch.balance_regen_bonus + rec.passive(ch, "balance_regen") + stg.value(ch, "balance_regen")
    return dv.balance_regen(ch.level, ability_mod(ch, "con"), other)


SPIRIT_BASE = 5
SPIRIT_PER_CHA = 5


def spirit_max(ch):
    """5 + 5 * Cha mod, never below 0, then bonuses/penalties by source; the total is never below 0."""
    base = max(0, SPIRIT_BASE + SPIRIT_PER_CHA * ability_mod(ch, "cha"))
    return max(0, base + sum(v for _, v in ch.spirit_bonuses) + stg.value(ch, "spirit_max"))


def spirit_pool(ch):
    return Pool(ch.spirit_current, spirit_max(ch))


ATTENTION_DRIVE_LEVEL = 4


def attention_per_cycle(ch):
    """1 + levels reached that are multiples of 3 + 1 per drive at level 4+ (narrative.md)."""
    return (1 + ch.level // 3 + sum(1 for d in ch.drives if d.level >= ATTENTION_DRIVE_LEVEL)
            + stg.value(ch, "attention_per_cycle"))


def natives(ch):
    return sum(1 for lang in ch.languages if lang.native)


def temp_hp_total(ch):
    """Temp HP 'until the end of combat' + temp HP held by statuses with their own duration."""
    return ch.temp_hp + sum(s.temp_hp_left for s in ch.statuses if s.active)


def comfort_max(ch):
    return tr.comfort_max(ch.level, ch.comfort_bonus + stg.value(ch, "comfort_max"))


def comfort_pool(ch):
    return Pool(ch.comfort_current, comfort_max(ch))


# --------------------------------------------------------------- bonuses, AC

def context(ch):
    """Values effects may read (buffs.md): the current overload and the CURRENT stat modifiers."""
    ctx = {ef.OVERLOAD: ch.overload, "level": ch.level, "bab": ch.bab}
    for name in ch.abilities:
        ctx[ef.stat_mod_key(name)] = ability_mod(ch, name)
        ctx["%s_mod" % name] = ctx[ef.stat_mod_key(name)]     # formula variables (package 14 C)
    return ctx


def item_effects(ch, ctx=None):
    """Exactly one tab acts per worn or held item (D17). A weapon's own attack/damage
    effects belong to its attack records (attack_view), not to every roll."""
    out = []
    ctx = context(ch) if ctx is None else ctx
    for it in _equipped(ch) + [i for i in _in_hands(ch) if not i.equipped] + at_base(ch):
        for e in item_tab(it, picks(ch, it)):
            b = e.as_bonus(it.name, ctx)
            if rec.attack_groups(it) and b.target in (bo.ATTACK, bo.DAMAGE):
                continue
            out.append(b)
    return out


def feat_bonuses(ch, ctx=None):
    """Feat effects: permanent while the feat is owned (package 11 D); a stance feat's effects only while
    it is the active stance (package 12, Q74)."""
    ctx = context(ch) if ctx is None else ctx
    return tuple(e.as_bonus(f.title or f.fid, ctx) for f in ch.feats if stv.feat_applies(ch, f) for e in f.effects)


def effect_bonuses(ch, ctx=None):
    """Typed bonuses of active statuses, owned feats and injuries (not items: their tab rules differ)."""
    ctx = context(ch) if ctx is None else ctx
    injuries = tuple(e.as_bonus(j.name or j.jid, ctx) for j in ch.injuries for e in j.effects)   # package 14 D
    extra = tuple(e.as_bonus(src, ctx) for src, effects in other_sources(ch) for e in effects)   # quirks, templates
    return tuple(ef.bonuses_from(ch.statuses, ctx)) + feat_bonuses(ch, ctx) + injuries + extra


def other_sources(ch):
    """(source id, effects) of quirks that are not burned and of templates (package 16 F, G6)."""
    return ([(q.kid, q.effects) for q in ch.quirks if not q.burned]
            + [(t.tid, t.effects) for t in ch.templates])


def all_bonuses(ch):
    """Typed bonuses from statuses, feats, items, morale and pain."""
    out = list(effect_bonuses(ch))
    out += item_effects(ch)
    out.append(bo.morale(morale_bonus(ch)))
    out.append(pn.penalty_bonus(pain_total(ch), pain_profile(ch)))
    return tuple(out)


def total(ch, target, weapon=None, skill=None):
    sub = bo.skill_target(skill) if skill is not None else None
    return bo.total(blk.unblocked(ch, all_bonuses(ch), target, sub), target, weapon, skill)


def ac_input(ch, flank_drops_shield=True, shield_enabled=True):
    eq = _equipped(ch)
    caps = [it.max_dex for it in eq if it.max_dex is not None]
    # parry = armor proficiency + odd levels + tower shield grade (training.md) + weapon mastery picks (weapons.md)
    parry = acm.base_parry(ch.armor_grade, ch.level, ch.shield_grade) + rec.passive(ch, "parry") + stg.value(ch, "parry")
    return acm.AcInput(dex_mod=ability_mod(ch, "dex"), armor=armor_bonus(ch), parry=parry,
                       natural=max([it.natural for it in eq] or [0]),
                       shield=shield_bonus(ch),
                       size_mod=size_mod(ch), max_dex=min(caps) + stg.value(ch, "max_dex") if caps else None,
                       overloaded=overloaded(ch), shield_enabled=shield_enabled, touch_armor=touch_armor(ch),
                       flank_drops_shield=flank_drops_shield,
                       bonuses=tuple(b for b in all_bonuses(ch) if b.target == bo.AC),
                       blocked=frozenset(blk.blocked_types(ch, bo.AC)))


def ac(ch, mode=acm.FRONT, from_shield_side=False, flank_drops_shield=True, shield_enabled=True):
    """AC for one direction. flank_drops_shield: checkbox (default on); shield_enabled=False after an
    attack with the shield (no shield bonus until the next turn, AttackView.drops_shield_ac)."""
    if mode == acm.FLANK and blk.cannot_be_flanked(ch):
        mode = acm.FRONT               # cannot_be_flanked: a flank attack is a front attack (package 13 B)
    return acm.ac(ac_input(ch, flank_drops_shield, shield_enabled), mode, from_shield_side)


# -------------------------------------------------------------------- skills

def skill(ch, name):
    for s in ch.skills:
        if s.name == name:
            return s
    raise KeyError("no skill %r" % (name,))


def armor_skill_penalty(ch):
    """Penalty to Str/Dex skills (gear.md 'Armor'): worn items + shields held in a hand (a shield
    counts as armor, package 8 R4); masterwork -1 smaller, broken doubled (items.skill_penalty)."""
    held = [it for it in _in_hands(ch) if not it.equipped and rec.is_shield(it)]
    pen = sum(itm.skill_penalty(it, picks(ch, it)) for it in _equipped(ch) + held)
    return min(0, pen + stg.value(ch, "armor_skill_penalty")) if pen < 0 else pen


def skill_bonus(ch, name):
    s = skill(ch, name)
    return sk.roll_bonus(s, ch.level, ability_mod(ch, s.stat), total(ch, bo.SKILL, skill=s.name),
                         armor_skill_penalty(ch))


# ------------------------------------------------------------------- weapons

def weapon_level(ch, wid):
    return wpn.level(ch.weapon_catalog(), wid)


from wp.model.sheet_numbers import (at_base, base_slots, base_used, base_view, comfort_rate_bonus,  # noqa: E402,F401
                                    mana_max, mana_pool, reactions, slot_pool, slot_pools)
