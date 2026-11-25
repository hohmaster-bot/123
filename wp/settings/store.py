"""The application settings file (package 19, D13, D22). Two layers like catalogs (D21):
- shipped: the defaults of the schema (settings_schema.json) and the default layout profiles (default_profiles.json),
  read-only, in the install folder;
- user: one file <user folder>/app_settings.json with only what the user changed.
File: {"kind": "app_settings", "format": 1, "values": {key: value}, "profiles": {"classic": [...], "lite": [...]},
"active": {"classic": id, "lite": id}, "quick_buttons": [...], "images": [...], "image_for": {"kind:id": image id},
"counter": n, "retired": [ids]}. Unknown keys inside "values" (and unknown fields of records) are kept as they are and
never interpreted; unknown top-level fields are dropped on load; no migrations. Atomic save (catalog store).
Character-bound settings live in the character file (Character.char_settings); game rule settings in
Character.rules_settings.
"""
import io
import json
import os
import re
from dataclasses import dataclass, replace
from typing import Any, Tuple

from wp.catalog import store as cs
from wp.core.frozen import FrozenDict
from wp.settings import schema as sch

KIND = "app_settings"
FORMAT = 1
FILE = "app_settings.json"
MODES = ("classic", "lite")
DEFAULT_PROFILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "default_profiles.json")
freeze = cs.freeze


IMAGE_FILE = re.compile(r"^images/([A-Za-z0-9_\-]+)\.([a-z0-9]{1,8})$")


def image_record_ok(rec):
    """An image record is {id, file = images/<id>.<ext>, ...} (review 5 F8): a file elsewhere is never used."""
    if not isinstance(rec, dict) or not isinstance(rec.get("id"), str) or not isinstance(rec.get("file"), str):
        return False
    m = IMAGE_FILE.match(rec["file"])
    return bool(m) and m.group(1) == rec["id"]


class SettingsError(ValueError):
    """A settings file could not be read or written."""


def _shipped_profiles():
    with io.open(DEFAULT_PROFILES, encoding="utf-8") as f:
        d = json.load(f)
    return freeze({m: d[m] for m in MODES})


@dataclass(frozen=True)
class AppSettings:
    values: Any = FrozenDict()         # only the keys the user changed (+ unknown keys, kept)
    profiles: Any = None               # {"classic": (profile, ...), "lite": (...)}
    active: Any = None                 # {"classic": id, "lite": id}
    quick_buttons: Tuple[Any, ...] = ()
    images: Tuple[Any, ...] = ()
    image_for: Any = FrozenDict()      # "target kind:target id" -> image id
    counter: int = 0                   # ids of profiles, quick buttons, images: number on a collision
    retired: Tuple[str, ...] = ()      # deleted ids, never given again
    path: str = ""

    def __post_init__(self):
        if self.profiles is None:
            object.__setattr__(self, "profiles", _shipped_profiles())
        if self.active is None:
            object.__setattr__(self, "active", FrozenDict({m: self.profiles[m][0]["id"] for m in MODES}))


def default_of(key):
    return sch.KEYS[key]["default"]


def get(app, key):
    """The value of an app key: the user's value, else the shipped default."""
    if key in app.values:
        return app.values[key]
    if key in sch.KEYS:
        return default_of(key)
    raise KeyError("no setting %r" % (key,))


def changed(app, key):
    return key in app.values and app.values[key] != default_of(key)


def profile(app, mode, pid=None):
    pid = pid or app.active[mode]
    return next((p for p in app.profiles[mode] if p["id"] == pid), None)


# ------------------------------------------------------------------ files

def _plain(v):
    return cs._plain(v)


def to_data(app):
    return {"kind": KIND, "format": FORMAT, "values": _plain(app.values), "profiles": _plain(app.profiles),
            "active": _plain(app.active), "quick_buttons": _plain(app.quick_buttons), "images": _plain(app.images),
            "image_for": _plain(app.image_for), "counter": app.counter, "retired": list(app.retired)}


def dumps(app):
    return json.dumps(to_data(app), ensure_ascii=False, indent=1)


def from_data(data, path=""):
    if not isinstance(data, dict) or data.get("kind") != KIND or data.get("format") != FORMAT:
        raise SettingsError("not a WipeFinder settings file: %s" % (path or "<text>"))
    profiles = data.get("profiles")
    if profiles is not None:
        shipped = _shipped_profiles()
        profiles = freeze({m: profiles.get(m) or shipped[m] for m in MODES})
    active = data.get("active")
    app = AppSettings(values=freeze(data.get("values", {})), profiles=profiles,
                      active=freeze(active) if active else None, quick_buttons=freeze(data.get("quick_buttons", [])),
                      images=freeze([i for i in data.get("images", []) or () if image_record_ok(i)]), image_for=freeze(data.get("image_for", {})),
                      counter=int(data.get("counter", 0)), retired=tuple(data.get("retired", ())), path=path)
    for m in MODES:                    # an active id that no longer exists falls back to the first profile
        if profile(app, m) is None:
            app = replace(app, active=FrozenDict(dict(app.active, **{m: app.profiles[m][0]["id"]})))
    return app


def loads(text, path=""):
    try:
        data = json.loads(text)
    except (ValueError, RecursionError) as e:
        raise SettingsError("settings file is not valid JSON: %s" % e)
    return from_data(data, path)


def load(user_folder):
    """The settings of a user folder (only the shipped defaults when the file does not exist yet)."""
    path = os.path.join(user_folder, FILE)
    if not os.path.exists(path):
        return AppSettings(path=path)
    with io.open(path, encoding="utf-8") as f:
        return loads(f.read(), path)


def save(app, path=None):
    path = path or app.path
    if not path:
        raise SettingsError("no path to save the settings to")
    if cs.in_shipped_folder(path) or os.path.normcase(os.path.abspath(path)).startswith(
            os.path.normcase(os.path.dirname(DEFAULT_PROFILES))):
        raise SettingsError("the shipped settings are read-only: %s" % path)
    try:
        cs.atomic_write(path, dumps(app))
    except cs.CatalogError as e:
        raise SettingsError(str(e))
    return replace(app, path=path)
