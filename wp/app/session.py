"""The session: the single entry point of the future UI (package 23 A, D25). No threads, no Qt.

Session(characters_dir, user_dir, clock=time.time)
- holds the open Character, the app settings (user_dir/app_settings.json), the catalogs (user_dir/catalogs), the
  themes (user_dir/themes.json), the active theme and layout profile;
- new(name) / open(name) / close(); restore_backup(name) after a refusal file_corrupt;
- dispatch(command id, **params) is the ONLY way to change the character: returns DispatchResult(ok, info, reason,
  params, topics); topics = the panels to refresh (data: wp/app/data/topics.json; an unknown command -> all);
  subscribers (callbacks) get the topics once per successful command;
- view(panel id, **params): the panel's view, computed inside rules.using(character);
- autosave (app settings autosave, autosave_mode every_command | interval, autosave_interval_s) with the injected
  clock: maybe_autosave() is called by the UI timer; backups rotated (backups_count, backups_folder);
- character files: list / duplicate / rename / delete (to trash) / export / import (wp/app/files.py).
"""
import io
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from wp.app import files
from wp.app import views as vw
from wp.catalog import store as cs
from wp.commands import CommandError
from wp.commands import dispatch as character_dispatch
from wp.commands import journal
from wp.commands.base import Result
from wp.model.character import Character, LogEntry
from wp.rules_data import rules as rd
from wp.settings import store as st
from wp.theme import themes

TOPICS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "topics.json")
ALL = "all"
EVERY_COMMAND = "every_command"


def _topics():
    with io.open(TOPICS_PATH, encoding="utf-8") as f:
        return json.load(f)["commands"]


TOPICS = _topics()
UNDO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "undo.json")


def _non_undoable():
    with io.open(UNDO_PATH, encoding="utf-8") as f:
        return frozenset(json.load(f)["non_undoable"])


NON_UNDOABLE = _non_undoable()


def topics_of(command):
    t = TOPICS.get(command)
    return (ALL,) if t is None else tuple(t)


@dataclass(frozen=True)
class DispatchResult:
    ok: bool
    topics: Tuple[str, ...] = ()
    info: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    params: Dict[str, Any] = field(default_factory=dict)


class Session(object):
    def __init__(self, characters_dir, user_dir, clock=time.time):
        self.characters_dir = characters_dir
        self.user_dir = user_dir
        self.clock = clock
        self.app = st.load(user_dir)
        self.themes = themes.load_layers(user_dir)
        self.character = None
        self.name = ""
        self.dirty_since = None
        self._subscribers = []
        self._catalogs = {}
        self._undo = []                # [(Character before, command)] newest last (package 25 A)
        self._redo = []

    # -------------------------------------------------------------- settings, catalogs, theme
    def setting(self, key):
        return st.get(self.app, key)

    def catalog(self, kind):
        if kind not in self._catalogs:
            self._catalogs[kind] = cs.load_layers(kind, os.path.join(self.user_dir, "catalogs"))
        return self._catalogs[kind]

    def theme(self):
        return themes.active(self.app, self.themes)

    def profile(self, mode):
        return st.profile(self.app, mode)

    # -------------------------------------------------------------- files
    def _sub(self):
        return self.setting("backups_folder")

    def list_characters(self):
        return files.list_characters(self.characters_dir)

    def new(self, name, character=None):
        files.create(self.characters_dir, name, character or Character())
        return self.open(name)

    def open(self, name):
        self.character = files.load(self.characters_dir, name, self._sub())
        self.name, self.dirty_since = name, None
        self._undo, self._redo = [], []
        return self.character

    def restore_backup(self, name):
        files.restore_backup(self.characters_dir, name, self._sub())
        return self.open(name)

    def close(self):
        if self.dirty_since is not None:
            self.save()
        self.character, self.name = None, ""

    def save(self):
        if self.character is None:
            raise CommandError("no character is open", "no_character")
        files.save(self.characters_dir, self.name, self.character, self._sub(), int(self.setting("backups_count")),
                   self.clock())
        self.dirty_since = None

    def maybe_autosave(self):
        """Called by the UI timer: saves when autosave is on and the changes are older than the interval."""
        if self.dirty_since is None or not self.setting("autosave"):
            return False
        if self.clock() - self.dirty_since >= int(self.setting("autosave_interval_s")):
            self.save()
            return True
        return False

    def duplicate(self, name, new_name):
        files.duplicate(self.characters_dir, name, new_name, self._sub())

    def rename(self, name, new_name):
        files.rename(self.characters_dir, name, new_name, self._sub())
        if self.name == name:
            self.name = new_name

    def delete(self, name):
        if self.name == name:
            raise CommandError("close the character before deleting it", "character_open", values=(name,))
        return files.delete(self.characters_dir, name, self.clock())

    def export(self, name, dest):
        return files.export(self.characters_dir, name, dest, self._sub())

    def import_file(self, src, name):
        return files.import_file(self.characters_dir, src, name)

    # -------------------------------------------------------------- commands and views
    def subscribe(self, fn):
        self._subscribers.append(fn)

    def dispatch(self, command, **params):
        if self.character is None:
            return DispatchResult(False, reason="no_character", params={})
        try:
            result = character_dispatch(self.character, command, **params)
        except CommandError as e:
            return DispatchResult(False, reason=e.reason, params=dict(e.params), info={"text": str(e)})
        if command not in NON_UNDOABLE and int(self.setting("undo_depth")) > 0:
            self._undo = (self._undo + [(self.character, command)])[-int(self.setting("undo_depth")):]
            self._redo = []
        self.character = result.state
        return self._changed(topics_of(command), dict(result.info))

    def _changed(self, topics, info):
        if self.dirty_since is None:
            self.dirty_since = self.clock()
        if self.setting("autosave") and self.setting("autosave_mode") == EVERY_COMMAND:
            self.save()
        for fn in self._subscribers:
            fn(topics)
        return DispatchResult(True, topics=topics, info=info)

    def can_undo(self):
        return bool(self._undo)

    def can_redo(self):
        return bool(self._redo)

    def _step(self, source, target, line):
        if self.character is None:
            return DispatchResult(False, reason="no_character", params={})
        if not source:
            return DispatchResult(False, reason="nothing_to_" + line, params={})
        state, command = source.pop()
        target.append((self.character, command))
        entry = Result(state=state, entry=LogEntry(command=line))
        self.character = journal.record(self.character, entry, line, {"command": command}).state
        return self._changed(topics_of(command), {"command": command})

    def undo(self):
        """The Character as it was before the last undoable command (states share their unchanged parts: frozen
        records, nothing is deep-copied); the journal gets a line "undo"; autosave sees a change."""
        return self._step(self._undo, self._redo, "undo")

    def redo(self):
        return self._step(self._redo, self._undo, "redo")

    def view(self, name, **params):
        if name not in vw.VIEWS:
            raise CommandError("no view %r" % (name,), "unknown_view", values=(name,))
        if self.character is None:
            raise CommandError("no character is open", "no_character")
        with rd.using(self.character):
            return vw.VIEWS[name](self.character, self, **params)
