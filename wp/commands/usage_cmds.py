"""Charges and cooldown commands (RULES/gear.md "Charges and cooldown", package 14 B):
spend_charge, set_charges, restore_charges for owner kinds item / status / feat / attack / maneuver."""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.model import usage as us


def _owner(ch, kind, oid):
    if kind not in us.KINDS:
        raise CommandError("owner kind must be one of %s" % ", ".join(us.KINDS), "owner_kind_must_one", values=", ".join(us.KINDS))
    owner = us.find(ch, kind, oid)
    if owner is None:
        raise CommandError("no %s with id %r" % (kind, oid), "not_found", values=(kind, oid))
    c = us.charges(kind, owner)
    if c is None:
        raise CommandError("%s %s has no charges" % (kind, oid), "has_no_charges", values=(kind, oid))
    return owner, c


@command
def spend_charge(ch, owner_kind="item", owner_id="", n=1):
    owner, (cur, _) = _owner(ch, owner_kind, owner_id)
    n = int(n)
    if n < 1:
        raise CommandError("spend at least 1", "spend_least_1")
    cool, rounds = us.cooldown(owner_kind, owner)
    if cool > 0:
        raise CommandError("%s %s is on cooldown (%d rounds left)" % (owner_kind, owner_id, cool), "cooldown_rounds_left", values=(owner_kind, owner_id, cool))
    if cur - n < 0:
        raise CommandError("not enough charges: have %d, spend %d" % (cur, n), "not_enough_charges_have", values=(cur, n))
    owner = us.with_values(owner_kind, owner, current=cur - n, cool=rounds if rounds > 0 else None)
    return commit(us.put(ch, owner_kind, owner, owner_id), "spend_charge", "%s %s -%d" % (owner_kind, owner_id, n),
                  {"left": cur - n, "cooldown": rounds})


@command
def set_charges(ch, owner_kind="item", owner_id="", value=0):
    owner, (_, mx) = _owner(ch, owner_kind, owner_id)
    value = int(value)
    if value < 0 or value > mx:
        raise CommandError("charges must be 0..%d" % mx, "charges_must_0", values=(mx,))
    return commit(us.put(ch, owner_kind, us.with_values(owner_kind, owner, current=value), owner_id), "set_charges",
                  "%s %s = %d" % (owner_kind, owner_id, value))


@command
def restore_charges(ch, owner_kind="item", owner_id=""):
    owner, (_, mx) = _owner(ch, owner_kind, owner_id)
    return commit(us.put(ch, owner_kind, us.with_values(owner_kind, owner, current=mx), owner_id), "restore_charges",
                  "%s %s restored to %d" % (owner_kind, owner_id, mx))


@command
def restore_all_balance(ch, pick_id=""):
    """Master pick "restore all balance" (once per combat, free action; weapons.md, package 17): spends the pick's
    charge and sets the balance to its max. No dice, no other effect. Refused while a block_restore covers the balance
    (assumption Q128)."""
    from wp.model import blocks as blk
    from wp.model import derived_view as dv
    owner, (cur, _) = _owner(ch, us.PICK, pick_id)
    if owner.bonus != "restore_balance":
        raise CommandError("pick %s is not \"restore all balance\"" % pick_id, "wrong_pick", values=(pick_id,))
    if cur < 1:
        raise CommandError("already used in this combat", "not_enough_charges_have", values=(cur, 1))
    if blk.restore_blocked(ch, "balance"):
        raise CommandError("restoring balance is blocked", "restoring_blocked", values=("balance",))
    new = us.put(ch, us.PICK, us.with_values(us.PICK, owner, current=0), pick_id)
    mx = dv.balance_max(new)
    new = replace(new, balance_current=max(new.balance_current, mx))
    return commit(new, "restore_all_balance", "balance -> %d" % mx, {"balance": new.balance_current})
