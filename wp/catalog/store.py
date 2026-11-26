"""Catalog files (RULES/catalog.md "Catalog files", package 18, D21).

One catalog = ONE self-contained JSON file:
    {"kind": "<kind>", "format": 1, "title": "...", "counter": 0, "retired": [ids], "meta": {...},
     "entries": [{"id": ..., "name": ..., "sample": false, <fields of the kind>, <unknown fields kept>}, ...]}
Known top-level fields: kind, format, title, counter, retired, meta, entries; any other top-level field is dropped on
load (no migrations). Unknown fields of an ENTRY are kept on edit and save, never interpreted.
A tombstone entry {"id": x, "deleted": true} lives only in a user file: it hides a shipped entry.

Two layers: SHIPPED catalogs (read-only, wp/catalog/data/<kind>.json) and USER catalogs (a folder next to the
characters, catalogs/<kind>.json). A user entry with the same id wins over the shipped one ("override"). The program
never writes into the shipped folder.
Ids: made by the program from the name (transliteration); on a collision with ANY id ever used in either layer
(live, tombstoned or retired) a number from the user file's counter is added. A deleted user id is kept in "retired"
and never given again.
Saving is atomic: the text is built first, written to <path>.tmp, then os.replace; a failed save leaves the old file.
"""
import base64
import io
import json
import os
import zlib
from dataclasses import dataclass, replace
from typing import Any, Optional, Tuple

from wp.core.frozen import FrozenDict
from wp.model import ids

FORMAT = 1
SHIPPED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TOP = ("kind", "format", "title", "counter", "retired", "meta", "entries")
DELETED = "deleted"
SHIPPED = "shipped"
USER = "user"
OVERRIDE = "override"
CODE_PREFIX = "WFC1:"
_replace = os.replace            # patched by the atomic-save test


class CatalogError(ValueError):
    """A catalog file could not be read or written."""


@dataclass(frozen=True)
class Catalog:
    kind: str
    entries: Tuple[Any, ...] = ()      # FrozenDicts, file order
    title: str = ""
    counter: int = 0
    retired: Tuple[str, ...] = ()
    meta: Any = FrozenDict()
    path: str = ""                     # where it was loaded from / is saved to ("" = not on disk yet)

    def ids(self):
        return tuple(e["id"] for e in self.entries)

    def find(self, eid):
        return next((e for e in self.entries if e["id"] == eid), None)


@dataclass(frozen=True)
class Layers:
    """The shipped catalog of a kind (or None) and the user catalog of the same kind."""
    shipped: Optional[Catalog]
    user: Catalog

    @property
    def kind(self):
        return self.user.kind


# ------------------------------------------------------------------ files

def freeze(v):
    """Read-only copy: dicts -> FrozenDict, lists -> tuples (deep)."""
    if isinstance(v, dict):
        return FrozenDict((k, freeze(x)) for k, x in v.items())
    if isinstance(v, (list, tuple)):
        return tuple(freeze(x) for x in v)
    return v


def from_data(data, path=""):
    if not isinstance(data, dict) or data.get("format") != FORMAT or not data.get("kind"):
        raise CatalogError("not a WipeFinder catalog file (kind + format 1 needed): %s" % (path or "<text>"))
    entries = []
    for e in data.get("entries", ()):
        if not isinstance(e, dict) or not e.get("id"):
            raise CatalogError("an entry without an id in %s" % (path or data["kind"]))
        entries.append(freeze(e))
    seen = [e["id"] for e in entries]
    if len(seen) != len(set(seen)):
        raise CatalogError("duplicate entry ids in %s" % (path or data["kind"]))
    return Catalog(kind=str(data["kind"]), entries=tuple(entries), title=str(data.get("title", "")),
                   counter=int(data.get("counter", 0)), retired=tuple(data.get("retired", ())),
                   meta=freeze(data.get("meta", {})), path=path)


