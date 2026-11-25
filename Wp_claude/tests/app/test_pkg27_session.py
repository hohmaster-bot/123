"""Package 27 D and E (review 5 F3 F16 F17 F18 F23 F28 F29): undo keeps the current non-undoable data and journal,
no-op commands, the missing view fields, the journal modes and the history archive.
Run: python Wp_claude/tests/app/test_pkg27_session.py"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import history  # noqa: E402
from wp.app import session as sm  # noqa: E402
from wp.model import blocks  # noqa: E402
from wp.core.weapons import Weapon  # noqa: E402
from wp.model.character import AttackRecord, Character, ResourcePool, WeaponEntry  # noqa: E402
from wp.settings.settings_cmds import settings_dispatch  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg27_session")
TMP = tempfile.mkdtemp(prefix="wp_p27d_")
DAY = 86400


class Clock(object):
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def session(ch=None, **app):
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "user"), Clock())
    for k, v in app.items():
        s.app = settings_dispatch(s.app, "settings_set", key=k, value=v).state
    s.new("hero", ch or Character(hp_rolls=(10,), hp_current=10, balance_current=6, bp_current=6))
    return s


# ---------------------------------------------------------------- D
def _keep_setting():
    s = session()
    s.dispatch("take_damage", amount=3)
    s.dispatch("set_char_setting", key="char_portrait", value="img1")
    s.undo()
    return s.character.hp_current, s.character.char_settings.get("char_portrait")


S.case("f3-keep", "F3: take_damage 3 (balance 6 -> 3), set the portrait, undo -> balance back, the portrait kept",
       (10, "img1"))(_keep_setting)


def _undo_lines():
    s = session()
    for _ in range(3):
        s.dispatch("spend_bp", n=1)
    s.undo()
    s.undo()
    a = [e.command for e in s.character.log]
    s.redo()
    return a, [e.command for e in s.character.log][-1], s.character.bp_current, [e.seq for e in s.character.log]


S.case("f17-lines", "F17: 3 commands + 2 undo -> 5 lines (both undo kept), redo adds a 6th; BP 6 -1 -1 -1 +1 +1 -1 = 4",
       (["spend_bp", "spend_bp", "spend_bp", "undo", "undo"], "redo", 4, [1, 2, 3, 4, 5, 6]))(_undo_lines)


def _noop():
    s = session()
    calls = []
    s.subscribe(calls.append)
    r = s.dispatch("spend_balance", n=0)
    return r.ok, r.topics, s.can_undo(), s.dirty_since, calls, len(s.character.log)


S.case("f18-noop", "F18: spend_balance 0 -> ok, no topics, no undo step, not dirty, no subscriber call, no line",
       (True, (), False, None, [], 0))(_noop)


def _fields():
    s = session(Character(attacks=(AttackRecord("u", "unarmed", "unarmed_combat"),), class_id="",
                          pools=(ResourcePool("fp", "fp", max="con_mod + level", current=6),)))
    s.dispatch("set_bab_override", value=7)
    s.dispatch("set_save_override", save="will", value=3)
    s.dispatch("set_primary_attack", rid="u", on=True)
    sheet, att, pool = s.view("sheet"), s.view("attacks")[0], s.view("resources")["pools"][0][2]
    return sheet["bab_override"], sheet["save_override"], att.primary, pool


S.case("f16-f28-fields", "F16: sheet shows bab_override 7 and save_override will 3; the attack view shows primary; F28: "
       "pool fp max con_mod + level = 0 + 1 = 1, current 6 kept and flagged over_max",
       (7, {"will": 3}, True, {"current": 6, "max": 1, "over_max": True}))(_fields)
S.case("f23-tuple", "F23: active_effects is a tuple (a cached list could be changed by a caller)", True)(
    lambda: isinstance(blocks.active_effects(Character()), tuple))


def _training_rows():
    s = session(Character(training=1000, weapons=(WeaponEntry(Weapon("blades", scale=3), "Blades"),)))
    wid = "blades"
    before = [r for r in s.view("training")["weapons"] if r[0] == wid][0]
    s.dispatch("buy_weapon_grade", wid=wid)
    after = [r for r in s.view("training")["weapons"] if r[0] == wid][0]
    return before[3], after[3]


S.case("f16-grades", "F16: the training view lists weapon grades: one bought -> 0 to 1", (0, 1))(_training_rows)


# ---------------------------------------------------------------- E
def _short():
    s = session(journal_mode="short", journal_short_max=5)
    for _ in range(8):
        s.dispatch("add_experience", amount=1)
    return [e.seq for e in s.character.log], os.path.exists(history.path_of(s.characters_dir, "hero"))


S.case("e-short", "F29 short: limit 5 from the settings, 8 lines -> the newest 5 (seq 4..8) kept, no archive",
       ([4, 5, 6, 7, 8], False))(_short)


def full(n=12, **extra):
    s = session(journal_archive_at=10, journal_archive_keep=3, **extra)
    for i in range(n):
        if i == 6:
            s.clock.t += DAY           # lines 7.. are on the next day
        s.dispatch("add_experience", amount=1)
    return s


def _full():
    s = full()
    arch = history.read(s.characters_dir, "hero")
    return ([e.seq for e in arch], [e.seq for e in s.character.log], [e.seq for e in s.full_log()])


S.case("e-full", "F29 full: archive at 10 keep 3: the 10th line moves seq 1..7 to the archive, 8..12 stay; the full log "
       "is 1..12", (list(range(1, 8)), [8, 9, 10, 11, 12], list(range(1, 13))))(_full)


def _dates():
    s = full()
    day2 = history.read(s.characters_dir, "hero", from_date="19700102")
    view = s.history_view(from_date="19700101", to_date="19700101")
    page = s.history_view(page=1, size=5)
    return [e.seq for e in day2], [e.seq for e in view["lines"]], view["total"], [e.seq for e in page["lines"]]


S.case("e-dates", "F29: lines 1..6 on 1970-01-01, 7..12 on 01-02: the archive from 01-02 = 7; the history view of "
       "01-01 = 1..6 (6 lines); page 1 of 5 = 6..10", ([7], [1, 2, 3, 4, 5, 6], 6, [6, 7, 8, 9, 10]))(_dates)


def _roundtrip():
    s = full()
    whole = s.full_log()
    return all(e.at for e in whole), whole[0].command, whole[0].params, whole[0].at


S.case("e-roundtrip", "F29: archived lines keep their command, params and time stamp (clock 1000 s)",
       (True, "add_experience", {"amount": 1, "at": "19700101-001640-000"}, "19700101-001640-000"))(_roundtrip)


def _travel():
    s = full()
    s.save()
    s.close()
    s.rename("hero", "sir")
    renamed = len(history.full_log(s.characters_dir, "sir", s.open("sir").log))
    s.close()
    s.duplicate("sir", "twin")
    twin = len(history.read(s.characters_dir, "twin"))
    dest = os.path.join(TMP, "export_%d.json" % id(s))
    s.export("sir", dest)
    exported = len(cio.load(dest).log)
    s.import_file(dest, "back")
    s.open("back")
    back = (len(history.read(s.characters_dir, "back")), len(s.character.log))
    s.close()
    trashed = s.delete("twin")
    in_trash = os.path.exists(trashed[:-len(".json")] + history.SUFFIX)
    return renamed, twin, exported, back, in_trash, os.path.exists(history.path_of(s.characters_dir, "hero"))


S.case("e-travel", "F29: rename keeps all 12 lines; duplicate copies the 7 archived; export holds 12; import + open "
       "archives 9 and keeps 3; delete moves the archive to the trash; nothing left under the old name",
       (12, 7, 12, (9, 3), True, False))(_travel)


def _failed_append():
    s = full(n=9)
    real = history._write_bytes

    def broken(f, data):
        raise OSError("disk full")
    history._write_bytes = broken
    try:
        s.dispatch("add_experience", amount=1)
        s.dispatch("add_experience", amount=1)
    finally:
        history._write_bytes = real
    size = os.path.getsize(history.path_of(s.characters_dir, "hero")) if os.path.exists(
        history.path_of(s.characters_dir, "hero")) else 0
    s.dispatch("add_experience", amount=1)
    return size, [e.seq for e in s.character.log][-3:], len(history.read(s.characters_dir, "hero"))


S.case("e-failed-append", "F29: a failing append keeps every line in memory and leaves no partial archive; the next "
       "command archives 1..9 (12 lines, keep 3)", (0, [10, 11, 12], 9))(_failed_append)


def _dedupe():
    s = full()
    arch = history.read(s.characters_dir, "hero")
    again = history.append(s.characters_dir, "hero", arch + s.character.log[:2])
    return again, [e.seq for e in history.read(s.characters_dir, "hero")]


S.case("e-dedupe", "F29: appending lines 1..9 when 1..7 are archived writes only 8 and 9 (never twice)",
       (2, list(range(1, 10))))(_dedupe)


def _undo_independent():
    s = full()
    s.undo()
    return s.character.log[-1].command, sum(e.amount for e in s.character.xp_log)


S.case("e-undo", "F29: undo works after archiving (xp 12 -> 11) and its line goes to the current journal",
       ("undo", 11))(_undo_independent)


def _settings_limits():
    from wp.settings import store as st
    a = st.AppSettings()
    return st.get(a, "journal_mode"), st.get(a, "journal_short_max"), st.get(a, "journal_archive_at")


S.case("e-defaults", "F29 (owner): default mode full, short max 100, archive at 1000", ("full", 100, 1000))(
    _settings_limits)


if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
