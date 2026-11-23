"""Themes as token data (package 21, D24). Two layers like catalogs (D21): shipped wp/theme/data/themes.json
(read-only) and the user file <user folder>/themes.json (overrides, tombstones, own themes). The file format, ids,
merge, atomic save and entry codes are the catalog store's (wp/catalog/store.py).

check(theme) -> None or (reason, params): missing_token, bad_color, bad_size; a theme must also build its QSS.
Commands (pure, on Layers; the active theme lives in the app settings key "theme"):
theme_add, theme_edit, theme_remove, theme_duplicate, theme_set_active(app, layers, tid) -> new AppSettings,
theme_export (a text code), theme_import.
"""
import io
import json
import os
import re
from dataclasses import replace

from wp.catalog import store as cs
from wp.commands.base import CommandError
from wp.core.frozen import FrozenDict
from wp.theme import qss

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SHIPPED = os.path.join(DATA, "themes.json")
KIND = "themes"
COLOR = re.compile(r"^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$")


def _schema():
    with io.open(os.path.join(DATA, "theme_schema.json"), encoding="utf-8") as f:
        return json.load(f)


SCHEMA = _schema()


def shipped():
    return cs.load(SHIPPED)


def shipped_ids():
    return shipped().ids()


def load_layers(user_folder):
    return cs.Layers(shipped(), cs.load_user(user_folder, KIND))


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def check(theme):
    colors = theme.get("colors") or {}
    for c in SCHEMA["colors"]:
        if c not in colors:
            return "missing_token", {"values": ("colors." + c,), "token": "colors." + c}
        if not isinstance(colors[c], str) or not COLOR.match(colors[c]):
            return "bad_color", {"values": (c, colors[c]), "token": "colors." + c}
    fonts = theme.get("fonts") or {}
    for name, kind in SCHEMA["fonts"].items():
        if name not in fonts:
            return "missing_token", {"values": ("fonts." + name,), "token": "fonts." + name}
        v = fonts[name]
        if (kind == "string" and not isinstance(v, str)) or (kind == "positive" and not (_num(v) and v > 0)):
            return "bad_size", {"values": ("fonts." + name, v), "token": "fonts." + name}
    for name, kind in SCHEMA["scalars"].items():
        if name not in theme:
            return "missing_token", {"values": (name,), "token": name}
        v = theme[name]
        ok = {"size": _num(v) and v >= 0, "string": isinstance(v, str),
              "percent": _num(v) and 0 <= v <= 100}[kind]
        if not ok:
            return "bad_size", {"values": (name, v), "token": name}
    try:
        qss.build(theme)
    except qss.ThemeError as e:
        return e.reason, e.params
    return None


def _valid(theme):
    bad = check(theme)
    if bad:
        reason, params = bad
        raise CommandError("%s: %s" % (reason, ", ".join(str(v) for v in params.get("values", ()))), reason, **params)
    return theme


def _current(layers, tid):
    for e, layer in cs.merged(layers):
        if e["id"] == tid:
            return e, layer
    raise CommandError("no theme %r" % (tid,), "not_found", values=("themes", tid))


def _put(layers, entry):
    user = layers.user
    rows = user.entries
    rows = tuple(entry if e["id"] == entry["id"] else e for e in rows) if user.find(entry["id"]) else rows + (entry,)
    return replace(layers, user=replace(user, entries=rows))


def theme_add(layers, theme=None):
    t = dict(theme or {})
    if not t.get("name"):
        raise CommandError("a theme needs a name", "name_needed")
    _valid(t)
    tid, counter = cs.new_id(layers, t["name"])
    t.update(id=tid, sample=bool(t.get("sample", False)))
    new = _put(layers, cs.freeze(t))
    return replace(new, user=replace(new.user, counter=counter)), tid


def theme_edit(layers, tid="", **fields):
    """Fields of a theme (colors / fonts are merged key by key). A shipped theme gets a user override copy."""
    if "id" in fields:
        raise CommandError("an id cannot be changed", "id_not_editable", values=("id",))
    entry, _ = _current(layers, tid)
    t = json.loads(json.dumps(cs._plain(entry)))
    for k, v in fields.items():
        if k in ("colors", "fonts") and isinstance(v, dict):
            t[k] = dict(t.get(k, {}), **v)
        else:
            t[k] = v
    return _put(layers, cs.freeze(_valid(t)))


def theme_remove(layers, tid=""):
    _, layer = _current(layers, tid)
    if layer in (cs.SHIPPED, cs.OVERRIDE):
        return _put(layers, FrozenDict(id=tid, deleted=True))
    user = layers.user
    return replace(layers, user=replace(user, entries=tuple(e for e in user.entries if e["id"] != tid),
                                        retired=user.retired + (tid,)))


def theme_duplicate(layers, tid="", name=""):
    entry, _ = _current(layers, tid)
    t = {k: v for k, v in cs._plain(entry).items() if k != "id"}
    t.update(name=name or t["name"], sample=False)
    return theme_add(layers, t)


def theme_set_active(app, layers, tid=""):
    _current(layers, tid)
    from wp.settings import settings_cmds as sc
    return sc.settings_dispatch(app, "settings_set", key="theme", value=tid).state


def active(app, layers):
    """The active theme (the app setting); an unknown id falls back to the first theme (light)."""
    from wp.settings import store as st
    tid = st.get(app, "theme")
    themes = dict((e["id"], e) for e, _ in cs.merged(layers))
    return themes.get(tid) or themes.get("light") or next(iter(themes.values()))


def theme_export(layers, tid=""):
    entry, _ = _current(layers, tid)
    return cs.export_entry(KIND, entry)


def theme_import(layers, code=""):
    kind, entry = cs.import_code(code)
    if kind != KIND:
        raise CommandError("the code is a %s entry, not a theme" % kind, "wrong_kind", values=(kind, KIND))
    entry.pop("id", None)
    return theme_add(layers, entry)


def save(layers, user_folder):
    return replace(layers, user=cs.save(layers.user, cs.user_path(user_folder, KIND)))
