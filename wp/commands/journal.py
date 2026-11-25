"""Long journal (RULES/resources.md "Journal", package 14 H): every command that CHANGES the character is
logged by dispatch (commands/base.py). An entry stores ids and numbers only (no texts; the UI translates
by the kind / command ids through wp/i18n): order counter, kind, command id, short params, result,
combat round (0 = not in combat). No revert. rules_settings.log_limit: keep the last N (0 = unlimited).
"""
import contextlib
import contextvars
import dataclasses
from dataclasses import replace

from wp.model.character import LogEntry

KIND = {
    "item": ("equip_item", "unequip_item", "equip_hands", "unequip_hands", "remove_item", "activate_item",
             "deactivate_item", "use_consumable", "set_item_masterwork", "set_ignore_bag_weight", "set_condition_tag"),
    "item_damage": ("damage_item", "set_item_hp", "hit_item"),
    "spell": ("cast_spell", "resolve_spell_failure"),
    "damage": ("take_damage", "damage_to_balance", "pay_hp_cost", "spend_balance"),
    "heal": ("restore", "set_value", "set_temp_hp", "restore_mana"),
    "status": ("add_status", "activate_status", "remove_status", "delete_status", "set_status_duration",
               "set_status_hidden", "set_status_favorite"),
    "charges": ("spend_charge", "set_charges", "restore_charges", "spend_pool", "restore_pool", "add_pool",
                "edit_pool", "remove_pool", "spend_bp", "restore_all_balance", "spend_reaction", "restore_reactions"),
    "rest": ("short_rest", "long_rest", "long_rest_end_combat"),
    "injury": ("add_injury", "remove_injury"),
    "stance": ("set_active_stance",),
    "combat": ("start_combat", "end_combat", "tick", "use_attack", "set_iterative_count"),
    "purchase": ("buy_ability", "buy_skill_rank", "buy_hp", "buy_weapon_grade", "buy_base_slot", "buy_shield_grade",
                 "buy_armor_grade", "buy_language", "buy_combat_basics", "buy_maneuver", "buy_item_qualification",
                 "buy_attention_course", "buy_reaction", "buy_seed", "sprout_seed", "make_language_native",
                 "promote_skill", "buy_professionalism", "learn_spell", "buy_spell_upgrade", "add_feat",
                 "attention_to_training", "attention_to_base_points"),
    "progression": ("level_up", "exchange_comfort", "set_hp_roll"),
    "ot": ("remove_ot_comfort", "remove_ot_attention", "raise_heal_rating"),
    "edit": ("edit_sheet", "edit_ability", "edit_rules", "add_entry", "edit_entry", "remove_entry"),
    "notebook": ("add_note", "change_lens", "set_drive_level", "burn_quirk"),
    "template": ("add_template", "remove_template"),
    "settings": ("set_rule_setting", "reset_rule_setting", "set_char_setting", "reset_char_setting",
                 "reset_settings_group"),
}
_BY_COMMAND = {c: k for k, cmds in KIND.items() for c in cmds}
OTHER = "other"
_PRIMITIVE = (bool, int, float, str, type(None))
_ID_FIELDS = ("sid", "iid", "fid", "mid", "pid", "rid", "jid", "lid", "name")


def kind_of(command):
    return _BY_COMMAND.get(command, OTHER)


def short(v, depth=0):
    """Ids and numbers only: primitives as they are, records by their id, small dataclasses (reports) as a
    dict of their primitive fields; anything else by its type name."""
    if isinstance(v, _PRIMITIVE):
        return v
    if isinstance(v, (tuple, list)):
        return tuple(short(x, depth + 1) for x in v) if depth < 2 else len(v)
    if isinstance(v, dict):
        return {str(k): short(x, depth + 1) for k, x in v.items()} if depth < 2 else len(v)
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        for f in _ID_FIELDS:
            if hasattr(v, f) and isinstance(getattr(v, f), str) and getattr(v, f):
                return getattr(v, f)
        if depth < 1:
            return {f.name: short(getattr(v, f.name), depth + 1) for f in dataclasses.fields(v)
                    if isinstance(getattr(v, f.name), _PRIMITIVE + (tuple,))}
    return type(v).__name__


_AT = contextvars.ContextVar("journal_at", default="")


@contextlib.contextmanager
def stamped(at):
    """Journal lines written inside get the time stamp `at` (the Session clock; package 27 E)."""
    token = _AT.set(at)
    try:
        yield
    finally:
        _AT.reset(token)


def record(before, result, command, params):
    """The result with a journal entry appended to its state (called by dispatch for changed states)."""
    ch = result.state
    entry = LogEntry(seq=before.log_seq + 1, command=command, kind=kind_of(command),
                     params={k: short(v) for k, v in params.items()}, result=short(dict(result.info)),
                     round=ch.combat_round if ch.in_combat else 0, at=_AT.get())
    log = ch.log + (entry,)
    limit = ch.rules_settings.log_limit
    if limit > 0:
        log = log[-limit:]
    return replace(result, state=replace(ch, log=log, log_seq=entry.seq), entry=entry)
