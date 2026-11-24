"""Doll slot commands (package 24 C, RULES/doll.md): equip an item into a chosen doll entry, take off what an entry
holds, swap two entries. Entries = the single doll slots and the two hands (model/doll_layout.py).

- equip_to_slot(iid, slot, swap): a hand entry = equip_hands with that side (hands rules, refusal hands full /
  hand taken); a single slot = equip_item; the item must fit: Item.slot is that slot (refusal item_not_fit_slot).
- unequip_slot(slot): takes the item off (refusal slot_empty).
- swap_slots(a, b): two hands = move_hand_item with swap; two single slots: each item must fit the other slot
  (refusal item_not_fit_slot); an empty side just moves.
"""
from dataclasses import replace

from wp.commands import attack_cmds, item_cmds
from wp.commands.base import CommandError, command, commit
from wp.model import doll
from wp.model import doll_layout as dl
from wp.model import hands as hd


def _check_entry(slot):
    if slot not in dl.ENTRY_IDS:
        raise CommandError("unknown doll slot %r" % (slot,), "unknown_slot", values=(slot,))


def _fits(it, slot):
    if it.slot != slot:
        raise CommandError("%s does not fit the slot %s" % (it.name, slot), "item_not_fit_slot", values=(it.name, slot))


@command
def equip_to_slot(ch, iid="", slot="", swap=False):
    _check_entry(slot)
    if slot in dl.HAND_ENTRIES:
        r = attack_cmds.equip_hands(ch, iid=iid, side=dl.HAND_ENTRIES[slot])
        return commit(r.state, "equip_to_slot", "%s in %s" % (iid, slot))
    _fits(ch.item(iid), slot)
    r = item_cmds.equip_item(ch, iid=iid, swap=swap)
    return commit(r.state, "equip_to_slot", "%s in %s" % (iid, slot))


def _holder(ch, slot):
    items, _ = dl.contents(ch)
    return items.get(slot, "")


@command
def unequip_slot(ch, slot=""):
    _check_entry(slot)
    iid = _holder(ch, slot)
    if not iid:
        raise CommandError("slot %s is empty" % slot, "slot_empty", values=(slot,))
    if slot in dl.HAND_ENTRIES:
        new = attack_cmds.unequip_hands(ch, iid=iid).state
    else:
        new = item_cmds.unequip_item(ch, iid=iid).state
    return commit(new, "unequip_slot", "%s emptied" % slot)


@command
def swap_slots(ch, a="", b=""):
    _check_entry(a)
    _check_entry(b)
    if a == b:
        raise CommandError("the same slot twice", "same_slot", values=(a,))
    hands = set(dl.HAND_ENTRIES)
    if {a, b} <= hands:
        ia, ib = _holder(ch, a), _holder(ch, b)
        moving = ia or ib
        if not moving:
            raise CommandError("both hands are empty", "slot_empty", values=(a,))
        target = dl.HAND_ENTRIES[b] if ia else dl.HAND_ENTRIES[a]
        new = attack_cmds.move_hand_item(ch, iid=moving, side=target, swap=True).state
        return commit(new, "swap_slots", "%s <-> %s" % (a, b))
    if a in hands or b in hands:
        raise CommandError("a hand swaps only with the other hand", "item_not_fit_slot", values=(a, b))
    ia, ib = _holder(ch, a), _holder(ch, b)
    if not ia and not ib:
        raise CommandError("both slots are empty", "slot_empty", values=(a,))
    for iid, target in ((ia, b), (ib, a)):
        if iid:
            _fits(ch.item(iid), target)
    return commit(ch, "swap_slots", "%s <-> %s" % (a, b))
