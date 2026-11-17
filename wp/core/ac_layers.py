"""Defense ladder (RULES/defense_layers.md): which AC layer an attack roll landed in.

AC = 10 + size + dodge (incl. Dex) + insight + morale + competence + luck + circumstance
     + deflection + shield + armor (incl. parry) + natural armor.
Layer i covers rolls from 10 + (sum of earlier layers) to 10 + (sum including it) - 1.
Rolls below 10: "position" (no position found). Roll == AC: "exact" (hit, but no full
damage; can be played as a maneuver). Roll > AC: "hit". A layer with a zero (or
negative) bonus has an empty range and is skipped.
"""
import io
import json
import os
from dataclasses import dataclass
from typing import Optional

from wp.core import ac as acm

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


def _layer_parts(ac_parts):
    """Only the owner's layers, in order (the 'unlisted' sum is not a layer, see OPEN_QUESTIONS)."""
    return [(t, v) for t, v in ac_parts if t != acm.UNLISTED]


def ac_total(ac_parts):
    return BASE + sum(v for _, v in _layer_parts(ac_parts))


def ladder(ac_parts):
    """All ranges: position, every layer with a positive bonus, exact, hit."""
    out = [Range(POSITION, None, BASE - 1)]
    start = BASE
    for t, v in _layer_parts(ac_parts):
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
    for r in ladder(ac_parts):
        lo_ok = r.lo is None or roll >= r.lo
        hi_ok = r.hi is None or roll <= r.hi
        if lo_ok and hi_ok:
            return r.layer, r
    # negative layers can push the AC below 10: rolls between AC and 9 are then hits/exact
    total = ac_total(ac_parts)
    if roll == total:
        return EXACT, Range(EXACT, total, total)
    return (HIT, Range(HIT, total + 1, None)) if roll > total else (POSITION, Range(POSITION, None, BASE - 1))


def texts(path=TEXTS_PATH):
    """Owner texts by layer type (data, not code)."""
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)["texts"]
