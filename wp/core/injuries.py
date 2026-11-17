"""Trauma points (OT), injuries, stat damage (RULES/injuries.md, RULES/stats.md).

OT are changed only by player actions: taking an injury, spending comfort or
attention, or manual delete. Rest never touches OT (rest.md, injuries.md).
Pure functions: they return new values and never mutate inputs.
"""
from dataclasses import dataclass, replace

from wp.core.damage import Pool

LIGHT = "light"
MEDIUM = "medium"
HEAVY = "heavy"

# severity -> (OT removed, base healing rating RL)
SEVERITY = {
    LIGHT: (2, 3),
    MEDIUM: (5, 2),
    HEAVY: (12, 1),
}

COMFORT_OT = 3          # 1 comfort removes 3 OT
ATTENTION_MIN = 2       # attention value = max(2, Str mod)


@dataclass(frozen=True)
class Injury:
    name: str
    severity: str
    heal_rating: int
    permanent: bool = False
    charges: Pool = Pool(0, 0)   # injury charges: never restored by rest


def attention_value(str_mod):
    """What 1 attention is worth for OT removal and RL: max(2, Str modifier)."""
    return max(ATTENTION_MIN, int(str_mod))


def take_injury(trauma, severity, name=""):
    """Take a standard injury to remove OT. Returns (new_trauma, Injury).

    Needs at least the injury's OT cost (RULES: the injury is traded for OT).
    """
    if severity not in SEVERITY:
        raise ValueError("unknown severity: %r" % (severity,))
    cost, rl = SEVERITY[severity]
    if trauma < cost:
        raise ValueError("not enough OT: need %d, have %d" % (cost, trauma))
    return trauma - cost, Injury(name=name or severity, severity=severity,
                                 heal_rating=rl)


def spend_comfort_for_ot(trauma, comfort):
    """1 comfort -> -3 OT (OT never below 0). Returns (new_trauma, new_comfort)."""
    if comfort.current < 1:
        raise ValueError("no comfort")
    if trauma <= 0:
        raise ValueError("no OT to remove")
    return max(0, trauma - COMFORT_OT), replace(comfort, current=comfort.current - 1)


def spend_attention_for_ot(trauma, attention, str_mod):
    """1 attention -> -max(2, Str mod) OT. Returns (new_trauma, new_attention)."""
    if attention.current < 1:
        raise ValueError("no attention")
    if trauma <= 0:
        raise ValueError("no OT to remove")
    return (max(0, trauma - attention_value(str_mod)),
            replace(attention, current=attention.current - 1))


def raise_heal_rating(injury, attention, str_mod):
    """1 attention -> RL + max(2, Str mod). Returns (new_injury, new_attention)."""
    if attention.current < 1:
        raise ValueError("no attention")
    return (replace(injury, heal_rating=injury.heal_rating + attention_value(str_mod)),
            replace(attention, current=attention.current - 1))


def remove_injury(injuries, index):
    """Remove an injury by hand. OT are NOT given back (buffs.md test)."""
    if not 0 <= index < len(injuries):
        raise IndexError("injury index out of range")
    return tuple(injuries[:index]) + tuple(injuries[index + 1:])


def delete_ot(trauma, n):
    """Manual OT delete (always allowed). Never below 0."""
    if n < 0:
        raise ValueError("n must be >= 0")
    return max(0, trauma - n)


# ------------------------------------------------------------- stat damage

def damage_stat(stat, n=1):
    """Stat damage lowers CURRENT only; max stays (stats.md)."""
    if n < 0:
        raise ValueError("n must be >= 0")
    return replace(stat, current=stat.current - n)


def restore_stat(stat, n=1):
    """Restore stat damage (e.g. short rest 1 BP -> 1 point). Never above max."""
    if n < 0:
        raise ValueError("n must be >= 0")
    return replace(stat, current=min(stat.max, stat.current + n))


def permanent_stat_damage(stat, n=1):
    """Permanent damage (curse/injury) lowers MAX and CURRENT by n (stats.md [OWNER, corrected])."""
    if n < 0:
        raise ValueError("n must be >= 0")
    return Pool(current=stat.current - n, max=stat.max - n)


def stat_damaged(stat):
    return stat.current < stat.max
