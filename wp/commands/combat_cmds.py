"""Combat commands: take_damage, cast_spell, add_status, tick."""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import damage as dm
from wp.core import effects as ef
from wp.core import magic as mg
from wp.core import tick as tk
from wp.model import bridge
from wp.model import derived_view as dv
from wp.model import ids
from wp.model import spell_view as sv


@command
def take_damage(ch, amount=0, dtype=dm.PHYSICAL, parts=None, reductions=None):
    """One hit: amount of dtype, or several typed parts [(amount, dtype), ...]."""
    if parts is None:
        parts = [(amount, dtype)]
    hit = [dm.DamagePart(int(a), t) for a, t in parts]
    if any(p.amount < 0 for p in hit):
        raise CommandError("damage must be >= 0")
    v, rep = dm.take_hit(bridge.to_vitals(ch), hit, reductions)
    new = bridge.from_vitals(ch, v)
    if ch.in_combat and rep.hp_loss > 0:
        # owner homerule: a hit that reached HP/balance lowers the balance cap by 1 this combat
        new = replace(new, balance_cap_hits=new.balance_cap_hits + 1)
    return commit(new, "take_damage", "hit %d -> hp -%d, balance -%d, OT +%d, pain +%d" % (
        rep.after_reduction, rep.hp_loss, rep.balance_loss, rep.overflow, rep.pain_added),
        {"report": rep})


@command
def damage_to_balance(ch, amount=0):
    """Empty-hand parry (owner): the enemy roll landed in the parry layer; the player types the damage.
    It goes straight to the balance: HP untouched, no percent/DR. Overflow -> OT +1 pain.
    In combat the balance cap drops by 1 if the balance really lost points."""
    v, rep = dm.balance_hit(bridge.to_vitals(ch), int(amount))
    new = bridge.from_vitals(ch, v, pain_source="balance damage overflow")
    if ch.in_combat and rep.balance_loss > 0:
        new = replace(new, balance_cap_hits=new.balance_cap_hits + 1)
    return commit(new, "damage_to_balance", "balance -%d, OT +%d, pain +%d" % (
        rep.balance_loss, rep.overflow, rep.pain_added), {"report": rep})


@command
def cast_spell(ch, circle=1, cast_actions=mg.STANDARD_ACTION, mana_cost=0, from_item=False,
               overload=None, penalty_balance=0):
    """Cast: mana/slot, balance, overload (formula or typed value), concentration DC.
    Mage, circle 1+: the armor spell penalty (spell_view) is added; penalty_balance = the part of it
    paid with balance (the rest with mana). Total capped at the mana level (package 9 I)."""
    if ch.caster is None and not from_item:
        raise CommandError("character is not a caster")
    extra, capped = 0, False
    if ch.caster == mg.MAGE and int(circle) > 0 and not from_item:
        mana_cost, extra, capped = sv.capped_cost(ch, int(mana_cost), sv.mana_penalty(ch))
    pb = int(penalty_balance)
    if pb < 0 or pb > extra:
        raise CommandError("penalty paid with balance must be 0..%d" % extra)
    c0 = ch.slots.get(0)
    cost = mg.cast_cost(ch.caster or mg.MAGE, circle, cast_actions, mana_cost,
                        circle0_slots=c0.max if c0 else 0, from_item=from_item, overload=overload,
                        extra_mana=extra - pb, extra_balance=pb)
    if not mg.can_pay(bridge.to_caster(ch), cost):
        raise CommandError("not enough mana or slots")
    state, res = mg.cast(bridge.to_caster(ch), cost)
    new = bridge.from_caster(ch, state)
    summary = "circle %d: mana -%d, balance -%d, overload +%d" % (
        circle, cost.mana, cost.balance, cost.overload)
    if res.concentration_dc:
        summary += ", concentration DC %d" % res.concentration_dc
    if capped:
        summary += ", capped at mana level %d" % ch.mana_level
    return commit(new, "cast_spell", summary, {"cost": cost, "result": res, "penalty": extra, "capped": capped})


@command
def resolve_spell_failure(ch, failed=False):
    """The player rolled the armor spell failure chance (the app rolls nothing). failed: mode "cancel"
    -> the spell is not cast (resources stay spent, see OPEN_QUESTIONS); "zero_balance" -> the spell
    works and the balance drops to 0 as an extra cost."""
    mode = sv.failure_mode(ch)
    if not failed:
        return commit(ch, "resolve_spell_failure", "no failure", {"cast": True, "mode": mode})
    if mode == sv.ZERO_BALANCE:
        return commit(replace(ch, balance_current=0), "resolve_spell_failure",
                      "failure: spell works, balance %d -> 0" % ch.balance_current, {"cast": True, "mode": mode})
    return commit(ch, "resolve_spell_failure", "failure: spell not cast", {"cast": False, "mode": mode})


