"""Resource commands: restore, set_value, short_rest, long_rest, spend_bp, add_injury."""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import damage as dm
from wp.core import injuries as inj
from wp.core import rest as rs
from wp.commands.gear_cmds import LONG, SHORT, switch_off_items
from wp.model import bridge
from wp.model import derived_view as dv

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
def spend_bp(ch, n=1):
    """Spend BP by hand (temporary BP first)."""
    if n < 0 or ch.bp_current + ch.temp_bp < n:
        raise CommandError("not enough BP")
    from_temp = min(n, ch.temp_bp)
    new = replace(ch, temp_bp=ch.temp_bp - from_temp, bp_current=ch.bp_current - (n - from_temp))
    return commit(new, "spend_bp", "BP -%d" % n)


@command
def short_rest(ch, spends=(), other_heal=0, extra_bp=0, extra_temp_bp=0):
    """Short rest: free gains, then spends [(option, {params}), ...], then 'Apply'."""
    session = rs.start_short_rest(bridge.to_rest(ch), other_heal, extra_bp, extra_temp_bp)
    for opt, params in spends:
        session = rs.spend(session, opt, **dict(params))
    new = switch_off_items(bridge.from_rest(ch, rs.apply_short_rest(session)), SHORT)
    return commit(new, "short_rest", "short rest: %s" % (
        ", ".join(o for o, _ in spends) or "free gains only"))


@command
def long_rest(ch):
    """Long rest (rest.md): also overload 0 and balance to max [OWNER confirmed]; all items off."""
    new = switch_off_items(bridge.from_rest(ch, rs.long_rest(bridge.to_rest(ch))), LONG)
    new = replace(new, overload=0)
    new = replace(new, balance_current=max(new.balance_current, dv.balance_max(new)))
    return commit(new, "long_rest", "long rest")


@command
def add_injury(ch, severity=inj.LIGHT, name=""):
    """Take an injury to remove OT (2 / 5 / 12)."""
    trauma, injury = inj.take_injury(ch.trauma, severity, name)
    new = replace(ch, trauma=trauma, injuries=ch.injuries + (injury,))
    return commit(new, "add_injury", "%s injury, OT %d -> %d" % (severity, ch.trauma, trauma))
