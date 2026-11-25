"""Save / load a Character as JSON (D11). Only base values exist in the model, so
only base values are written (D6). No migrations, ever (D1): an unknown format
version is a clear error.

File layout: {"format": "wipefinder.character", "version": 1, "character": {...}}
Dataclasses are written as {"_t": "ClassName", field: value...}; dicts as
{"_dict": [[key, value], ...]} (keeps int keys); tuples as lists.

Atomic write: text is built first, written to <path>.tmp, flushed and fsynced,
the previous file (only if it still reads correctly) is copied to <path>.bak,
then <path>.tmp replaces <path>. A failed write leaves the old file untouched.
"""
import dataclasses
import json
from dataclasses import replace
import os
import shutil

from wp.core.damage import Pool
from wp.core.effects import Effect, OneShot, Status
from wp.core.injuries import Injury
from wp.core.pain import PainEntry, PainProfile
from wp.core.rest import Charge
from wp.core.skills import Skill
from wp.core.statuses import NegativeTraits
from wp.core.weapons import Pick, Weapon
from wp.model import ids
from wp.model.class_types import ClassInfo, HiddenProperty, SpellDamage
from wp.model.experience import LevelRecord, XpEntry
from wp.model.notebook import Court, Drive, Lens, Quest, Quirk, Story
from wp.model.template import Template
from wp.model.character import (Ability, AttackRecord, Character, Feat, Item, Language, LogEntry, Maneuver,
                                ResourcePool, RulesSettings, Seed, Spell, SpellUpgrade, Usage, WeaponEntry)

FORMAT = "wipefinder.character"
VERSION = 1
TMP_SUFFIX = ".tmp"
BAK_SUFFIX = ".bak"

# Fields that were removed from the model: an old file may still have them; they are dropped on load
# (nothing is converted, the value is simply not used). Character.mana_level: package 10, Q49.
DROPPED = {"Character": ("mana_level", "size_mod", "size_cmb"),
           "Status": ("cost_resource", "cost_amount"),
           "AttackRecord": ("kind", "base_record"),
           "Item": ("count",),
           "LogEntry": ("summary",)}   # old text journal entries keep only their command id
_SKIP = object()               # a record not read at all (see _skipped)


def _skipped(name, v):
    """Item-bound maneuver records (kind "maneuver", packages 9-11) are dropped on load (package 12 B, D1)."""
    if name == "AttackRecord" and v.get("kind") == "maneuver":
        return True
    # old by-name item charges (Character.charges kind "item") are dropped: charges live on the item (pkg 14 B, D1)
    return name == "Charge" and v.get("kind") == "item"   # read from old files, then ignored

_TYPES = {cls.__name__: cls for cls in (
    Pool, Effect, OneShot, Status, Injury, PainEntry, PainProfile, Charge, Skill,
    NegativeTraits, Pick, Weapon, Ability, AttackRecord, Character, Feat, Item, Language, LogEntry, Maneuver,
    ResourcePool, RulesSettings, Seed, Spell, SpellUpgrade, Usage, WeaponEntry,
    Court, Drive, Lens, Quest, Quirk, Story, Template, ClassInfo, HiddenProperty, SpellDamage, XpEntry, LevelRecord)}


class StorageError(Exception):
    """A character file could not be read or written."""


# ------------------------------------------------------------------ encode

def _encode(v):
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        name = type(v).__name__
        if name not in _TYPES:
            raise StorageError("cannot save type %s" % name)
        out = {"_t": name}
        for f in dataclasses.fields(v):
            out[f.name] = _encode(getattr(v, f.name))
        return out
    if isinstance(v, dict):
        return {"_dict": [[_encode(k), _encode(x)] for k, x in v.items()]}
    if isinstance(v, (tuple, list)):
        return [_encode(x) for x in v]
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    raise StorageError("cannot save value of type %s" % type(v).__name__)


def _tuple_field(f):
    return f.default is not dataclasses.MISSING and isinstance(f.default, tuple)


