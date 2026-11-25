"""Application settings commands (package 19, D22): the ONLY way to change the app settings file. Pure functions on
AppSettings returning a new one (save with store.save). Refusals: CommandError with a reason id + params.
Rule settings and character-bound settings are changed by CHARACTER commands (set_rule_setting, set_char_setting...,
wp/commands/settings_char_cmds.py) so they are journaled with the character.

- settings_set / settings_reset / settings_reset_group / settings_export / settings_import
- profile_create / profile_duplicate / profile_rename / profile_delete / profile_set_active / profile_set /
  profile_export / profile_import (per mode: classic / lite)
- layout_add / layout_edit / layout_remove: panels and cells (classic), elements (lite)
- quick_add / quick_edit / quick_remove: quick buttons (both modes); a macro is a plain list of existing commands
Hotkeys: two actions on the same key are REFUSED (reason hotkey_conflict; assumption Q139). Deleting the ACTIVE
profile (or the last one of a mode) is refused (reason profile_active / last_profile; assumption Q138).
"""
import json
from dataclasses import dataclass, field, replace
from typing import Any, Dict

from wp.commands.base import CommandError
from wp.core.frozen import FrozenDict
from wp.model import ids
from wp.panels import registry
from wp.settings import schema as sch
from wp.settings import store as st

REGISTRY = {}
COLLECTIONS = {"classic": ("panels", "cells"), "lite": ("elements",)}
ITEM_KIND = {"panels": "panel", "cells": "cell", "elements": "element"}


@dataclass(frozen=True)
class SettingsResult:
    state: Any
    info: Dict[str, Any] = field(default_factory=dict)


def settings_command(fn):
    REGISTRY[fn.__name__] = fn
    return fn


def settings_dispatch(app, name, /, **params):
    from wp.settings import images  # noqa: F401  (registers the image commands)
    if name not in REGISTRY:
        raise CommandError("unknown settings command: %r" % (name,), "unknown_command", command=name)
    try:
        return REGISTRY[name](app, **params)
    except CommandError:
        raise
    except st.SettingsError as e:
        raise CommandError(str(e), "settings_error")


def refuse(bad):
    reason, params = bad
    raise CommandError("%s: %s" % (reason, ", ".join(str(v) for v in params.get("values", ()))), reason, **params)


# ------------------------------------------------------------------ hotkeys

def hotkey_table(app):
    """[(key, action)] of every hotkey: app hotkeys, quick buttons, and each lite profile's own hotkeys."""
    out = [(k, "hotkey:" + a) for a, k in st.get(app, "hotkeys").items() if k]
    out += [(b["hotkey"], "quick:" + b["id"]) for b in app.quick_buttons if b.get("hotkey")]
    return out


def _conflict(pairs):
    seen = {}
    for key, action in pairs:
        norm = "+".join(sorted(key.split("+")[:-1]) + key.split("+")[-1:])
        if norm in seen and seen[norm] != action:
            return "hotkey_conflict", {"values": (key, seen[norm], action), "key": key, "actions": (seen[norm], action)}
        seen[norm] = action
    return None


def check_hotkeys(app):
    base = hotkey_table(app)
    bad = _conflict(base)
    if bad:
        return bad
    for p in app.profiles["lite"]:
        own = [(p.get(k, ""), "lite:%s:%s" % (p["id"], k)) for k in ("show_hotkey", "click_through_hotkey") if p.get(k)]
        bad = _conflict(base + own)
        if bad:
            return bad
    return None


def _checked(app):
    bad = check_hotkeys(app)
    if bad:
        refuse(bad)
    return app


# ------------------------------------------------------------------ values

@settings_command
def settings_set(app, key="", value=None):
    if key in sch.KEYS and sch.KEYS[key]["domain"] != "app":
        raise CommandError("%s is a %s setting: use the character command" % (key, sch.KEYS[key]["domain"]),
                           "not_app_setting", values=(key,), domain=sch.KEYS[key]["domain"])
    bad = sch.check_key(key, value)
    if bad:
        refuse(bad)
    new = replace(app, values=FrozenDict(dict(app.values, **{key: st.freeze(value)})))
    return SettingsResult(_checked(new), {"key": key})


@settings_command
def settings_reset(app, key=""):
    if key not in sch.KEYS:
        refuse(("unknown_setting", {"values": (key,)}))
    return SettingsResult(replace(app, values=FrozenDict({k: v for k, v in app.values.items() if k != key})), {"key": key})


@settings_command
def settings_reset_group(app, group=""):
    keys = {k for k, s in sch.KEYS.items() if s["group"] == group and s["domain"] == "app"}
    if not keys:
        refuse(("unknown_group", {"values": (group,)}))
    return SettingsResult(replace(app, values=FrozenDict({k: v for k, v in app.values.items() if k not in keys})),
                          {"reset": tuple(sorted(keys))})


@settings_command
def settings_export(app):
    return SettingsResult(app, {"text": st.dumps(app)})


