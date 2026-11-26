"""Situational bonuses and effect conditions per sheet number (package 36, owner decisions 7, 8).

A situational effect ("+2 vs magic", "-4 vs dazzle") is NEVER in a total: hovering the number lists it, a small star
marks the cell, the Sources dialog shows a "situational" row. A conditioned effect counts only while its condition
holds; the Sources dialog shows the condition and whether it holds now.
targets_of(number) -> the effect targets that act on a sheet number (sources numbers of wp/model/sources.py).
by_number(ch) -> {number: ((value, text, source), ...)} of the situational effects.
conditions(ch, number) -> ((source, condition id, holds, value), ...) of the conditioned effects of a number.
"""
from wp.core import ac_zones as acz
from wp.model import blocks as blk
from wp.model import derived_view as dv
from wp.model import source_row as sr

SAVES = ("fort", "ref", "will")
ROLL_NUMBERS = ("attack_melee", "attack_ranged", "initiative", "cmb") + SAVES
NUMBERS = ROLL_NUMBERS + ("cmd", "speed") + tuple(sr.AC + c for c in acz.CELLS if c != "5")


def targets_of(number):
    if number.startswith(sr.AC):
        return ("ac",)
    if number in SAVES:
        return ("save:" + number, "save", "rolls")
    if number in ("attack_melee", "attack_ranged"):
        return (number, "attack", "rolls")
    if number in ("initiative", "cmb"):
        return (number, "rolls")
    target, _ = sr.target_of(number)
    return (target,) if target else ()


def _effects(ch, number):
    ts = targets_of(number)
    cell = number[len(sr.AC):] if number.startswith(sr.AC) else None
    for src, e in blk.active_effects(ch):
        if e.target in ts and (cell is None or not e.cells or cell in tuple(str(c) for c in e.cells)):
            yield src, e


def situational(ch, number, ctx=None):
    ctx = dv.context(ch) if ctx is None else ctx
    return tuple((int(e.nominal(ctx)), e.situational, src) for src, e in _effects(ch, number) if e.situational)


def by_number(ch):
    ctx = dv.context(ch)
    out = {}
    for n in NUMBERS:
        rows = situational(ch, n, ctx)
        if rows:
            out[n] = rows
    return out


def conditions(ch, number):
    ctx = dv.context(ch)
    return tuple((src, e.condition, bool(e.applies(ctx)), int(e.nominal(ctx))) for src, e in _effects(ch, number)
                 if e.condition and not e.situational)