def _decode(v):
    if isinstance(v, list):
        return tuple(x for x in (_decode(x) for x in v) if x is not _SKIP)
    if isinstance(v, dict):
        if "_dict" in v:
            return {_decode(k): _decode(x) for k, x in v["_dict"]}
        name = v.get("_t")
        if name not in _TYPES:
            raise StorageError("unknown record type in file: %r" % (name,))
        cls = _TYPES[name]
        if _skipped(name, v):
            return _SKIP
        fields = {f.name: f for f in dataclasses.fields(cls)}
        # unknown fields are dropped on load (no migrations; CLAUDE.md, package 16 A8); a field whose stored kind
        # no longer fits (a dict where the model now keeps a list of records) is dropped the same way
        out = {}
        for k, x in v.items():
            if k == "_t" or k not in fields or k in DROPPED.get(name, ()):
                continue
            val = _decode(x)
            if isinstance(val, dict) and _tuple_field(fields[k]):
                continue
            out[k] = val
        return cls(**out)
    return v


def dumps(ch):
    """The file text; NaN / inf are never written (review 5 F13: allow_nan=False -> StorageError)."""
    try:
        return json.dumps({"format": FORMAT, "version": VERSION, "character": _encode(ch)},
                          ensure_ascii=True, indent=1, sort_keys=False, allow_nan=False)
    except ValueError as e:
        raise StorageError("cannot save a value that is not a finite number: %s" % e)


def loads(text):
    try:
        data = json.loads(text)
    except (ValueError, RecursionError) as e:
        raise StorageError("file is not valid JSON: %s" % e)
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        raise StorageError("not a WipeFinder character file")
    if data.get("version") != VERSION:
        raise StorageError("unsupported character file version %r; this app reads version %d "
                           "(old files are not converted)" % (data.get("version"), VERSION))
    try:
        ch = _decode(data.get("character"))
    except (TypeError, ValueError, KeyError, AttributeError, RecursionError) as e:
        raise StorageError("broken character data: %s" % e)
    if not isinstance(ch, Character):
        raise StorageError("file does not contain a character")
    from wp.storage import typecheck
    bad = typecheck.character_problem(ch)
    if bad:                            # review 5 F9: every value fits its field type, ids are unique
        raise StorageError("broken character data: %s" % bad)
    from wp.settings import schema as sch
    for key, value in ch.rules_settings.constants.items():
        wrong = sch.check_key(key, value) if key in sch.KEYS else None
        if wrong:                      # review 5 F6: a rule constant in the file keeps its limits
            raise StorageError("broken rule constant %s: %s" % (key, wrong[0]))
    # injuries saved before package 12 have no id: the program gives them one (owner, Q70)
    injuries, counter = ids.with_injury_ids(ch.injuries, ch.injury_counter)
    return replace(ch, injuries=injuries, injury_counter=counter)


# -------------------------------------------------------------- disk I/O

def _write_text(f, text):
    """Single place that writes the bytes (tests replace it to simulate a crash)."""
    f.write(text)


def _readable(path):
    try:
        load(path)
        return True
    except StorageError:
        return False


def save(ch, path):
    """Atomic save. The previous good file is kept as <path>.bak."""
    text = dumps(ch)                       # fail before touching the disk
    tmp = path + TMP_SUFFIX
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            _write_text(f, text)
            f.flush()
            os.fsync(f.fileno())
        if os.path.exists(path) and _readable(path):
            shutil.copy2(path, path + BAK_SUFFIX)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    return path


def load(path):
    """Load a character; never changes any file. StorageError on any problem."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise StorageError("cannot read %s: %s" % (path, e))
    try:
        return loads(text)
    except StorageError as e:
        hint = " (a backup exists: %s)" % (path + BAK_SUFFIX) if os.path.exists(path + BAK_SUFFIX) else ""
        raise StorageError("%s: %s%s" % (os.path.basename(path), e, hint))


def load_with_backup(path):
    """Load the file, or the last good copy if the file is broken. Returns (character, source)."""
    try:
        return load(path), "file"
    except StorageError:
        bak = path + BAK_SUFFIX
        if not os.path.exists(bak):
            raise
        return load(bak), "backup"
