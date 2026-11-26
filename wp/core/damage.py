"""Damage pipeline and resource ops (RULES/resources.md, D5, D15).

Pipeline for one hit (a hit may have several typed parts):
  1. percent reduction by damage type (25/50/75 %), rounded UP
  2. flat reduction by damage type (DR = flat vs PHYSICAL; does not touch fire)
  3. temp HP
  4. temp-HP analogs (e.g. racial mana), in the configured order
  5. HP; only the part reaching HP touches balance.
Balance floors at 0. Overflow = part reaching HP - balance -> trauma points (OT);
+1 pain per hit with overflow > 0 (also when balance is already 0).
HP always loses the full part that reaches it and may go below 0.

Everything here is pure: functions take values and return new values.
"""
from dataclasses import dataclass, field, replace
from typing import Dict, Tuple

PHYSICAL = "physical"


# --------------------------------------------------------------- resources

@dataclass(frozen=True)
class Pool:
    """A resource with current and max (HP, balance, mana, spirit, comfort...)."""
    current: int
    max: int

    @property
    def over_max(self):
        """True when current > max (manual set / overfill). Shown red, never trimmed."""
        return self.current > self.max


def restore(pool, amount):
    """Gameplay restore (regen, heal, rest, tick): never raises above max.

    A pool that is already over max stays as it is (not trimmed, not raised).
    """
    amount = int(amount)
    if amount < 0:
        raise ValueError("restore amount must be >= 0")
    if pool.current >= pool.max:
        return pool
    return replace(pool, current=min(pool.max, pool.current + amount))


def set_value(pool, value):
    """Manual set / overfill: no clamp. `over_max` is True if value > max."""
    return replace(pool, current=int(value))


# ------------------------------------------------------------------ damage

@dataclass(frozen=True)
class DamagePart:
    amount: int
    dtype: str = PHYSICAL


@dataclass(frozen=True)
class Reductions:
    """Reductions taken from the sheet's effects, by damage type.

    percent: dtype -> 25 / 50 / 75 (percent removed).
    flat:    dtype -> points removed (DR is flat[PHYSICAL]).
    One value per type: overlap of two reductions on one part is not modeled
    (the player picks which applies before taking damage).
    """
    percent: Dict[str, int] = field(default_factory=dict)
    flat: Dict[str, int] = field(default_factory=dict)
    modifier: Dict[str, int] = field(default_factory=dict)   # signed % per type: -100 immune, +50 takes 50% more
    order: Tuple[str, ...] = ("percent", "flat", "modifier")  # steps of one part (rules_settings.damage_order)


@dataclass(frozen=True)
class Absorber:
    """A temp-HP analog (e.g. racial mana pool). Absorbs 1:1, does not hit balance. Package 36 (P2.9): dtypes = the
    damage types it takes (() = every type: the static pool of an azana takes only electricity)."""
    name: str
    current: int
    dtypes: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Vitals:
    hp: Pool
    balance: Pool
    temp_hp: int = 0
    absorbers: Tuple[Absorber, ...] = ()
    pain: int = 0          # stored pain counter (not pain from HP, that is derived)
    trauma: int = 0        # trauma points (OT)


@dataclass(frozen=True)
class DamageReport:
    after_reduction: int   # total after percent + flat
    temp_hp_loss: int
    absorbed: Tuple[Tuple[str, int], ...]
    hp_loss: int
    balance_loss: int
    overflow: int          # -> trauma points
    pain_added: int


