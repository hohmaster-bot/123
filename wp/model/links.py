"""The "held by" link (package 36, owner decision 14): an ability (feat), a status or a quirk may be held by another
ability, an item, a quirk, a status or a text holder (a manual kept / lost checkbox). When the holder is gone (the item
removed, the ability deleted, the status ended, the quirk gone or burned, the text holder unticked) the dependent gets
a "not backed" mark and a reminder; nothing is removed or switched off automatically.
"""
from wp.core.effects import is_effective

FEAT, ITEM, QUIRK, STATUS, TEXT = "feat:", "item:", "quirk:", "status:", "text:"


def holder_present(ch, holder):
    if holder.startswith(FEAT):
        return any(f.fid == holder[len(FEAT):] for f in ch.feats)
    if holder.startswith(ITEM):
        return any(it.iid == holder[len(ITEM):] for it in ch.items)
    if holder.startswith(QUIRK):
        return any(q.kid == holder[len(QUIRK):] and not q.burned for q in ch.quirks)
    if holder.startswith(STATUS):
        return any(s.sid == holder[len(STATUS):] and is_effective(s) for s in ch.statuses)
    return False


def _rows(ch):
    out = [("feats", f.fid, f.title or f.fid, f.held_by, f.held_kept) for f in ch.feats]
    out += [("statuses", s.sid, s.name, s.held_by, s.held_kept) for s in ch.statuses]
    out += [("quirks", q.kid, q.name, q.held_by, q.held_kept) for q in ch.quirks]
    return [(coll, oid, name, holder, kept) for coll, oid, name, holder, kept in out if holder]


def backed(ch, holder, kept=True):
    if holder.startswith(TEXT):
        return bool(kept)
    return holder_present(ch, holder)


def not_backed(ch):
    """((collection, id, name, holder), ...) of the dependents whose holder is gone."""
    return tuple((coll, oid, name, holder) for coll, oid, name, holder, kept in _rows(ch)
                 if not backed(ch, holder, kept))


def reminders(ch):
    return tuple(("reminder.not_backed", (name, holder)) for _c, _o, name, holder in not_backed(ch))
