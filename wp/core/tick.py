"""Zero-initiative phase (RULES/resources.md "Zero initiative phase").

After everyone acted:
  1. active statuses lose 1 duration (expired ones become inactive; inactive ones do not tick);
  2. balance restoration (forbidden while overload > 0);
  3. DoT damage and heal per tick (balance FIRST, then DoT: best for the player);
     the negative-HP state loss (dying / resting) is applied here like a DoT.
Overload counts down by 1 per tick after the regen check.
"""
from dataclasses import dataclass, field, replace
from typing import Dict, Tuple

from wp.core import effects as ef
from wp.core.damage import DamagePart, Vitals, restore, take_hit
from wp.core.magic import balance_regen_blocked
from wp.core.statuses import NegativeTraits, hp_loss_per_tick


@dataclass(frozen=True)
class TickState:
    vitals: Vitals
    statuses: Tuple[ef.Status, ...] = ()
    overload: int = 0
    balance_regen: int = 1             # derived.balance_regen(...)
    negative_state: object = None      # statuses.DYING / RESTING / STABILIZED / None
    traits: NegativeTraits = NegativeTraits()
    regen_blocked: bool = False        # a block_balance_regen effect is active (package 13 B)
    pools: Dict[str, int] = field(default_factory=dict)   # resource pool id -> current (package 13 C)
    heal_blocked: bool = False         # block_restore hp: no HP restore in this tick (package 14 F)
    hp_regen: int = 0                  # rule switch hp_regen_per_tick (package 14 G)
    overload_enabled: bool = True      # rule switch: False -> the overload never blocks regen (package 14 G)


@dataclass(frozen=True)
class TickReport:
    steps: Tuple[str, ...]             # order of what happened
    expired: Tuple[str, ...]
    balance_gained: int
    regen_blocked: bool
    dot_damage: int
    healed: int
    cap_hits: int = 0                  # flagged DoT hits that reached HP (balance cap homerule)
    acted: Tuple[int, ...] = ()        # indexes of the statuses that acted in this tick (package 14 F)


def zero_initiative(state, reductions=None):
    """Run one zero-initiative phase. Returns (new_state, TickReport)."""
    steps = []
    # 1) per-round payments (package 13 C), then durations. A status that cannot pay ends now and does
    #    not act in this tick (assumption Q84).
    paid, pools = ef.pay_all(state.statuses, state.pools)
    acted = tuple(i for i, s in enumerate(paid) if s.active and (s.duration != ef.TICKS or s.remaining > 0))
    acting = tuple(paid[i] for i in acted)
    new_statuses = ef.tick_all(paid)
    expired = tuple(a.name for a, b in zip(state.statuses, new_statuses) if ef.expired_now(a, b))
    steps.append("durations")

    # 2) balance
    v = state.vitals
    blocked = (state.overload_enabled and balance_regen_blocked(state.overload)) or state.regen_blocked
    gained = 0
    if not blocked:
        before = v.balance.current
        v = replace(v, balance=restore(v.balance, state.balance_regen))
        gained = v.balance.current - before
    overload = max(0, state.overload - 1)
    steps.append("balance")

    # 3) DoT / heal per tick (statuses active at the start of the tick), negative-HP loss
    dot = 0
    healed = 0
    cap_hits = 0
    for s in acting:
        if s.per_tick_hp < 0:
            v, r = take_hit(v, [DamagePart(-s.per_tick_hp, s.dot_type)], reductions)
            dot += r.hp_loss + r.temp_hp_loss + sum(a for _, a in r.absorbed)
            if s.lowers_balance_cap and r.hp_loss > 0:
                cap_hits += 1
        elif s.per_tick_hp > 0 and not state.heal_blocked:
            before = v.hp.current
            v = replace(v, hp=restore(v.hp, s.per_tick_hp))
            healed += v.hp.current - before
    if state.hp_regen > 0 and not state.heal_blocked:   # rule switch hp_regen_per_tick (package 14 G)
        before = v.hp.current
        v = replace(v, hp=restore(v.hp, state.hp_regen))
        healed += v.hp.current - before
    loss = hp_loss_per_tick(state.negative_state, state.traits) if v.hp.current < 0 else 0
    if loss > 0:
        v, r = take_hit(v, [DamagePart(loss, "untyped")])
        dot += r.hp_loss + r.temp_hp_loss + sum(a for _, a in r.absorbed)
    steps.append("dot")

    new = replace(state, vitals=v, statuses=new_statuses, overload=overload, pools=pools)
    return new, TickReport(steps=tuple(steps), expired=expired, balance_gained=gained,
                           regen_blocked=blocked, dot_damage=dot, healed=healed, cap_hits=cap_hits, acted=acted)
