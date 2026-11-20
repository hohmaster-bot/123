"""Charges and cooldown of anything usable (RULES/gear.md "Charges and cooldown", package 14 B).

Owners: item, status, feat, attack (record), maneuver.
  - item / feat / attack / maneuver: the optional Usage block (charges_max, charges_current, recharge,
    cooldown_rounds, cooldown_current);
  - status: its existing charges (Pool; rests restore them as before) + cooldown_rounds / cooldown_current.
spend: refused below 0 or while cooldown_current > 0; with cooldown_rounds > 0 it starts the cooldown.
The tick lowers every cooldown by 1. Rests and start_combat restore Usage charges by their recharge rule
(a long rest also restores "short_rest" ones, like pools, assumption Q96).
"""
from dataclasses import replace

from wp.model.character import Usage

KINDS = ("item", "status", "feat", "attack", "maneuver")
SHORT_REST = "short_rest"
LONG_REST = "long_rest"
COMBAT_START = "combat_start"
MANUAL = "manual"
RECHARGES = (SHORT_REST, LONG_REST, COMBAT_START, MANUAL)
_FIELD = {"item": ("items", "iid"), "status": ("statuses", "sid"), "feat": ("feats", "fid"),
          "attack": ("attacks", "rid"), "maneuver": ("maneuvers", "mid")}


def find(ch, kind, oid):
    name, key = _FIELD[kind]
    return next((x for x in getattr(ch, name) if getattr(x, key) == oid), None)


def put(ch, kind, owner):
    name, key = _FIELD[kind]
    oid = getattr(owner, key)
    return replace(ch, **{name: tuple(owner if getattr(x, key) == oid else x for x in getattr(ch, name))})


def charges(kind, owner):
    """(current, max) or None when the owner has no charges."""
    if kind == "status":
        return (owner.charges.current, owner.charges.max) if owner.charges is not None else None
    u = owner.usage
    return (u.charges_current, u.charges_max) if u is not None and u.charges_max > 0 else None


def cooldown(kind, owner):
    """(cooldown_current, cooldown_rounds)."""
    if kind == "status":
        return owner.cooldown_current, owner.cooldown_rounds
    u = owner.usage
    return (u.cooldown_current, u.cooldown_rounds) if u is not None else (0, 0)


def with_values(kind, owner, current=None, cool=None):
    """The owner with new charges current and / or cooldown current."""
    if kind == "status":
        out = owner
        if current is not None:
            out = replace(out, charges=replace(out.charges, current=current))
        if cool is not None:
            out = replace(out, cooldown_current=cool)
        return out
    u = owner.usage or Usage()
    if current is not None:
        u = replace(u, charges_current=current)
    if cool is not None:
        u = replace(u, cooldown_current=cool)
    return replace(owner, usage=u)


def _each(ch):
    for kind in KINDS:
        name, _ = _FIELD[kind]
        for x in getattr(ch, name):
            yield kind, x


def tick_cooldowns(ch):
    """Every cooldown -1 (never below 0), for every owner."""
    for kind, x in list(_each(ch)):
        cur, _ = cooldown(kind, x)
        if cur > 0:
            ch = put(ch, kind, with_values(kind, x, cool=cur - 1))
    return ch


def recharge(ch, *rules):
    """Usage charges with one of these recharge rules go back to max (statuses: unchanged, see rest rules)."""
    for kind, x in list(_each(ch)):
        if kind == "status" or x.usage is None or x.usage.recharge not in rules:
            continue
        ch = put(ch, kind, with_values(kind, x, current=x.usage.charges_max))
    return ch
