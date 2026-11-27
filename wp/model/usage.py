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

KINDS = ("item", "status", "feat", "attack", "maneuver", "pick")
PICK = "pick"                      # a once-per-combat mastery pick; id "<weapon node id>:<slot>" (package 17)
SHORT_REST = "short_rest"
LONG_REST = "long_rest"
COMBAT_START = "combat_start"
COMBAT_END = "combat_end"          # package 17: master counters
MANUAL = "manual"
RECHARGES = (SHORT_REST, LONG_REST, COMBAT_START, COMBAT_END, MANUAL)
_FIELD = {"item": ("items", "iid"), "status": ("statuses", "sid"), "feat": ("feats", "fid"),
          "attack": ("attacks", "rid"), "maneuver": ("maneuvers", "mid")}


def pick_id(entry, pick):
    return "%s:%d" % (entry.weapon.name, pick.slot)


def _picks(ch):
    from wp.core import weapons as wpn
    return [(pick_id(e, p), e, p) for e in ch.weapons for p in e.picks if p.bonus in wpn.COUNTER_PICKS]


def find(ch, kind, oid):
    if kind == PICK:
        return next((p for i, _, p in _picks(ch) if i == oid), None)
    name, key = _FIELD[kind]
    return next((x for x in getattr(ch, name) if getattr(x, key) == oid), None)


def put(ch, kind, owner, oid=None):
    if kind == PICK:
        weapons = tuple(replace(e, picks=tuple(owner if (pick_id(e, p) == oid) else p for p in e.picks))
                        for e in ch.weapons)
        return replace(ch, weapons=weapons)
    name, key = _FIELD[kind]
    oid = getattr(owner, key)
    return replace(ch, **{name: tuple(owner if getattr(x, key) == oid else x for x in getattr(ch, name))})


def charges(kind, owner):
    """(current, max) or None when the owner has no charges."""
    if kind == "status":
        return (owner.charges.current, owner.charges.max) if owner.charges is not None else None
    if kind == PICK:
        return (1 - min(1, owner.used), 1)
    u = owner.usage
    return (u.charges_current, u.charges_max) if u is not None and u.charges_max > 0 else None


def cooldown(kind, owner):
    """(cooldown_current, cooldown_rounds)."""
    if kind == "status":
        return owner.cooldown_current, owner.cooldown_rounds
    if kind == PICK:
        return (0, 0)
    u = owner.usage
    return (u.cooldown_current, u.cooldown_rounds) if u is not None else (0, 0)


def with_values(kind, owner, current=None, cool=None):
    """The owner with new charges current and / or cooldown current."""
    if kind == PICK:
        return owner if current is None else replace(owner, used=1 - int(current))
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
        if kind == PICK:
            continue
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
    if COMBAT_END in rules:            # master counters: once per combat (package 17)
        for oid, _, p in _picks(ch):
            if p.used:
                ch = put(ch, PICK, replace(p, used=0), oid)
    from wp.model import reroll_view as rv
    return rv.refill(ch, rules)        # package 38: reroll grants follow the same rules


# ------------------------------------------------ status charges follow their source (Q108, package 16 G3)
SOURCE_KINDS = {"feat": "feats", "item": "items", "attack": "attacks", "maneuver": "maneuvers", "pool": "pools",
                "template": "templates"}


def source_rule(ch, status):
    """The recharge rule a status's charges follow: the rule of its source (Status.source_ref "kind:id"): a feat /
    item / attack record / maneuver -> its Usage.recharge; a pool -> its restore rule; a template or a missing
    source -> None (no recharge). A status without a source has no rule (buffs.md Q97)."""
    kind, _, oid = status.source_ref.partition(":")
    if kind not in SOURCE_KINDS or not oid:
        return None
    if kind == "pool":
        p = next((p for p in ch.pools if p.pid == oid), None)
        return p.restore if p is not None else None
    if kind == "template":
        return None
    owner = find(ch, kind, oid)
    return owner.usage.recharge if owner is not None and owner.usage is not None else None


def status_recharge(before, after, rules, revert=False):
    """Status charges after a rest / start_combat: a status whose source rule is in `rules` goes to max; with
    revert=True every other status keeps the charges it had BEFORE (the long rest no longer refills them)."""
    old = {s.sid: s for s in before.statuses}
    out = []
    for s in after.statuses:
        if s.charges is not None and source_rule(after, s) in rules:
            s = replace(s, charges=replace(s.charges, current=max(s.charges.current, s.charges.max)))
        elif revert and s.charges is not None and s.sid in old and old[s.sid].charges is not None:
            s = replace(s, charges=old[s.sid].charges)
        out.append(s)
    return replace(after, statuses=tuple(out))
