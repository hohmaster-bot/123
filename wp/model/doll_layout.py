"""Doll layout data (package 24 C, RULES/doll.md; no UI).

The layout lives in the classic layout profile (field "doll", package 19): {"background": image id, "basic": [entry],
"body": [entry]}; an entry = {id, x, y, width, height (relative 0..1 on the body picture), icon, label, visible}.
Entry ids: the 21 single doll slots and the two hands left_hand / right_hand (the shared hands slot is drawn as its
two hands, assumption Q164). Two views: "basic" (only the hands visible) and "body" (every slot on the figure).
A profile without a doll layout uses the shipped one (default_profiles.json); the coordinates are SAMPLES.
check(entries) returns warnings (never refusals): a missing entry, a rectangle out of 0..1, two visible rectangles
that overlap.
"""
from wp.model import doll
from wp.model import hands as hd

LEFT_HAND = "left_hand"
RIGHT_HAND = "right_hand"
HAND_ENTRIES = {LEFT_HAND: hd.LEFT, RIGHT_HAND: hd.RIGHT}
ENTRY_IDS = tuple(s for s in doll.SLOT_IDS if s != doll.HANDS) + (LEFT_HAND, RIGHT_HAND)
VIEWS = ("basic", "body")
MISSING = "doll_entry_missing"
OUT_OF_RANGE = "doll_out_of_range"
OVERLAP = "doll_overlap"
UNKNOWN = "doll_unknown_entry"


def shipped():
    from wp.settings import store as st
    return st._shipped_profiles()["classic"][0]["doll"]


def layout_of(profile):
    d = (profile or {}).get("doll") if profile is not None else None
    return d if d else shipped()


def _rect(e):
    return (float(e["x"]), float(e["y"]), float(e["width"]), float(e["height"]))


def check(entries):
    out = []
    ids = [e["id"] for e in entries]
    out += [(MISSING, i) for i in ENTRY_IDS if i not in ids]
    out += [(UNKNOWN, i) for i in ids if i not in ENTRY_IDS]
    for e in entries:
        x, y, w, h = _rect(e)
        if min(x, y, w, h) < 0 or x + w > 1 or y + h > 1:
            out.append((OUT_OF_RANGE, e["id"]))
    vis = [e for e in entries if e.get("visible", True)]
    for i, a in enumerate(vis):
        ax, ay, aw, ah = _rect(a)
        for b in vis[i + 1:]:
            bx, by, bw, bh = _rect(b)
            if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                out.append((OVERLAP, a["id"], b["id"]))
    return tuple(out)


def contents(ch):
    """{entry id: item iid or ""}: the worn item of each single slot, the item of each hand."""
    worn = doll.doll_view(ch)
    out = {s: worn[s] for s in ENTRY_IDS if s in worn}
    h = hd.view(ch)
    out[LEFT_HAND], out[RIGHT_HAND] = h[hd.LEFT], h[hd.RIGHT]
    return out, h[hd.BOTH]


def view(ch, profile=None, which="body", background=None):
    """The doll for the UI: background {image, path, warning} (background = images.resolve result or None) and per
    entry {id, slot, side, item, item_name, icon, label, rect, visible, two_handed}."""
    lay = layout_of(profile)
    entries = lay.get(which) or shipped()[which]
    items, both = contents(ch)
    out = []
    for e in entries:
        iid = items.get(e["id"], "")
        side = HAND_ENTRIES.get(e["id"], "")
        out.append({"id": e["id"], "slot": doll.HANDS if side else e["id"], "side": side, "item": iid,
                    "item_name": ch.item(iid).name if iid else "", "icon": e.get("icon", ""),
                    "label": e.get("label", ""), "rect": _rect(e), "visible": bool(e.get("visible", True)),
                    "two_handed": bool(side and both)})
    path, warning = background if background is not None else (None, None)
    return {"view": which, "background": {"image": lay.get("background", ""), "path": path, "warning": warning},
            "entries": tuple(out), "warnings": check(entries)}
