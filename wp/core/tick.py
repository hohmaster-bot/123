"""Zero-initiative phase (RULES/resources.md "Zero initiative phase").

After everyone acted:
  1. active statuses lose 1 duration (expired ones become inactive; inactive ones do not tick);
  2. balance restoration (forbidden while overload > 0) and the damage items of the tick (DoT statuses, the
     negative-HP state loss dying / resting) are applied in the order MOST FAVOURABLE for the player (package 22 A4):
     the order with the smallest overflow (OT, then pain) and then the highest final balance (assumption Q150: the
     owner's second example needs the overflow first). All orders are tried up to MAX_ORDER_ITEMS items, beyond that a
     greedy order (damages ascending, the regen tried at every place);
  3. heals per tick and the rule switch hp_regen_per_tick, after the damage (no heal wasted at full HP).
Overload counts down by 1 per tick after the regen check.
"""
import itertools
from dataclasses import dataclass, field, replace
from typing import Dict, Tuple

from wp.core import effects as ef
from wp.core.damage import DamagePart, Vitals, restore, take_hit
from wp.core.magic import balance_regen_blocked
from wp.core.statuses import NegativeTraits, hp_loss_per_tick
from wp.rules_data import rules as rd

MAX_ORDER_ITEMS = rd.ref("tick.max_order_items")   # all orders are tried up to this many balance items


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

    # 2) balance items in the most favourable order (package 22 A4), then 3) heals
    v0 = state.vitals
    blocked = (state.overload_enabled and balance_regen_blocked(state.overload)) or state.regen_blocked
    overload = max(0, state.overload - 1)
    items = [("regen", state.balance_regen, None)] if not blocked else []
    items += [("dot", -s.per_tick_hp, s) for s in acting if s.per_tick_hp < 0]
    loss = hp_loss_per_tick(state.negative_state, state.traits)
    if loss > 0 and _hp_after(v0, items, acting, state, reductions) < 0:
        items.append(("loss", loss, None))
    v, dot, cap_hits, gained = _best(v0, items, reductions)
    steps.append("balance")
    healed = 0
    for s in acting:
        if s.per_tick_hp > 0 and not state.heal_blocked:
            before = v.hp.current
            v = replace(v, hp=restore(v.hp, s.per_tick_hp))
            healed += v.hp.current - before
    if state.hp_regen > 0 and not state.heal_blocked:   # rule switch hp_regen_per_tick (package 14 G)
        before = v.hp.current
        v = replace(v, hp=restore(v.hp, state.hp_regen))
        healed += v.hp.current - before
    steps.append("dot")

    new = replace(state, vitals=v, statuses=new_statuses, overload=overload, pools=pools)
    return new, TickReport(steps=tuple(steps), expired=expired, balance_gained=gained,
                           regen_blocked=blocked, dot_damage=dot, healed=healed, cap_hits=cap_hits, acted=acted)


def _apply(v, order, reductions):
    """Run the balance items in this order. Returns (vitals, dot damage, cap hits, balance gained)."""
    dot = cap_hits = gained = 0
    for kind, amount, s in order:
        if kind == "regen":
            before = v.balance.current
            v = replace(v, balance=restore(v.balance, amount))
            gained += v.balance.current - before
            continue
        dtype = s.dot_type if s is not None else "untyped"
        v, r = take_hit(v, [DamagePart(amount, dtype)], reductions if kind == "dot" else None)
        dot += r.hp_loss + r.temp_hp_loss + sum(a for _, a in r.absorbed)
        if s is not None and s.lowers_balance_cap and r.hp_loss > 0:
            cap_hits += 1
    return v, dot, cap_hits, gained


def _key(v):
    return (v.trauma, v.pain, -v.balance.current)


def _orders(items):
    if len(items) <= int(MAX_ORDER_ITEMS):
        return itertools.permutations(items)
    regen = [x for x in items if x[0] == "regen"]
    dmg = sorted((x for x in items if x[0] != "regen"), key=lambda x: x[1])
    if not regen:
        return [tuple(dmg)]
    return [tuple(dmg[:k] + regen + dmg[k:]) for k in range(len(dmg) + 1)]


def _best(v, items, reductions):
    best = None
    for order in _orders(items):           # the first best order wins a tie (the listed order first)
        out = _apply(v, order, reductions)
        if best is None or _key(out[0]) < _key(best[0]):
            best = out
    return best if best is not None else (v, 0, 0, 0)


def _hp_after(v, items, acting, state, reductions):
    """HP after the damage items and the heals of this tick (decides whether the negative-HP loss applies, as before)."""
    v, _, _, _ = _apply(v, items, reductions)
    for s in acting:
        if s.per_tick_hp > 0 and not state.heal_blocked:
            v = replace(v, hp=restore(v.hp, s.per_tick_hp))
    if state.hp_regen > 0 and not state.heal_blocked:
        v = replace(v, hp=restore(v.hp, state.hp_regen))
    return v.hp.current
