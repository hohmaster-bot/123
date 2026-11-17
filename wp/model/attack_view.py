"""Attack and damage breakdown for a weapon in hand or an unarmed attack
(RULES/combat.md, weapons.md, defense.md, buffs.md). Computed on read (D6).

To hit = BAB + attack stat mod + pain penalty + qualification penalty
         + typed bonuses ("drum", stacked by bonuses.py: larger absolute value wins,
           flat adds, proficiency adds): weapon-group bonuses, weapon proficiency
           (mastery picks), morale (trunc(scale/2)), items, statuses.
Damage = Str mod by grip + pain penalty + typed bonuses on damage
         (group bonuses, mastery damage, morale, items, statuses).
Str by grip: one hand 1x, off-hand 0.5x, two hands 1.5x; a positive mod is
multiplied and rounded DOWN, a negative mod is applied once as is.
Morale and pain never touch the lucky attack die or the crit die (not computed here).
Crit hint (text only): x2 -> +0, x3 -> +4, x4 -> +8.
"""
from dataclasses import dataclass, replace
from typing import Optional, Tuple

from wp.catalog.feats_catalog import FINESSE, has_flag
from wp.core import bonuses as bo
from wp.core import effects as ef
from wp.core import pain as pn
from wp.core import weapons as wpn
from wp.model import derived_view as dv

UNARMED = "unarmed"
ONE = "one"
OFF = "off"
TWO = "two"
GRIP_FACTOR = {ONE: (1, 1), OFF: (1, 2), TWO: (3, 2)}   # multiplier as a fraction
DEFAULT_STAT = "str"
CRIT_HINT = {2: "+0", 3: "+4", 4: "+8"}


@dataclass(frozen=True)
class Line:
    label: str
    value: int
    sources: Tuple[str, ...] = ()


@dataclass(frozen=True)
class AttackView:
    weapon: str                        # item id, or UNARMED
    stat: str
    to_hit: int
    to_hit_lines: Tuple[Line, ...]
    damage: int
    damage_lines: Tuple[Line, ...]
    crit_hint: str = ""


# ------------------------------------------------------------------ helpers

def str_damage(mod, grip):
    """Str to damage by grip. Positive: multiply, round down. Negative: once, as is."""
    mod = int(mod)
    if mod <= 0:
        return mod
    num, den = GRIP_FACTOR[grip]
    return mod * num // den


def crit_hint(mult):
    """House-rule tooltip text only, no calculation."""
    return CRIT_HINT.get(int(mult), "")


def weapons_in_hand(ch):
    """Equipped items linked to the weapon catalog."""
    return tuple(it for it in ch.items if it.equipped and it.weapon_id)


def _node(ch, item):
    wid = item.weapon_id if item is not None else UNARMED
    for e in ch.weapons:
        if e.weapon.name == wid:
            return e
    return None


def scope_ids(ch, item):
    """Ids a weapon-scoped bonus may name: the item, its weapon node and all ancestors."""
    ids = set()
    wid = item.weapon_id if item is not None else UNARMED
    ids.add(wid)
    if item is not None:
        ids.add(item.iid)
    catalog = ch.weapon_catalog()
    if wid in catalog:
        ids.update(wpn.ancestors(catalog, wid))
    return frozenset(ids)


def attack_stat(ch, item, stat=None):
    """Chosen stat > forced by the item > best of Str/Dex (finesse weapon + Finesse feat) > Str."""
    if stat:
        return stat
    if item is not None and item.attack_stat:
        return item.attack_stat
    if item is not None and item.finesse and has_flag(ch, FINESSE):
        return max(("str", "dex"), key=lambda a: (dv.ability_mod(ch, a), a == "dex"))
    return DEFAULT_STAT


