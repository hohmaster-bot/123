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
from wp.model.cache import cached

ALL = "all"
ANY = "any"
OVERLOAD_REASON = "overload"


@cached
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
    for it in dv.at_base(ch):              # base contents give their effects (gear.md "Base", package 16)
        out += [(it.iid, e) for e in dv.item_tab(it, dv.picks(ch, it))]
    for j in ch.injuries:                  # injuries carry effects while they exist (package 14 D)
        out += [(j.jid or j.name, e) for e in j.effects]
    for src, effects in dv.other_sources(ch):   # quirks not burned, templates (package 16)
        out += [(src, e) for e in effects]
    return out


def _of(ch, target):
    return [(src, e) for src, e in active_effects(ch) if e.target == target]


ACTIONS = ("attack", "move", "spell_cast", "heal")
RESOURCES = ("hp", "mana", "spirit", "balance")


def restore_block_reasons(ch, resource):
    """Source ids of block_restore effects for this resource ("hp", "mana", "spirit", "balance", "pool:<id>")
    or "any"; block_balance_regen is the balance case (old name kept as an alias, package 14 F)."""
    out = [src for src, e in _of(ch, bo.BLOCK_RESTORE) if ANY in e.block_resources or resource in e.block_resources]
    if resource == "balance":
        out += [src for src, _ in _of(ch, bo.BLOCK_REGEN)]
    return tuple(out)


def restore_blocked(ch, resource):
    return bool(restore_block_reasons(ch, resource))


def regen_block_reasons(ch):
    """Why the balance does not regenerate now: "overload" (overload > 0, while the overload switch is on) and the
    source ids of block_balance_regen / block_restore balance effects."""
    out = [OVERLOAD_REASON] if ch.overload > 0 and ch.rules_settings.overload_enabled else []
    return tuple(out + list(restore_block_reasons(ch, "balance")))


def regen_blocked_by_effect(ch):
    return restore_blocked(ch, "balance")


def blocked_actions(ch):
    """{action: (source ids)} for every blocked action (block_action effects; "any" blocks all)."""
    out = {}
    for src, e in _of(ch, bo.BLOCK_ACTION):
        for a in (ACTIONS if ANY in e.block_actions else e.block_actions):
            out.setdefault(a, []).append(src)
    return {a: tuple(v) for a, v in out.items()}


def action_block_reasons(ch, action):
    return blocked_actions(ch).get(action, ())


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
