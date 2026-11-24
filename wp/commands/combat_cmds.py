"""Combat commands: take_damage, cast_spell, add_status, tick."""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import damage as dm
from wp.core import effects as ef
from wp.core import magic as mg
from wp.core import tick as tk
from wp.model import bridge
from wp.model import sheet_targets as stg
from wp.model import defense_view as dfv
from wp.model import derived_view as dv
from wp.model import ids
from wp.core import formula as fm
from wp.model import formulas as fx
from wp.model import blocks as blk
from wp.model import pool_view as pv
from wp.model import restores as rst
from wp.model import usage as us
from wp.model import spell_view as sv


@command
def take_damage(ch, amount=0, dtype=dm.PHYSICAL, parts=None, reductions=None, skip=()):
    """One hit: amount of dtype, or several typed parts [(amount, dtype), ...]. The sheet's DR and resistances
    (effects "dr", "resist:<type>", package 16 D) apply per part; skip = the reductions the player switched off
    for this hit ("dr", "resist:fire"...); `reductions` = extra values typed by the caller (the larger one counts)."""
    if parts is None:
        parts = [(amount, dtype)]
    hit = [dm.DamagePart(int(a), t) for a, t in parts]
    if any(p.amount < 0 for p in hit):
        raise CommandError("damage must be >= 0", "damage_must_0")
    red = dfv.reductions(ch, [p.dtype for p in hit], tuple(skip), reductions)
    v, rep = dm.take_hit(bridge.to_vitals(ch), hit, red)
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
def cast_spell(ch, circle=1, cast_actions=mg.STANDARD_ACTION, mana_cost=None, from_item=False,
               overload=None, penalty_balance=0):
    """Cast: mana/slot, balance, overload (formula or typed value), concentration DC.
    mana_cost None = the circle table (magic.CIRCLE_MANA). Mage, circle 1+: the armor spell penalty
    (spell_view) is added; penalty_balance = the part of it paid with balance (the rest with mana).
    Mage: cost + penalty above the mana level (= level) -> refused (package 10, Q49)."""
    if not mg.valid_circle(circle):
        raise CommandError("circle must be 0..%d" % mg.CIRCLES[-1], "circle_out_of_range", values=(mg.CIRCLES[-1],),
                           circle=circle)
    why = blk.action_block_reasons(ch, "spell_cast")
    if why:
        raise CommandError("casting is blocked by %s" % ", ".join(why), "casting_blocked", values=", ".join(why))
    if ch.caster is None and not from_item:
        raise CommandError("character is not a caster", "character_not_caster")
    mana_cost = mg.circle_mana(circle) if mana_cost is None else int(mana_cost)
    if int(circle) > 0:
        mana_cost = max(0, mana_cost + stg.value(ch, "spell_cost"))   # effect target spell_cost (package 17)
    extra = 0
    if ch.caster == mg.MAGE and not from_item:
        if int(circle) > 0:
            extra = sv.mana_penalty(ch)
        why = sv.over_limit(ch, mana_cost, extra)
        if why:
            raise CommandError(why, "over_mana_level")
    pb = int(penalty_balance)
    if pb < 0 or pb > extra:
        raise CommandError("penalty paid with balance must be 0..%d" % extra, "penalty_paid_balance_must", values=(extra,))
    c0 = ch.slots.get(0)
    cost = mg.cast_cost(ch.caster or mg.MAGE, circle, cast_actions, mana_cost,
                        circle0_slots=c0.max if c0 else 0, from_item=from_item, overload=overload,
                        extra_mana=extra - pb, extra_balance=pb)
    cost = replace(cost, overload=max(0, cost.overload + stg.value(ch, "spell_overload")))   # package 17
    if not mg.can_pay(bridge.to_caster(ch), cost):
        raise CommandError("not enough mana or slots", "not_enough_mana_slots")
    state, res = mg.cast(bridge.to_caster(ch), cost)
    new = bridge.from_caster(ch, state)
    if not ch.rules_settings.overload_enabled:     # rule switch: the overload counter is not applied (pkg 14 G)
        new = replace(new, overload=ch.overload)
    summary = "circle %d: mana -%d, balance -%d, overload +%d" % (
        circle, cost.mana, cost.balance, cost.overload)
    if res.concentration_dc:
        summary += ", concentration DC %d" % res.concentration_dc
    return commit(new, "cast_spell", summary, {"cost": cost, "result": res, "penalty": extra})


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
        raise CommandError("not enough balance: need %d, have %d" % (n, ch.balance_current), "not_enough_balance_need", values=(n, ch.balance_current))
    return commit(replace(ch, balance_current=ch.balance_current - n), "spend_balance", "balance -%d" % n)


