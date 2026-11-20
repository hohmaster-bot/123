"""Iterative attack penalty (RULES/combat.md "Attack tag and iteration", package 16 C).

A separate NEGATIVE bonus line "iterative", never typed by the player: computed from Character.iterative_count
(attacks already used in this round's series, combat state).
- step: AttackRecord.iterative_step if set, else rules_settings.iterative_step (data, default -5);
  effects "iterative_penalty" make every step smaller: step = min(0, step + value) (value 2: -5 -> -3).
- penalty of the next attack = iterative_count * step (first attack of a series: 0).
- an effective status with ignores_iterative: no penalty.
- use_attack +1 to the counter; the zero-initiative tick (new round) and end_combat reset it; set_iterative_count
  sets it by hand.
Effect.when_iterative is stored only (no formula is defined for it yet, package 16 C).
"""
from wp.core import effects as ef
from wp.model import sheet_targets as stg

TARGET = "iterative_penalty"


def step(ch, record=None):
    base = ch.rules_settings.iterative_step
    if record is not None and record.iterative_step is not None:
        base = record.iterative_step
    return min(0, int(base) + stg.value(ch, TARGET))


def penalty(ch, record=None, count=None):
    """Penalty of the NEXT attack with this record (0 for the first attack of the series)."""
    if ef.ignores_iterative(ch.statuses):
        return 0
    n = ch.iterative_count if count is None else int(count)
    return n * step(ch, record)
