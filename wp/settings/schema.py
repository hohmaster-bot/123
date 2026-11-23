"""Settings schema (data: wp/settings/data/settings_schema.json, package 19, D22).

check_value(spec, value) -> None or (reason id, params): wrong_type, out_of_range, not_allowed, bad_color, bad_hotkey.
check_key(key, value) -> the same for a known key; unknown_setting for a key not in the schema.
check_fields(kind, fields) checks the fields of a profile / panel / cell / element / quick button / image record
(fields that are not in the table are kept, not checked).
"""
import io
import json
import os
import re

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "settings_schema.json")
DOMAINS = ("rules", "character", "app")
COLOR = re.compile(r"^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$")
MODIFIERS = ("Ctrl", "Shift", "Alt", "Win")
NAMED_KEYS = ("Space", "Tab", "Esc", "Enter", "Home", "End", "PageUp", "PageDown", "Insert", "Delete", "Up", "Down",
              "Left", "Right", "Backspace")


def _load(path=PATH):
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    keys = {}
    for k in d["keys"]:
        k = dict(k)
        k.setdefault("label", "settings.%s" % k["id"])
        k.setdefault("description", "settings.%s.desc" % k["id"])
        keys[k["id"]] = k
    from wp.rules_data import rules as rd
    for cid, c in rd.TABLE.items():    # every rule constant is a rules-domain key (package 20, D23)
        keys[cid] = {"id": cid, "domain": "rules", "type": c["type"], "default": c["value"], "group": "rules." + c["group"],
                     "label": c.get("label", "rules." + cid), "description": "rules.%s.desc" % cid, "constant": True}
    return keys, {name: {f["id"]: f for f in fs} for name, fs in d["profile_fields"].items()}, tuple(d["image_targets"])


KEYS, FIELDS, IMAGE_TARGETS = _load()


def keys_of(domain):
    return tuple(k for k, s in KEYS.items() if s["domain"] == domain)


def valid_hotkey(text):
    """"" (no hotkey) or Modifier+...+Key: modifiers Ctrl / Shift / Alt / Win (each once), one key: A-Z, 0-9, F1-F24
    or a named key."""
    if text == "":
        return True
    parts = text.split("+")
    mods, key = parts[:-1], parts[-1]
    if len(set(mods)) != len(mods) or any(m not in MODIFIERS for m in mods):
        return False
    return (len(key) == 1 and key.isascii() and key.isalnum() and (key.isdigit() or key.isupper())) or \
        key in NAMED_KEYS or (key[:1] == "F" and key[1:].isdigit() and 1 <= int(key[1:]) <= 24)


def _num(v, ints):
    if isinstance(v, bool):
        return False
    return isinstance(v, int) if ints else isinstance(v, (int, float))


def check_value(spec, value, t=None):
    t = t or spec.get("type", "any")
    if t == "any":
        return None
    if t == "bool" and not isinstance(value, bool):
        return "wrong_type", {"values": (t,), "expected": t}
    if t in ("int", "float"):
        if not _num(value, t == "int"):
            return "wrong_type", {"values": (t,), "expected": t}
        if ("min" in spec and value < spec["min"]) or ("max" in spec and value > spec["max"]):
            return "out_of_range", {"values": (value, spec.get("min"), spec.get("max")), "min": spec.get("min"),
                                    "max": spec.get("max")}
    if t in ("string", "enum", "color", "hotkey") and not isinstance(value, str):
        return "wrong_type", {"values": (t,), "expected": t}
    if t == "enum" and value not in spec.get("allowed", ()):
        return "not_allowed", {"values": (value,), "allowed": tuple(spec.get("allowed", ()))}
    if t == "color" and not COLOR.match(value):
        return "bad_color", {"values": (value,)}
    if t == "hotkey" and not valid_hotkey(value):
        return "bad_hotkey", {"values": (value,)}
    if t in ("point", "rect"):
        n = 2 if t == "point" else 4
        if not isinstance(value, (list, tuple)) or len(value) != n or not all(_num(x, True) for x in value):
            return "wrong_type", {"values": (t,), "expected": t}
        if t == "rect" and (value[2] < 0 or value[3] < 0):
            return "out_of_range", {"values": (tuple(value),), "min": 0, "max": None}
    if t == "list":
        if not isinstance(value, (list, tuple)):
            return "wrong_type", {"values": (t,), "expected": t}
        if "item" in spec:
            for x in value:
                bad = check_value(spec, x, spec["item"])
                if bad:
                    return bad
    if t == "map":
        if not isinstance(value, dict) or not all(isinstance(k, str) for k in value):
            return "wrong_type", {"values": (t,), "expected": t}
        if "value" in spec:
            for x in value.values():
                bad = check_value(spec, x, spec["value"])
                if bad:
                    return bad
    return None


def check_key(key, value):
    if key not in KEYS:
        return "unknown_setting", {"values": (key,)}
    return check_value(KEYS[key], value)


def check_fields(kind, fields):
    table = FIELDS[kind]
    for name, value in fields.items():
        if name in table:
            bad = check_value(table[name], value)
            if bad:
                reason, params = bad
                return reason, dict(params, field=name, values=(name,) + tuple(params.get("values", ())))
    return None
