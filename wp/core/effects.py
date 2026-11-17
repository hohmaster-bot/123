"""One effect system for every sheet part (D14, RULES/buffs.md).

Status = buff = debuff = situational. A status holds:
  - timed part: typed bonuses (target, value, bonus type) via bonuses.py;
  - one-shot part: applied once on activation (e.g. temp HP);
  - per-tick HP change (DoT < 0, heal > 0), applied in the zero-initiative phase;
  - condition: always / in combat only / out of combat only;
  - duration: N ticks (typed in by hand), until end of combat, infinite, instant;
  - charges (current/max); no charges left -> cannot activate;
  - flags: temp HP stacks, ignores iterative penalty; active / off.
Pure functions, frozen data.
"""
from dataclasses import dataclass, replace
from typing import Optional, Tuple

from wp.core import bonuses as bo
from wp.core.damage import Pool

ALWAYS = "always"
IN_COMBAT = "in_combat"
OUT_OF_COMBAT = "out_of_combat"

TICKS = "ticks"
END_OF_COMBAT = "end_of_combat"
INFINITE = "infinite"
INSTANT = "instant"

TEMP_HP = "temp_hp"


OVERLOAD = "overload"      # value source: the current overload number


@dataclass(frozen=True)
class Effect:
    target: str
    value: int = 0
    btype: str = bo.FLAT
    weapon: Optional[str] = None
    value_source: Optional[str] = None   # e.g. OVERLOAD: value = current overload

    def resolve(self, context=None):
        """The effect's number: fixed value, or read from the context (buffs.md)."""
        if self.value_source is None:
            return int(self.value)
        return int((context or {}).get(self.value_source, 0))

    def as_bonus(self, source="", context=None):
        return bo.Bonus(self.resolve(context), self.btype, self.target, self.weapon, source)


@dataclass(frozen=True)
class OneShot:
    resource: str          # e.g. TEMP_HP
    amount: int


@dataclass(frozen=True)
class Status:
    name: str
    sid: str = ""                      # stable id (D7)
    effects: Tuple[Effect, ...] = ()
    one_shot: Tuple[OneShot, ...] = ()
    per_tick_hp: int = 0               # DoT < 0, heal per tick > 0
    dot_type: str = "untyped"          # damage type of the DoT part
    condition: str = ALWAYS
    duration: str = INFINITE
    remaining: int = 0                 # ticks left (duration == TICKS)
    charges: Optional[Pool] = None     # None = no charges
    temp_hp_stacks: bool = False
    ignores_iterative: bool = False
    lowers_balance_cap: bool = False   # DoT flag: its hits lower the balance cap in combat
    temp_hp_left: int = 0              # temp HP given by this status, lasting as long as the status
    active: bool = True
    source: str = ""


# ------------------------------------------------------------- reading

def condition_ok(status, in_combat):
    if status.condition == IN_COMBAT:
        return bool(in_combat)
    if status.condition == OUT_OF_COMBAT:
        return not in_combat
    return True


def is_effective(status, in_combat):
    """Active, condition met, not expired."""
    if not status.active or not condition_ok(status, in_combat):
        return False
    if status.duration == TICKS and status.remaining <= 0:
        return False
    return status.duration != INSTANT


def bonuses_from(statuses, in_combat, context=None):
    """Typed bonuses of every effective status (feed into bonuses.total).
    context: values effects may read, e.g. {OVERLOAD: 3}."""
    out = []
    for s in statuses:
        if is_effective(s, in_combat):
            out.extend(e.as_bonus(s.name, context) for e in s.effects)
    return tuple(out)


def ignores_iterative(statuses, in_combat):
    """True if an effective status carries the 'ignores iterative penalty' flag."""
    return any(s.ignores_iterative for s in statuses if is_effective(s, in_combat))


# ------------------------------------------------------------- changing

def can_activate(status):
    return status.charges is None or status.charges.current > 0


def activate(status, ticks=None):
    """Spend one charge (if any), switch on, set ticks for TICKS duration.
    No charges left -> ValueError."""
    if not can_activate(status):
        raise ValueError("no charges left: %s" % status.name)
    charges = status.charges
    if charges is not None:
        charges = replace(charges, current=charges.current - 1)
    remaining = status.remaining if ticks is None else int(ticks)
    return replace(status, charges=charges, active=True, remaining=remaining)


def set_active(status, on):
    return replace(status, active=bool(on))


def apply_temp_hp(current_temp, amount, stacks):
    """Temp HP from a status: adds if the flag says so, else the higher value."""
    amount = int(amount)
    return current_temp + amount if stacks else max(current_temp, amount)


def apply_one_shot(status, temp_hp):
    """Apply the one-shot part. Returns new temp HP (other resources: caller)."""
    for o in status.one_shot:
        if o.resource == TEMP_HP:
            temp_hp = apply_temp_hp(temp_hp, o.amount, status.temp_hp_stacks)
    return temp_hp


def tick_duration(status):
    """Duration -1 for TICKS statuses. Returns the status, or None if it expired."""
    if status.duration != TICKS:
        return status
    left = status.remaining - 1
    if left <= 0:
        return None
    return replace(status, remaining=left)


def tick_all(statuses):
    """Step 1 of the zero-initiative phase: durations -1, expired removed."""
    out = []
    for s in statuses:
        t = tick_duration(s)
        if t is not None:
            out.append(t)
    return tuple(out)


def end_combat(statuses):
    """Remove 'until end of combat' statuses."""
    return tuple(s for s in statuses if s.duration != END_OF_COMBAT)


def holds_temp_hp(status):
    """Temp HP from a status with its own duration (ticks / infinite) lives with the status;
    instant and 'until end of combat' temp HP go to the combat pool."""
    return status.duration in (TICKS, INFINITE)


def drop_instant(statuses):
    """Instant statuses are applied once and not kept."""
    return tuple(s for s in statuses if s.duration != INSTANT)
