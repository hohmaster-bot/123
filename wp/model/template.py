"""Templates as an ability source (package 16 G6).

A template (race, class-like package, monster template...) can carry effects, hit dice, feats, resource pools and
statuses. add_template copies its feats / pools / statuses into the sheet marked with source "template:<tid>"; its
effects and hit dice are read from the stored template. remove_template removes the template and EVERY contribution
marked with its source.
"""
from dataclasses import dataclass
from typing import Tuple

from wp.core.effects import Effect

PREFIX = "template:"


@dataclass(frozen=True)
class Template:
    tid: str
    name: str
    effects: Tuple[Effect, ...] = ()
    hit_dice: Tuple[int, ...] = ()     # HP of each extra hit die (max(1, die + Con mod) each, like every die)
    feats: Tuple = ()                  # Feat records (copied into Character.feats on add)
    pools: Tuple = ()                  # ResourcePool records (copied into Character.pools)
    statuses: Tuple = ()               # Status records (copied into Character.statuses)
    text: str = ""


def source_of(tid):
    return PREFIX + tid
