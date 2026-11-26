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
- character files: list / duplicate / rename / delete (to trash) / export / import (wp/app/files.py);
- [package 32] settings(command, **params): the app settings commands for the UI (theme, language, scale, hints,
  window geometry): saved to the user folder at once, subscribers get the topic "settings"; theme(system_dark),
  themes_view(system_dark), hint_visible(hint id).
"""
import io
import json
import os
import time
from dataclasses import dataclass, field, replace
from typing import Any, Dict, Tuple

from wp.app import files
from wp.app import history
from wp.app import limits
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
SETTINGS_TOPICS = ("settings",)        # what subscribers get after an app settings change (package 32)
ANY_TOPIC_VIEWS = ("sources",)         # views that read every number: re-read on ANY non-empty topics (package 34)
EDITOR_TOPICS = ("editor",)
REMINDER_TOPIC = "reminders"           # one-shot reminders added / dismissed (package 34)
RESOURCE_GROUP = "resource:"           # quick buttons shown under a resource (package 33), not in the grid            # the editor mode switched (package 34)
EDITOR_NEEDED = "editor_mode_needed"   # refusal of an editor-only command outside the editor mode


def _topics():
    with io.open(TOPICS_PATH, encoding="utf-8") as f:
        return json.load(f)["commands"]


TOPICS = _topics()
UNDO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "undo.json")


def _undo_table():
    with io.open(UNDO_PATH, encoding="utf-8") as f:
        return json.load(f)


NON_UNDOABLE = frozenset(_undo_table()["non_undoable"])
KEEP_CURRENT = tuple(_undo_table()["keep_current"])   # fields an undo / redo takes from the current state (F3 F17)
SHORT = "short"
QUICK = "run_quick"                   # the undo entry of a quick button (package 30)
STAMPS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "stamps.json")


def _stamped():
    with io.open(STAMPS_PATH, encoding="utf-8") as f:
        return frozenset(json.load(f)["stamped"])


STAMPED = _stamped()                   # commands that get at = the Session clock stamp (package 26 C)


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
        self.editor_mode = False       # package 34: the editor mode (UI state, not saved); gates EDITOR_ONLY
        self.notes = ()                # package 34: one-shot reminders of command results, until dismissed

    def reminders_view(self):
        """The standing reminders of the character (statuses view) + the one-shot ones of this Session
        ({"standing": ((key, values), ...), "notes": ((key, values), ...)})."""
        standing = self.view("statuses")["reminders"] if self.character is not None else ()
        return {"standing": tuple(standing), "notes": tuple(self.notes)}

    def dismiss_note(self, index):
        """Drop one one-shot reminder (or all with index None); subscribers get the topic "reminders"."""
        self.notes = () if index is None else tuple(n for i, n in enumerate(self.notes) if i != int(index))
        for fn in self._subscribers:
            fn((REMINDER_TOPIC,))

    def quick_view(self, mode="classic"):
        """The quick-access grid (package 34): {"cells", "columns", "buttons": ((id, label, cost_actions), ...)} =
        the profile fields quick_cells / quick_columns and the app quick buttons without a resource group, by order."""
        prof = self.profile(mode)
        bs = sorted((b for b in self.app.quick_buttons if not str(b.get("group") or "").startswith(RESOURCE_GROUP)),
                    key=lambda b: (int(b.get("order") or 0), b["id"]))
        return {"cells": int(prof.get("quick_cells") or 0), "columns": int(prof.get("quick_columns") or 0),
                "buttons": tuple((b["id"], b.get("label") or b["id"], int(b.get("cost_actions") or 0)) for b in bs)}

    def set_editor_mode(self, on):
        """The editor mode on / off (package 34): the subscribers get the topic "editor"."""
        self.editor_mode = bool(on)
        for fn in self._subscribers:
            fn(EDITOR_TOPICS)

    # -------------------------------------------------------------- settings, catalogs, theme
    def setting(self, key):
        return st.get(self.app, key)

    def catalog(self, kind):
        if kind not in self._catalogs:
            self._catalogs[kind] = cs.load_layers(kind, os.path.join(self.user_dir, "catalogs"))
        return self._catalogs[kind]

    def theme(self, system_dark=None):
        return themes.active(self.app, self.themes, system_dark)

    def themes_view(self, system_dark=None):
        return themes.view(self.app, self.themes, system_dark)

    def hint_visible(self, hint_id):
        from wp.settings import screen_settings as ss
        return ss.hint_visible(self.app, hint_id)

    def settings(self, command, **params):
        """An app settings command (wp/settings/settings_cmds.py) for the UI (package 32): the new settings are saved
        to the user folder at once; a refusal is a result like dispatch; subscribers get the topic "settings"."""
        from wp.settings.settings_cmds import settings_dispatch
        try:
            result = settings_dispatch(self.app, command, **params)
        except CommandError as e:
            return DispatchResult(False, reason=e.reason, params=dict(e.params), info={"text": str(e)})
        if result.state == self.app:
            return DispatchResult(True, topics=(), info=dict(result.info))
        try:
            self.app = st.save(result.state) if result.state.path else result.state
        except st.SettingsError as e:
            return DispatchResult(False, reason="settings_error", params={}, info={"text": str(e)})
        for fn in self._subscribers:
            fn(SETTINGS_TOPICS)
        return DispatchResult(True, topics=SETTINGS_TOPICS, info=dict(result.info))

    THEME_COMMANDS = ("theme_copy", "theme_edit", "theme_reset", "theme_remove")

    def theme_command(self, command, **params):
        """A theme command of the theme editor (package 35 P3): theme_copy / theme_edit / theme_reset / theme_remove on
        the theme layers, saved to the user folder at once; subscribers get "settings" (the window restyles live).
        The shipped themes stay untouched: theme_edit / theme_remove of a shipped id are refused (shipped_theme)."""
        tid = params.get("tid", "")
        try:
            if command not in self.THEME_COMMANDS:
                raise CommandError("unknown theme command %r" % (command,), "unknown_command", values=(command,))
            if command in ("theme_edit", "theme_remove") and tid in themes.shipped_ids():
                raise CommandError("%s is a shipped theme" % (tid,), "shipped_theme", values=(tid,))
            out = getattr(themes, command)(self.themes, **params)
            layers, new_id = out if isinstance(out, tuple) else (out, tid)
            self.themes = themes.save(layers, self.user_dir)
        except CommandError as e:
            return DispatchResult(False, reason=e.reason, params=dict(e.params), info={"text": str(e)})
        except OSError as e:
            return DispatchResult(False, reason="settings_error", params={}, info={"text": str(e)})
        for fn in self._subscribers:
            fn(SETTINGS_TOPICS)
        return DispatchResult(True, topics=SETTINGS_TOPICS, info={"id": new_id})

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
        self.notes = ()                # one-shot reminders belong to the open character
        self._journal()                # an imported long journal goes into the archive at once
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
        from wp.commands import source_cmds
        if command in source_cmds.EDITOR_ONLY and not self.editor_mode:
            return DispatchResult(False, reason=EDITOR_NEEDED, params={"values": (command,)})
        at = files.stamp(self.clock())
        if command in STAMPED and "at" not in params:
            params = dict(params, at=at)
        try:
            with journal.stamped(at):
                result = character_dispatch(self.character, command, **params)
        except CommandError as e:
            return DispatchResult(False, reason=e.reason, params=dict(e.params), info={"text": str(e)})
        if result.state == self.character:     # nothing changed (F18): no undo step, no subscribers, not dirty
            return DispatchResult(True, topics=(), info=dict(result.info))
        if command not in NON_UNDOABLE and int(self.setting("undo_depth")) > 0:
            self._undo = (self._undo + [(self.character, command)])[-int(self.setting("undo_depth")):]
            self._redo = []
        self.character = result.state
        return self._changed(topics_of(command), dict(result.info))

    def _changed(self, topics, info):
        new = tuple((k, tuple(v)) for k, v in info.get("reminders", ()))
        if new:                        # one-shot reminders kept until dismissed (package 34; not saved)
            self.notes = self.notes + new
            topics = tuple(topics) + (REMINDER_TOPIC,)
        self._journal()
        if self.dirty_since is None:
            self.dirty_since = self.clock()
        if self.setting("autosave") and self.setting("autosave_mode") == EVERY_COMMAND:
            self.save()
        for fn in self._subscribers:
            fn(topics)
        return DispatchResult(True, topics=topics, info=info)

    def run_quick(self, button):
        """A quick button (its dict or its id among the app quick buttons) through the Session (package 30): its
        action or macro steps {"command", "params"} run in order as ONE undo step; "set / add / subtract X" on any
        resource = the steps set_value / adjust_value. A refused step rolls the whole macro back (nothing changes)."""
        if self.character is None:
            return DispatchResult(False, reason="no_character", params={})
        if isinstance(button, str):
            button = next((b for b in self.app.quick_buttons if b.get("id") == button), None)
            if button is None:
                return DispatchResult(False, reason="not_found", params={"values": ("quick_buttons", button)})
        steps = list(button.get("macro") or ()) or ([button["action"]] if button.get("action") else [])
        state, topics = self.character, []
        with journal.stamped(files.stamp(self.clock())):
            for i, step in enumerate(steps):
                try:
                    state = character_dispatch(state, step["command"], **dict(step.get("params", {}))).state
                except (CommandError, KeyError, TypeError) as e:
                    reason = getattr(e, "reason", "invalid_value")
                    return DispatchResult(False, reason=reason, params=dict(getattr(e, "params", {}), step=i + 1),
                                          info={"text": str(e)})
                topics += [t for t in topics_of(step["command"]) if t not in topics]
        if state == self.character:
            return DispatchResult(True, topics=(), info={"steps": len(steps)})
        if int(self.setting("undo_depth")) > 0:
            self._undo = (self._undo + [(self.character, QUICK)])[-int(self.setting("undo_depth")):]
            self._redo = []
        self.character = state
        return self._changed(tuple(topics), {"steps": len(steps)})

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
        state = replace(state, **{f: getattr(self.character, f) for f in KEEP_CURRENT})
        entry = Result(state=state, entry=LogEntry(command=line))
        with journal.stamped(files.stamp(self.clock())):
            self.character = journal.record(self.character, entry, line, {"command": command}).state
        return self._changed(topics_of(command), {"command": command})

    def undo(self):
        """The Character as it was before the last undoable command (states share their unchanged parts: frozen
        records, nothing is deep-copied); the journal gets a line "undo"; autosave sees a change."""
        return self._step(self._undo, self._redo, "undo")

    def redo(self):
        return self._step(self._redo, self._undo, "redo")

    # -------------------------------------------------------------- journal (package 27 E, D29)
    def _journal(self):
        """journal_mode short: keep the newest journal_short_max lines, older ones are dropped. full: at
        journal_archive_at lines the oldest go into the archive file (wp/app/history.py), the newest
        journal_archive_keep stay; a failed append keeps every line in memory."""
        ch = self.character
        if ch is None:
            return
        log = ch.log
        if self.setting("journal_mode") == SHORT:
            mx = int(self.setting("journal_short_max"))
            if len(log) > mx:
                self.character = replace(ch, log=log[-mx:])
            return
        if len(log) < int(self.setting("journal_archive_at")):
            return
        block = log[:max(0, len(log) - int(self.setting("journal_archive_keep")))]
        try:
            history.append(self.characters_dir, self.name, block)
        except OSError:
            return
        self.character = replace(ch, log=log[len(block):])

    def journal_view(self, count=vw.LOG_TAIL, offset=0):
        """The recent journal lines in memory, newest last: `count` lines ending `offset` lines before the end."""
        log = self.character.log if self.character is not None else ()
        end = len(log) - int(offset)
        return tuple(log[max(0, end - int(count)):max(0, end)])

    def history_view(self, from_date="", to_date="", page=0, size=None):
        """The whole journal (archive + memory) between two dates YYYYMMDD (inclusive, "" = open), page by page."""
        def inside(e):
            d = history.date_of(e.at)
            return (not from_date or d >= from_date) and (not to_date or d <= to_date)
        arch = history.read(self.characters_dir, self.name, from_date, to_date)   # by the date index
        last = history.load_index(self.characters_dir, self.name)["last_seq"]
        lines = arch + tuple(e for e in (self.character.log if self.character else ()) if e.seq > last and inside(e))
        size = int(size or limits.get("history_page"))
        start = int(page) * size
        return {"lines": lines[start:start + int(size)], "total": len(lines), "page": int(page), "size": int(size)}

    def cell_sources(self):
        """Every number a cell may show for the open character (source id, label key): the layout editor's list
        (package 30; wp/model/screen_view.py cell_sources)."""
        from wp.model import screen_view as scr
        with rd.using(self.character):
            return scr.cell_sources(self.character)

    def full_log(self):
        return history.full_log(self.characters_dir, self.name, self.character.log if self.character else ())

    def view(self, name, **params):
        if name not in vw.VIEWS:
            raise CommandError("no view %r" % (name,), "unknown_view", values=(name,))
        if self.character is None:
            raise CommandError("no character is open", "no_character")
        with rd.using(self.character):
            return vw.VIEWS[name](self.character, self, **params)
