"""Settings view for the UI (package 19): list(group) and get(key) over the three domains, with the default and a
"changed" flag. Read only."""
from dataclasses import dataclass, fields
from typing import Any

from wp.model.character import RulesSettings
from wp.settings import schema as sch
from wp.settings import store as st

_RULE_DEFAULTS = {f.name: f.default for f in fields(RulesSettings)}


@dataclass(frozen=True)
class SettingView:
    key: str
    domain: str
    group: str
    type: str
    value: Any
    default: Any
    changed: bool
    label: str                         # i18n key
    description: str                   # i18n key


def _value(app, ch, key):
    spec = sch.KEYS[key]
    if spec["domain"] == "app":
        return st.get(app, key)
    if ch is None:
        return spec["default"]
    if spec["domain"] == "rules" and spec.get("constant"):
        return ch.rules_settings.constants.get(key, spec["default"])
    if spec["domain"] == "rules":
        v = getattr(ch.rules_settings, key)
        return list(v) if isinstance(v, tuple) else v
    return ch.char_settings.get(key, spec["default"])


def get(app, ch, key):
    spec = sch.KEYS.get(key)
    if spec is None:
        raise KeyError("no setting %r" % (key,))
    v = _value(app, ch, key)
    default = spec["default"]
    return SettingView(key, spec["domain"], spec["group"], spec["type"], v, default, v != default, spec["label"],
                       spec["description"])


def list_settings(app, ch=None, group=None):
    return tuple(get(app, ch, k) for k, s in sch.KEYS.items() if group is None or s["group"] == group)


def groups():
    out = []
    for s in sch.KEYS.values():
        if s["group"] not in out:
            out.append(s["group"])
    return tuple(out)
