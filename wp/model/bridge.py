"""Bridge between the Character model and the core states (Vitals, RestState,
CasterState, TickState). Pure functions: build a core state, take one back.
"""
from dataclasses import replace

from wp.core import pain as pn
from wp.core import rest as rs
from wp.core.damage import Absorber, Pool, Vitals
from wp.core.magic import CasterState
from wp.core.tick import TickState
from wp.model import blocks as blk
from wp.model import derived_view as dv

OVERFLOW = "balance overflow"


def _absorber_pool(ch, name):
    if name == "mana":
        return ch.mana
    return ch.resources[name]


def to_vitals(ch):
    abs_ = tuple(Absorber(n, _absorber_pool(ch, n).current) for n in ch.absorbers)
    return Vitals(hp=dv.hp_pool(ch), balance=dv.balance_pool(ch), temp_hp=dv.temp_hp_total(ch),
                  absorbers=abs_, pain=0, trauma=ch.trauma)


def _spend_temp(ch, left):
    """Split the remaining temp HP back: the "by button" pool is used first, then statuses in order (Q23)."""
    used = dv.temp_hp_total(ch) - left
    take = min(used, ch.temp_hp)
    temp = ch.temp_hp - take
    used -= take
    statuses = []
    for s in ch.statuses:
        t = min(used, s.temp_hp_left) if s.active else 0
        used -= t
        statuses.append(replace(s, temp_hp_left=s.temp_hp_left - t) if t else s)
    return temp, tuple(statuses)


def from_vitals(ch, v, pain_source=OVERFLOW):
    """Write HP, balance, temp HP, absorbers, OT back; new pain becomes an entry."""
    mana, resources = ch.mana, dict(ch.resources)
    for a in v.absorbers:
        if a.name == "mana":
            mana = replace(mana, current=a.current)
        else:
            resources[a.name] = replace(resources[a.name], current=a.current)
    pain = pn.add(ch.pain, v.pain, pain_source) if v.pain else ch.pain
    temp, statuses = _spend_temp(ch, v.temp_hp)
    return replace(ch, hp_current=v.hp.current, balance_current=v.balance.current,
                   temp_hp=temp, statuses=statuses, mana=mana, resources=resources, trauma=v.trauma, pain=pain)


STATUS_CHARGE = "status:"          # rest charge name for the charges kept on a status (rage 2/3)


def _status_charges(ch):
    """Charges kept on statuses go to the rest as ability charges: the short rest option
    "restore charges" and the long rest bring them back (buffs.md, package 8 R16)."""
    return tuple(rs.Charge(STATUS_CHARGE + s.sid, rs.ABILITY, s.charges)
                 for s in ch.statuses if s.charges is not None)


def to_rest(ch):
    stats = {n: Pool(a.current, a.score_max) for n, a in ch.abilities.items()}
    return rs.RestState(level=ch.level, hp=dv.hp_pool(ch), bp=dv.bp_pool(ch),
                        pain=ch.pain, spirit=dv.spirit_pool(ch), mana=ch.mana, mana_enabled=ch.mana_enabled,
                        divine=ch.divine_slots, slots=dict(ch.slots), resources=dict(ch.resources),
                        charges=ch.charges + _status_charges(ch),
                        stats=stats, trauma=ch.trauma, comfort=dv.comfort_pool(ch))


def from_rest(ch, s):
    abilities = {n: replace(a, damage=s.stats[n].max - s.stats[n].current)
                 for n, a in ch.abilities.items()}
    own = tuple(c for c in s.charges if not c.name.startswith(STATUS_CHARGE))
    back = {c.name[len(STATUS_CHARGE):]: c.pool for c in s.charges if c.name.startswith(STATUS_CHARGE)}
    statuses = tuple(replace(st, charges=back[st.sid]) if st.charges is not None and st.sid in back else st
                     for st in ch.statuses)
    return replace(ch, hp_current=s.hp.current, bp_current=s.bp.current,
                   pain=s.pain, spirit_current=s.spirit.current, mana=s.mana, slots=dict(s.slots),
                   resources=dict(s.resources), charges=own, abilities=abilities, statuses=statuses)


def to_caster(ch):
    return CasterState(mana=ch.mana, balance=dv.balance_pool(ch), slots=dict(ch.slots),
                       overload=ch.overload, pain=0, trauma=ch.trauma)


def from_caster(ch, c):
    pain = pn.add(ch.pain, c.pain, "spell: balance short") if c.pain else ch.pain
    return replace(ch, mana=c.mana, balance_current=c.balance.current, slots=dict(c.slots),
                   overload=c.overload, trauma=c.trauma, pain=pain)


def to_tick(ch):
    return TickState(vitals=to_vitals(ch), statuses=ch.statuses, overload=ch.overload,
                     balance_regen=dv.balance_regen(ch), negative_state=ch.negative_state,
                     traits=ch.traits, regen_blocked=blk.regen_blocked_by_effect(ch),
                     pools={p.pid: p.current for p in ch.pools})


def from_tick(ch, t):
    """Statuses after the tick (expired ones inactive, their temp HP gone), then vitals.
    tick_all keeps the order and the number of entries."""
    pairs = tuple(zip(ch.statuses, t.statuses))
    statuses = tuple(after if not after.active else replace(after, temp_hp_left=before.temp_hp_left)
                     for before, after in pairs)
    gone = sum(before.temp_hp_left for before, after in pairs if before.active and not after.active)
    base = replace(ch, statuses=statuses)
    v = replace(t.vitals, temp_hp=max(0, t.vitals.temp_hp - gone))
    ch = from_vitals(base, v, pain_source="tick: balance overflow")
    pools = tuple(replace(p, current=t.pools.get(p.pid, p.current)) for p in ch.pools)
    return replace(ch, overload=t.overload, pools=pools)
