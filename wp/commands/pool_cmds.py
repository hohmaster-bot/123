"""Resource pools (RULES/resources.md "Resource pools", package 13 C): Ki-like counters at character
level. add_pool / edit_pool / remove_pool / spend_pool / restore_pool. Rests and start_combat restore
pools by their rule (restore_by); a status may pay its per-round cost from a pool (buffs.md).
"""
import dataclasses
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.model import ids
from wp.model.character import ResourcePool

SHORT_REST = "short_rest"
LONG_REST = "long_rest"
COMBAT_START = "combat_start"
MANUAL = "manual"
RESTORES = (SHORT_REST, LONG_REST, COMBAT_START, MANUAL)
_FIELDS = tuple(f.name for f in dataclasses.fields(ResourcePool) if f.name != "pid")


def _check(p):
    if not p.name:
        raise CommandError("a pool needs a name")
    if p.restore not in RESTORES:
        raise CommandError("restore must be one of %s" % ", ".join(RESTORES))
    if p.max < 0 or p.current < 0:
        raise CommandError("pool values cannot be negative")
    return p


def _find(ch, pid):
    p = next((x for x in ch.pools if x.pid == pid), None)
    if p is None:
        raise CommandError("no pool %r" % (pid,))
    return p


def _put(ch, p):
    return replace(ch, pools=tuple(p if x.pid == p.pid else x for x in ch.pools))


def restore_by(ch, rule):
    """Pools with this restore rule go back to max (called by short_rest, long_rest, start_combat)."""
    return replace(ch, pools=tuple(replace(p, current=p.max) if p.restore == rule else p for p in ch.pools))


@command
def add_pool(ch, name="", max=0, current=None, restore=MANUAL):
    p = _check(ResourcePool(pid=ids.make_id(name or "pool", (x.pid for x in ch.pools)), name=name, max=int(max),
                            current=int(max) if current is None else int(current), restore=restore))
    return commit(replace(ch, pools=ch.pools + (p,)), "add_pool", "pool %s %d/%d" % (p.name, p.current, p.max),
                  {"pid": p.pid})


@command
def edit_pool(ch, pid="", **fields):
    unknown = set(fields) - set(_FIELDS)
    if unknown:
        raise CommandError("unknown pool fields: %s" % ", ".join(sorted(unknown)))
    p = _check(replace(_find(ch, pid), **fields))
    return commit(_put(ch, p), "edit_pool", "pool %s: %s" % (p.name, ", ".join(sorted(fields)) or "no change"))


@command
def remove_pool(ch, pid=""):
    p = _find(ch, pid)
    return commit(replace(ch, pools=tuple(x for x in ch.pools if x.pid != pid)), "remove_pool", "pool %s removed" % p.name)


@command
def spend_pool(ch, pid="", n=1):
    p = _find(ch, pid)
    n = int(n)
    if n < 0:
        raise CommandError("cannot spend a negative amount")
    if p.current - n < 0:
        raise CommandError("not enough %s: need %d, have %d" % (p.name, n, p.current))
    return commit(_put(ch, replace(p, current=p.current - n)), "spend_pool", "%s -%d" % (p.name, n))


@command
def restore_pool(ch, pid=""):
    p = _find(ch, pid)
    return commit(_put(ch, replace(p, current=p.max)), "restore_pool", "%s restored to %d" % (p.name, p.max))
