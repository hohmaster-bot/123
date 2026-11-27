"""A catalog training the character bought (package 37, owner decision 2): kind trainings of the catalog.

TrainingTaken(tid, name, units, effects, module, held_by, held_kept): the units bought and the effect of ONE unit
(a snapshot of the entry: a later catalog change never changes what was bought). On read the effect counts units times
and is shown as one source row "name x units" (effects(record)). No refund.
"""
from dataclasses import dataclass, replace
from typing import Tuple

from wp.core.effects import Effect


@dataclass(frozen=True)
class TrainingTaken:
    tid: str
    name: str = ""
    units: int = 0
    effects: Tuple[Effect, ...] = ()   # the effect of one unit
    module: str = ""
    held_by: str = ""                  # package 37 (decision 5): a training may be held by a holder too
    held_kept: bool = True


def scaled(e, units):
    """The effect of `units` units (a number times units; a formula "(f) * units")."""
    if isinstance(e.value, str):
        return replace(e, value="(%s) * %d" % (e.value, int(units)))
    return replace(e, value=int(e.value) * int(units))


def effects(records):
    """(source id, effects) of the bought trainings: source "training:<id>"."""
    return [("training:" + r.tid, tuple(scaled(e, r.units) for e in r.effects)) for r in records if r.units > 0]
