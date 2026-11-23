"""Catalog commands (package 18, D21): the ONLY way to change a catalog, like character commands (D5).

Pure functions on Layers (the shipped catalog of a kind + the user catalog); they return a new Layers and never save.
The UI (later) reads catalogs through catalog_view and writes them only through these commands; saving is
store.save(result.state.user) (atomic). Refusals are CommandError with a reason id and params.
Commands: catalog_add_entry, catalog_edit_entry, catalog_rename_entry, catalog_remove_entry, catalog_duplicate_entry,
catalog_reset_entry, catalog_import_entry, catalog_create.
- A shipped entry is never changed: editing / renaming it writes an OVERRIDE copy into the user file; removing it
  writes a tombstone; catalog_reset_entry drops the override or the tombstone (the shipped entry comes back).
- Removing a user-only entry deletes it for real; its id goes to "retired" and is never given again.
"""
import os
from dataclasses import dataclass, field, replace
from typing import Any, Dict

from wp.catalog import schema
from wp.catalog import store as cs
from wp.commands.base import CommandError
from wp.core.frozen import FrozenDict

REGISTRY = {}


@dataclass(frozen=True)
class CatalogResult:
    state: Any                         # the new Layers
    info: Dict[str, Any] = field(default_factory=dict)


def catalog_command(fn):
    REGISTRY[fn.__name__] = fn
    return fn


def catalog_dispatch(layers, name, /, **params):
    if name not in REGISTRY:
        raise CommandError("unknown catalog command: %r" % (name,), "unknown_command", command=name)
    try:
        return REGISTRY[name](layers, **params)
    except CommandError:
        raise
    except cs.CatalogError as e:
        raise CommandError(str(e), "catalog_error")


def _valid(kind, entry):
    bad = schema.check(kind, entry)
    if bad:
        reason, params = bad
        raise CommandError("%s: %s" % (reason, ", ".join(str(v) for v in params.get("values", ()))), reason, **params)
    return entry


def _with_user(layers, user):
    return replace(layers, user=user)


def _put_user(layers, entry):
    """Replace or append an entry in the user file (same id)."""
    entries = layers.user.entries
    if any(e["id"] == entry["id"] for e in entries):
        entries = tuple(entry if e["id"] == entry["id"] else e for e in entries)
    else:
        entries = entries + (entry,)
    return _with_user(layers, replace(layers.user, entries=entries))


def _current(layers, eid):
    for e, layer in cs.merged(layers):
        if e["id"] == eid:
            return e, layer
    raise CommandError("no entry %r in the %s catalog" % (eid, layers.kind), "not_found", values=(layers.kind, eid))


def _add(layers, fields, info=None):
    fields = dict(fields)
    if not fields.get("name"):
        raise CommandError("an entry needs a name", "entry_needs_name")
    eid, counter = cs.new_id(layers, fields["name"])
    fields["id"] = eid
    fields.setdefault("sample", False)
    entry = cs.freeze(_valid(layers.kind, fields))
    new = _put_user(layers, entry)
    new = _with_user(new, replace(new.user, counter=counter))
    return CatalogResult(new, dict(info or {}, id=eid))


@catalog_command
def catalog_add_entry(layers, fields=None):
    return _add(layers, fields or {})


@catalog_command
def catalog_edit_entry(layers, eid="", **fields):
    """Any field (unknown fields are kept as they are); the id never changes."""
    if "id" in fields:
        raise CommandError("an id cannot be changed", "id_not_editable", values=("id",))
    entry, layer = _current(layers, eid)
    new = dict(entry)
    new.update(fields)
    entry = cs.freeze(_valid(layers.kind, new))
    return CatalogResult(_put_user(layers, entry), {"id": eid, "layer": cs.OVERRIDE if layer != cs.USER else cs.USER})


@catalog_command
def catalog_rename_entry(layers, eid="", name=""):
    if not name:
        raise CommandError("an entry needs a name", "entry_needs_name")
    return catalog_edit_entry(layers, eid=eid, name=name)


@catalog_command
def catalog_remove_entry(layers, eid=""):
    _, layer = _current(layers, eid)
    if layer in (cs.SHIPPED, cs.OVERRIDE):     # tombstone: the shipped entry is hidden, the id stays taken
        return CatalogResult(_put_user(layers, FrozenDict(id=eid, deleted=True)), {"id": eid, "tombstone": True})
    user = layers.user
    user = replace(user, entries=tuple(e for e in user.entries if e["id"] != eid), retired=user.retired + (eid,))
    return CatalogResult(_with_user(layers, user), {"id": eid, "tombstone": False})


@catalog_command
def catalog_duplicate_entry(layers, eid="", name=""):
    entry, _ = _current(layers, eid)
    fields = {k: v for k, v in entry.items() if k != "id"}
    if name:
        fields["name"] = name
    fields["sample"] = False           # a copy made by the user is not a shipped sample (assumption Q132)
    return _add(layers, fields, {"from": eid})


@catalog_command
def catalog_reset_entry(layers, eid=""):
    shipped = layers.shipped.find(eid) if layers.shipped else None
    if shipped is None or layers.user.find(eid) is None:
        raise CommandError("%r has no user override to drop" % (eid,), "no_override", values=(eid,))
    user = replace(layers.user, entries=tuple(e for e in layers.user.entries if e["id"] != eid))
    return CatalogResult(_with_user(layers, user), {"id": eid})


@catalog_command
def catalog_import_entry(layers, code=""):
    """An entry from a text code (store.export_entry): added as a NEW user entry (a new id, the name kept)."""
    kind, entry = cs.import_code(code)
    if kind != layers.kind:
        raise CommandError("the code is a %s entry, this catalog is %s" % (kind, layers.kind), "wrong_kind",
                           values=(kind, layers.kind))
    entry.pop("id", None)
    return _add(layers, entry, {"imported": True})


@catalog_command
def catalog_create(layers=None, kind="", path="", title=""):
    """A new EMPTY user catalog file of a kind (not written yet: store.save writes it)."""
    if kind not in schema.KINDS:
        raise CommandError("unknown catalog kind %r" % (kind,), "unknown_kind", values=(kind,))
    if not path:
        raise CommandError("a new catalog needs a file path", "path_needed")
    if os.path.exists(path):
        raise CommandError("the file already exists: %s" % path, "catalog_exists", values=(path,))
    if cs.in_shipped_folder(path):
        raise CommandError("shipped catalogs are read-only", "shipped_read_only", values=(path,))
    return CatalogResult(cs.Layers(None, cs.Catalog(kind=kind, title=title, path=path)), {"kind": kind})
