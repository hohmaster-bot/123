"""Resource pool values on read (RULES/resources.md "Resource pools"). Computed on read (D6).

max_of: the pool's max (a number, or a formula string evaluated on the current sheet, package 14 C).
current: the stored current, clamped to the max on read (the stored number is not rewritten).
"""
from wp.model import formulas as fx


def max_of(ch, pool):
    """Pool max on read; a bad formula never raises here (it counts as 0, see formulas.safe_value)."""
    return max(0, fx.safe_value(pool.max, ch))


def current(ch, pool):
    return max(0, min(pool.current, max_of(ch, pool)))
