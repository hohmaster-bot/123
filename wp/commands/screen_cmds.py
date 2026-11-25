"""Commands of the Classic screen v2 (package 30, owner).

- set_attack_source(kind, source): the general melee / ranged attack number reads BAB + the modifier of `source`
  (an ability id) or a specific attack record ("record:<rid>"); "" = the default (melee str, ranged dex).
- adjust_value(resource, delta): the tube editor "+N / -N" (a correction, NO game mechanics: no heal block, no pain,
  no cap). Resources: hp, balance, bp, comfort, spirit, mana, overload (the caster overload), pool:<id> (a class
  pool; "pool" alone = the first class pool). A negative result is refused (out_of_range) except HP (HP may go below
  0 by the rules, resources.md); a value above max is kept (the views flag over_max). A plain number in the editor
  maps to set_value; temporary HP to set_temp_hp.
- set_favorite(kind, oid, on): a favourite ability "kind:id" (feat / item / attack / maneuver / spell).
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.commands import resource_cmds as rc
from wp.core import damage as dm
from wp.model import pool_view as pv
from wp.model import screen_view as scr

POOL = "pool"
OVERLOAD = "overload"
HP = "hp"
FAVORITE_KINDS = ("feat", "item", "attack", "maneuver", "spell")


@command
def set_attack_source(ch, kind="", source=""):
    if kind not in scr.KINDS:
        raise CommandError("the attack kind is melee or ranged", "not_allowed", values=(kind,), allowed=scr.KINDS)
    if source.startswith(scr.RECORD):
        if not any(r.rid == source[len(scr.RECORD):] for r in ch.attacks):
            raise CommandError("no attack record %r" % (source,), "no_attack_record", values=(source,))
    elif source and source not in ch.abilities:
        raise CommandError("the source is an ability or record:<id>", "not_allowed", values=(source,),
                           allowed=tuple(ch.abilities))
    sources = {k: v for k, v in ch.attack_sources.items() if k != kind}
    if source:
        sources[kind] = source
    return commit(replace(ch, attack_sources=sources), "set_attack_source", "%s attack from %s" % (kind, source or "default"))


def _pool_of(ch, resource):
    pid = resource[len(POOL) + 1:] if resource.startswith(POOL + ":") else ""
    if resource == POOL and ch.pools:
        return ch.pools[0]
    p = next((x for x in ch.pools if x.pid == pid), None)
    if p is None:
        raise CommandError("no class pool %r" % (resource,), "not_found", values=("pools", resource))
    return p


def _refuse_negative(resource, value):
    if value < 0 and resource != HP:
        raise CommandError("%s cannot go below 0" % resource, "out_of_range", values=(value, 0, None), min=0, max=None,
                           parameter="delta")


@command
def adjust_value(ch, resource="", delta=0):
    delta = int(delta)
    if resource == POOL or resource.startswith(POOL + ":"):
        p = _pool_of(ch, resource)
        value = pv.current(ch, p) + delta
        _refuse_negative(resource, value)
        new = replace(ch, pools=tuple(replace(x, current=value) if x.pid == p.pid else x for x in ch.pools))
    elif resource == OVERLOAD:
        value = ch.overload + delta
        _refuse_negative(resource, value)
        new = replace(ch, overload=value)
    else:
        pool = rc._get(ch, resource)
        value = pool.current + delta
        _refuse_negative(resource, value)
        new = rc._put(ch, resource, dm.set_value(pool, value))
    return commit(new, "adjust_value", "%s %+d -> %d" % (resource, delta, value), {"value": value})


@command
def set_favorite(ch, kind="", oid="", on=True):
    if kind not in FAVORITE_KINDS:
        raise CommandError("a favourite is a feat, item, attack, maneuver or spell", "not_allowed", values=(kind,),
                           allowed=FAVORITE_KINDS)
    key = "%s:%s" % (kind, oid)
    favs = tuple(f for f in ch.favorites if f != key) + ((key,) if on else ())
    return commit(replace(ch, favorites=favs), "set_favorite", "%s favourite %s" % (key, on))
