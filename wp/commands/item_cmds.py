"""Doll and item list commands (RULES/gear.md "Doll", "Item HP").

- equip_item / unequip_item: wear an item on the doll (armor, rings...). Armor or a shield at
  item HP 0 (or destroyed) cannot be put on.
- remove_item: the player removes an item from the list by hand; works for destroyed items too.
  Items are never removed automatically. Attack records of the item go with it.
- set_item_masterwork: the masterwork flag (package 8 D3), independent of activation.
- set_ignore_bag_weight: the "drop bag" button (gear.md "Bag", package 8 E).
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.model import derived_view as dv
from wp.model import items as itm


def _put(ch, item):
    return replace(ch, items=tuple(item if it.iid == item.iid else it for it in ch.items))


def check_wearable(ch, it):
    """Armor or a shield at item HP 0 / destroyed cannot be put on (gear.md [OWNER pkg 7])."""
    if itm.defensive(it) and not dv.works(ch, it):
        raise CommandError("%s cannot be put on: item HP %d (%s)" % (
            it.name, itm.hp_current(it), "destroyed" if it.destroyed else "repair it first"))


@command
def equip_item(ch, iid=""):
    it = ch.item(iid)
    if it.equipped:
        raise CommandError("%s is already worn" % it.name)
    check_wearable(ch, it)
    return commit(_put(ch, replace(it, equipped=True)), "equip_item", "%s worn" % it.name)


@command
def unequip_item(ch, iid=""):
    it = ch.item(iid)
    if not it.equipped:
        raise CommandError("%s is not worn" % it.name)
    return commit(_put(ch, replace(it, equipped=False)), "unequip_item", "%s taken off" % it.name)


@command
def set_item_masterwork(ch, iid="", value=True):
    it = ch.item(iid)
    return commit(_put(ch, replace(it, masterwork=bool(value))), "set_item_masterwork",
                  "%s masterwork %s" % (it.name, "on" if value else "off"))


TAGS = ("none", "combat_only", "out_of_combat_only")


@command
def set_condition_tag(ch, target="item", oid="", tag="none"):
    """Display-only condition tag on an item / status / feat (package 9 E); changes no number."""
    if tag not in TAGS:
        raise CommandError("tag must be one of %s" % ", ".join(TAGS))
    fields = {"item": ("items", "iid"), "status": ("statuses", "sid"), "feat": ("feats", "fid")}
    if target not in fields:
        raise CommandError("target must be item, status or feat")
    name, key = fields[target]
    rows = getattr(ch, name)
    if not any(getattr(r, key) == oid for r in rows):
        raise CommandError("no %s with id %r" % (target, oid))
    rows = tuple(replace(r, condition_tag=tag) if getattr(r, key) == oid else r for r in rows)
    return commit(replace(ch, **{name: rows}), "set_condition_tag", "%s %s tag %s" % (target, oid, tag))


@command
def set_ignore_bag_weight(ch, value=True):
    """While on, the bag's weight is not counted in the carried weight (derived_view.weight_view)."""
    return commit(replace(ch, ignore_bag_weight=bool(value)), "set_ignore_bag_weight",
                  "bag weight %s" % ("ignored" if value else "counted"))


@command
def remove_item(ch, iid=""):
    """Remove an item from the list (only by hand; destroyed items too)."""
    it = ch.item(iid)
    new = replace(ch, items=tuple(i for i in ch.items if i.iid != iid),
                  attacks=tuple(r for r in ch.attacks if r.item != iid))
    return commit(new, "remove_item", "%s removed" % it.name)


@command
def use_consumable(ch, iid="", n=1):
    """Use n of a consumable (gear.md "Consumables", package 13 D): quantity -n, refused below 0. At 0 the
    item stays (spent, grey, weight 0); only remove_item deletes it. on_use_status: that status is
    activated; if it cannot be activated, the whole use is refused (assumption Q87)."""
    it = ch.item(iid)
    n = int(n)
    if not it.consumable:
        raise CommandError("%s is not a consumable" % it.name)
    if n < 1:
        raise CommandError("use at least 1")
    if it.quantity - n < 0:
        raise CommandError("not enough %s: have %d, use %d" % (it.name, it.quantity, n))
    new = _put(ch, replace(it, quantity=it.quantity - n))
    if it.on_use_status:
        from wp.commands import combat_cmds as cc
        st = next((s for s in new.statuses if s.sid == it.on_use_status), None)
        if st is None:
            raise CommandError("%s activates status %r, which is not on the sheet" % (it.name, it.on_use_status))
        new, started = cc._start(new, st)
        new = cc._put_status(new, started)
    return commit(new, "use_consumable", "%s -%d (%d left)" % (it.name, n, it.quantity - n))
