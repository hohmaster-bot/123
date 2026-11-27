"""The effect editor for the UI, Qt-free (package 38 P5, owner decision 9; ARCH decision D37).

Character carriers: carriers(session) -> ((collection, oid, name, fields), ...) of feats / race abilities, items,
statuses, quirks, trainings, injuries; effects(session, collection, oid, field) -> the effects; apply(session, op,
...) runs the character command effect_add / effect_change / effect_remove (journal, undo).
Catalog entries: catalog_effects(session, kind, eid, field) and catalog_apply(session, kind, eid, op, index, form,
field): the new list is checked by effect_form.build (nothing invalid is saved) and written with catalog_edit_entry
into the user layer of the kind (the entry keeps every other field, its module tag included).
"""
from wp.app.session import DispatchResult
from wp.core import bonuses as bo
from wp.catalog import convert
from wp.catalog import store as cs
from wp.model import effect_form as ef

CHARACTER = (("feats", "fid", ("effects",)), ("items", "iid", ("effects_off", "effects_on")),
             ("statuses", "sid", ("effects",)), ("quirks", "kid", ("effects",)), ("trainings", "tid", ("effects",)),
             ("injuries", "jid", ("effects",)))
CATALOG_KINDS = {"feats": ("effects",), "items": ("effects_off", "effects_on"), "statuses": ("effects",),
                 "trainings": ("effects",)}           # race abilities keep their effects inside the race entry
BTYPES = (bo.FLAT,) + tuple(sorted(t for t in bo.TYPES if t != bo.FLAT))
COMMAND = {"add": "effect_add", "change": "effect_change", "remove": "effect_remove"}


def _name(r):
    return getattr(r, "title", "") or getattr(r, "name", "") or ""


def carriers(session):
    ch = session.character
    if ch is None:
        return ()
    return tuple((coll, getattr(r, key), _name(r) or getattr(r, key), fields)
                 for coll, key, fields in CHARACTER for r in getattr(ch, coll))


def effects(session, collection, oid, field="effects"):
    for coll, key, fields in CHARACTER:
        if coll == collection:
            rec = next((r for r in getattr(session.character, coll) if getattr(r, key) == oid), None)
            return tuple(getattr(rec, field)) if rec is not None and field in fields else ()
    return ()


def apply(session, op, collection, oid, index=0, form=None, field="effects"):
    params = {"collection": collection, "oid": oid, "field": field}
    if op != "add":
        params["index"] = int(index)
    if op != "remove":
        params["form"] = dict(form or {})
    return session.dispatch(COMMAND[op], **params)


def _entry(session, kind, eid):
    return next((dict(e) for e, _layer in cs.merged(session.catalog(kind)) if e["id"] == eid), None)


def catalog_effects(session, kind, eid, field="effects"):
    e = _entry(session, kind, eid)
    return tuple(convert.effect(cs._plain(d)) for d in (e or {}).get(field, ()))


def _refused(err):
    return DispatchResult(False, reason=err.reason, params={"values": err.values}, info={"text": str(err)})


def catalog_apply(session, kind, eid, op, index=0, form=None, field="effects"):
    have = list(catalog_effects(session, kind, eid, field))
    try:
        if op == "add":
            have.append(ef.build(form))
        elif not 0 <= int(index) < len(have):
            raise ef.EffectFormError("not_found", ("effects", index))
        elif op == "change":
            have[int(index)] = ef.build(form)
        else:
            del have[int(index)]
    except ef.EffectFormError as e:
        return _refused(e)
    return session.catalog_command(kind, "catalog_edit_entry", eid=eid, **{field: [ef.to_data(x) for x in have]})
