"""Short and long rest (RULES/rest.md, classes_magic.md "Restore", buffs.md charges).

BP above the max ("overcap", e.g. narrative temporary BP or the free +1 at max) is stored simply as
BP above max; there is no separate temporary BP (owner, package 8 C).
Short rest is a small session:
  start_short_rest()  -> free gains: +1 BP (at max it goes over max) and the free heal
  options()           -> only options that have something to restore
  spend()             -> pay BP for one option
  apply_short_rest()  -> end: BP above max is lost, unless keep_overcap=True
Long rest: everything back except OT, comfort, injury charges, permanent pain; BP exactly to max
(overcap dropped).
Pure functions; nothing is mutated in place.
"""
from dataclasses import dataclass, field, replace
from typing import Dict, Tuple

from wp.core import pain as pn
from wp.core.damage import Pool
from wp.core.injuries import restore_stat, stat_damaged

# charge kinds
ABILITY = "ability"     # class, race, feat, quirk charges
ITEM = "item"
INJURY = "injury"

# short rest options and their BP cost
OPT_HEAL = "heal"            # repeat 2+level HP heal
OPT_CHARGES = "charges"      # restore daily/session ability charges
OPT_SPIRIT = "spirit"        # restore all spirit
OPT_STAT = "stat"            # restore 1 point of stat damage
OPT_PAIN = "pain"            # remove 1 pain
OPT_MANA = "mana"            # restore mana by regen (amount: GM, manual)
OPT_DIVINE = "divine"        # restore divine casts (Court chance rolled outside)

COST = {OPT_HEAL: 1, OPT_CHARGES: 2, OPT_SPIRIT: 2, OPT_STAT: 1,
        OPT_PAIN: 1, OPT_MANA: 1, OPT_DIVINE: 1}


@dataclass(frozen=True)
class Charge:
    name: str
    kind: str                     # ABILITY / ITEM / INJURY
    pool: Pool
    restore_on_long_rest: bool = True   # only read for ITEM


@dataclass(frozen=True)
class RestState:
    level: int
    hp: Pool
    bp: Pool                      # current may be above max (overcap)
    pain: Tuple[pn.PainEntry, ...] = ()   # list of pain entries (permanent ones stay)
    spirit: Pool = Pool(0, 0)
    mana: Pool = Pool(0, 0)
    mana_enabled: bool = False
    divine: bool = False          # the caster's slots are divine (short rest "divine casts" option)
    slots: Dict[int, Pool] = field(default_factory=dict)       # circle -> pool
    resources: Dict[str, Pool] = field(default_factory=dict)   # ki, darkness...
    charges: Tuple[Charge, ...] = ()
    stats: Dict[str, Pool] = field(default_factory=dict)       # current/max score
    trauma: int = 0
    comfort: Pool = Pool(0, 0)


@dataclass(frozen=True)
class ShortRest:
    state: RestState
    free_heal: int                # 2 + level or more (race/effect)
    heals_done: int = 1           # the free heal is done at start
    mana_free_used: bool = False


def _restore_full(pool):
    """Gameplay restore to max; a pool already over max is kept (resources.md)."""
    return pool if pool.current >= pool.max else replace(pool, current=pool.max)


def _heal(hp, amount):
    if hp.current >= hp.max:
        return hp
    return replace(hp, current=min(hp.max, hp.current + amount))


def _restore_charges(charges, kinds):
    out = []
    for ch in charges:
        if ch.kind in kinds:
            ch = replace(ch, pool=_restore_full(ch.pool))
        out.append(ch)
    return tuple(out)


# -------------------------------------------------------------- short rest

def free_heal_amount(level, other_heal=0):
    """2 + level HP; if race or an effect gives more, the larger value is used."""
    return max(2 + int(level), int(other_heal))


def start_short_rest(state, other_heal=0, extra_bp=0):
    """Free gains: +1 BP (at max it goes above max), the free heal, extra BP from
    other sources (allies, skills, class, feats); all may go above max (overcap)."""
    bp = replace(state.bp, current=state.bp.current + 1 + int(extra_bp))
    heal = free_heal_amount(state.level, other_heal)
    st = replace(state, bp=bp, hp=_heal(state.hp, heal))
    return ShortRest(state=st, free_heal=heal)


def bp_available(rest):
    return rest.state.bp.current


def option_cost(rest, option):
    if option == OPT_MANA and not rest.mana_free_used:
        return 0
    return COST[option]


