"""Field table per catalog kind (data: wp/catalog/data/catalog_schemas.json, package 18).

check(kind, entry) -> None, or (reason id, params) for the first problem: unknown_kind, field_required, field_type,
field_not_allowed. Fields that are not in the table are not checked (they are kept as they are).
"""
import io
import json
import os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "catalog_schemas.json")


def _load(path=PATH):
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    common = tuple(d["common"])
    return {k: common + tuple(v) for k, v in d["kinds"].items()}


SCHEMAS = _load()
KINDS = tuple(SCHEMAS)


def _is(value, t):
    if t == "any":
        return True
    if value is None:
        return t.endswith("_or_null")
    t = t.replace("_or_null", "")
    if t == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == "str":
        return isinstance(value, str)
    if t == "bool":
        return isinstance(value, bool)
    if t == "list":
        return isinstance(value, (list, tuple))
    if t == "dict":
        return isinstance(value, dict)
    return False


def check(kind, entry):
    if kind not in SCHEMAS:
        return "unknown_kind", {"values": (kind,)}
    for f in SCHEMAS[kind]:
        name = f["name"]
        if name not in entry:
            if f.get("required"):
                return "field_required", {"values": (name,), "field": name}
            continue
        v = entry[name]
        if not _is(v, f["type"]):
            return "field_type", {"values": (name, f["type"]), "field": name, "expected": f["type"]}
        if "allowed" in f and v is not None and v not in f["allowed"]:
            return "field_not_allowed", {"values": (name, v), "field": name, "allowed": tuple(f["allowed"])}
    return None
