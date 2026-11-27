"""Package 38 P4 (owner decision 8): the "!" notes of the layout, Qt-free: add, edit, move, delete, bad input refused,
the save / load round trip (a new Session on the same folder = a restart), a profile reset keeps the notes, the notes
never enter the character.
Run: python Wp_claude/tests/app/test_notes38.py"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app.session import Session  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.settings import notes as nt  # noqa: E402
from wp.settings import settings_cmds as sc  # noqa: E402
from wp.settings import store as st  # noqa: E402

S = Suite("test_notes38")
TMP = tempfile.mkdtemp(prefix="wp_notes38_")


def app():
    return st.AppSettings()


def run(a, *steps):
    for n, p in steps:
        a = sc.settings_dispatch(a, n, **p).state
    return a


def notes(a):
    return [(n["id"], n["target"], n["text"]) for n in nt.notes(st.profile(a, "classic"))]


def ref(fn):
    from wp.commands import CommandError
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "no refusal"


S.case("add", "decision 8: two notes, on a block and on a tab; ids made by the program",
       [("note_1", "combat", "Check the shield"), ("note_2", "tab:training", "Ask the GM")])(
    lambda: notes(run(app(), ("note_add", {"target": "combat", "text": "Check the shield"}),
                      ("note_add", {"target": "tab:training", "text": " Ask the GM "}))))
S.case("edit-move-delete", "decision 8: edit the text, move to the bottom strip, delete the first",
       [("note_2", "bottom_strip", "Second")])(
    lambda: notes(run(app(), ("note_add", {"target": "combat", "text": "First"}),
                      ("note_add", {"target": "rerolls", "text": "2"}),
                      ("note_edit", {"nid": "note_2", "text": "Second"}),
                      ("note_move", {"nid": "note_2", "target": "bottom_strip"}),
                      ("note_remove", {"nid": "note_1"}))))
S.case("refused", "decision 8: an unknown place, an empty text, an unknown note are refused; nothing saved",
       ("unknown_note_target", "note_text_needed", "not_found", "note_text_needed"))(
    lambda: (ref(lambda: run(app(), ("note_add", {"target": "nowhere", "text": "x"}))),
             ref(lambda: run(app(), ("note_add", {"target": "combat", "text": "  "}))),
             ref(lambda: run(app(), ("note_edit", {"nid": "note_9", "text": "x"}))),
             ref(lambda: run(app(), ("note_add", {"target": "combat", "text": "x"}),
                             ("note_edit", {"nid": "note_1", "text": ""})))))
S.case("targets", "decision 8: every block of the profile and every tab is a place (the tab list from the screen data)",
       (True, True, True, True))(
    lambda: (lambda t: ("combat" in t, "bottom_strip" in t, "tab:combat" in t, "tab:rest" in t))(
        nt.targets(st.profile(app(), "classic"), __import__("wp.settings.note_cmds", fromlist=["tabs"]).tabs())))


def _restart():
    d = tempfile.mkdtemp(dir=TMP)
    s = Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    s.new("Hero", Character())
    r = s.settings("note_add", target="identity", text="Portrait later")
    s2 = Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    return r.ok, notes(s2.app), "Portrait later" in repr(s.character)


S.case("restart", "decision 8: a note survives a restart (saved with the UI settings) and is not in the character",
       (True, [("note_1", "identity", "Portrait later")], False))(_restart)
S.case("reset-keeps", "decision 8: a reset of the layout profile keeps the owner's notes",
       [("note_1", "combat", "Keep me")])(
    lambda: notes(run(app(), ("note_add", {"target": "combat", "text": "Keep me"}), ("profile_reset", {"mode": "classic"}))))


def _export_import():
    a = run(app(), ("note_add", {"target": "combat", "text": "Travel with me"}))
    text = sc.settings_dispatch(a, "profile_export", mode="classic", pid=st.profile(a, "classic")["id"]).info["text"]
    b = sc.settings_dispatch(app(), "profile_import", mode="classic", text=text)
    prof = next(p for p in b.state.profiles["classic"] if p["id"] == b.info["id"])
    return [(n["target"], n["text"]) for n in nt.notes(prof)]


S.case("export-import", "decision 8: the notes are a profile field: an exported profile brings them back on import",
       [("combat", "Travel with me")])(_export_import)


def _bad_import():
    import json
    text = json.dumps({"kind": "layout_profile", "mode": "classic", "profile": {"name": "x", "notes": "not a list"}})
    return ref(lambda: sc.settings_dispatch(app(), "profile_import", mode="classic", text=text))


S.case("import-typed", "decision 8: the notes field is typed in the profile schema: a text instead of a list is "
       "refused on import", "wrong_type")(_bad_import)

if __name__ == "__main__":
    sys.exit(S.run())