@command
def pay_hp_cost(ch, amount=0):
    """HP cost of an ability (package 9 C): paid from the CURRENT balance first (HP untouched); the
    part over the balance -> OT and +1 pain like damage_to_balance; never lowers the balance cap."""
    v, rep = dm.balance_hit(bridge.to_vitals(ch), int(amount))
    new = bridge.from_vitals(ch, v, pain_source="HP cost overflow")
    return commit(new, "pay_hp_cost", "HP cost %d: balance -%d, OT +%d, pain +%d" % (
        int(amount), rep.balance_loss, rep.overflow, rep.pain_added), {"report": rep})


def _start(ch, st, ticks=None):
    """Activate a status entry: refusals, charge, full duration, one-shot part. A status has NO cost of its
    own (buffs.md, Q69): the ability or spell that creates it pays.
    Returns (new character, the started status). The status is NOT yet placed in ch.statuses."""
    if st.active:
        raise CommandError("status %s is already active" % st.name, "status_already_active", values=(st.name,))
    if not ef.can_activate(st):
        raise CommandError("no charges left: %s" % st.name, "no_charges_left", values=(st.name,))
    cost = 1
    if st.charge_per_round > 0:
        # package 14 A (Q83/Q91): the activation pays the FIRST round; every tick pays the next one
        n = st.charge_per_round
        if st.charge_source == ef.OWN:
            if st.charges is None or st.charges.current < n:
                raise CommandError("not enough charges for %s: need %d per round, have %d" % (
                    st.name, n, st.charges.current if st.charges is not None else 0), "not_enough_charges_need", values=(
                    st.name, n, st.charges.current if st.charges is not None else 0))
            cost = n                       # instead of the usual single charge
        else:
            pool = next((p for p in ch.pools if p.pid == st.charge_source), None)
            if pool is None:
                raise CommandError("status %s pays from pool %r, which does not exist" % (st.name, st.charge_source), "status_pays_from_pool", values=(st.name, st.charge_source))
            have = pv.current(ch, pool)
            if have < n:
                raise CommandError("not enough %s for %s: need %d per round, have %d" % (pool.name, st.name, n, have), "not_enough_need_per", values=(pool.name, st.name, n, have))
            ch = replace(ch, pools=tuple(replace(p, current=have - n) if p.pid == pool.pid else p for p in ch.pools))
    started = ef.activate(st, ticks, cost)
    if started.duration == ef.TICKS and started.remaining <= 0:
        raise CommandError("status %s lasts N ticks: give the number of ticks (> 0)" % st.name, "status_lasts_n_ticks", values=(st.name,))
    ch = rst.one_shot(ch, started)             # one-shot resources at activation (package 14 F)
    if ef.holds_temp_hp(started):
        before = dv.temp_hp_total(ch)
        gained = ef.apply_one_shot(started, before) - before
        started = replace(started, temp_hp_left=started.temp_hp_left + max(0, gained))
    else:
        ch = replace(ch, temp_hp=ef.apply_one_shot(started, ch.temp_hp))
    if started.duration == ef.INSTANT:
        started = ef.deactivate(started)   # applied once; the entry stays in the container
    return ch, started


def _put_status(ch, st):
    return replace(ch, statuses=tuple(st if s.sid == st.sid else s for s in ch.statuses))


def _find(ch, sid):
    st = next((s for s in ch.statuses if s.sid == sid), None)
    if st is None:
        raise CommandError("no status with id %r" % (sid,), "no_status_id", values=(sid,))
    return st


