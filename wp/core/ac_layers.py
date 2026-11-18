"""Defense ladder (RULES/defense_layers.md): which AC layer an attack roll landed in.

base = 10 + penalty (sum of ALL negative parts: low Dex, negative dodge sum, any typed or untyped
penalty). AC = base + size + dodge + insight + morale + competence + luck + circumstance + deflection
+ shield + armor (incl. parry) + flat + natural armor; every layer >= 0.
Rolls below the base: "position". Layer i covers rolls from base + (sum of earlier layers) to
base + (sum including it) - 1. Roll == AC: "exact" (hit, but no full damage; can be played as a
maneuver). Roll > AC: "hit". A layer with a zero bonus has an empty range and is skipped.
"""
import io
import json
import os
from dataclasses import dataclass
from typing import Optional

from wp.core.ac import PENALTY


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


def _split(ac_parts):
    """(penalty, [(layer, value), ...]) from ac.parts()."""
    penalty = sum(v for t, v in ac_parts if t == PENALTY)
    return penalty, [(t, v) for t, v in ac_parts if t != PENALTY]


def base(ac_parts):
    return BASE + _split(ac_parts)[0]


def ac_total(ac_parts):
    return BASE + sum(v for _, v in ac_parts)


def ladder(ac_parts):
    """All ranges: position (below the base), every layer with a positive bonus, exact, hit."""
    penalty, layers = _split(ac_parts)
    start = BASE + penalty
    out = [Range(POSITION, None, start - 1)]
    for t, v in layers:
        if v > 0:
            out.append(Range(t, start, start + v - 1))
        start += v
    out.append(Range(EXACT, start, start))
    out.append(Range(HIT, start + 1, None))
    return tuple(out)


def layer_for_roll(ac_parts, roll):
    """(layer, Range) for one attack roll total."""
    roll = int(roll)
    for r in ladder(ac_parts):
        if (r.lo is None or roll >= r.lo) and (r.hi is None or roll <= r.hi):
            return r.layer, r
    raise AssertionError("ladder has a gap")      # ranges cover every roll


def texts(path=TEXTS_PATH):
    """Owner texts by layer type (data, not code)."""
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)["texts"]