@settings_command
def settings_import(app, text=""):
    """A whole settings file from text (another PC, a backup); every known value is checked."""
    try:
        data = json.loads(text)
    except (ValueError, RecursionError) as e:
        raise CommandError("not a settings file: %s" % (e,), "bad_settings_file")
    if isinstance(data, dict) and any(not st.image_record_ok(i) for i in data.get("images", []) or ()):
        raise CommandError("an image record points outside images/<id>.<ext>", "bad_image_record")
    try:
        new = st.from_data(data)
    except (st.SettingsError, TypeError, AttributeError, KeyError, ValueError) as e:
        raise CommandError("not a settings file: %s" % (e,), "bad_settings_file")
    for k, v in new.values.items():
        if k in sch.KEYS:
            bad = sch.check_key(k, v)
            if bad:
                refuse(bad)
    return SettingsResult(_checked(replace(new, path=app.path)), {"imported": True})


# ------------------------------------------------------------------ ids

def _new_id(app, name, taken):
    base = ids.slug(name)
    taken = set(taken) | set(app.retired)
    if base not in taken:
        return base, app.counter
    n = app.counter
    while True:
        n += 1
        if "%s_%d" % (base, n) not in taken:
            return "%s_%d" % (base, n), n


def _mode(mode):
    if mode not in st.MODES:
        raise CommandError("mode must be classic or lite", "unknown_mode", values=(mode,))
    return mode


def _profile(app, mode, pid):
    p = st.profile(app, _mode(mode), pid)
    if p is None:
        raise CommandError("no %s profile %r" % (mode, pid), "not_found", values=(mode, pid))
    return p


def _put_profiles(app, mode, profiles, **extra):
    return replace(app, profiles=FrozenDict(dict(app.profiles, **{mode: tuple(profiles)})), **extra)


def _with_profile(app, mode, prof):
    return _put_profiles(app, mode, [prof if p["id"] == prof["id"] else p for p in app.profiles[mode]])


# ------------------------------------------------------------------ profiles

def _add_profile(app, mode, data, name):
    pid, counter = _new_id(app, name, (p["id"] for p in app.profiles[mode]))
    data = dict(data, id=pid, name=name)
    bad = sch.check_fields(mode, data)
    if bad:
        refuse(bad)
    new = _put_profiles(app, mode, list(app.profiles[mode]) + [st.freeze(data)], counter=counter)
    return SettingsResult(_checked(new), {"id": pid})


@settings_command
def profile_create(app, mode="", name=""):
    """A new profile with the shipped default content of its mode."""
    if not name:
        raise CommandError("a profile needs a name", "name_needed")
    base = st._shipped_profiles()[_mode(mode)][0]
    return _add_profile(app, mode, {k: v for k, v in base.items() if k != "id"}, name)


@settings_command
def profile_duplicate(app, mode="", pid="", name=""):
    src = _profile(app, mode, pid)
    return _add_profile(app, mode, {k: v for k, v in src.items() if k != "id"}, name or src["name"])


@settings_command
def profile_rename(app, mode="", pid="", name=""):
    if not name:
        raise CommandError("a profile needs a name", "name_needed")
    p = _profile(app, mode, pid)
    return SettingsResult(_with_profile(app, mode, st.freeze(dict(p, name=name))), {"id": pid})


@settings_command
def profile_delete(app, mode="", pid=""):
    _profile(app, mode, pid)
    if app.active[mode] == pid:
        raise CommandError("the active %s profile cannot be deleted: switch first" % mode, "profile_active",
                           values=(mode, pid))
    if len(app.profiles[mode]) <= 1:
        raise CommandError("the last %s profile cannot be deleted" % mode, "last_profile", values=(mode,))
    left = [p for p in app.profiles[mode] if p["id"] != pid]
    return SettingsResult(_put_profiles(app, mode, left, retired=app.retired + (pid,)), {"id": pid})


@settings_command
def profile_set_active(app, mode="", pid=""):
    _profile(app, mode, pid)
    return SettingsResult(replace(app, active=FrozenDict(dict(app.active, **{mode: pid}))), {"id": pid})


@settings_command
def profile_set(app, mode="", pid="", **fields):
    """Profile-wide fields (lite: opacity, click_through and its hotkey, always_on_top, show_hotkey, lock_layout...)."""
    if "id" in fields:
        raise CommandError("an id cannot be changed", "id_not_editable", values=("id",))
    p = dict(_profile(app, mode, pid))
    unknown = sorted(set(fields) - set(sch.FIELDS[_mode(mode)]))
    if unknown:                        # review 5 F25: profile_set(dock=...) is not a profile field (a panel one)
        raise CommandError("not a %s profile field: %s" % (mode, ", ".join(unknown)), "unknown_fields",
                           values=(", ".join(unknown),), allowed=tuple(sch.FIELDS[mode]))
    p.update(fields)
    bad = sch.check_fields(mode, fields)
    if bad:
        refuse(bad)
    return SettingsResult(_checked(_with_profile(app, mode, st.freeze(p))), {"id": pid})


