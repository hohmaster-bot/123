"""Pain (RULES/resources.md "Pain").

Pain is a list of entries (amount, source, permanent or temporary); total = sum of
entries + pain from HP below 0 (derived, never stored). Death when total >= cap
(default 8; race/template/feat change it, e.g. 12). Penalty: -1 per pain to ALL
rolls except the lucky attack. Some races ignore pain, some get no penalty from it,
some get a damage bonus per pain.
"""
from dataclasses import dataclass, replace
from typing import Tuple

from wp.core import bonuses as bo
from wp.core.derived import pain_from_hp

DEFAULT_CAP = 8


@dataclass(frozen=True)
class PainEntry:
    amount: int
    source: str = ""
    permanent: bool = False     # injuries, curses: rest never removes it


@dataclass(frozen=True)
class PainProfile:
    cap: int = DEFAULT_CAP
    ignores_pain: bool = False       # pain gives no penalty and no death
    no_penalty: bool = False         # pain gives no penalty (death still counts)
    damage_per_pain: int = 0         # e.g. race: +1 damage per pain
    penalty_per_pain: int = 1        # roll penalty per pain point (package 17: effect pain_penalty_per_pain)


def entries_total(entries):
    return sum(int(e.amount) for e in entries)


def total_pain(entries, hp):
    """Sum of pain entries + pain from HP below 0 (floor(-hp/3))."""
    return entries_total(entries) + pain_from_hp(hp)


def is_dead(total, profile=PainProfile()):
    if profile.ignores_pain:
        return False
    return int(total) >= profile.cap


def penalty(total, profile=PainProfile()):
    """Roll penalty from pain: -penalty_per_pain per pain (default 1; 0 if the profile ignores it)."""
    if profile.ignores_pain or profile.no_penalty:
        return 0
    return -int(total) * max(0, int(profile.penalty_per_pain))


def penalty_bonus(total, profile=PainProfile()):
    """Pain penalty as a FLAT bonus on all rolls (ROLLS excludes lucky and crit)."""
    return bo.Bonus(penalty(total, profile), bo.FLAT, bo.ROLLS, source="pain")


def damage_bonus(total, profile=PainProfile()):
    """Race bonus to damage per pain."""
    return int(profile.damage_per_pain) * int(total)


def add(entries, amount, source="", permanent=False):
    """Add pain (e.g. as the price of activating an ability or item)."""
    return tuple(entries) + (PainEntry(int(amount), source, permanent),)


def remove(entries, n=1):
    """Remove n pain from TEMPORARY entries (newest first). Permanent pain stays."""
    n = int(n)
    out = list(entries)
    for i in range(len(out) - 1, -1, -1):
        if n <= 0:
            break
        e = out[i]
        if e.permanent or e.amount <= 0:
            continue
        take = min(n, e.amount)
        n -= take
        out[i] = replace(e, amount=e.amount - take)
    if n > 0:
        raise ValueError("not enough temporary pain to remove")
    return tuple(e for e in out if e.amount > 0)


def clear_temporary(entries):
    """Long rest: all pain except permanent (injuries, curses)."""
    return tuple(e for e in entries if e.permanent)