def options(rest):
    """Options that have something to restore, with their current BP cost."""
    s = rest.state
    can = {
        OPT_HEAL: s.hp.current < s.hp.max,
        OPT_CHARGES: any(c.kind == ABILITY and c.pool.current < c.pool.max
                         for c in s.charges),
        OPT_SPIRIT: s.spirit.current < s.spirit.max,
        OPT_STAT: any(stat_damaged(p) for p in s.stats.values()),
        OPT_PAIN: any(e.amount > 0 and not e.permanent for e in s.pain),
        OPT_MANA: s.mana_enabled and s.mana.current < s.mana.max,
        OPT_DIVINE: s.divine and any(p.current < p.max for p in s.slots.values()),
    }
    order = (OPT_HEAL, OPT_CHARGES, OPT_SPIRIT, OPT_STAT, OPT_PAIN,
             OPT_MANA, OPT_DIVINE)
    return tuple((o, option_cost(rest, o)) for o in order if can[o])


def _pay(state, cost):
    """Pay BP (BP above max is spent like any BP)."""
    if state.bp.current < cost:
        raise ValueError("not enough BP: need %d" % cost)
    return replace(state, bp=replace(state.bp, current=state.bp.current - cost))


def spend(rest, option, stat=None, mana_amount=0, circle=None):
    """Pay for one option. stat: which stat (OPT_STAT); mana_amount: X set by
    the GM (OPT_MANA); circle: which slot returns (OPT_DIVINE, success rolled
    outside the app)."""
    if option not in dict(options(rest)):
        raise ValueError("option not available: %r" % (option,))
    s = _pay(rest.state, option_cost(rest, option))
    if option == OPT_HEAL:
        s = replace(s, hp=_heal(s.hp, rest.free_heal))
        rest = replace(rest, heals_done=rest.heals_done + 1)
    elif option == OPT_CHARGES:
        s = replace(s, charges=_restore_charges(s.charges, (ABILITY,)))
    elif option == OPT_SPIRIT:
        s = replace(s, spirit=_restore_full(s.spirit))
    elif option == OPT_STAT:
        if stat not in s.stats or not stat_damaged(s.stats[stat]):
            raise ValueError("stat is not damaged: %r" % (stat,))
        stats = dict(s.stats)
        stats[stat] = restore_stat(stats[stat], 1)
        s = replace(s, stats=stats)
    elif option == OPT_PAIN:
        s = replace(s, pain=pn.remove(s.pain, 1))
    elif option == OPT_MANA:
        m = s.mana
        s = replace(s, mana=replace(m, current=min(m.max, m.current + int(mana_amount))))
        rest = replace(rest, mana_free_used=True)
    elif option == OPT_DIVINE:
        p = s.slots.get(circle)
        if p is None or p.current >= p.max:
            raise ValueError("no spent slot of circle %r" % (circle,))
        slots = dict(s.slots)
        slots[circle] = replace(p, current=p.current + 1)
        s = replace(s, slots=slots)
    return replace(rest, state=s)


def drop_overcap(bp):
    """BP above max is lost (short rest by default, long rest, end of cycle)."""
    return replace(bp, current=min(bp.current, bp.max))


def apply_short_rest(rest, keep_overcap=False):
    """'Apply': end of short rest. BP above max is lost, unless keep_overcap (package 8 C)."""
    s = rest.state
    return s if keep_overcap else replace(s, bp=drop_overcap(s.bp))


# --------------------------------------------------------------- long rest

def long_rest(state):
    """Long rest (rest.md): HP, BP, spirit, mana, slots, class resources to max;
    ability charges and items with "restore on long rest" back; temporary pain gone;
    stat damage healed (current -> max; permanent damage already lowered max).
    BP goes exactly to max (overcap dropped, package 8 C); mana always (racial mana too, R18).
    NOT touched: OT, comfort, injury charges, permanent pain, temp HP."""
    charges = []
    for ch in state.charges:
        if ch.kind == ABILITY or (ch.kind == ITEM and ch.restore_on_long_rest):
            ch = replace(ch, pool=_restore_full(ch.pool))
        charges.append(ch)
    return replace(
        state,
        hp=_restore_full(state.hp),
        bp=replace(state.bp, current=state.bp.max),
        pain=pn.clear_temporary(state.pain),
        spirit=_restore_full(state.spirit),
        mana=_restore_full(state.mana),
        slots={c: _restore_full(p) for c, p in state.slots.items()},
        resources={n: _restore_full(p) for n, p in state.resources.items()},
        charges=tuple(charges),
        stats={n: restore_stat(p, p.max) for n, p in state.stats.items()},
    )