@settings_command
def profile_export(app, mode="", pid=""):
    p = _profile(app, mode, pid)
    return SettingsResult(app, {"text": json.dumps({"kind": "layout_profile", "mode": mode, "profile": st._plain(p)},
                                                   ensure_ascii=False)})


@settings_command
def profile_import(app, mode="", text=""):
    try:
        data = json.loads(text)
    except (ValueError, RecursionError) as e:
        raise CommandError("not a profile: %s" % e, "bad_profile")
    if not isinstance(data, dict) or data.get("kind") != "layout_profile":
        raise CommandError("not a layout profile", "bad_profile")
    if data.get("mode") != _mode(mode):
        raise CommandError("a %s profile cannot go into %s" % (data.get("mode"), mode), "wrong_mode",
                           values=(data.get("mode"), mode))
    if not isinstance(data.get("profile"), dict):
        raise CommandError("not a layout profile", "bad_profile")
    prof = dict(data["profile"])
    return _add_profile(app, mode, {k: v for k, v in prof.items() if k != "id"}, prof.get("name") or "imported")


# ------------------------------------------------------------------ panels, cells, elements

def _coll(mode, collection):
    if collection not in COLLECTIONS[_mode(mode)]:
        raise CommandError("%s profiles have no %s" % (mode, collection), "unknown_collection", values=(mode, collection))
    return collection


@settings_command
def layout_add(app, mode="", pid="", collection="", item=None):
    _coll(mode, collection)
    p = dict(_profile(app, mode, pid))
    item = dict(item or {})
    bad = sch.check_fields(ITEM_KIND[collection], item) or registry.check_item(collection, item, mode)
    if bad:
        refuse(bad)
    rows = list(p.get(collection, ()))
    iid, counter = _new_id(app, item.get("label") or item.get("kind") or collection, (r["id"] for r in rows))
    item["id"] = iid
    p[collection] = tuple(rows) + (st.freeze(item),)
    return SettingsResult(replace(_with_profile(app, mode, st.freeze(p)), counter=counter), {"id": iid})


def _item(p, collection, item_id):
    for r in p.get(collection, ()):
        if r["id"] == item_id:
            return r
    raise CommandError("no %s %r" % (collection, item_id), "not_found", values=(collection, item_id))


@settings_command
def layout_edit(app, mode="", pid="", collection="", item_id="", **fields):
    _coll(mode, collection)
    if "id" in fields:
        raise CommandError("an id cannot be changed", "id_not_editable", values=("id",))
    p = dict(_profile(app, mode, pid))
    new_item = dict(_item(p, collection, item_id), **fields)
    bad = sch.check_fields(ITEM_KIND[collection], fields) or registry.check_item(collection, new_item, mode)
    if bad:
        refuse(bad)
    p[collection] = tuple(st.freeze(dict(r, **fields)) if r["id"] == item_id else r for r in p[collection])
    return SettingsResult(_with_profile(app, mode, st.freeze(p)), {"id": item_id})


@settings_command
def layout_remove(app, mode="", pid="", collection="", item_id=""):
    _coll(mode, collection)
    p = dict(_profile(app, mode, pid))
    _item(p, collection, item_id)
    p[collection] = tuple(r for r in p[collection] if r["id"] != item_id)
    return SettingsResult(_with_profile(app, mode, st.freeze(p)), {"id": item_id})


# ------------------------------------------------------------------ quick buttons

def _quick_check(button):
    bad = sch.check_fields("quick_button", button)
    if bad:
        refuse(bad)
    if not button.get("action") and not button.get("macro"):
        raise CommandError("a quick button needs an action or a macro", "action_needed")


@settings_command
def quick_add(app, button=None):
    b = dict(button or {})
    _quick_check(b)
    bid, counter = _new_id(app, b.get("label") or "button", (x["id"] for x in app.quick_buttons))
    b["id"] = bid
    new = replace(app, quick_buttons=app.quick_buttons + (st.freeze(b),), counter=counter)
    return SettingsResult(_checked(new), {"id": bid})


@settings_command
def quick_edit(app, bid="", **fields):
    if "id" in fields:
        raise CommandError("an id cannot be changed", "id_not_editable", values=("id",))
    old = next((b for b in app.quick_buttons if b["id"] == bid), None)
    if old is None:
        raise CommandError("no quick button %r" % (bid,), "not_found", values=("quick_buttons", bid))
    b = dict(old, **fields)
    _quick_check(b)
    new = replace(app, quick_buttons=tuple(st.freeze(b) if x["id"] == bid else x for x in app.quick_buttons))
    return SettingsResult(_checked(new), {"id": bid})


@settings_command
def quick_remove(app, bid=""):
    if not any(b["id"] == bid for b in app.quick_buttons):
        raise CommandError("no quick button %r" % (bid,), "not_found", values=("quick_buttons", bid))
    return SettingsResult(replace(app, quick_buttons=tuple(b for b in app.quick_buttons if b["id"] != bid),
                                  retired=app.retired + (bid,)), {"id": bid})
