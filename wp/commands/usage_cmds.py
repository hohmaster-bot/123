"""Charges and cooldown commands (RULES/gear.md "Charges and cooldown", package 14 B):
spend_charge, set_charges, restore_charges for owner kinds item / status / feat / attack / maneuver."""
from wp.commands.base import CommandError, command, commit
from wp.model import usage as us


def _owner(ch, kind, oid):
    if kind not in us.KINDS:
        raise CommandError("owner kind must be one of %s" % ", ".join(us.KINDS))
    owner = us.find(ch, kind, oid)
    if owner is None:
        raise CommandError("no %s with id %r" % (kind, oid))
    c = us.charges(kind, owner)
    if c is None:
        raise CommandError("%s %s has no charges" % (kind, oid))
    return owner, c


@command
def spend_charge(ch, owner_kind="item", owner_id="", n=1):
    owner, (cur, _) = _owner(ch, owner_kind, owner_id)
    n = int(n)
    if n < 1:
        raise CommandError("spend at least 1")
    cool, rounds = us.cooldown(owner_kind, owner)
    if cool > 0:
        raise CommandError("%s %s is on cooldown (%d rounds left)" % (owner_kind, owner_id, cool))
    if cur - n < 0:
        raise CommandError("not enough charges: have %d, spend %d" % (cur, n))
    owner = us.with_values(owner_kind, owner, current=cur - n, cool=rounds if rounds > 0 else None)
    return commit(us.put(ch, owner_kind, owner), "spend_charge", "%s %s -%d" % (owner_kind, owner_id, n),
                  {"left": cur - n, "cooldown": rounds})


@command
def set_charges(ch, owner_kind="item", owner_id="", value=0):
    owner, (_, mx) = _owner(ch, owner_kind, owner_id)
    value = int(value)
    if value < 0 or value > mx:
        raise CommandError("charges must be 0..%d" % mx)
    return commit(us.put(ch, owner_kind, us.with_values(owner_kind, owner, current=value)), "set_charges",
                  "%s %s = %d" % (owner_kind, owner_id, value))


@command
def restore_charges(ch, owner_kind="item", owner_id=""):
    owner, (_, mx) = _owner(ch, owner_kind, owner_id)
    return commit(us.put(ch, owner_kind, us.with_values(owner_kind, owner, current=mx)), "restore_charges",
                  "%s %s restored to %d" % (owner_kind, owner_id, mx))