def ceil_div(a, b):
    """Integer ceil(a / b) for a >= 0, b > 0."""
    return -(-a // b)


def apply_percent(amount, percent):
    """Remove `percent` % of amount; damage is never fractional, round UP."""
    amount = int(amount)
    percent = int(percent)
    if not 0 <= percent <= 100:
        raise ValueError("percent must be 0..100")
    return ceil_div(amount * (100 - percent), 100)


PERCENT = "percent"
FLAT = "flat"
MODIFIER = "modifier"


def apply_modifier(amount, pct):
    """Signed percent modifier (package 17): amount * (100 + pct) / 100, rounded UP (against the player); -100 = 0."""
    pct = max(-100, int(pct))
    return max(0, ceil_div(int(amount) * (100 + pct), 100))


def reduce_part(part, reductions):
    """Steps for one part in reductions.order (default: percent reduction, flat, signed modifier), each by the part's
    own type. Never below 0."""
    if part.amount < 0:
        raise ValueError("damage amount must be >= 0")
    amount = part.amount
    for step in reductions.order:
        if step == PERCENT:
            amount = apply_percent(amount, reductions.percent.get(part.dtype, 0))
        elif step == FLAT:
            amount = max(0, amount - int(reductions.flat.get(part.dtype, 0)))
        elif step == MODIFIER:
            amount = apply_modifier(amount, reductions.modifier.get(part.dtype, 0))
        else:
            raise ValueError("unknown damage step %r" % (step,))
    return max(0, amount)


def reduce_hit(parts, reductions=None):
    """Steps 1-2 for a whole hit: each part by its own type, then summed."""
    reductions = reductions or Reductions()
    return sum(reduce_part(p, reductions) for p in parts)


def _absorb(vitals, amount, typed=None):
    """Steps 3-4: temp HP, then absorbers in order. Returns (vitals, left, temp_loss, absorbed).
    typed = [[dtype, amount], ...] of the reduced parts (package 36): a typed absorber takes only its types."""
    typed = [[t, a] for t, a in (typed or [[None, amount]])]
    temp_loss = min(amount, vitals.temp_hp)
    rest = temp_loss
    for part in typed:                 # temp HP takes any type, part by part
        t = min(rest, part[1])
        part[1] -= t
        rest -= t
    new_abs = []
    absorbed = []
    for ab in vitals.absorbers:
        cap = max(0, ab.current)
        take = 0
        for part in typed:
            if ab.dtypes and part[0] not in ab.dtypes:
                continue
            t = min(cap - take, part[1])
            part[1] -= t
            take += t
        new_abs.append(replace(ab, current=ab.current - take))
        if take:
            absorbed.append((ab.name, take))
    left = sum(a for _t, a in typed)
    vitals = replace(vitals, temp_hp=vitals.temp_hp - temp_loss,
                     absorbers=tuple(new_abs))
    return vitals, left, temp_loss, tuple(absorbed)


def take_hit(vitals, parts, reductions=None):
    """Apply one hit (one or more typed parts). Returns (new_vitals, DamageReport)."""
    reductions = reductions or Reductions()
    typed = [[p.dtype, reduce_part(p, reductions)] for p in parts]
    total = sum(a for _t, a in typed)
    vitals, to_hp, temp_loss, absorbed = _absorb(vitals, total, typed)

    bal = max(0, vitals.balance.current)
    balance_loss = min(to_hp, bal)
    overflow = to_hp - balance_loss
    pain_added = 1 if overflow > 0 else 0

    vitals = replace(
        vitals,
        hp=replace(vitals.hp, current=vitals.hp.current - to_hp),
        balance=replace(vitals.balance, current=bal - balance_loss),
        pain=vitals.pain + pain_added,
        trauma=vitals.trauma + overflow,
    )
    report = DamageReport(after_reduction=total, temp_hp_loss=temp_loss,
                          absorbed=absorbed, hp_loss=to_hp,
                          balance_loss=balance_loss, overflow=overflow,
                          pain_added=pain_added)
    return vitals, report


def balance_hit(vitals, amount):
    """Damage straight to the balance (empty-hand parry, owner): HP untouched, no percent/DR.
    Balance floors at 0; overflow -> OT and +1 pain. Returns (new_vitals, DamageReport)."""
    amount = int(amount)
    if amount < 0:
        raise ValueError("damage must be >= 0")
    bal = max(0, vitals.balance.current)
    loss = min(amount, bal)
    overflow = amount - loss
    pain_added = 1 if overflow > 0 else 0
    vitals = replace(vitals, balance=replace(vitals.balance, current=bal - loss),
                     pain=vitals.pain + pain_added, trauma=vitals.trauma + overflow)
    return vitals, DamageReport(after_reduction=amount, temp_hp_loss=0, absorbed=(), hp_loss=0,
                                balance_loss=loss, overflow=overflow, pain_added=pain_added)


def take_damage(vitals, amount, dtype=PHYSICAL, reductions=None):
    """Shortcut for a single-part hit."""
    return take_hit(vitals, [DamagePart(int(amount), dtype)], reductions)
