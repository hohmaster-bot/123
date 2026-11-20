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
from wp.model import blocks as blk
from wp.model import derived_view as dv
from wp.model import items as itm
from wp.model import records as rec
from wp.model import stats_view as stv

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
    item_state: str = "ok"             # items.py: ok / broken / not_working / destroyed
    lucky: int = 20                    # lucky attack threshold (mastery picks, enchantment, lucky effects)
    crit_range: int = 20               # lowest d20 that threatens a crit (base, keen, picks, feats)
    extra_dice: Tuple[Tuple[str, str], ...] = ()   # (dice, note) from the weapon's effects, e.g. ("1d6", "fire")
    cmb: int = 0                       # CMB with this record: sheet CMB + the record group's mastery attack (Q58)
    available: bool = True             # all weapons it needs are in the hands (records.attack_available)
    missing: Tuple[str, ...] = ()      # item ids that must be taken in hand
    in_hands: Tuple[str, ...] = ()     # item ids now in the hands
    drops_shield_ac: bool = False      # attacking with a shield: no shield bonus to AC until the next turn


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


# a weapon's own effects on these targets belong to that weapon only (lucky / crit range: package 10)
WEAPON_TARGETS = (bo.ATTACK, bo.DAMAGE, bo.LUCKY, bo.CRIT_RANGE)


def _item_bonuses(ch, item):
    """Worn/held items. This weapon's attack/damage effects are scoped to it; other
    weapons' attack/damage effects do not count for this record."""
    out = []
    ctx = dv.context(ch)
    for it in ch.items:
        if not (it.equipped or it.in_hands):
            continue
        for e in dv.item_tab(it, dv.picks(ch, it)):
            b = e.as_bonus(it.name, ctx)
            if rec.attack_groups(it) and b.target in WEAPON_TARGETS and b.weapon is None:
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


def enchant_bonuses(ch, item):
    """Weapon enchantment N: +N enhancement to attack and damage of this weapon, ONLY while the
    weapon is activated and works (gear.md, Q30, R2). A shield's enchantment raises its shield bonus
    instead. Masterwork: +1 enhancement to attack, so with +N the larger wins (package 8 D3)."""
    out = []
    if item is None:
        return out
    n = weapon_enchant(ch, item)
    if n > 0:
        out += [bo.Bonus(n, bo.ENHANCEMENT, t, item.iid, "enchant +%d" % n) for t in (bo.ATTACK, bo.DAMAGE)]
    mw = itm.masterwork_attack(item, dv.picks(ch, item))
    if mw:
        out.append(bo.Bonus(mw, bo.ENHANCEMENT, bo.ATTACK, item.iid, "masterwork"))
    return out


def weapon_enchant(ch, item):
    return 0 if item is None or rec.is_shield(item) else dv.enchant(item, dv.picks(ch, item))


def extra_dice(ch, item):
    """Dice parts of the weapon's active tab (any kind: fire, acid...): shown, not summed."""
    if item is None:
        return ()
    return tuple((e.dice, e.note) for e in dv.item_tab(item, dv.picks(ch, item))
                 if e.dice and e.target == bo.DAMAGE)


def broken_bonuses(ch, item):
    """Broken weapon: -2 to attack and damage with it (gear.md, package 6)."""
    if item is None or not itm.broken(item, dv.picks(ch, item)):
        return []
    return [bo.Bonus(itm.BROKEN_PENALTY, bo.FLAT, t, item.iid, "broken") for t in (bo.ATTACK, bo.DAMAGE)]


def drum(ch, record, item):
    out = list(dv.effect_bonuses(ch))
    out += _item_bonuses(ch, item)
    out += enchant_bonuses(ch, item)
    out += broken_bonuses(ch, item)
    out += _group_bonuses(ch, record)
    out += proficiency_penalty(ch)
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

def _scoped(bonuses, target, ids):
    """Positive values of effects aimed at `target` for this weapon (or for every weapon)."""
    return sum(max(0, int(b.value)) for b in bonuses
               if b.target == target and (b.weapon is None or b.weapon in ids))


def lucky_extra(bonuses, ids):
    """+N to the lucky attack from class / race / feat / ability effects (target "lucky"), for this
    weapon or all weapons (combat.md "Lucky attack"; package 10, R7)."""
    return _scoped(bonuses, bo.LUCKY, ids)


def crit_range(ch, record, item, bonuses, ids):
    """Crit range shown on the attack (combat.md "Crit", package 10 R8): the weapon's base range, keen
    doubles it, each mastery pick "crit +1" and each feat effect (target "crit_range") widen it by 1."""
    base = item.crit_range if item is not None else 20
    keen = item.keen if item is not None else False
    return wpn.crit_threshold(base, keen, rec.group_picks(ch, record.group), _scoped(bonuses, bo.CRIT_RANGE, ids))


