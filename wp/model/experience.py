"""Experience (package 26 C, package 33; RULES/narrative.md "Experience", progression.md "Level up"): a tracked
counter with a log and notes and a level history written by level_up. The total is derived from the log (base values
only): removing an entry recomputes it. Package 33 (owner): a level-up needs and SPENDS exp.level_cost (1000); the
total never goes above exp.max_banked (1999): an entry that would pass it counts only up to it (the entry keeps what
was entered). The goal shown is always the constant (the hand-typed goal is retired).
Ids (xid / lid) come from Character.xp_counter and are never reused. `at` = the time stamp the Session gives
(files.stamp of its clock; "" when a command runs without a Session).
"""
from dataclasses import dataclass
from typing import Optional

from wp.rules_data import rules as rd

PCT = 100                              # a percent
LEVEL_COST = rd.ref("exp.level_cost")
MAX_BANKED = rd.ref("exp.max_banked")
KIND_LEVEL_UP = "level_up"             # the entry that pays for a level-up


@dataclass(frozen=True)
class XpEntry:
    xid: str
    amount: int = 0                    # the amount COUNTED (may be negative); the total is the sum of these
    note: str = ""
    at: str = ""
    entered: Optional[int] = None      # what the player typed, kept when the cap counted less (package 33)
    kind: str = ""                     # "" = a plain entry, "level_up" = the cost of a level-up


@dataclass(frozen=True)
class LevelRecord:
    lid: str
    level: int = 1
    experience_total: int = 0          # the total at the moment of level_up (before the cost is spent)
    hp_roll: int = 0
    note: str = ""
    at: str = ""


def total(ch):
    return sum(int(e.amount) for e in ch.xp_log)


def counted(current_total, amount):
    """How much of `amount` counts: the total never passes exp.max_banked. A negative amount counts whole; a total
    already at or above the cap counts nothing more."""
    amount = int(amount)
    if amount <= 0:
        return amount
    return max(0, min(amount, int(MAX_BANKED) - int(current_total)))


def can_level_up(ch):
    return total(ch) >= int(LEVEL_COST)


def progress_pct(ch) -> int:
    """total * 100 // exp.level_cost, 0 .. 100."""
    return max(0, min(PCT, total(ch) * PCT // int(LEVEL_COST)))


def view(ch):
    return {"total": total(ch), "next_level_at": int(LEVEL_COST), "progress_pct": progress_pct(ch),
            "can_level_up": can_level_up(ch), "max_banked": int(MAX_BANKED),
            "log": tuple(reversed(ch.xp_log)), "level_history": ch.level_history}
