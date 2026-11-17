"""Defense ladder (RULES/defense_layers.md): which AC layer an attack roll landed in.

AC = 10 + size + dodge (Dex bonus) + insight + morale + competence + luck + circumstance
     + deflection + shield + armor (incl. parry) + flat + natural armor.
Typed layers are never below 0. "flat" holds untyped bonuses, types without a layer and ALL
penalties (low Dex too); it can be negative. The sum of the layers is always AC - 10.
Layer i covers rolls from 10 + (sum of earlier layers) to 10 + (sum including it) - 1.
Rolls below 10: "position" (no position found). Roll == AC: "exact" (hit, but no full
damage; can be played as a maneuver). Roll > AC: "hit". A layer with a zero bonus (or a
negative flat) has an empty range and is skipped.
"""
import io
import json
import os
from dataclasses import dataclass
from typing import Optional


BASE = 10
POSITION = "position"
EXACT = "exact"
HIT = "hit"
TEXTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "catalog", "data", "defense_layers.json")


@dataclass(frozen=True)
class Range:
    layer: str
    lo: Optional[int]          # first roll of the layer (None = open start)
    hi: Optional[int]          # last roll of the layer (None = open end)


def ac_total(ac_parts):
    return BASE + sum(v for _, v in ac_parts)


def ladder(ac_parts):
    """All ranges: position, every layer with a positive bonus, exact, hit."""
    out = [Range(POSITION, None, BASE - 1)]
    start = BASE
    for t, v in ac_parts:
        if v > 0:
            out.append(Range(t, start, start + v - 1))
        start += v
    total = ac_total(ac_parts)
    out.append(Range(EXACT, total, total))
    out.append(Range(HIT, total + 1, None))
    return tuple(out)


def layer_for_roll(ac_parts, roll):
    """(layer, Range) for one attack roll total."""
    roll = int(roll)
    total = ac_total(ac_parts)
    if roll > total:
        return HIT, Range(HIT, total + 1, None)
    if roll == total:
        return EXACT, Range(EXACT, total, total)
    for r in ladder(ac_parts):
        lo_ok = r.lo is None or roll >= r.lo
        hi_ok = r.hi is None or roll <= r.hi
        if lo_ok and hi_ok:
            return r.layer, r
    return POSITION, Range(POSITION, None, BASE - 1)


def texts(path=TEXTS_PATH):
    """Owner texts by layer type (data, not code)."""
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)["texts"]
