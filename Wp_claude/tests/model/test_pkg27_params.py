"""Package 27 B (review 5 F4 F5 F13 F14 F20 F21 F24, D29): declared parameter types, checked before a command runs.
Run: python Wp_claude/tests/model/test_pkg27_params.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import formula as fm  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.model.notebook import Drive  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg27_params")
NAN, INF = float("nan"), float("inf")


def ref(cmd, ch=None, **p):
    try:
        dispatch(ch or Character(hp_rolls=(10,), hp_current=10, balance_current=5, bp_current=6), cmd, **p)
    except CommandError as e:
        return e.reason
    return "allowed"


S.case("b-numbers", "F4 F21: spend_balance n=inf -> invalid_value (not finite); restore_mana 2.7 and "
       "remove_ot_comfort 2.5 refused (never truncated); n=True refused",
       ("invalid_value", "wrong_type", "wrong_type", "wrong_type"))(
    lambda: (ref("spend_balance", n=INF), ref("restore_mana", amount=2.7), ref("remove_ot_comfort", n=2.5),
             ref("spend_balance", n=True)))
S.case("b-nonneg", "F14: short_rest extra_bp -1 and other_heal -1 -> out_of_range; spend_actions n -1 -> out_of_range",
       ("out_of_range", "out_of_range", "out_of_range"))(
    lambda: (ref("short_rest", extra_bp=-1000000000), ref("short_rest", other_heal=-1), ref("spend_actions", n=-1)))
S.case("b-signed", "pkg 26 C stays: add_experience -50 is allowed (a penalty)", "allowed")(
    lambda: ref("add_experience", amount=-50))
S.case("b-texts", "F13: learn_spell name NaN, add_drive principle None, set_status_favorite value NaN -> refused",
       ("invalid_value", "wrong_type", "invalid_value"))(
    lambda: (ref("learn_spell", name=NAN), ref("add_drive", name="d", principle=None),
             ref("set_status_favorite", sid="x", value=NAN)))
S.case("b-flags", "F13: a flag takes only true / false: set_ignore_bag_weight value 1 refused", "wrong_type")(
    lambda: ref("set_ignore_bag_weight", value=1))
S.case("b-dtype", "F20: take_damage dtype 'nope' -> unknown_damage_type; skip as a text -> wrong_type; fire passes",
       ("unknown_damage_type", "wrong_type", "allowed"))(
    lambda: (ref("take_damage", amount=3, dtype="nope"), ref("take_damage", amount=3, skip="../../etc"),
             ref("take_damage", amount=3, dtype="fire")))


def _dtype_hp():
    c = dispatch(Character(hp_rolls=(10,), hp_current=10, balance_current=0), "take_damage", amount=3, dtype="fire").state
    return c.hp_current


S.case("b-dtype-hp", "F20: a known type still hits: 3 fire on HP 10, balance 0 -> HP 7", 7)(_dtype_hp)
S.case("b-ids", "F5: add_attack stat 'nope' -> not_allowed; buy_ability name 'luck' -> not_allowed; equip_to_slot "
       "slot 'tail' -> not_allowed", ("not_allowed", "not_allowed", "not_allowed"))(
    lambda: (ref("add_attack", group="unarmed", stat="nope"), ref("buy_ability", name="luck"),
             ref("equip_to_slot", iid="x", slot="tail")))
S.case("b-unknown-param", "pkg 27 B: an unknown parameter -> unknown_parameter", "unknown_parameter")(
    lambda: ref("spend_balance", count=1))
S.case("b-safety-net", "F4: add_feat catalog 'x' and take_damage reductions True -> invalid_value (no crash)",
       ("invalid_value", "invalid_value"))(
    lambda: (ref("add_feat", catalog="x", fid="f"), ref("take_damage", amount=1, reductions=True)))
S.case("b-edit-sheet", "F5: edit_sheet hp_current None, abilities 3, level 2.5 -> wrong_type; level 2 passes",
       ("wrong_type", "wrong_type", "wrong_type", "allowed"))(
    lambda: (ref("edit_sheet", hp_current=None), ref("edit_sheet", abilities=3), ref("edit_sheet", level=2.5),
             ref("edit_sheet", level=2)))
def _field_named():
    try:
        dispatch(Character(), "edit_sheet", hp_current=None)
    except CommandError as e:
        return e.reason, e.params.get("field")


S.case("b-edit-field", "F5: edit_sheet names the field that does not fit", ("wrong_type", "hp_current"))(_field_named)


def _result_check():
    from dataclasses import replace
    from wp.commands.base import command, commit

    @command
    def p27_test_breaks_state(ch):     # a command that writes a wrong type (test only)
        return commit(replace(ch, hp_current="ten"), "p27_test_breaks_state", "")
    return ref("p27_test_breaks_state")


S.case("b-result-check", "F5: a command whose result does not fit the stored types is refused (wrong_type)",
       "wrong_type")(_result_check)
S.case("b-record", "F5: add_entry of a drive whose principle is None -> wrong_type (the record is type checked)",
       "wrong_type")(lambda: ref("add_entry", collection="drives", record=Drive("d1", name="d", principle=None)))
S.case("b-nested", "pkg 27 B: a list parameter nested 60 deep (max_depth 50) -> invalid_value", "invalid_value")(
    lambda: ref("short_rest", spends=(lambda x: [x])(eval("[" * 60 + "]" * 60))))


def _nan_file():
    try:
        cio.dumps(Character(rules_settings=Character().rules_settings, char_settings={"x": NAN}))
    except cio.StorageError:
        return "refused"
    return "written"


S.case("b-no-nan-file", "F13: a NaN never reaches the file (allow_nan=False -> StorageError)", "refused")(_nan_file)


def _formula():
    out = []
    for t in ("\u0663", "\u0661\u0662", "12"):
        try:
            out.append(fm.evaluate(t, {}))
        except fm.FormulaError:
            out.append("refused")
    return tuple(out)


S.case("f24-digits", "F24: an Arabic 3 and an Arabic 12 are not numbers; ASCII 12 is 12", ("refused", "refused", 12))(
    _formula)
S.case("f19-set-value", "F19 (owner): set_value balance -1, mana -1, spirit -1 -> out_of_range; HP -3 allowed",
       ("out_of_range", "out_of_range", "out_of_range", "allowed"))(
    lambda: (ref("set_value", resource="balance", value=-1), ref("set_value", resource="mana", value=-1),
             ref("set_value", resource="spirit", value=-1), ref("set_value", resource="hp", value=-3)))
S.case("b-finite", "pkg 27 B: an inf inside a list parameter is refused (invalid_value)", "invalid_value")(
    lambda: ref("take_damage", parts=[(INF, "fire")]))

if __name__ == "__main__":
    sys.exit(S.run())
