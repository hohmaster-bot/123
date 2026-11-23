"""Character-side settings commands (package 19, D13, D22): game rule settings (Character.rules_settings) and
character-bound settings (Character.char_settings), checked by the settings schema, journaled like every command.
set_rule_setting / reset_rule_setting / set_char_setting / reset_char_setting / reset_settings_group.
(edit_rules stays the edit-mode command without limits.)"""
from dataclasses import fields, replace

from wp.commands.base import CommandError, command, commit
from wp.core.frozen import FrozenDict
from wp.model.character import RulesSettings
from wp.settings import schema as sch


def _check(key, value, domain):
    spec = sch.KEYS.get(key)
    if spec is None or spec["domain"] != domain:
        raise CommandError("%s is not a %s setting" % (key, domain), "unknown_setting", values=(key,), domain=domain)
    bad = sch.check_value(spec, value)
    if bad:
        reason, params = bad
        raise CommandError("%s: %s" % (reason, key), reason, **dict(params, key=key))


def _rule_value(key, value):
    return tuple(value) if isinstance(value, list) else value


@command
def set_rule_setting(ch, key="", value=None):
    _check(key, value, "rules")
    return commit(replace(ch, rules_settings=replace(ch.rules_settings, **{key: _rule_value(key, value)})),
                  "set_rule_setting", "rule %s" % key, {"key": key})


@command
def reset_rule_setting(ch, key=""):
    _check(key, sch.KEYS.get(key, {}).get("default"), "rules")
    default = {f.name: f.default for f in fields(RulesSettings)}[key]
    return commit(replace(ch, rules_settings=replace(ch.rules_settings, **{key: default})), "reset_rule_setting",
                  "rule %s reset" % key, {"key": key})


@command
def set_char_setting(ch, key="", value=None):
    _check(key, value, "character")
    return commit(replace(ch, char_settings=FrozenDict(dict(ch.char_settings, **{key: value}))), "set_char_setting",
                  "setting %s" % key, {"key": key})


@command
def reset_char_setting(ch, key=""):
    _check(key, sch.KEYS.get(key, {}).get("default"), "character")
    return commit(replace(ch, char_settings=FrozenDict({k: v for k, v in ch.char_settings.items() if k != key})),
                  "reset_char_setting", "setting %s reset" % key, {"key": key})


@command
def reset_settings_group(ch, group=""):
    """Every rule / character setting of a group back to its default."""
    keys = [k for k, s in sch.KEYS.items() if s["group"] == group and s["domain"] in ("rules", "character")]
    if not keys:
        raise CommandError("no character settings in group %r" % (group,), "unknown_group", values=(group,))
    defaults = {f.name: f.default for f in fields(RulesSettings)}
    rules = replace(ch.rules_settings, **{k: defaults[k] for k in keys if sch.KEYS[k]["domain"] == "rules"})
    own = FrozenDict({k: v for k, v in ch.char_settings.items() if k not in keys})
    return commit(replace(ch, rules_settings=rules, char_settings=own), "reset_settings_group", "group %s reset" % group,
                  {"reset": tuple(sorted(keys))})
