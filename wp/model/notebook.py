"""Narrative notebook (RULES/narrative.md, package 16 F): notes for the player, no mechanics unless stated.

- Quest, Story: plain notes.
- Court: level + tier, shown like "Skull 5t1" (label()).
- Quirk: a narrative ability; its effects work like a feat's while it is not burned. "Burn" = grey, status
  "destroyed", reversible by hand; deleted only by hand.
- Lens: a counter 1..X shown "11/15"; strictly 0..X (commands clamp); 0 = red end state, X = green end state.
- Drive: level 0..5; each drive at level 4+ gives +1 attention at the end of a cycle (the only income role).
Ids are made by the program (D7).
"""
from dataclasses import dataclass
from typing import Tuple

from wp.core.effects import Effect
from wp.rules_data import rules as rd

DRIVE_MAX = rd.ref("narrative.drive_max")
DRIVE_ATTENTION_LEVEL = rd.ref("attention.drive_level")
LENS_START = rd.ref("narrative.lens_start")
RED = "red"
GREEN = "green"
DESTROYED = "destroyed"


@dataclass(frozen=True)
class Quest:
    qid: str
    name: str
    text: str = ""
    giver: str = ""                    # court / drive / lens id or free text
    done: bool = False


@dataclass(frozen=True)
class Story:
    stid: str
    name: str
    text: str = ""


@dataclass(frozen=True)
class Court:
    cid: str
    name: str
    level: int = 0
    tier: int = 0
    note: str = ""

    def label(self):
        return "%s %dt%d" % (self.name, self.level, self.tier)


@dataclass(frozen=True)
class Quirk:
    kid: str
    name: str
    seedling: str = ""                 # quirk fields (training.md "Seeds, quirks, stories")
    court: str = ""
    focus: str = ""
    story: str = ""
    text: str = ""
    effects: Tuple[Effect, ...] = ()   # like a feat: active while the quirk is not burned
    burned: bool = False               # "burn": grey, status destroyed, reversible by hand


@dataclass(frozen=True)
class Lens:
    lid: str
    name: str
    value: int = rd.default("narrative.lens_start")
    max: int = 1
    text: str = ""


@dataclass(frozen=True)
class Drive:
    did: str
    name: str
    level: int = 0
    text: str = ""


# collection name on Character -> (record type, id field)
KINDS = {
    "quest": ("quests", Quest, "qid"),
    "story": ("stories", Story, "stid"),
    "court": ("courts", Court, "cid"),
    "quirk": ("quirks", Quirk, "kid"),
    "lens": ("lenses", Lens, "lid"),
    "drive": ("drives", Drive, "did"),
}


def lens_state(lens):
    if lens.value <= 0:
        return RED
    if lens.value >= lens.max:
        return GREEN
    return ""


def quirk_state(quirk):
    return DESTROYED if quirk.burned else ""


def clamp_lens(value, mx):
    return max(0, min(int(mx), int(value)))
