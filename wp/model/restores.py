"""Restoring resources: restore blocks, restore by effect, rest HP switch (package 14 F, G). Pure functions
on the character; commands call them.

Resources: "hp", "mana", "spirit", "balance", "pool:<id>".
  - add(ch, res, n): +n, never above the max (an over-max value is not lowered), nothing while a
    block_restore effect covers the resource.
  - guard(before, after): every resource covered by a block_restore effect that went UP between before and
    after is set back (rests, start_combat pool restores). Lowering is never blocked.
  - per_tick(ch, acted): the per_tick_restore of the statuses that acted in this tick.
  - one_shot(ch, status): the one-shot resources of a status at activation (temp HP stays in effects.py).
  - rest_hp(before, after): rule switch rest_regen_multiplier / rest_regen_bonus on the HP a rest gave.
"""
import math
from dataclasses import replace
from fractions import Fraction

from wp.model import blocks as blk
from wp.model import derived_view as dv
from wp.model import pool_view as pv

POOL = "pool:"
BASE = ("hp", "mana", "spirit", "balance")


def valid(res):
    return res in BASE or res.startswith(POOL)


def _pool(ch, res):
    pid = res[len(POOL):]
    return next((p for p in ch.pools if p.pid == pid), None)


def get(ch, res):
    """(current, max) of a resource; None for an unknown pool."""
    if res == "hp":
        return ch.hp_current, dv.hp_max(ch)
    if res == "mana":
        return ch.mana.current, ch.mana.max
    if res == "spirit":
        return ch.spirit_current, dv.spirit_max(ch)
    if res == "balance":
        return ch.balance_current, dv.balance_max(ch)
    p = _pool(ch, res)
    return (pv.current(ch, p), pv.max_of(ch, p)) if p is not None else None


def put(ch, res, value):
    if res == "hp":
        return replace(ch, hp_current=value)
    if res == "mana":
        return replace(ch, mana=replace(ch.mana, current=value))
    if res == "spirit":
        return replace(ch, spirit_current=value)
    if res == "balance":
        return replace(ch, balance_current=value)
    pid = res[len(POOL):]
    return replace(ch, pools=tuple(replace(p, current=value) if p.pid == pid else p for p in ch.pools))


def add(ch, res, n):
    cur = get(ch, res)
    if cur is None or n <= 0 or blk.restore_blocked(ch, res):
        return ch
    current, mx = cur
    if current >= mx:
        return ch
    return put(ch, res, min(mx, current + int(n)))


def _all(ch):
    return BASE + tuple(POOL + p.pid for p in ch.pools)


def guard(before, after):
    out = after
    for res in _all(before):
        if not blk.restore_blocked(before, res):
            continue
        b, a = get(before, res), get(after, res)
        if b is not None and a is not None and a[0] > b[0]:
            out = put(out, res, b[0])
    return out


def per_tick(ch, acted):
    for i in acted:
        for res, n in ch.statuses[i].per_tick_restore.items():
            ch = add(ch, res, n)
    return ch


def one_shot(ch, status):
    for o in status.one_shot:
        if valid(o.resource):
            ch = add(ch, o.resource, o.amount)
    return ch


def rest_hp(before, after):
    """HP a rest gave -> floor(gain * rest_regen_multiplier) + rest_regen_bonus, never above the max."""
    rs = after.rules_settings
    gain = after.hp_current - before.hp_current
    if gain <= 0 or (rs.rest_regen_multiplier == 1 and rs.rest_regen_bonus == 0):
        return after
    new_gain = int(math.floor(gain * Fraction(str(rs.rest_regen_multiplier)))) + int(rs.rest_regen_bonus)
    return replace(after, hp_current=min(dv.hp_max(after), before.hp_current + max(0, new_gain)))
