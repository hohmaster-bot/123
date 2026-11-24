"""Experience (package 26 C; RULES/narrative.md "Experience"): a tracked counter with a log and notes, a goal
(next_level_at, typed by the player: not a rule, no threshold table) and a level history written by level_up.
No automatic level-up. The total is derived from the log (base values only): removing an entry recomputes it.
Ids (xid / lid) come from Character.xp_counter and are never reused. `at` = the time stamp the Session gives
(files.stamp of its clock; "" when a command runs without a Session).
"""
from dataclasses import dataclass
from typing import Optional

PCT = 100                              # a percent


@dataclass(frozen=True)
class XpEntry:
    xid: str
    amount: int = 0                    # may be negative
    note: str = ""
    at: str = ""


@dataclass(frozen=True)
class LevelRecord:
    lid: str
    level: int = 1
    experience_total: int = 0          # the total at the moment of level_up
    hp_roll: int = 0
    note: str = ""
    at: str = ""


def total(ch):
    return sum(int(e.amount) for e in ch.xp_log)


def progress_pct(ch) -> Optional[int]:
    """total * 100 // next_level_at (0 .. 100; None without a goal)."""
    if not ch.next_level_at or ch.next_level_at <= 0:
        return None
    return max(0, min(PCT, total(ch) * PCT // int(ch.next_level_at)))


def view(ch):
    return {"total": total(ch), "next_level_at": ch.next_level_at, "progress_pct": progress_pct(ch),
            "log": tuple(reversed(ch.xp_log)), "level_history": ch.level_history}
