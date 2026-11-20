"""Edit-mode commands (package 16 A3, owner: "all of them, no limits"): create, change, rename and delete ANY sheet
value or record by command, WITHOUT rule limits (prices, caps, refusals of the play commands do not apply here).
They stay the only mutation path (D5) and are journaled (kind "edit"). Ids never change (D7): a rename edits the
name field; a new record without an id gets one made by the program.

- edit_sheet(**fields): any Character field except the journal and the collections below (numbers, flags, Pools,
  PainProfile, RulesSettings, the slots / resources / save dicts...).
- edit_ability(name, **fields): base / race / bonuses / damage / permanent of one ability.
- edit_rules(**fields): fields of rules_settings.
- add_entry(collection, record) / edit_entry(collection, oid, **fields) / remove_entry(collection, oid): one record of
  a collection (COLLECTIONS). Effects given here are validated like everywhere (formulas, package 14 C).
The UI editors themselves (values, layout, view settings) are the UI phase.
"""
import dataclasses
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import formula as fm
from wp.model import formulas as fx
from wp.model import ids

# collection -> id field ("weapon.name" = the id is inside the record)
COLLECTIONS = {
    "items": "iid", "feats": "fid", "statuses": "sid", "pools": "pid", "injuries": "jid", "attacks": "rid",
    "maneuvers": "mid", "skills": "name", "weapons": "weapon.name", "languages": "lid", "seeds": "sid",
    "spells": "spid", "quests": "qid", "stories": "stid", "courts": "cid", "quirks": "kid", "lenses": "lid",
    "drives": "did", "templates": "tid", "charges": "name",
}
NOT_EDITABLE = ("log", "log_seq")
NAME_FIELDS = ("name", "title")


def _oid(rec, key):
    if key == "weapon.name":
        return rec.weapon.name
    return getattr(rec, key)


def _collection(name):
    if name not in COLLECTIONS:
        raise CommandError("unknown collection %r" % (name,), "unknown_collection", values=(name,))
    return COLLECTIONS[name]


def _check_effects(rec):
    for f in ("effects", "effects_on", "effects_off"):
        if hasattr(rec, f):
            try:
                fx.validate_effects(getattr(rec, f))
            except fm.FormulaError as e:
                raise CommandError("bad effect formula: %s" % e, "bad_effect_formula", values=(str(e),))


def _fields(rec, fields, protect=()):
    known = {f.name for f in dataclasses.fields(rec)}
    bad = sorted(set(fields) - known)
    if bad:
        raise CommandError("unknown fields: %s" % ", ".join(bad), "unknown_fields", values=(", ".join(bad),))
    fixed = sorted(set(fields) & set(protect))
    if fixed:
        raise CommandError("ids cannot be changed: %s" % ", ".join(fixed), "id_not_editable", values=(", ".join(fixed),))
    return replace(rec, **fields)


@command
def edit_sheet(ch, **fields):
    blocked = sorted(set(fields) & (set(NOT_EDITABLE) | set(COLLECTIONS)))
    if blocked:
        raise CommandError("use the collection / journal commands for: %s" % ", ".join(blocked), "not_a_sheet_value",
                           values=(", ".join(blocked),))
    new = _fields(ch, fields)
    return commit(new, "edit_sheet", "edit: %s" % ", ".join(sorted(fields)))


@command
def edit_ability(ch, name="", **fields):
    if name not in ch.abilities:
        raise CommandError("no ability %r" % (name,), "not_found", values=(name,))
    ab = _fields(ch.abilities[name], fields)
    abilities = dict(ch.abilities)
    abilities[name] = ab
    return commit(replace(ch, abilities=abilities), "edit_ability", "edit %s" % name)


@command
def edit_rules(ch, **fields):
    return commit(replace(ch, rules_settings=_fields(ch.rules_settings, fields)), "edit_rules",
                  "rules: %s" % ", ".join(sorted(fields)))


def _with_id(ch, coll, key, rec):
    if key == "weapon.name":
        if not rec.weapon.name:
            raise CommandError("a weapon node needs its id (weapon.name)", "id_needed")
        return rec
    if getattr(rec, key):
        return rec
    title = next((getattr(rec, f) for f in NAME_FIELDS if getattr(rec, f, "")), coll)
    return replace(rec, **{key: ids.make_id(title, (_oid(r, key) for r in getattr(ch, coll)))})


@command
def add_entry(ch, collection="", record=None):
    key = _collection(collection)
    if record is None:
        raise CommandError("no record given", "no_record")
    if collection == "injuries" and not record.jid:     # injury ids come from the counter (Q75)
        injuries, counter = ids.with_injury_ids(ch.injuries + (record,), ch.injury_counter)
        _check_effects(injuries[-1])
        return commit(replace(ch, injuries=injuries, injury_counter=counter), "add_entry",
                      "injuries + %s" % injuries[-1].jid, {"id": injuries[-1].jid})
    rec = _with_id(ch, collection, key, record)
    if any(_oid(r, key) == _oid(rec, key) for r in getattr(ch, collection)):
        raise CommandError("%s already has %r" % (collection, _oid(rec, key)), "id_taken", values=(collection, _oid(rec, key)))
    _check_effects(rec)
    new = replace(ch, **{collection: getattr(ch, collection) + (rec,)})
    return commit(new, "add_entry", "%s + %s" % (collection, _oid(rec, key)), {"id": _oid(rec, key)})


def _find(ch, collection, oid):
    key = _collection(collection)
    rec = next((r for r in getattr(ch, collection) if _oid(r, key) == oid), None)
    if rec is None:
        raise CommandError("no %s %r" % (collection, oid), "not_found", values=(collection, oid))
    return key, rec


@command
def edit_entry(ch, collection="", oid="", **fields):
    key, rec = _find(ch, collection, oid)
    new_rec = _fields(rec, fields, protect=(key,) if "." not in key else ())
    if key == "weapon.name" and new_rec.weapon.name != oid:
        raise CommandError("ids cannot be changed: weapon.name", "id_not_editable", values=("weapon.name",))
    _check_effects(new_rec)
    rows = tuple(new_rec if _oid(r, key) == oid else r for r in getattr(ch, collection))
    return commit(replace(ch, **{collection: rows}), "edit_entry", "%s %s: %s" % (collection, oid, ", ".join(sorted(fields))))


@command
def remove_entry(ch, collection="", oid=""):
    key, _ = _find(ch, collection, oid)
    rows = tuple(r for r in getattr(ch, collection) if _oid(r, key) != oid)
    new = replace(ch, **{collection: rows})
    if collection == "items":          # the item's attack records and links go with it, like remove_item
        from wp.commands.item_cmds import remove_item
        return remove_item(ch, iid=oid)
    if collection == "feats" and ch.active_stance == oid:
        new = replace(new, active_stance=None)
    return commit(new, "remove_entry", "%s - %s" % (collection, oid))


EDIT_COMMANDS = ("edit_sheet", "edit_ability", "edit_rules", "add_entry", "edit_entry", "remove_entry")
