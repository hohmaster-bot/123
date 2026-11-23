"""Doll slots (RULES/doll.md, package 16 E). The slot list is data: wp/catalog/data/doll_slots.json.

Item.slot names the slot ("" = no slot: worn without a slot check, as before package 16). Every slot except the
shared hands slot holds ONE worn item; the hands slot is the two-hand rule of equip_hands. Bonuses of an item count
only while it is worn (or held), as before; an item that is not worn stays in the bag.
"""


def _load():
    """Doll slots from the catalog file of kind "doll_slots" (package 18)."""
    from wp.catalog import store as cs
    cat = cs.load_shipped("doll_slots")
    return tuple((e["id"], e["name"]) for e in cat.entries), next(e["id"] for e in cat.entries if e.get("hands"))


SLOTS, HANDS = _load()
SLOT_IDS = tuple(s for s, _ in SLOTS)


def occupant(ch, slot, but=""):
    """The worn item in this slot (other than `but`), or None."""
    return next((it for it in ch.items if it.equipped and it.slot == slot and it.iid != but), None)


def doll_view(ch):
    """{slot id: worn item id or ""} for the 21 single slots; the hands slot lists the held items."""
    out = {s: "" for s in SLOT_IDS}
    for it in ch.items:
        if it.equipped and it.slot in out and it.slot != HANDS:
            out[it.slot] = it.iid
    out[HANDS] = tuple(it.iid for it in ch.items if it.in_hands)
    return out
