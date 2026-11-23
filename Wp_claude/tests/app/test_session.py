"""Package 23 A: the Session (the single entry point of the future UI), topics, views, autosave with a fake clock,
backups, corrupt file recovery, character files. Run: python Wp_claude/tests/app/test_session.py"""
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import files, session as sm  # noqa: E402
from wp.commands import REGISTRY, CommandError  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.settings.settings_cmds import settings_dispatch  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_session")
TMP = tempfile.mkdtemp(prefix="wp_ses_")


class Clock(object):
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


def new_session(clock=None, **settings):
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "characters"), os.path.join(d, "user"), clock or Clock())
    for k, v in settings.items():
        s.app = settings_dispatch(s.app, "settings_set", key=k, value=v).state
    s.new("Hero", Character(hp_rolls=(8,), hp_current=8, bp_current=2))
    return s


def refusal(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


def text(s, name="Hero"):
    return io.open(files.path_of(s.characters_dir, name), encoding="utf-8").read()


# ---------------------------------------------------------------- dispatch, topics, subscribers
def _dispatch():
    s = new_session()
    calls = []
    s.subscribe(calls.append)
    ok = s.dispatch("take_damage", amount=3)
    bad = s.dispatch("spend_bp", n=9)
    return ok.ok, ok.topics, s.character.hp_current, bad.ok, bad.reason, calls


S.case("d-dispatch", "pkg 23: success (topics from the table, HP 8 -> 5); refusal (reason id, nothing changed, no call); "
       "the subscriber is called once", (True, ("combat", "resources", "log"), 5, False, "not_enough_bp",
                                         [("combat", "resources", "log")]))(_dispatch)
S.case("d-topics-cover", "pkg 23: the topics table names every registered command and nothing else", ([], []))(
    lambda: (sorted(set(REGISTRY) - set(sm.TOPICS)), sorted(set(sm.TOPICS) - set(REGISTRY))))
S.case("d-unknown-command-all", "pkg 23: a command missing from the table refreshes every panel", ("all",))(
    lambda: sm.topics_of("no_such_command"))
S.case("v-view", "pkg 23: views by panel; the view runs in the character's rule scope (AC base 12 -> front 12)",
       (8, 12, "unknown_view"))(
    lambda: (lambda s: (s.view("resources")["hp"]["current"],
                        (s.dispatch("set_rule_setting", key="ac.base", value=12), s.view("defense")["modes"]["front"])[1],
                        refusal(lambda: s.view("nope"))))(new_session()))


# ---------------------------------------------------------------- autosave, backups
def _autosave():
    clock = Clock()
    s = new_session(clock, autosave_interval_s=10)
    before = text(s)
    s.dispatch("take_damage", amount=3)
    clock.t += 5
    early = s.maybe_autosave(), text(s) == before
    clock.t += 5
    late = s.maybe_autosave(), cio.loads(text(s)).hp_current
    return early, late


S.case("a-interval", "pkg 23: autosave after 10 s of changes: at 5 s nothing, at 10 s saved (HP 5)",
       ((False, True), (True, 5)))(_autosave)
S.case("a-every-command", "pkg 23: autosave_mode every_command saves after each command", 5)(
    lambda: (lambda s: (s.dispatch("take_damage", amount=3), cio.loads(text(s)).hp_current)[1])(
        new_session(autosave_mode="every_command")))


def _backups():
    clock = Clock()
    s = new_session(clock, backups_count=2)
    for i in range(3):
        clock.t += 1
        s.dispatch("take_damage", amount=1)
        s.save()
    return len(files.backups_of(s.characters_dir, "Hero", s.setting("backups_folder")))


S.case("a-backups", "pkg 23: 3 saves with backups_count 2 -> 2 backups kept", 2)(_backups)


def _corrupt():
    clock = Clock()
    s = new_session(clock)
    s.dispatch("take_damage", amount=2)
    clock.t += 1
    s.save()                                   # backup = the file with HP 8, file = HP 6
    s.close()
    with open(files.path_of(s.characters_dir, "Hero"), "w") as f:
        f.write("{broken")
    reason = refusal(lambda: s.open("Hero"))
    ch = s.restore_backup("Hero")
    return reason, ch.hp_current


S.case("a-corrupt", "pkg 23: a damaged file is a refusal (file_corrupt), never a crash; restore from the newest valid "
       "backup", ("file_corrupt", 8))(_corrupt)


def _failing_save():
    s = new_session()
    before = text(s)
    s.dispatch("take_damage", amount=3)
    real = cio._write_text

    def boom(f, t):
        raise OSError("disk full")
    cio._write_text = boom
    try:
        reason = refusal(s.save)
    finally:
        cio._write_text = real
    return reason, text(s) == before


S.case("a-failing-save", "pkg 23: a failing save is a refusal and keeps the old file", ("save_failed", True))(_failing_save)


# ---------------------------------------------------------------- character files
def _files():
    s = new_session()
    s.duplicate("Hero", "Copy")
    s.rename("Copy", "Twin")
    s.close()
    trash = s.delete("Twin")
    return s.list_characters(), os.path.exists(trash), os.path.basename(os.path.dirname(trash))


S.case("f-files", "pkg 23: duplicate, rename, delete to the trash folder (never a hard delete)", (("Hero",), True, "trash"))(_files)
S.case("f-delete-open", "pkg 23: the open character cannot be deleted", "character_open")(
    lambda: refusal(lambda: new_session().delete("Hero")))
S.case("f-bad-name", "pkg 23: a name with a path character is refused", "bad_name")(
    lambda: refusal(lambda: new_session().new("a/b")))


def _export_import():
    s = new_session()
    s.dispatch("take_damage", amount=3)
    s.save()
    dest = os.path.join(tempfile.mkdtemp(dir=TMP), "hero_export.json")
    s.export("Hero", dest)
    s.import_file(dest, "Imported")
    return s.open("Imported") == s.open("Hero")


S.case("f-export-import", "pkg 23: export one character and import it back: the same character", True)(_export_import)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
