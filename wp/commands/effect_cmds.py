"""Effect editor commands (package 38 P5, owner decision 9; wp/model/effect_form.py; ARCH decision D37).

The effects of a character carrier change only here (journal, undo): effect_add(collection, oid, form, field),
effect_change(collection, oid, index, form, field), effect_remove(collection, oid, index, field).
collection: feats / items / statuses / quirks / trainings / injuries; field: "effects" (items: "effects_off" = not
activated, "effects_on" = activated, D17). The form is checked by effect_form.build: invalid input is refused with
its reason and nothing changes.
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.model import effect_form as ef

CARRIERS = {"feats": "fid", "items": "iid", "statuses": "sid", "quirks": "kid", "trainings": "tid",
            "injuries": "jid"}
ITEM_FIELDS = ("effects_off", "effects_on")


def _field(collection, field):
    allowed = ITEM_FIELDS if collection == "items" else ("effects",)
    field = field or allowed[0]
    if field not in allowed:
        raise CommandError("%s has no %s" % (collection, field), "unknown_fields", values=(field,))
    return field


def _owner(ch, collection, oid):
    key = CARRIERS.get(collection)
    if key is None:
        raise CommandError("no effects in %s" % collection, "unknown_collection", values=(collection,))
    rec = next((r for r in getattr(ch, collection) if getattr(r, key) == oid), None)
    if rec is None:
        raise CommandError("no %s %r" % (collection, oid), "not_found", values=(collection, oid))
    return key, rec


def _effect(form):
    try:
        return ef.build(form)
    except ef.EffectFormError as e:
        raise CommandError("%s %s" % (e.reason, ", ".join(e.values)), e.reason, values=e.values)


def _put(ch, collection, key, rec, field, effects):
    new = replace(rec, **{field: tuple(effects)})
    rows = tuple(new if getattr(r, key) == getattr(rec, key) else r for r in getattr(ch, collection))
    return replace(ch, **{collection: rows})


def _index(effects, index):
    i = int(index)
    if not 0 <= i < len(effects):
        raise CommandError("no effect %d" % i, "not_found", values=("effects", i))
    return i


@command
def effect_add(ch, collection="", oid="", form=None, field=""):
    key, rec = _owner(ch, collection, oid)
    field = _field(collection, field)
    e = _effect(form)
    new = _put(ch, collection, key, rec, field, tuple(getattr(rec, field)) + (e,))
    return commit(new, "effect_add", "%s %s %s" % (collection, oid, e.target), {"index": len(getattr(rec, field))})


@command
def effect_change(ch, collection="", oid="", index=0, form=None, field=""):
    key, rec = _owner(ch, collection, oid)
    field = _field(collection, field)
    have = list(getattr(rec, field))
    i = _index(have, index)
    have[i] = _effect(form)
    return commit(_put(ch, collection, key, rec, field, have), "effect_change", "%s %s #%d" % (collection, oid, i))


@command
def effect_remove(ch, collection="", oid="", index=0, field=""):
    key, rec = _owner(ch, collection, oid)
    field = _field(collection, field)
    have = list(getattr(rec, field))
    i = _index(have, index)
    del have[i]
    return commit(_put(ch, collection, key, rec, field, have), "effect_remove", "%s %s #%d" % (collection, oid, i))