@command
def spend_balance(ch, n=0):
    """Pay balance for a maneuver or ability (a payment, not damage: the cap does not drop)."""
    n = int(n)
    if n < 0 or n > max(0, ch.balance_current):
        raise CommandError("not enough balance: need %d, have %d" % (n, ch.balance_current))
    return commit(replace(ch, balance_current=ch.balance_current - n), "spend_balance", "balance -%d" % n)


@command
def pay_hp_cost(ch, amount=0):
    """HP cost of an ability (package 9 C): paid from the CURRENT balance first (HP untouched); the
    part over the balance -> OT and +1 pain like damage_to_balance; never lowers the balance cap."""
    v, rep = dm.balance_hit(bridge.to_vitals(ch), int(amount))
    new = bridge.from_vitals(ch, v, pain_source="HP cost overflow")
    return commit(new, "pay_hp_cost", "HP cost %d: balance -%d, OT +%d, pain +%d" % (
        int(amount), rep.balance_loss, rep.overflow, rep.pain_added), {"report": rep})


@command
def add_status(ch, status=None, ticks=None):
    """Activate a status: spend a charge, apply the one-shot part, keep the timed part."""
    if status is None:
        raise CommandError("no status given")
    if not ef.can_activate(status):
        raise CommandError("no charges left: %s" % status.name)
    st = ef.activate(status, ticks)
    if st.duration == ef.TICKS and st.remaining <= 0:
        raise CommandError("status %s lasts N ticks: give the number of ticks (> 0)" % st.name)
    if st.sid and any(s.sid == st.sid for s in ch.statuses):
        raise CommandError("a status with id %r is already on the sheet" % (st.sid,))
    if not st.sid:                     # the program makes the stable id from the name (D7)
        st = replace(st, sid=ids.make_id(st.name, (s.sid for s in ch.statuses)))
    if ef.holds_temp_hp(st):
        before = dv.temp_hp_total(ch)
        gained = ef.apply_one_shot(st, before) - before
        st = replace(st, temp_hp_left=st.temp_hp_left + max(0, gained))
        temp = ch.temp_hp
    else:
        temp = ef.apply_one_shot(st, ch.temp_hp)
    kept = ch.statuses if st.duration == ef.INSTANT else ch.statuses + (st,)
    new = replace(ch, statuses=kept, temp_hp=temp)
    return commit(new, "add_status", "status %s" % st.name)


@command
def set_status_duration(ch, sid="", remaining=0):
    """Set the ticks left of an N-ticks status by hand (buffs.md [OWNER pkg 8]: long effects are not
    simulated; the player lowers them by ticks or by hand). 0 or less removes the status."""
    st = next((s for s in ch.statuses if s.sid == sid), None)
    if st is None:
        raise CommandError("no status with id %r" % (sid,))
    if st.duration != ef.TICKS:
        raise CommandError("status %s has no tick duration" % st.name)
    remaining = int(remaining)
    if remaining <= 0:
        kept = tuple(s for s in ch.statuses if s.sid != sid)
        return commit(replace(ch, statuses=kept), "set_status_duration", "status %s removed" % st.name)
    statuses = tuple(replace(s, remaining=remaining) if s.sid == sid else s for s in ch.statuses)
    return commit(replace(ch, statuses=statuses), "set_status_duration", "status %s: %d ticks" % (st.name, remaining))


@command
def remove_status(ch, sid=""):
    left = tuple(s for s in ch.statuses if s.sid != sid)
    if len(left) == len(ch.statuses):
        raise CommandError("no status with id %r" % (sid,))
    return commit(replace(ch, statuses=left), "remove_status", "status %s removed" % sid)


@command
def tick(ch, reductions=None):
    """Zero-initiative phase: durations, balance, DoT, overload -1."""
    t, rep = tk.zero_initiative(bridge.to_tick(ch), reductions)
    new = bridge.from_tick(ch, t)
    if ch.in_combat and rep.cap_hits:
        new = replace(new, balance_cap_hits=new.balance_cap_hits + rep.cap_hits)
    return commit(new, "tick", "balance +%d, dot %d, heal %d, expired %s" % (
        rep.balance_gained, rep.dot_damage, rep.healed, ",".join(rep.expired) or "-"),
        {"report": rep})
