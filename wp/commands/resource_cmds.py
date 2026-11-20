"""Resource commands: restore, set_value, set_temp_hp, short_rest, long_rest, spend_bp, add_injury."""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import damage as dm
from wp.core import injuries as inj
from wp.core import rest as rs
from wp.commands import pool_cmds as pools
from wp.commands.gear_cmds import LONG, SHORT, switch_off_items
from wp.model import bridge
from wp.model import derived_view as dv
from wp.model import blocks as blk
from wp.model import ids
from wp.model import restores as rst

# resource name -> (read pool, write current)
_SCALAR = {
    "hp": (dv.hp_pool, "hp_current"),
    "balance": (dv.balance_pool, "balance_current"),
    "bp": (dv.bp_pool, "bp_current"),
    "comfort": (dv.comfort_pool, "comfort_current"),
    "spirit": (dv.spirit_pool, "spirit_current"),
}
_POOLS = ("mana",)


def _get(ch, name):
    if name in _SCALAR:
        return _SCALAR[name][0](ch)
    if name in _POOLS:
        return getattr(ch, name)
    if name in ch.resources:
        return ch.resources[name]
    raise CommandError("unknown resource: %r" % (name,))


def _put(ch, name, pool):
    if name in _SCALAR:
        return replace(ch, **{_SCALAR[name][1]: pool.current})
    if name in _POOLS:
        return replace(ch, **{name: pool})
    res = dict(ch.resources)
    res[name] = pool
    return replace(ch, resources=res)


@command
def restore(ch, resource="hp", amount=0):
    """Gameplay restore: never above max (an over-max value is kept)."""
    if amount < 0:
        raise CommandError("amount must be >= 0")
    if resource == "hp" and blk.action_block_reasons(ch, "heal"):
        raise CommandError("healing is blocked by %s" % ", ".join(blk.action_block_reasons(ch, "heal")))
    if blk.restore_blocked(ch, resource):
        raise CommandError("restoring %s is blocked by %s" % (resource, ", ".join(blk.restore_block_reasons(ch, resource))))
    before = _get(ch, resource)
    after = dm.restore(before, amount)
    return commit(_put(ch, resource, after), "restore", "%s %d -> %d" % (
        resource, before.current, after.current))


@command
def set_value(ch, resource="hp", value=0):
    """Manual set: no clamp; over max is flagged (derived: current > max)."""
    after = dm.set_value(_get(ch, resource), value)
    return commit(_put(ch, resource, after), "set_value", "%s = %d%s" % (
        resource, after.current, " (over max)" if after.over_max else ""))


@command
def set_temp_hp(ch, value=0):
    """Temp HP "by button" (resources.md [OWNER]): set by hand, live until the short rest."""
    if value < 0:
        raise CommandError("temp HP cannot be negative")
    return commit(replace(ch, temp_hp=int(value)), "set_temp_hp", "temp HP (button) = %d" % int(value))


@command
def spend_bp(ch, n=1):
    """Spend BP by hand (BP above max is ordinary BP)."""
    if n < 0 or ch.bp_current < n:
        raise CommandError("not enough BP")
    new = replace(ch, bp_current=ch.bp_current - n)
    return commit(new, "spend_bp", "BP -%d" % n)


@command
def short_rest(ch, spends=(), other_heal=0, extra_bp=0, keep_overcap=False):
    """Short rest: free gains, then spends [(option, {params}), ...], then 'Apply'.
    BP above max is lost at the end unless keep_overcap=True (package 8 C)."""
    session = rs.start_short_rest(bridge.to_rest(ch), other_heal, extra_bp)
    for opt, params in spends:
        session = rs.spend(session, opt, **dict(params))
    new = switch_off_items(bridge.from_rest(ch, rs.apply_short_rest(session, keep_overcap)), SHORT)
    # rest.md [OWNER]: after the spends the short rest clears ALL temp HP
    new = replace(new, temp_hp=0, statuses=tuple(replace(s, temp_hp_left=0) for s in new.statuses))
    new = pools.restore_by(new, pools.SHORT_REST)      # resource pools with restore "short_rest" (package 13 C)
    new = rst.guard(ch, rst.rest_hp(ch, new))           # rest HP switch, then restore blocks (package 14 F, G)
    return commit(new, "short_rest", "short rest: %s" % (
        ", ".join(o for o, _ in spends) or "free gains only"))


@command
def long_rest(ch):
    """Long rest (rest.md): also overload 0 and balance to max [OWNER confirmed]; all items off."""
    # charges of statuses (rage 2/3) come back through the bridge as ability charges (buffs.md)
    new = switch_off_items(bridge.from_rest(ch, rs.long_rest(bridge.to_rest(ch))), LONG)
    new = replace(new, overload=0)
    new = replace(new, balance_current=max(new.balance_current, dv.balance_max(new)))
    # a long rest includes a short one: "long_rest" and "short_rest" pools (package 14, Q88)
    new = pools.restore_by(pools.restore_by(new, pools.LONG_REST), pools.SHORT_REST)
    new = rst.guard(ch, rst.rest_hp(ch, new))           # rest HP switch, then restore blocks (package 14 F, G)
    return commit(new, "long_rest", "long rest")


@command
def add_injury(ch, severity=inj.LIGHT, name=""):
    """Take an injury to remove OT (2 / 5 / 12)."""
    trauma, injury = inj.take_injury(ch.trauma, severity, name)
    injuries, counter = ids.with_injury_ids(ch.injuries + (injury,), ch.injury_counter)
    new = replace(ch, trauma=trauma, injuries=injuries, injury_counter=counter)
    return commit(new, "add_injury", "%s injury, OT %d -> %d" % (severity, ch.trauma, trauma))


@command
def remove_injury(ch, injury_id=""):
    """Remove an injury by its id (manual, editor level, no resource cost, injuries.md). The id is not
    given again to a later injury (the counter stays)."""
    left = tuple(j for j in ch.injuries if j.jid != injury_id)
    if len(left) == len(ch.injuries):
        raise CommandError("no injury with id %r" % (injury_id,))
    return commit(replace(ch, injuries=left), "remove_injury", "injury %s removed" % injury_id)