def proficiency_penalty(ch):
    """Armor worn / shields held without proficiency: their skill penalty (after masterwork, doubled
    if broken) ALSO to every attack roll (package 9 B)."""
    return [bo.Bonus(p, bo.FLAT, bo.ATTACK, source="not proficient: " + iid)
            for iid, p in dv.non_proficient_penalties(ch) if p]


def record_cmb(ch, record):
    """CMB with this record (combat.md, package 12 C, Q58): the sheet CMB (BAB + Str / Finesse rule + size +
    typed "cmb" bonuses + pain + morale) + the mastery attack bonus of the record's group (the same "attack +1"
    picks the record gets)."""
    return stv.cmb(ch).total + wpn.mastery_flat(rec.group_picks(ch, record.group))["attack"]


def attack(ch, record, extra=()):
    """Breakdown for one attack record. extra: more typed bonuses for this attack only (a maneuver's
    own modifiers and effects, maneuver_view)."""
    item = _item(ch, record)
    ids = scope_ids(record)
    st = attack_stat(ch, item, record)
    bonuses = drum(ch, record, item) + list(extra)
    pain = pn.penalty(dv.pain_total(ch), ch.pain_profile)

    hit = [Line("bab", ch.bab), Line("stat:" + st, dv.ability_mod(ch, st))]
    if dv.size_mod(ch):
        hit.append(Line("size", dv.size_mod(ch)))      # size affects attack (combat.md, R9)
    q = qualification(ch, record, item)
    if q:
        hit.append(Line("qualification", q))
    if pain:
        hit.append(Line("pain", pain))
    hit += _typed_lines(blk.unblocked(ch, bonuses, bo.ATTACK), bo.ATTACK, ids)

    dmg = [Line("str:" + record.grip, str_damage(dv.ability_mod(ch, "str"), record.grip))]
    if pain:
        dmg.append(Line("pain", pain))
    race = pn.damage_bonus(dv.pain_total(ch), ch.pain_profile)
    if race:
        dmg.append(Line("pain: race bonus", race))   # resources.md: damage bonus per pain (R6)
    dmg += _typed_lines(blk.unblocked(ch, bonuses, bo.DAMAGE), bo.DAMAGE, ids)

    p = wpn.mastery_flat(rec.group_picks(ch, record.group))["parry"]
    parry_lines = (Line("group parry", p, (record.group,)),) if p else ()
    if item is not None and item.no_parry:
        # spiked gauntlets: no parry with the weapon itself; it is parrying with an empty hand
        p, parry_lines = 0, (Line("no parry: empty hand", 0, (item.iid,)),)

    ok, why = rec.attack_available(ch, record)
    return AttackView(record=record.rid, weapon=record.item, group=record.group, stat=st,
                      to_hit=sum(x.value for x in hit), to_hit_lines=tuple(hit),
                      damage=sum(x.value for x in dmg), damage_lines=tuple(dmg),
                      parry=p, parry_lines=parry_lines,
                      crit_hint=crit_hint(item.crit_mult if item is not None else 2),
                      dice=dice_row(item, 1) if item is None or dv.works(ch, item) else ("", ""),
                      item_state=itm.state(item, dv.picks(ch, item)) if item is not None else itm.OK,
                      lucky=wpn.lucky_threshold(rec.group_picks(ch, record.group), weapon_enchant(ch, item),
                                                lucky_extra(blk.unblocked(ch, bonuses, bo.LUCKY), ids)),
                      crit_range=crit_range(ch, record, item, blk.unblocked(ch, bonuses, bo.CRIT_RANGE), ids),
                      extra_dice=extra_dice(ch, item), cmb=record_cmb(ch, record),
                      available=ok, missing=why["missing"], in_hands=why["in_hands"],
                      drops_shield_ac=item is not None and rec.is_shield(item))


def dice_row(item, row):
    """Damage dice (small, medium): row 1 = the normal (top) row; row 2 = the other end of a double weapon."""
    if item is None:
        return ("", "")
    if row == 2 and item.double:
        return (item.damage_small2, item.damage_medium2)
    return (item.damage_small, item.damage_medium)


def all_attacks(ch):
    """Every visible record: weapons in the hands + the unarmed attack (always). Each view has the
    availability flag (a two-weapon record with only one of its weapons in hand is visible but
    not available)."""
    return tuple(attack(ch, r) for r in rec.visible(ch))


def all_records(ch):
    """EVERY attack record (also of weapons not in the hands) + unarmed, each with `available`
    and `missing`, so the UI can grey out what cannot be used now (package 8 B)."""
    recs = [r for r in ch.attacks if r.item != UNARMED]
    recs += [r for r in rec.visible(ch) if r.item == UNARMED]
    return tuple(attack(ch, r) for r in recs)


def by_record(ch, rid):
    for r in rec.visible(ch):
        if r.rid == rid:
            return attack(ch, r)
    raise KeyError("no visible attack record %r" % (rid,))
