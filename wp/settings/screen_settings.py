"""One-time hints, layout safety and the default profile (package 31; UI_WISHES.md "Classic screen v2" 13, 14).

Hints: every explanatory hint has an id (data: wp/settings/data/hints.json; texts i18n hint.<id>); it is shown until
the player ticks "Understood!" (hint_dismiss); app settings hints_seen (the dismissed ids) and hints_off (no hint at
all); hints_reset shows every hint again. hint_visible / hints_view tell the UI what to show.
Layout warnings (never refusals): a block under its minimum size (the registry min_size), all HP controls hidden (no
visible resources panel and no cell / element showing resource:hp), a block outside the window. profile_reset puts
the shipped default profile back (always available; the profile keeps its id and name).
"""
import io
import json
import os
from dataclasses import replace

from wp.commands.base import CommandError
from wp.panels import registry
from wp.settings import settings_cmds as sc
from wp.settings import store as st

HINTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "hints.json")
UNDER_MINIMUM = "block_under_minimum"
HP_HIDDEN = "hp_controls_hidden"
OUTSIDE = "block_outside_window"
HP_SOURCE = "resource:hp"
HP_PANEL = "resources"


def _hints():
    with io.open(HINTS_PATH, encoding="utf-8") as f:
        return tuple(json.load(f)["hints"])


HINTS = _hints()


def hint_visible(app, hint_id):
    return not st.get(app, "hints_off") and hint_id not in st.get(app, "hints_seen")


def hints_view(app):
    """((hint id, text key, visible), ...) of every known hint."""
    return tuple((h, "hint." + h, hint_visible(app, h)) for h in HINTS)


@sc.settings_command
def hint_dismiss(app, hint_id=""):
    """The player ticked "Understood!" (the ru text in ru.json): the hint is not shown again."""
    if hint_id not in HINTS:
        raise CommandError("no hint %r" % (hint_id,), "not_found", values=("hints", hint_id))
    seen = tuple(st.get(app, "hints_seen"))
    if hint_id in seen:
        return sc.SettingsResult(app, {"id": hint_id})
    return sc.settings_dispatch(app, "settings_set", key="hints_seen", value=list(seen) + [hint_id])


@sc.settings_command
def hints_reset(app):
    """"Show all hints again"."""
    return sc.settings_dispatch(app, "settings_set", key="hints_seen", value=[])


def _rect(item):
    pos, size = item.get("position") or (0, 0), item.get("size")
    return (int(pos[0]), int(pos[1]), int(size[0]), int(size[1])) if size else None


def layout_warnings(app, mode="classic", pid=None, window=None):
    """((warning id, item id, panel id), ...) of a profile; window = (width, height) of the screen area or None."""
    prof = sc._profile(app, mode, pid)
    out = []
    items = [i for coll in ("panels", "cells", "elements") for i in prof.get(coll, ())]
    for item in prof.get("panels", ()):
        r, pnl = _rect(item), item.get("panel", "")
        if r and registry.known(pnl):
            mw, mh = registry.get(pnl).get("min_size", (0, 0))
            if r[2] < mw or r[3] < mh:
                out.append((UNDER_MINIMUM, item.get("id", ""), pnl))
    visible = [i for i in items if i.get("visible", True)]
    if not any(i.get("panel") == HP_PANEL or i.get("source") == HP_SOURCE for i in visible):
        out.append((HP_HIDDEN, "", HP_PANEL))
    if window is not None:
        for item in visible:
            r = _rect(item)
            if r and (r[0] < 0 or r[1] < 0 or r[0] + r[2] > window[0] or r[1] + r[3] > window[1]):
                out.append((OUTSIDE, item.get("id", ""), item.get("panel", "")))
    return tuple(out)


@sc.settings_command
def profile_reset(app, mode="", pid=""):
    """The shipped default profile of the mode back into this profile (its id and name stay)."""
    prof = sc._profile(app, mode, pid or None)
    shipped = st._shipped_profiles()[mode][0]
    data = dict(st._plain(shipped), id=prof["id"], name=prof.get("name", shipped.get("name", "")))
    if prof.get("notes"):              # package 38: the owner's "!" notes survive a reset of the layout
        data["notes"] = st._plain(prof["notes"])
    new = sc._with_profile(app, mode, st.freeze(data))
    return sc.SettingsResult(replace(new), {"id": prof["id"]})
