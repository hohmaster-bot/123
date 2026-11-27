"""Rerolls (package 38, owner decisions 6, 7; RULES/buffs.md "Rerolls").

Any carrier (feat / race ability, item, status, quirk, injury, training) may grant reroll charges: Reroll(rrid, name,
charges_max, charges_current, recharge). The recharge rule is one of the usage rules (short_rest, long_rest,
combat_start, combat_end, manual): rests and the combat events refill it like usage charges (wp/model/usage.py
recharge); "manual" only by hand. The program never rolls dice: it only counts what is left (spend_reroll).
from_data(list) -> the Reroll records of catalog data {"id", "name", "charges", "recharge"}.
"""
from dataclasses import dataclass, replace

RECHARGES = ("short_rest", "long_rest", "combat_start", "combat_end", "manual")


@dataclass(frozen=True)
class Reroll:
    rrid: str                          # id inside the carrier (from the data or made by the program)
    name: str = ""
    charges_max: int = 1
    charges_current: int = 1           # stored base value (what is left)
    recharge: str = "long_rest"        # one of RECHARGES


def from_data(rows):
    out = []
    for i, d in enumerate(rows or ()):
        n = int(d.get("charges", 1))
        rule = str(d.get("recharge", "long_rest"))
        if rule not in RECHARGES:
            raise ValueError("unknown reroll recharge %r" % rule)
        out.append(Reroll(str(d.get("id") or "reroll_%d" % (i + 1)), str(d.get("name", "")), n, n, rule))
    return tuple(out)


def refill(rolls, rules):
    """The rerolls whose rule is in rules go back to max (an over-max count is not lowered)."""
    return tuple(replace(r, charges_current=max(r.charges_current, r.charges_max)) if r.recharge in rules else r
                 for r in rolls)
