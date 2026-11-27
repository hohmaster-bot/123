"""Data the Classic UI needs from the core layers it must not import itself (package 35; D25: wp/ui imports only
wp.app, wp.i18n, wp.theme, wp.panels). Thin read-only helpers over a Session; nothing here changes anything.

journal_kinds() -> the journal kinds (the filter of the Journal tab) + "other".
catalog_kinds() -> every catalog kind (game-module data: nothing is hard-coded in the UI).
catalog_rows(session, kind) -> ((id, name, layer), ...) sorted by id (shipped / override / user entries).
setting_range(key) / profile_field_range(mode, field) -> (min, max) of an app setting / a profile field.
layout_warnings(session, mode) -> the layout warnings of the active profile (never refusals).
background_path(session) -> the file of the own background picture, or "" (none, unknown or missing).
"""
import json

from wp.catalog import schema as csch
from wp.catalog import store as cs
from wp.commands import journal
from wp.settings import images
from wp.settings import schema as sch
from wp.settings import screen_settings as ss


def journal_kinds():
    return tuple(journal.KIND) + (journal.OTHER,)


def catalog_kinds():
    return tuple(csch.KINDS)


def catalog_rows(session, kind):
    return tuple(sorted((e["id"], str(e.get("name") or e.get("title") or ""), layer)
                        for e, layer in cs.merged(session.catalog(kind))))


def catalog_entry(session, kind, eid):
    """One catalog entry as a plain dict (the race tab gives it to take_race / change_race), or None."""
    for e, _layer in cs.merged(session.catalog(kind)):
        if e["id"] == eid:
            return json.loads(json.dumps(e))
    return None


def race_grants(session, aid):
    """The catalog entries of the feats a race ability grants for free (package 38: Wall of Bones -> Toughness)."""
    from wp.model import races
    ch = session.character
    a = races.ability(ch, aid) if ch is not None else None
    found = [catalog_entry(session, "feats", fid) for fid in (a.get("grants_feats", ()) if a else ())]
    return [e for e in found if e]


def setting_range(key):
    k = sch.KEYS[key]
    return int(k["min"]), int(k["max"])


def profile_field_range(mode, field):
    f = sch.FIELDS[mode][field]
    return int(f["min"]), int(f["max"])


def layout_warnings(session, mode="classic"):
    return ss.layout_warnings(session.app, mode, None, None)


def background_path(session):
    image = session.setting("background_image")
    if not image:
        return ""
    path, warn = images.resolve(session.app, image, session.user_dir)
    return path if warn is None else ""
