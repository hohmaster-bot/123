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
from dataclasses import dataclass, field, replace
from typing import Dict, Optional, Tuple, Union

from wp.core import bonuses as bo
from wp.core import formula as fm
from wp.core.frozen import freeze_fields
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
    value: Union[int, str] = 0          # a number, a formula text (package 14 C) or "all"
    btype: str = bo.FLAT
    weapon: Optional[str] = None
    value_source: Optional[str] = None   # e.g. OVERLOAD: value = current overload
    dice: str = ""                     # extra dice (e.g. "1d6" on damage); not a number, shown as is
    note: str = ""                     # free text: "fire", "crit protection 25%" ... (any kind, D14)
    stat_mod: Optional[str] = None     # value = CURRENT modifier of this stat * multiplier (buffs.md, Q65)
    multiplier: float = 1
    block_type: str = ""               # block_bonus: bonus type or "any" (package 13 B)
    block_scope: Tuple[str, ...] = ()  # block_bonus: ("all",) (default when empty) or targets
    block_stats: Tuple[str, ...] = ()  # block_stat_bonus: stat names or ("all",)
    block_actions: Tuple[str, ...] = ()    # block_action: attack / move / spell_cast / heal / any (package 14 F)
    block_resources: Tuple[str, ...] = ()  # block_restore: hp / mana / spirit / balance / pool:<id> / any
    when_iterative: str = ""            # behaviour while an iterative penalty exists: STORED ONLY (package 16 C)
    stacks: bool = False               # DR entry: adds to the others (package 17, Q115); False = only the largest
    cells: Tuple[str, ...] = ()        # AC cell ids (package 24 B2): an AC / parry bonus counts only there; for the
                                       # targets parry_cells / shield_cells / dex_loss_cells: the cells added (value >= 0)
                                       # or removed (value < 0); () = every cell

    def resolve(self, context=None):
        """The effect's number: a fixed value, a context value (current overload), or the current
        modifier of a stat times the multiplier (rounded down; a negative modifier stays negative)."""
        ctx = context or {}
        if self.value == ALL:
            return ALL_VALUE
        if self.stat_mod is not None:
            return int(math.floor(ctx.get(stat_mod_key(self.stat_mod), 0) * self.multiplier))
        if isinstance(self.value, str):    # a formula (package 14 C); a broken one counts as 0
            try:
                return fm.evaluate(self.value, ctx)
            except fm.FormulaError:
                return 0
        if self.value_source is None:
            return int(self.value)
        return int(ctx.get(self.value_source, 0))

    def as_bonus(self, source="", context=None):
        return bo.Bonus(self.resolve(context), self.btype, self.target, self.weapon, source,
                        tuple(str(c) for c in self.cells))


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
    source_ref: str = ""               # charges follow this source (feat:<id> / item:<id> / pool:<id> / attack:<id> /
                                       # maneuver:<id> / template:<id>); "" = no recharge by rests (Q108, package 16 G3)
    full_ticks: int = 0                # full duration in ticks (per charge); used when activated
    charge_source: str = "own"         # per-round payment from: "own" (its charges) or a pool id (package 13 C)
    charge_per_round: int = 0          # paid every tick while active; cannot pay -> the status ends
    per_tick_restore: Dict[str, int] = field(default_factory=dict)   # {mana|spirit|balance|pool:<id>: n} per tick (pkg 14 F)
    cooldown_rounds: int = 0           # spend_charge starts this cooldown (package 14 B)
    cooldown_current: int = 0          # rounds left; the tick lowers it by 1
    hidden: bool = False               # DISPLAY ONLY: hidden on the panel, still active / ticking
    favorite: bool = False             # pinned for the panel / screen

    def __post_init__(self):
        freeze_fields(self, ("per_tick_restore",))     # read-only (package 16 A7)


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


def activate(status, ticks=None, cost=1):
    """Spend `cost` charges (if it has charges; 1 normally, charge_per_round for a per-round status with
    source "own", package 14 A), switch on, set ticks for TICKS duration. Not enough charges -> ValueError."""
    if not can_activate(status) or (status.charges is not None and status.charges.current < cost):
        raise ValueError("no charges left: %s" % status.name)
    charges = status.charges
    if charges is not None:
        charges = replace(charges, current=charges.current - cost)
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


OWN = "own"


def pay_round(status, pools):
    """Per-round payment of an ACTIVE status (buffs.md "Per-round cost", package 13 C), before its
    duration drops. Returns (status, pools). Cannot pay -> the status ends (inactive, entry stays)."""
    n = status.charge_per_round
    if not status.active or n <= 0:
        return status, pools
    if status.duration == TICKS and status.remaining <= 1:
        return status, pools       # it ends at this tick: no next round, nothing to pay (package 15, Q95)
    if status.charge_source == OWN:
        if status.charges is None or status.charges.current < n:
            return deactivate(status), pools
        return replace(status, charges=replace(status.charges, current=status.charges.current - n)), pools
    have = pools.get(status.charge_source)
    if have is None or have < n:
        return deactivate(status), pools
    out = dict(pools)
    out[status.charge_source] = have - n
    return status, out


def pay_all(statuses, pools):
    out = []
    for s in statuses:
        s, pools = pay_round(s, pools)
        out.append(s)
    return tuple(out), pools


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
