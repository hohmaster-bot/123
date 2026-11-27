"""The "held by" link (package 36, owner decision 14): an ability (feat), a status or a quirk may be held by another
ability, an item, a quirk, a status or a text holder (a manual kept / lost checkbox). When the holder is gone (the item
removed, the ability deleted, the status ended, the quirk gone or burned, the text holder unticked) the dependent gets
a "not backed" mark and a reminder; nothing is removed or switched off automatically.
"""
from wp.core.effects import is_effective

FEAT, ITEM, QUIRK, STATUS, TEXT, TRAINING = "feat:", "item:", "quirk:", "status:", "text:", "training:"
PREFIXES = (FEAT, ITEM, QUIRK, STATUS, TEXT, TRAINING)
REF = {"feats": FEAT, "statuses": STATUS, "quirks": QUIRK, "trainings": TRAINING, "items": ITEM}


def holder_present(ch, holder):
    if holder.startswith(FEAT):
        return any(f.fid == holder[len(FEAT):] for f in ch.feats)
    if holder.startswith(ITEM):
        return any(it.iid == holder[len(ITEM):] for it in ch.items)
    if holder.startswith(QUIRK):
        return any(q.kid == holder[len(QUIRK):] and not q.burned for q in ch.quirks)
    if holder.startswith(STATUS):
        return any(s.sid == holder[len(STATUS):] and is_effective(s) for s in ch.statuses)
    if holder.startswith(TRAINING):
        return any(t.tid == holder[len(TRAINING):] and t.units > 0 for t in ch.trainings)
    return False


def _rows(ch):
    out = [("feats", f.fid, f.title or f.fid, f.held_by, f.held_kept) for f in ch.feats]
    out += [("statuses", s.sid, s.name, s.held_by, s.held_kept) for s in ch.statuses]
    out += [("quirks", q.kid, q.name, q.held_by, q.held_kept) for q in ch.quirks]
    out += [("trainings", t.tid, t.name, t.held_by, t.held_kept) for t in ch.trainings]
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


def holds(ch, ref):
    """((collection, id, name), ...) of the dependents held by one carrier ref ("feat:<id>", "item:<id>" ...)."""
    return tuple((coll, oid, name) for coll, oid, name, holder, _kept in _rows(ch) if holder == ref)


def view(ch):
    """{carrier ref: {"name", "held_by", "backed", "holds"}} for every feat, status, quirk, training and item (package
    37, owner decision 5: the link shown both ways)."""
    out = {}
    carriers = [("feats", f.fid, f.title or f.fid, f.held_by, f.held_kept) for f in ch.feats]
    carriers += [("statuses", s.sid, s.name, s.held_by, s.held_kept) for s in ch.statuses]
    carriers += [("quirks", q.kid, q.name, q.held_by, q.held_kept) for q in ch.quirks]
    carriers += [("trainings", t.tid, t.name, t.held_by, t.held_kept) for t in ch.trainings]
    carriers += [("items", it.iid, it.name, "", True) for it in ch.items]
    for coll, oid, name, holder, kept in carriers:
        ref = REF[coll] + oid
        out[ref] = {"name": name, "collection": coll, "held_by": holder,
                    "backed": (backed(ch, holder, kept) if holder else True),
                    "holds": tuple((c, o, n) for c, o, n in holds(ch, ref))}
    return out
