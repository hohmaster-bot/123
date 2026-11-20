"""Resource pools (RULES/resources.md "Resource pools", package 13 C): Ki-like counters at character
level. add_pool / edit_pool / remove_pool / spend_pool / restore_pool. Rests and start_combat restore
pools by their rule (restore_by); a status may pay its per-round cost from a pool (buffs.md).
"""
import dataclasses
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import formula as fm
from wp.model import formulas as fx
from wp.model import blocks as blk
from wp.model import ids
from wp.model import pool_view as pv
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
    try:
        fx.validate(p.max)             # a number or a formula (package 14 C)
    except fm.FormulaError as e:
        raise CommandError("bad pool max formula %r: %s" % (p.max, e))
    if (not isinstance(p.max, str) and p.max < 0) or p.current < 0:
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
    return replace(ch, pools=tuple(replace(p, current=pv.max_of(ch, p)) if p.restore == rule else p for p in ch.pools))


@command
def add_pool(ch, name="", max=0, current=None, restore=MANUAL):
    """max: a number or a formula (buffs.md "Formulas"); current defaults to the max on the current sheet."""
    m = max if isinstance(max, str) else int(max)
    p = _check(ResourcePool(pid=ids.make_id(name or "pool", (x.pid for x in ch.pools)), name=name, max=m,
                            current=0 if current is None else int(current), restore=restore))
    if current is None:
        p = replace(p, current=pv.max_of(ch, p))
    return commit(replace(ch, pools=ch.pools + (p,)), "add_pool", "pool %s %d/%d" % (p.name, p.current, pv.max_of(ch, p)),
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
    have = pv.current(ch, p)               # clamped to the max on read
    if have - n < 0:
        raise CommandError("not enough %s: need %d, have %d" % (p.name, n, have))
    return commit(_put(ch, replace(p, current=have - n)), "spend_pool", "%s -%d" % (p.name, n))


@command
def restore_pool(ch, pid=""):
    p = _find(ch, pid)
    if blk.restore_blocked(ch, "pool:" + pid):
        raise CommandError("restoring %s is blocked by %s" % (p.name, ", ".join(blk.restore_block_reasons(ch, "pool:" + pid))))
    m = pv.max_of(ch, p)
    return commit(_put(ch, replace(p, current=m)), "restore_pool", "%s restored to %d" % (p.name, m))