@command
def add_status(ch, status=None, ticks=None, active=False):
    """Add a status to the container (from the catalog or by hand). A new entry starts INACTIVE
    unless active=True; then it is started like activate_status (charge, cost, duration)."""
    if status is None:
        raise CommandError("no status given", "no_status_given")
    try:
        fx.validate_effects(status.effects)     # formula values are checked when added (package 14 C)
    except fm.FormulaError as e:
        raise CommandError("bad effect formula in %s: %s" % (status.name, e), "bad_effect_formula", values=(status.name, e))
    bad = [r for r in status.per_tick_restore if not rst.valid(r)]
    if bad:
        raise CommandError("unknown per-tick restore resources: %s (use mana, spirit, balance, pool:<id>)" % ", ".join(bad), "unknown_per_tick_restore", values=", ".join(bad))
    if status.sid and any(s.sid == status.sid for s in ch.statuses):
        raise CommandError("a status with id %r is already on the sheet" % (status.sid,), "status_id_already_sheet", values=(status.sid,))
    st = status
    if not st.sid:                     # the program makes the stable id from the name (D7)
        st = replace(st, sid=ids.make_id(st.name, (s.sid for s in ch.statuses)))
    if ticks is not None and not st.full_ticks:
        st = replace(st, full_ticks=int(ticks))
    st = ef.deactivate(st)
    if active:
        ch, st = _start(ch, st, ticks)
    new = replace(ch, statuses=ch.statuses + (st,))
    return commit(new, "add_status", "status %s added (%s)" % (st.name, "active" if st.active else "inactive"))


@command
def activate_status(ch, sid="", ticks=None):
    """Start an inactive status: one charge is spent (if it has charges) and it runs its full duration."""
    st = _find(ch, sid)
    ch2, started = _start(ch, st, ticks)
    return commit(_put_status(ch2, started), "activate_status", "status %s active" % st.name)


@command
def set_status_duration(ch, sid="", remaining=0):
    """Set the ticks left of an N-ticks status by hand (buffs.md [OWNER pkg 8]: long effects are not
    simulated; the player lowers them by ticks or by hand). 0 or less ends it (inactive, entry stays)."""
    st = _find(ch, sid)
    if st.duration != ef.TICKS:
        raise CommandError("status %s has no tick duration" % st.name, "status_has_no_tick", values=(st.name,))
    remaining = int(remaining)
    if remaining <= 0:
        return commit(_put_status(ch, ef.deactivate(st)), "set_status_duration", "status %s ended" % st.name)
    return commit(_put_status(ch, replace(st, remaining=remaining)), "set_status_duration",
                  "status %s: %d ticks" % (st.name, remaining))


@command
def remove_status(ch, sid=""):
    """End an active status now (narrative reasons): inactive, time cleared; the entry stays."""
    st = _find(ch, sid)
    if not st.active:
        raise CommandError("status %s is not active" % st.name, "status_not_active", values=(st.name,))
    return commit(_put_status(ch, ef.deactivate(st)), "remove_status", "status %s ended" % st.name)


@command
def delete_status(ch, sid=""):
    """Remove the entry from the container entirely (by hand)."""
    st = _find(ch, sid)
    return commit(replace(ch, statuses=tuple(s for s in ch.statuses if s.sid != sid)), "delete_status",
                  "status %s deleted" % st.name)


@command
def set_status_hidden(ch, sid="", value=True):
    """Display only: a hidden status still gives effects and ticks."""
    st = _find(ch, sid)
    return commit(_put_status(ch, replace(st, hidden=bool(value))), "set_status_hidden",
                  "status %s hidden %s" % (st.name, "on" if value else "off"))


@command
def set_status_favorite(ch, sid="", value=True):
    st = _find(ch, sid)
    return commit(_put_status(ch, replace(st, favorite=bool(value))), "set_status_favorite",
                  "status %s favorite %s" % (st.name, "on" if value else "off"))


@command
def tick(ch, reductions=None):
    """Zero-initiative phase: durations, balance, DoT, overload -1."""
    t, rep = tk.zero_initiative(bridge.to_tick(ch), reductions)
    new = rst.per_tick(bridge.from_tick(ch, t), rep.acted)     # restore by effect (package 14 F)
    new = us.tick_cooldowns(new)                               # cooldowns -1 (package 14 B)
    new = replace(new, iterative_count=0)                      # a new round: the iterative series starts again (pkg 16 C)
    new = replace(new, reactions_current=None)                 # a new round: reactions back to max (pkg 22 A2)
    new = replace(new, actions_current=None)                   # and the actions (package 26 A)
    if ch.in_combat:
        new = replace(new, combat_round=ch.combat_round + 1)   # the next round starts (journal, package 14 H)
    if ch.in_combat and rep.cap_hits:
        new = replace(new, balance_cap_hits=new.balance_cap_hits + rep.cap_hits)
    return commit(new, "tick", "balance +%d, dot %d, heal %d, expired %s" % (
        rep.balance_gained, rep.dot_damage, rep.healed, ",".join(rep.expired) or "-"),
        {"report": rep})
