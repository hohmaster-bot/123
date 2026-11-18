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
               overload=None):
    """Cast: mana/slot, balance, overload (formula or typed value), concentration DC."""
    if ch.caster is None and not from_item:
        raise CommandError("character is not a caster")
    c0 = ch.slots.get(0)
    cost = mg.cast_cost(ch.caster or mg.MAGE, circle, cast_actions, mana_cost,
                        circle0_slots=c0.max if c0 else 0, from_item=from_item, overload=overload)
    if not mg.can_pay(bridge.to_caster(ch), cost):
        raise CommandError("not enough mana or slots")
    state, res = mg.cast(bridge.to_caster(ch), cost)
    new = bridge.from_caster(ch, state)
    summary = "circle %d: mana -%d, balance -%d, overload +%d" % (
        circle, cost.mana, cost.balance, cost.overload)
    if res.concentration_dc:
        summary += ", concentration DC %d" % res.concentration_dc
    return commit(new, "cast_spell", summary, {"cost": cost, "result": res})


@command
def add_status(ch, status=None, ticks=None):
    """Activate a status: spend a charge, apply the one-shot part, keep the timed part."""
    if status is None:
        raise CommandError("no status given")
    if not ef.can_activate(status):
        raise CommandError("no charges left: %s" % status.name)
    st = ef.activate(status, ticks)
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
