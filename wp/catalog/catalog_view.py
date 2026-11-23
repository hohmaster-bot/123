"""Catalog view for the UI (package 18): list and get, with the layer of each entry (shipped / user / override).
Read only: changes go through catalog_cmds."""
from dataclasses import dataclass
from typing import Any

from wp.catalog import store as cs


@dataclass(frozen=True)
class EntryView:
    id: str
    name: str
    layer: str                         # shipped / user / override
    sample: bool
    fields: Any                        # the whole entry (read-only mapping)


def _view(entry, layer):
    return EntryView(entry["id"], str(entry.get("name", "")), layer, bool(entry.get("sample", False)), entry)


def list_entries(layers, text="", sort="name"):
    """Entries whose name or id contains `text` (case-insensitive), sorted by name, id or layer (file order for
    "")."""
    t = text.casefold()
    out = [_view(e, layer) for e, layer in cs.merged(layers)
           if not t or t in str(e.get("name", "")).casefold() or t in e["id"].casefold()]
    if sort in ("name", "id", "layer"):
        out.sort(key=lambda v: (getattr(v, sort).casefold(), v.id))
    return tuple(out)


def get(layers, eid):
    for e, layer in cs.merged(layers):
        if e["id"] == eid:
            return _view(e, layer)
    raise KeyError("no entry %r in the %s catalog" % (eid, layers.kind))
