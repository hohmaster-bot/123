"""Hands with sides (package 24 A, RULES/gear.md "Doll", ac_zones.md).

The two hands are two positions, left and right. Item.hand stores the side chosen by equip_hands / move_hand_item
("left" / "right"; a two-handed item takes both). sides(ch) is computed on read: an item that has a valid stored
side keeps it (first come first served); a held item without a stored side (an older file, or a test record)
gets one by the order of the held list: a shield the default shield side (hands.default_shield_side), any other
item the first free hand of hands.default_weapon_sides; a two-handed item both. Nothing is written back.
"""
from wp.model import records as rec
from wp.rules_data import rules as rd

LEFT = "left"
RIGHT = "right"
BOTH = "both"
SIDES = (LEFT, RIGHT)
TWO_HANDED = rd.ref("hands.two_handed")


def other(side):
    return RIGHT if side == LEFT else LEFT


def held(ch):
    return [it for it in ch.items if it.in_hands]


def two_handed(item):
    return item.hands >= TWO_HANDED


def preferred(ch, item):
    """Sides to try for an item without a chosen side, best first."""
    if rec.is_shield(item):
        first = rd.const("hands.default_shield_side", ch)
        return (first, other(first))
    return tuple(rd.const("hands.default_weapon_sides", ch))


def sides(ch):
    """{iid: "left" | "right" | "both" | ""} for every held item ("" = no hand left for it, or needs no hands)."""
    free = set(SIDES)
    out = {}
    items = [it for it in held(ch) if it.hands > 0]
    for it in items:                                   # stored sides first
        if two_handed(it):
            continue
        if it.hand in free:
            out[it.iid] = it.hand
            free.discard(it.hand)
    for it in items:                                   # two-handed items and items without a valid side
        if it.iid in out:
            continue
        if two_handed(it):
            if free == set(SIDES):
                out[it.iid] = BOTH
                free = set()
            else:
                out[it.iid] = ""
            continue
        side = next((s for s in preferred(ch, it) if s in free), "")
        out[it.iid] = side
        free.discard(side)
    return out


def side_of(ch, iid):
    return sides(ch).get(iid, "")


def occupant(ch, side):
    """The item held in this hand (a two-handed item occupies both), or None."""
    for iid, s in sides(ch).items():
        if s == side or s == BOTH:
            return ch.item(iid)
    return None


def free_sides(ch):
    used = set()
    for s in sides(ch).values():
        used |= set(SIDES) if s == BOTH else {s}
    return tuple(s for s in SIDES if s not in used)


def view(ch):
    """Both hands for the UI: {"left": iid or "", "right": iid or "", "both": bool (one two-handed item)}."""
    out = {LEFT: "", RIGHT: "", BOTH: False}
    for iid, s in sides(ch).items():
        if s == BOTH:
            out[LEFT] = out[RIGHT] = iid
            out[BOTH] = True
        elif s:
            out[s] = iid
    return out
