"""Settings commands of the "!" notes (package 38, owner decision 8; wp/settings/notes.py). Classic profiles only.

note_add(pid, target, text) -> {"id"}; note_edit(pid, nid, text); note_move(pid, nid, target); note_remove(pid, nid).
pid "" = the active classic profile. The tabs a note may sit on come from the screen data (wp/ui/data/
screen_blocks.json "tabs": read as data, no Qt).
"""
import io
import json
import os

from wp.commands.base import CommandError
from wp.settings import notes as nt
from wp.settings import settings_cmds as sc
from wp.settings import store as st

CLASSIC = "classic"
SCREEN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui", "data", "screen_blocks.json")


def tabs():
    with io.open(SCREEN, encoding="utf-8") as f:
        return tuple(json.load(f)["tabs"])


def _apply(app, pid, fn, *args):
    prof = dict(sc._profile(app, CLASSIC, pid or None))
    try:
        new_notes, nid = fn(prof, *args)
    except nt.NoteError as e:
        raise CommandError("%s %s" % (e.reason, ", ".join(str(v) for v in e.values)), e.reason, values=e.values)
    prof[nt.FIELD] = [dict(n) for n in new_notes]
    return sc.SettingsResult(sc._with_profile(app, CLASSIC, st.freeze(prof)), {"id": nid})


@sc.settings_command
def note_add(app, pid="", target="", text=""):
    return _apply(app, pid, lambda p: nt.add(p, tabs(), target, text))


@sc.settings_command
def note_edit(app, pid="", nid="", text=""):
    return _apply(app, pid, lambda p: nt.edit(p, nid, text))


@sc.settings_command
def note_move(app, pid="", nid="", target=""):
    return _apply(app, pid, lambda p: nt.move(p, tabs(), nid, target))


@sc.settings_command
def note_remove(app, pid="", nid=""):
    return _apply(app, pid, lambda p: nt.remove(p, nid))