def _plain(v):
    if isinstance(v, dict):
        return {k: _plain(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_plain(x) for x in v]
    return v


def to_data(cat):
    return {"kind": cat.kind, "format": FORMAT, "title": cat.title, "counter": cat.counter,
            "retired": list(cat.retired), "meta": _plain(cat.meta), "entries": [_plain(e) for e in cat.entries]}


def dumps(cat):
    return json.dumps(to_data(cat), ensure_ascii=False, indent=1)


def loads(text, path=""):
    try:
        data = json.loads(text)
    except ValueError as e:
        raise CatalogError("catalog file is not valid JSON: %s" % e)
    return from_data(data, path)


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return loads(f.read(), path)


def shipped_path(kind):
    return os.path.join(SHIPPED_DIR, kind + ".json")


def load_shipped(kind):
    """The shipped catalog of a kind; package 36: a folder data/<kind>/ of one file per game module (races) is
    merged into one catalog (the entries of every module file, in file name order)."""
    folder = os.path.join(SHIPPED_DIR, kind)
    if os.path.isdir(folder):
        data = {"kind": kind, "format": FORMAT, "title": kind, "counter": 0, "retired": [], "meta": {}, "entries": []}
        for name in sorted(os.listdir(folder)):
            if name.endswith(".json"):
                with io.open(os.path.join(folder, name), encoding="utf-8") as f:
                    data["entries"] += json.load(f)["entries"]
        return from_data(data, folder)
    p = shipped_path(kind)
    return load(p) if os.path.exists(p) else None


def user_path(folder, kind):
    return os.path.join(folder, kind + ".json")


def load_user(folder, kind):
    """The user catalog of a kind (an empty one when the file does not exist yet)."""
    p = user_path(folder, kind)
    return load(p) if os.path.exists(p) else Catalog(kind=kind, path=p)


def load_layers(kind, user_folder):
    return Layers(load_shipped(kind), load_user(user_folder, kind))


def in_shipped_folder(path):
    a = os.path.normcase(os.path.abspath(path))
    b = os.path.normcase(os.path.abspath(SHIPPED_DIR))
    return a == b or a.startswith(b + os.sep)


def save(cat, path=None):
    """Atomic save of a USER catalog. Never into the shipped folder."""
    path = path or cat.path
    if not path:
        raise CatalogError("no path to save the catalog to")
    if in_shipped_folder(path):
        raise CatalogError("shipped catalogs are read-only: %s" % path)
    atomic_write(path, dumps(cat))        # the text is built before anything is written
    return replace(cat, path=path)


def atomic_write(path, text):
    """Write text to <path>.tmp, flush, fsync, then replace <path>; a failure leaves the old file (also used by the
    settings files, package 19)."""
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    try:
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        _replace(tmp, path)
    except OSError as e:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise CatalogError("saving failed (the old file is kept): %s" % e)


# ------------------------------------------------------------------ layers

def is_tombstone(e):
    return bool(e.get(DELETED))


def merged(layers):
    """[(entry, layer)] in order: shipped entries (overridden or hidden by the user file), then user-only entries."""
    user = {e["id"]: e for e in layers.user.entries}
    out = []
    for e in (layers.shipped.entries if layers.shipped else ()):
        u = user.get(e["id"])
        if u is None:
            out.append((e, SHIPPED))
        elif not is_tombstone(u):
            out.append((u, OVERRIDE))
    shipped_ids = set(layers.shipped.ids()) if layers.shipped else set()
    out += [(e, USER) for e in layers.user.entries if e["id"] not in shipped_ids and not is_tombstone(e)]
    return out


def taken_ids(layers):
    out = set(layers.user.ids()) | set(layers.user.retired)
    if layers.shipped:
        out |= set(layers.shipped.ids()) | set(layers.shipped.retired)
    return out


def new_id(layers, name):
    """(id, new counter): the slug of the name, or slug_N with N from the counter when it was ever used."""
    base = ids.slug(name)
    taken = taken_ids(layers)
    counter = layers.user.counter
    if base not in taken:
        return base, counter
    while True:
        counter += 1
        eid = "%s_%d" % (base, counter)
        if eid not in taken:
            return eid, counter


# ------------------------------------------------------------------ entry codes

def export_entry(kind, entry):
    """One entry as a text code for the clipboard (gear.md "Item codes / sharing")."""
    raw = json.dumps({"kind": kind, "entry": _plain(entry)}, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return CODE_PREFIX + base64.urlsafe_b64encode(zlib.compress(raw)).decode("ascii")


def import_code(code):
    """(kind, entry dict) from a code made by export_entry. Review 5 F11: the code length and the unpacked size are
    limited (wp/app/data/limits.json code_max_chars / code_max_unpacked, a bounded decompress); the data must be
    {"kind": text, "entry": {...}}; every problem is a CatalogError (the command gives catalog_error)."""
    from wp.app import limits
    if not isinstance(code, str) or not code.startswith(CODE_PREFIX):
        raise CatalogError("not a WipeFinder entry code")
    if len(code) > limits.get("code_max_chars"):
        raise CatalogError("the entry code is too long")
    cap = limits.get("code_max_unpacked")
    try:
        z = zlib.decompressobj()
        raw = z.decompress(base64.urlsafe_b64decode(code[len(CODE_PREFIX):].encode("ascii")), cap + 1)
        if len(raw) > cap or z.unconsumed_tail:
            raise CatalogError("the entry code unpacks to more than %d bytes" % cap)
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, zlib.error, RecursionError, UnicodeError) as e:
        raise CatalogError("broken entry code: %s" % e)
    if not isinstance(data, dict) or not isinstance(data.get("kind"), str) or not isinstance(data.get("entry"), dict):
        raise CatalogError("broken entry code: not {kind, entry}")
    return data["kind"], dict(data["entry"])