def _item_bonuses(ch, item):
    """Effects of equipped items. This weapon's attack/damage effects are scoped to it;
    other weapons' attack/damage effects do not count for this attack."""
    out = []
    ctx = dv.context(ch)
    for it in ch.items:
        if not it.equipped:
            continue
        for e in (it.effects_on if it.activated else it.effects_off):
            b = e.as_bonus(it.name, ctx)
            if b.target in (bo.ATTACK, bo.DAMAGE) and b.weapon is None and it.weapon_id:
                if item is None or it.iid != item.iid:
                    continue
                b = replace(b, weapon=it.iid)
            out.append(b)
    return out


def _mastery_bonuses(ch, item):
    """Mastery picks of this weapon node: proficiency to attack (adds with itself),
    damage +3 as flat (weapons.md), scoped to the node."""
    node = _node(ch, item)
    if node is None:
        return []
    flat = wpn.mastery_flat(node.picks)
    wid = node.weapon.name
    out = []
    if flat["attack"]:
        out.append(bo.Bonus(flat["attack"], bo.PROFICIENCY, bo.ATTACK, wid, "weapon mastery"))
    if flat["damage"]:
        out.append(bo.Bonus(flat["damage"], bo.FLAT, bo.DAMAGE, wid, "weapon mastery"))
    return out


def drum(ch, item):
    """All typed bonuses for this attack (statuses, items, mastery, morale)."""
    out = list(ef.bonuses_from(ch.statuses, ch.in_combat, dv.context(ch)))
    out += _item_bonuses(ch, item)
    out += _mastery_bonuses(ch, item)
    out.append(replace(bo.morale(dv.morale_bonus(ch)), source="morale scale"))
    return out


def _typed_lines(bonuses, target, ids):
    """One line per bonus type, already stacked; sources listed."""
    lines = []
    for btype, value in sorted(bo.by_type(bonuses, target, ids).items()):
        srcs = tuple(b.source for b in bonuses if b.btype == btype and bo.applies(b, target, ids))
        if value or srcs:
            lines.append(Line(btype, value, srcs))
    return lines


def qualification(ch, item):
    node = _node(ch, item)
    if node is None:
        return 0
    lvl = wpn.level(ch.weapon_catalog(), node.weapon.name)
    return wpn.qualification_penalty(lvl, node.weapon.required_level)


# --------------------------------------------------------------------- view

def attack(ch, item=None, stat=None, crit_mult=2):
    """Breakdown for one weapon item (None = unarmed)."""
    ids = scope_ids(ch, item)
    st = attack_stat(ch, item, stat)
    bonuses = drum(ch, item)
    pain = pn.penalty(dv.pain_total(ch), ch.pain_profile)
    grip = item.grip if item is not None else ONE

    hit = [Line("bab", ch.bab), Line("stat:" + st, dv.ability_mod(ch, st))]
    q = qualification(ch, item)
    if q:
        hit.append(Line("qualification", q))
    if pain:
        hit.append(Line("pain", pain))
    hit += _typed_lines(bonuses, bo.ATTACK, ids)

    dmg = [Line("str:" + grip, str_damage(dv.ability_mod(ch, "str"), grip))]
    if pain:
        dmg.append(Line("pain", pain))
    dmg += _typed_lines(bonuses, bo.DAMAGE, ids)

    return AttackView(weapon=item.iid if item is not None else UNARMED, stat=st,
                      to_hit=sum(x.value for x in hit), to_hit_lines=tuple(hit),
                      damage=sum(x.value for x in dmg), damage_lines=tuple(dmg),
                      crit_hint=crit_hint(crit_mult))


def all_attacks(ch):
    """Every weapon in hand, plus the unarmed attack: unarmed combat is always available (owner)."""
    return tuple(attack(ch, it) for it in weapons_in_hand(ch)) + (attack(ch, None),)


def find(view, label):
    """Value of a line by label (to_hit lines first, then damage); 0 if absent."""
    for line in view.to_hit_lines:
        if line.label == label:
            return line.value
    return 0


def find_damage(view, label):
    for line in view.damage_lines:
        if line.label == label:
            return line.value
    return 0


def line_sources(lines, label) -> Optional[Tuple[str, ...]]:
    for line in lines:
        if line.label == label:
            return line.sources
    return None
