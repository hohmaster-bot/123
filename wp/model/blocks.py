"""Block effects (RULES/buffs.md "Block effects", package 13 B). Computed on read (D6).

Effect kinds (Effect.target), from any CURRENTLY ACTIVE source: an active status, an owned feat
(a stance feat only while it is the active stance), the acting tab of a worn / held item.
Blocks drop only POSITIVE values; penalties always stay.
  - block_balance_regen: balance does not regenerate (like overload).
  - block_bonus (Effect.block_type: a bonus type or "any"; Effect.block_scope: ("all",) or targets such
    as attack, damage, ac, save, save:fort, skill, skill:<id>): positive bonuses of that type to that
    scope are dropped before stacking. Type dodge on scope ac also drops the positive Dex part of the
    dodge layer (Dex + dodge are netted; the low-Dex penalty stays).
  - block_stat_bonus (Effect.block_stats: stat names or ("all",)): a positive modifier of those stats
    counts as 0 everywhere; a negative one stays.
  - cannot_be_flanked: the FLANK AC option behaves exactly like a front attack.
Injuries carry effects while they exist (package 14 D), so an injury can be a block source too.
"""
from wp.core import bonuses as bo
from wp.core import effects as ef
from wp.model import derived_view as dv
from wp.model import stance_view as stv

ALL = "all"
ANY = "any"
OVERLOAD_REASON = "overload"


def active_effects(ch):
    """(source id, Effect) of every effect from an active source (no values resolved here)."""
    out = []
    for s in ch.statuses:
        if ef.is_effective(s):
            out += [(s.sid, e) for e in s.effects]
    for f in ch.feats:
        if stv.feat_applies(ch, f):
            out += [(f.fid, e) for e in f.effects]
    for it in ch.items:
        if it.equipped or it.in_hands:
            out += [(it.iid, e) for e in dv.item_tab(it, dv.picks(ch, it))]
    for j in ch.injuries:                  # injuries carry effects while they exist (package 14 D)
        out += [(j.jid or j.name, e) for e in j.effects]
    return out


def _of(ch, target):
    return [(src, e) for src, e in active_effects(ch) if e.target == target]


def regen_block_reasons(ch):
    """Why the balance does not regenerate now: "overload" (overload > 0) and the source ids of
    block_balance_regen effects."""
    out = [OVERLOAD_REASON] if ch.overload > 0 else []
    return tuple(out + [src for src, _ in _of(ch, bo.BLOCK_REGEN)])


def regen_blocked_by_effect(ch):
    return bool(_of(ch, bo.BLOCK_REGEN))


def cannot_be_flanked(ch):
    return bool(_of(ch, bo.NO_FLANK))


def stat_blocked(ch, stat):
    return any(ALL in e.block_stats or stat in e.block_stats for _, e in _of(ch, bo.BLOCK_STAT))


def _in_scope(scope, target, sub=None):
    if ALL in scope or target in scope:
        return True
    return sub is not None and sub in scope


def blocked_types(ch, target, sub=None):
    """Bonus types blocked for one query target ("any" = every type). sub: "skill:<id>", "save:fort"..."""
    return {e.block_type or ANY for _, e in _of(ch, bo.BLOCK_BONUS) if _in_scope(e.block_scope or (ALL,), target, sub)}


def drop(bonuses, types):
    """Drop POSITIVE bonuses of the blocked types; penalties stay."""
    if not types:
        return list(bonuses)
    return [b for b in bonuses if not (b.value > 0 and (ANY in types or b.btype in types))]


def unblocked(ch, bonuses, target, sub=None):
    return drop(bonuses, blocked_types(ch, target, sub))
