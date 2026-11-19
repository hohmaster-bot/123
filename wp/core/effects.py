"""One effect system for every sheet part (D14, RULES/buffs.md).

Status = buff = debuff = situational. A status holds:
  - timed part: typed bonuses (target, value, bonus type) via bonuses.py;
  - one-shot part: applied once on activation (e.g. temp HP);
  - per-tick HP change (DoT < 0, heal > 0), applied in the zero-initiative phase;
  - no combat-only condition (owner, package 8): ticks are the combat clock; DoT, regen and
    buff durations all count down the same way, long effects are lowered by hand;
  - duration: N ticks (typed in by hand), until end of combat, infinite, instant;
  - charges (current/max), duration per charge (full_ticks); no cost of its own (Q69);
    no charges left -> cannot activate;
  - flags: temp HP stacks, ignores iterative penalty.
Container (buffs.md, package 11): a status is either ACTIVE or not; no on/off toggle, no pause.
An active status with a duration runs it out (ticks) unless removed by hand; the end of its
duration makes it inactive and the entry stays. An inactive status gives no effects and does
not tick. hidden / favorite are display only.
Pure functions, frozen data.
"""
import math
from dataclasses import dataclass, replace
from typing import Optional, Tuple

from wp.core import bonuses as bo
from wp.core.damage import Pool

TICKS = "ticks"
END_OF_COMBAT = "end_of_combat"
INFINITE = "infinite"
INSTANT = "instant"

TEMP_HP = "temp_hp"


OVERLOAD = "overload"      # value source: the current overload number
STAT_MOD = "stat_mod:"     # context key prefix: "stat_mod:str" = the CURRENT Str modifier
ALL = "all"                # value "all": unlimited (e.g. ignore the armor slowdown completely, gear.md)
ALL_VALUE = 10 ** 6        # what "all" resolves to: more than any real number on the sheet


def stat_mod_key(stat):
    return STAT_MOD + stat


@dataclass(frozen=True)
class Effect:
    target: str
    value: int = 0
    btype: str = bo.FLAT
    weapon: Optional[str] = None
    value_source: Optional[str] = None   # e.g. OVERLOAD: value = current overload
    dice: str = ""                     # extra dice (e.g. "1d6" on damage); not a number, shown as is
    note: str = ""                     # free text: "fire", "crit protection 25%" ... (any kind, D14)
    stat_mod: Optional[str] = None     # value = CURRENT modifier of this stat * multiplier (buffs.md, Q65)
    multiplier: float = 1

    def resolve(self, context=None):
        """The effect's number: a fixed value, a context value (current overload), or the current
        modifier of a stat times the multiplier (rounded down; a negative modifier stays negative)."""
        ctx = context or {}
        if self.value == ALL:
            return ALL_VALUE
        if self.stat_mod is not None:
            return int(math.floor(ctx.get(stat_mod_key(self.stat_mod), 0) * self.multiplier))
        if self.value_source is None:
            return int(self.value)
        return int(ctx.get(self.value_source, 0))

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
    duration: str = INFINITE
    remaining: int = 0                 # ticks left (duration == TICKS)
    charges: Optional[Pool] = None     # None = no charges
    temp_hp_stacks: bool = False
    ignores_iterative: bool = False
    lowers_balance_cap: bool = False   # DoT flag: its hits lower the balance cap in combat
    temp_hp_left: int = 0              # temp HP given by this status, lasting as long as the status
    active: bool = True
    source: str = ""
    condition_tag: str = "none"        # display only: none / combat_only / out_of_combat_only (no effect)
    full_ticks: int = 0                # full duration in ticks (per charge); used when activated
    hidden: bool = False               # DISPLAY ONLY: hidden on the panel, still active / ticking
    favorite: bool = False             # pinned for the panel / screen


# ------------------------------------------------------------- reading

def is_effective(status):
    """Active and not expired."""
    if not status.active:
        return False
    if status.duration == TICKS and status.remaining <= 0:
        return False
    return status.duration != INSTANT


def bonuses_from(statuses, context=None):
    """Typed bonuses of every effective status (feed into bonuses.total).
    context: values effects may read, e.g. {OVERLOAD: 3}."""
    out = []
    for s in statuses:
        if is_effective(s):
            out.extend(e.as_bonus(s.name, context) for e in s.effects)
    return tuple(out)


def ignores_iterative(statuses):
    """True if an effective status carries the 'ignores iterative penalty' flag."""
    return any(s.ignores_iterative for s in statuses if is_effective(s))


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
    if ticks is not None:
        remaining = int(ticks)
    else:
        remaining = status.full_ticks or status.remaining
    return replace(status, charges=charges, active=True, remaining=remaining)


def deactivate(status):
    """End the status now: inactive, no time left, its temp HP gone; the entry stays."""
    return replace(status, active=False, remaining=0, temp_hp_left=0)


def set_active(status, on):
    return replace(status, active=True) if on else deactivate(status)


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
    """Duration -1 for an ACTIVE TICKS status; at 0 it becomes inactive (the entry stays).
    An inactive status does not tick."""
    if status.duration != TICKS or not status.active:
        return status
    left = status.remaining - 1
    if left <= 0:
        return deactivate(status)
    return replace(status, remaining=left)


def expired_now(before, after):
    return before.active and not after.active


def tick_all(statuses):
    """Step 1 of the zero-initiative phase: durations -1; expired ones become inactive."""
    return tuple(tick_duration(s) for s in statuses)


def end_combat(statuses):
    """'Until end of combat' statuses become inactive (entries stay)."""
    return tuple(deactivate(s) if s.duration == END_OF_COMBAT and s.active else s for s in statuses)


def holds_temp_hp(status):
    """Temp HP from a status with a duration (ticks / until end of combat / infinite) lives with
    the status and goes when it ends (resources.md, package 8 R1); an instant status keeps nothing,
    its temp HP go to the "by button" pool (until the short rest)."""
    return status.duration in (TICKS, END_OF_COMBAT, INFINITE)


def drop_instant(statuses):
    """Instant statuses are applied once and not kept."""
    return tuple(s for s in statuses if s.duration != INSTANT)
