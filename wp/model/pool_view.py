"""Resource pool values on read (RULES/resources.md "Resource pools"). Computed on read (D6).

max_of: the pool's max (a number, or a formula string evaluated on the current sheet, package 14 C).
current: the stored current as it is, never below 0; above the max it is shown as is (resources.md "Over max",
package 16 A6: no clamp).
"""
from wp.model import formulas as fx


def max_of(ch, pool):
    """Pool max on read; a bad formula never raises here (it counts as 0, see formulas.safe_value)."""
    from wp.model import sheet_targets as stg
    return max(0, fx.safe_value(pool.max, ch) + stg.value(ch, stg.POOL_MAX + pool.pid))


def current(ch, pool):
    return max(0, pool.current)
