"""The "!" notes of the Classic layout (package 38, owner decision 8; UI_WISHES "Notes", ARCH/settings.md).

The owner places a note anywhere the layout editor places widgets: on a block of the classic profile (its item id:
"combat", "bottom_strip", "rerolls" ...) or on a tab page ("tab:<tab id>"). The note shows as a "!" mark, the text on
hover / click. Notes are UI settings: the classic profile field "notes" = [{"id", "target", "text"}] (saved with the
profile in app_settings.json, never in the character). Ids are made by the program (note_1, note_2 ...).
Qt-free: targets(profile, tabs), add / edit / move / remove(profile, ...) -> (new notes list, note id); a bad input
raises NoteError(reason, values) and changes nothing. The settings commands are in wp/settings/note_cmds.py.
"""
TAB = "tab:"
FIELD = "notes"
PREFIX = "note_"


class NoteError(ValueError):
    def __init__(self, reason, values=()):
        super().__init__(reason)
        self.reason, self.values = reason, tuple(values)


def targets(profile, tabs):
    """Every place a note may sit: the block ids of the profile, then tab:<id> of every tab."""
    blocks = [i.get("id", i.get("panel")) for i in profile.get("panels", ())]
    return tuple(b for b in blocks if b) + tuple(TAB + t for t in tabs)


def notes(profile):
    return tuple(dict(n) for n in profile.get(FIELD, ()) or ())


def _check(profile, tabs, target, text):
    if target not in targets(profile, tabs):
        raise NoteError("unknown_note_target", (target,))
    if not str(text).strip():
        raise NoteError("note_text_needed")


def _new_id(have):
    n = 1
    taken = {x["id"] for x in have}
    while PREFIX + str(n) in taken:
        n += 1
    return PREFIX + str(n)


def _find(have, nid):
    if not any(x["id"] == nid for x in have):
        raise NoteError("not_found", ("notes", nid))


def add(profile, tabs, target="", text=""):
    _check(profile, tabs, target, text)
    have = notes(profile)
    nid = _new_id(have)
    return have + ({"id": nid, "target": target, "text": str(text).strip()},), nid


def edit(profile, nid="", text=""):
    have = notes(profile)
    _find(have, nid)
    if not str(text).strip():
        raise NoteError("note_text_needed")
    return tuple(dict(x, text=str(text).strip()) if x["id"] == nid else x for x in have), nid


def move(profile, tabs, nid="", target=""):
    have = notes(profile)
    _find(have, nid)
    if target not in targets(profile, tabs):
        raise NoteError("unknown_note_target", (target,))
    return tuple(dict(x, target=target) if x["id"] == nid else x for x in have), nid


def remove(profile, nid=""):
    have = notes(profile)
    _find(have, nid)
    return tuple(x for x in have if x["id"] != nid), nid


def on(profile, target):
    """The notes placed on one target, in order."""
    return tuple(x for x in notes(profile) if x.get("target") == target)
