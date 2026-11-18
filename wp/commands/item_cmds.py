"""Doll and item list commands (RULES/gear.md "Doll", "Item HP").

- equip_item / unequip_item: wear an item on the doll (armor, rings...). Armor or a shield at
  item HP 0 (or destroyed) cannot be put on.
- remove_item: the player removes an item from the list by hand; works for destroyed items too.
  Items are never removed automatically. Attack records of the item go with it.
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.model import items as itm


def _put(ch, item):
    return replace(ch, items=tuple(item if it.iid == item.iid else it for it in ch.items))


def check_wearable(it):
    """Armor or a shield at item HP 0 / destroyed cannot be put on (gear.md [OWNER pkg 7])."""
    if itm.defensive(it) and not itm.works(it):
        raise CommandError("%s cannot be put on: item HP %d (%s)" % (
            it.name, itm.hp_current(it), "destroyed" if it.destroyed else "repair it first"))


@command
def equip_item(ch, iid=""):
    it = ch.item(iid)
    if it.equipped:
        raise CommandError("%s is already worn" % it.name)
    check_wearable(it)
    return commit(_put(ch, replace(it, equipped=True)), "equip_item", "%s worn" % it.name)


@command
def unequip_item(ch, iid=""):
    it = ch.item(iid)
    if not it.equipped:
        raise CommandError("%s is not worn" % it.name)
    return commit(_put(ch, replace(it, equipped=False)), "unequip_item", "%s taken off" % it.name)


@command
def remove_item(ch, iid=""):
    """Remove an item from the list (only by hand; destroyed items too)."""
    it = ch.item(iid)
    new = replace(ch, items=tuple(i for i in ch.items if i.iid != iid),
                  attacks=tuple(r for r in ch.attacks if r.item != iid))
    return commit(new, "remove_item", "%s removed" % it.name)
