"""Attack, damage and parry breakdown per ATTACK RECORD (RULES/combat.md, weapons.md,
defense.md, buffs.md). Computed on read (D6).

A record = weapon + one chosen weapon group + grip + attack stat (wp/model/records.py).
To hit = BAB + attack stat mod + pain penalty + qualification penalty
         + typed bonuses ("drum", stacked by bonuses.py): the chosen group's bonuses
           (mastery "attack +1" as proficiency, statuses scoped to the group), morale,
           the weapon's own tab, other worn items, statuses.
Damage = Str mod by grip + pain penalty + typed bonuses on damage.
Parry  = the chosen group's mastery "parry +1" picks.
Only the CHOSEN group counts: no second group, no parent groups.
Group "Basic/simple": no qualification penalty.
Str by grip: one hand 1x, off-hand 0.5x, two hands 1.5x; positive multiplied and
rounded DOWN, negative applied once. Morale and pain never touch the lucky die or
the crit die. Crit hint (text only): x2 -> +0, x3 -> +4, x4 -> +8.
"""
from dataclasses import dataclass, replace
from typing import Tuple

from wp.catalog.feats_catalog import FINESSE, has_flag
from wp.core import bonuses as bo
from wp.core import effects as ef
from wp.core import pain as pn
from wp.core import weapons as wpn
from wp.model import derived_view as dv
from wp.model import records as rec

UNARMED = rec.UNARMED
ONE = "one"
OFF = "off"
TWO = "two"
GRIPS = (ONE, OFF, TWO)
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
    record: str                        # record id
    weapon: str                        # item iid, or UNARMED
    group: str
    stat: str
    to_hit: int
    to_hit_lines: Tuple[Line, ...]
    damage: int
    damage_lines: Tuple[Line, ...]
    parry: int
    parry_lines: Tuple[Line, ...]
    crit_hint: str = ""
    dice: Tuple[str, str] = ("", "")   # damage dice (small, medium) of the row used


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


def _item(ch, record):
    """The weapon card of a record. Unarmed: the "unarmed" card if the sheet has one."""
    if record.item == UNARMED:
        return next((it for it in ch.items if it.iid == UNARMED), None)
    return ch.item(record.item)


def scope_ids(record):
    """Ids a scoped bonus may name: the item and the ONE chosen group (no parents)."""
    return frozenset((record.item, record.group))


def attack_stat(ch, item, record):
    """Record's stat > best of Str/Dex (finesse weapon + Finesse feat) > Str."""
    if record.stat:
        return record.stat
    if item is not None and item.finesse and has_flag(ch, FINESSE):
        return max(("str", "dex"), key=lambda a: (dv.ability_mod(ch, a), a == "dex"))
    return DEFAULT_STAT


def _item_bonuses(ch, item):
    """Worn/held items. This weapon's attack/damage effects are scoped to it; other
    weapons' attack/damage effects do not count for this record."""
    out = []
    ctx = dv.context(ch)
    for it in ch.items:
        if not (it.equipped or it.in_hands):
            continue
        for e in (it.effects_on if it.activated else it.effects_off):
            b = e.as_bonus(it.name, ctx)
            if rec.attack_groups(it) and b.target in (bo.ATTACK, bo.DAMAGE) and b.weapon is None:
                if item is None or it.iid != item.iid:
                    continue
                b = replace(b, weapon=it.iid)
            out.append(b)
    return out


def _group_bonuses(ch, record):
    """Mastery picks of the chosen group only: attack +1 (proficiency), damage +3 (flat)."""
    flat = wpn.mastery_flat(rec.group_picks(ch, record.group))
    out = []
    if flat["attack"]:
        out.append(bo.Bonus(flat["attack"], bo.PROFICIENCY, bo.ATTACK, record.group, record.group))
    if flat["damage"]:
        out.append(bo.Bonus(flat["damage"], bo.FLAT, bo.DAMAGE, record.group, record.group))
    return out


def drum(ch, record, item):
    out = list(ef.bonuses_from(ch.statuses, ch.in_combat, dv.context(ch)))
    out += _item_bonuses(ch, item)
    out += _group_bonuses(ch, record)
    out.append(replace(bo.morale(dv.morale_bonus(ch)), source="morale scale"))
    return out


def _typed_lines(bonuses, target, ids):
    lines = []
    for btype, value in sorted(bo.by_type(bonuses, target, ids).items()):
        srcs = tuple(b.source for b in bonuses if b.btype == btype and bo.applies(b, target, ids))
        if value or srcs:
            lines.append(Line(btype, value, srcs))
    return lines


def qualification(ch, record, item):
    """-2 one level below, -4 further below (weapons.md). Basic/simple: none. No card: none."""
    if item is None or rec.is_basic(ch, record.group):
        return 0
    n = rec.node(ch, record.group)
    lvl = wpn.level(ch.weapon_catalog(), record.group) if n is not None else 0
    return wpn.qualification_penalty(lvl, item.required_level)


# --------------------------------------------------------------------- view

def attack(ch, record):
    """Breakdown for one attack record."""
    item = _item(ch, record)
    ids = scope_ids(record)
    st = attack_stat(ch, item, record)
    bonuses = drum(ch, record, item)
    pain = pn.penalty(dv.pain_total(ch), ch.pain_profile)

    hit = [Line("bab", ch.bab), Line("stat:" + st, dv.ability_mod(ch, st))]
    q = qualification(ch, record, item)
    if q:
        hit.append(Line("qualification", q))
    if pain:
        hit.append(Line("pain", pain))
    hit += _typed_lines(bonuses, bo.ATTACK, ids)

    dmg = [Line("str:" + record.grip, str_damage(dv.ability_mod(ch, "str"), record.grip))]
    if pain:
        dmg.append(Line("pain", pain))
    dmg += _typed_lines(bonuses, bo.DAMAGE, ids)

    p = wpn.mastery_flat(rec.group_picks(ch, record.group))["parry"]
    parry_lines = (Line("group parry", p, (record.group,)),) if p else ()
    if item is not None and item.no_parry:
        # spiked gauntlets: no parry with the weapon itself; it is parrying with an empty hand
        p, parry_lines = 0, (Line("no parry: empty hand", 0, (item.iid,)),)

    return AttackView(record=record.rid, weapon=record.item, group=record.group, stat=st,
                      to_hit=sum(x.value for x in hit), to_hit_lines=tuple(hit),
                      damage=sum(x.value for x in dmg), damage_lines=tuple(dmg),
                      parry=p, parry_lines=parry_lines,
                      crit_hint=crit_hint(item.crit_mult if item is not None else 2),
                      dice=dice_row(item, 1))


def dice_row(item, row):
    """Damage dice (small, medium): row 1 = the normal (top) row; row 2 = the other end of a double weapon."""
    if item is None:
        return ("", "")
    if row == 2 and item.double:
        return (item.damage_small2, item.damage_medium2)
    return (item.damage_small, item.damage_medium)


def all_attacks(ch):
    """Every visible record: weapons in the hands + the unarmed attack (always)."""
    return tuple(attack(ch, r) for r in rec.visible(ch))


def by_record(ch, rid):
    for r in rec.visible(ch):
        if r.rid == rid:
            return attack(ch, r)
    raise KeyError("no visible attack record %r" % (rid,))
