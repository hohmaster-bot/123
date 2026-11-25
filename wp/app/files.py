"""Character files (package 23 A3, A4): list, create, duplicate, rename, delete to trash, export / import, rotated
backups and recovery from the newest valid backup. Pure logic on a folder; the clock is injected (tests never sleep).

A character file is <folder>/<name>.json (atomic save of wp/storage/character_io, which keeps <name>.json.bak too).
Backups: <folder>/<backup folder>/<name>.<YYYYMMDD-HHMMSS-mmm>.json, a copy of the file made before it is overwritten;
only the newest N are kept (app settings backups_count / backups_folder). Delete moves the file into <folder>/trash/
(never a hard delete). Refusals are CommandError with a reason id.
"""
import os
import re
import shutil
import time

from wp.app import history
from wp.app import limits
from wp.commands.base import CommandError
from wp.storage import character_io as cio

EXT = ".json"
TRASH = "trash"
BAD_CHARS = '/\\:*?"<>|'


STAMP_TAIL = re.compile(r"^[0-9]{8}-[0-9]{6}-[0-9]{3}\.json$")     # what follows "<name>." in a backup file name
RESERVED = frozenset(["CON", "PRN", "AUX", "NUL"] + ["COM%d" % i for i in range(1, 10)] +
                     ["LPT%d" % i for i in range(1, 10)])


def name_problem(name):
    """None, or why a name cannot be a file name (review 5 F10): not a string, empty, spaces around it, a bad or
    control character, longer than the limit name_max, "." / "..", a reserved Windows name (CON, NUL, COM1, aux.txt),
    a trailing dot or space, or a name ending in .json."""
    if not isinstance(name, str) or not name:
        return "empty"
    if name.strip() != name or name.endswith("."):
        return "edge"
    if any(c in BAD_CHARS or ord(c) < 32 or ord(c) == 127 for c in name):
        return "char"
    if len(name) > limits.get("name_max"):
        return "long"
    if name.split(".")[0].strip().upper() in RESERVED:
        return "reserved"
    if name.lower().endswith(EXT):
        return "ext"
    return None


def check_name(name):
    why = name_problem(name)
    if why:
        raise CommandError("bad character name %r (%s)" % (name, why), "bad_name", values=(name,), why=why)
    return name


def path_of(folder, name):
    return os.path.join(folder, check_name(name) + EXT)


def list_characters(folder):
    if not os.path.isdir(folder):
        return ()
    return tuple(sorted(f[:-len(EXT)] for f in os.listdir(folder)
                        if f.endswith(EXT) and os.path.isfile(os.path.join(folder, f))))


def stamp(t):
    """A sortable time stamp from a clock value in seconds (UTC)."""
    return time.strftime("%Y%m%d-%H%M%S", time.gmtime(t)) + "-%03d" % int((t % 1) * 1000)


def backup_dir(folder, sub):
    return os.path.join(folder, sub)


def backups_of(folder, name, sub):
    d = backup_dir(folder, sub)
    if not os.path.isdir(d):
        return ()
    pre = name + "."                   # "a" must not take the backups of "a.b" (review 5 F1): the rest is a stamp
    return tuple(sorted((os.path.join(d, f) for f in os.listdir(d)
                         if f.startswith(pre) and STAMP_TAIL.match(f[len(pre):])), reverse=True))


def make_backup(folder, name, sub, keep, now):
    """Copy the current file into the backup folder (before it is overwritten); keep the newest `keep` copies."""
    src = path_of(folder, name)
    if not os.path.exists(src) or keep <= 0:
        return None
    d = backup_dir(folder, sub)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, "%s.%s%s" % (name, stamp(now), EXT))
    shutil.copy2(src, dst)
    for old in backups_of(folder, name, sub)[keep:]:
        os.remove(old)
    return dst


def newest_valid_backup(folder, name, sub):
    for p in backups_of(folder, name, sub):
        try:
            cio.load(p)
            return p
        except cio.StorageError:
            continue
    return None


def load(folder, name, sub):
    """The character, or CommandError file_corrupt (params: path, backup = the newest valid backup or None)."""
    p = path_of(folder, name)
    if not os.path.exists(p):
        raise CommandError("no character %r" % (name,), "not_found", values=("characters", name))
    try:
        return cio.load(p)
    except cio.StorageError as e:
        raise CommandError("the file of %r is damaged: %s" % (name, e), "file_corrupt", values=(name,), path=p,
                           backup=newest_valid_backup(folder, name, sub))


def save(folder, name, ch, sub, keep, now):
    """Backup of the old file (rotated), then the atomic save. A failing save keeps the old file."""
    make_backup(folder, name, sub, keep, now)
    try:
        cio.save(ch, path_of(folder, name))
    except (OSError, cio.StorageError) as e:
        raise CommandError("saving %r failed (the old file is kept): %s" % (name, e), "save_failed", values=(name,))


def restore_backup(folder, name, sub):
    """Put the newest valid backup back as the character file; returns the character."""
    b = newest_valid_backup(folder, name, sub)
    if b is None:
        raise CommandError("no valid backup of %r" % (name,), "no_backup", values=(name,))
    ch = cio.load(b)
    cio.save(ch, path_of(folder, name))
    return ch


def _free(folder, name):
    if os.path.exists(path_of(folder, name)):
        raise CommandError("a character %r already exists" % (name,), "name_taken", values=(name,))


def create(folder, name, ch):
    _free(folder, name)
    cio.save(ch, path_of(folder, name))


def duplicate(folder, name, new_name, sub):
    """A whole character copy (gear.md "Item codes / sharing": copy character), its journal archive too."""
    ch = load(folder, name, sub)
    _free(folder, new_name)
    cio.save(ch, path_of(folder, new_name))
    history.copy(folder, name, new_name)


def rename(folder, name, new_name, sub):
    load(folder, name, sub)
    _free(folder, new_name)
    os.replace(path_of(folder, name), path_of(folder, new_name))
    for p in backups_of(folder, name, sub):          # backups follow the new name
        base = os.path.basename(p)[len(name):]
        os.replace(p, os.path.join(os.path.dirname(p), new_name + base))
    bak = path_of(folder, name) + cio.BAK_SUFFIX
    if os.path.exists(bak):
        os.replace(bak, path_of(folder, new_name) + cio.BAK_SUFFIX)
    history.rename(folder, name, new_name)       # the journal archive follows (package 27 E)


def delete(folder, name, now):
    """Move the file into the trash folder (never a hard delete)."""
    p = path_of(folder, name)
    if not os.path.exists(p):
        raise CommandError("no character %r" % (name,), "not_found", values=("characters", name))
    t = os.path.join(folder, TRASH)
    os.makedirs(t, exist_ok=True)
    dst = os.path.join(t, "%s.%s%s" % (name, stamp(now), EXT))
    os.replace(p, dst)
    history.to_trash(folder, name, dst[:-len(EXT)])
    return dst


def export(folder, name, dest, sub):
    """The exported file holds the WHOLE journal (archive + file): it travels with the character (package 27 E);
    opening it again moves the old lines back into an archive."""
    from dataclasses import replace
    ch = load(folder, name, sub)
    cio.save(replace(ch, log=history.full_log(folder, name, ch.log)), dest)
    return dest


def import_file(folder, src, name):
    try:
        ch = cio.load(src)
    except cio.StorageError as e:
        raise CommandError("not a character file: %s" % e, "file_corrupt", values=(src,), path=src, backup=None)
    create(folder, name, ch)
    return ch
