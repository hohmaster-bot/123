"""Package 27 C (review 5 F9, F6): the loaders check value types and unique ids; every rule constant has limits.
Run: python Wp_claude/tests/storage/test_pkg27_load.py"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import files  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.model.character import Character, Item  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402
from wp.settings import store as st  # noqa: E402
from wp.settings.settings_cmds import settings_dispatch  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg27_load")
TMP = tempfile.mkdtemp(prefix="wp_p27c_")
BASE = json.loads(cio.dumps(Character(level=3, hp_rolls=(8,), hp_current=8, items=(Item("sw", "Sword"),))))


def edited(mut=None, raw=None):
    d = json.loads(json.dumps(BASE))
    if mut:
        mut(d["character"])
    text = json.dumps(d, allow_nan=True)
    return raw(text) if raw else text


def verdict(text):
    try:
        cio.loads(text)
    except cio.StorageError:
        return "corrupt"
    return "loaded"


def _item0(c, k, v):
    c["items"][0][k] = v


CASES = (
    ("hp_current null", lambda c: c.update(hp_current=None)),
    ("hp_current NaN", lambda c: c.update(hp_current=float("nan"))),
    ("level text", lambda c: c.update(level="5")),
    ("level 2.5", lambda c: c.update(level=2.5)),
    ("level true", lambda c: c.update(level=True)),
    ("items a text", lambda c: c.update(items="x")),
    ("abilities 3", lambda c: c.update(abilities=3)),
    ("item hp ten", lambda c: _item0(c, "hp", "ten")),
    ("two items sw", lambda c: c.update(items=c["items"] + c["items"])),
)
S.case("f9-types", "F9: null / NaN / text / 2.5 / true in a number, a text for a list, 3 for a table, a text item HP, "
       "two items with one id -> the file is damaged", ("corrupt",) * len(CASES))(
    lambda: tuple(verdict(edited(m)) for _, m in CASES))
S.case("f9-deep", "F9: 5000 nested brackets -> damaged (not RecursionError)", "corrupt")(
    lambda: verdict(edited(raw=lambda t: t.replace('"level": 3', '"level": ' + "[" * 5000 + "]" * 5000))))
S.case("f9-valid", "F9: the untouched file and an unknown field still load (unknown fields are dropped, D1)",
       ("loaded", "loaded"))(lambda: (verdict(edited()), verdict(edited(lambda c: c.update(zzz=1)))))


def _backup_offer():
    d = tempfile.mkdtemp(dir=TMP)
    files.create(d, "hero", Character(level=3))
    files.save(d, "hero", Character(level=4), "backups", 5, 10.0)
    with open(files.path_of(d, "hero"), "w", encoding="utf-8") as f:
        f.write(edited(lambda c: c.update(hp_current=None)))
    try:
        files.load(d, "hero", "backups")
    except CommandError as e:
        return e.reason, cio.load(e.params["backup"]).level
    return "loaded", None


S.case("f9-backup", "F9: a file with hp_current null -> file_corrupt and the backup (level 3) is offered",
       ("file_corrupt", 3))(_backup_offer)
S.case("f9-settings-deep", "F9: settings_import and profile_import of 5000 nested brackets are refused",
       ("bad_settings_file", "bad_profile"))(
    lambda: tuple(_reason(lambda c=cmd, k=kw: settings_dispatch(st.AppSettings(), c, **k)) for cmd, kw in (
        ("settings_import", {"text": "[" * 5000 + "]" * 5000}),
        ("profile_import", {"mode": "classic", "text": "[" * 5000 + "]" * 5000}))))


def _reason(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


# ---------------------------------------------------------------- F6 constants
DIVISORS = ("ability.mod_divisor", "bp.cap_divisor", "morale.divisor", "training.tenths_per_point",
            "ac.odd_level_step", "training.attention_comfort_divisor")


def setr(key, value):
    return _reason(lambda: dispatch(Character(), "set_rule_setting", key=key, value=value))


S.case("f6-divisors", "F6: every divider set to 0 / -1 / 10**30 -> out_of_range, NaN -> invalid_value, 2 accepted",
       tuple(("out_of_range", "out_of_range", "out_of_range", "invalid_value", "allowed") for _ in DIVISORS))(
    lambda: tuple(tuple(setr(k, v) for v in (0, -1, 10 ** 30, float("nan"), 2.0 if "comfort" in k else 2))
                  for k in DIVISORS))


def _maps():
    out = []
    for c in rd.TABLE.values():
        if c["type"] != "map":
            continue
        good = c["value"]
        k0 = sorted(good)[0]
        wrong_keys = dict((k, v) for k, v in good.items() if k != k0)
        nan = dict(good, **{k0: float("nan")})
        huge = dict(good, **{k0: 10 ** 30 if not isinstance(good[k0], list) else [10 ** 30] * len(good[k0])})
        row = (setr(c["id"], wrong_keys), setr(c["id"], nan), setr(c["id"], good))
        if c.get("value_type") in ("int", "float", "intlist"):
            row += (setr(c["id"], huge),)
        out.append((c["id"],) + row)
    return out


def _maps_expected():
    out = []
    for c in rd.TABLE.values():
        if c["type"] == "map":
            row = (c["id"], "wrong_keys", "invalid_value", "allowed")
            out.append(row + (("out_of_range",) if c.get("value_type") in ("int", "float", "intlist") else ()))
    return out


S.case("f6-maps", "F6: every map constant: a missing key -> wrong_keys, a NaN -> invalid_value, a 10**30 number -> "
       "out_of_range, the shipped value accepted", _maps_expected())(_maps)
S.case("f6-map-types", "F6: class.bab_factor good 'x' -> wrong_type; size.attack_ac {'a': 1} -> wrong_keys; "
       "attack.grip_factor one [1, 0] (a divider 0) -> out_of_range", ("wrong_type", "wrong_keys", "out_of_range"))(
    lambda: (setr("class.bab_factor", {"good": "x", "medium": 0.75, "poor": 0.5}), setr("size.attack_ac", {"a": 1}),
             setr("attack.grip_factor", {"one": [1, 0], "off": [1, 2], "two": [3, 2]})))
S.case("f6-every-number-bounded", "F6: every constant holding numbers has min and max; dividers have min 1", (0, 0))(
    lambda: (len([c for c in rd.TABLE.values() if c["type"] in ("int", "float", "map", "list") and
                  c.get("value_type", c.get("item_type", "int")) in ("int", "float", "intlist") and
                  ("min" not in c or "max" not in c)]),
             len([k for k in DIVISORS + ("attack.grip_factor",) if rd.TABLE[k]["min"] < 1])))


def _file_constant():
    d = json.loads(cio.dumps(dispatch(Character(), "set_rule_setting", key="ability.mod_divisor", value=2).state))
    text = json.dumps(d).replace('"ability.mod_divisor", 2', '"ability.mod_divisor", 0')
    return verdict(json.dumps(d)), verdict(text)


S.case("f6-file", "F6: a character file with the divider ability.mod_divisor 0 is damaged; 2 loads",
       ("loaded", "corrupt"))(_file_constant)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
