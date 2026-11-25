"""Panel registry as data (package 21, D24): wp/panels/data/panels.json. No Qt here.

PANELS: {id: panel} with every field filled (the "defaults" block of the file for what a panel does not give):
id, title (i18n key panel.<id>), description (panel.<id>.desc), modes (classic / lite), defaults per mode (dock,
position, size), min_size, resizable, cell_capable, requires, icon (icon id), source (the model view it shows),
described (False: the docs only name it).
Views: list_panels(mode), get(pid), check_profile(profile, mode) -> warnings, warnings(app) for every stored profile.
BLOCKS (package 32): {id: block} = the layout blocks of the Classic screen v2 (the "blocks" list of the file): title,
description, min_size, defaults like a panel, modes classic only, and reads (the registry views the block shows).
A classic layout item may name a panel or a block; get(pid) and known(pid) know both; reads(pid) = a block's views or
[pid] for a panel.
check_item(collection, item, mode) -> None or (reason, params): the layout commands refuse unknown panels at set time.
"""
import copy
import io
import json
import os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "panels.json")
MODES = ("classic", "lite")
UNKNOWN_PANEL = "unknown_panel"
PANEL_NOT_IN_MODE = "panel_not_in_mode"
PANEL_NEEDED = "panel_needed"


def _load(path=PATH):
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    base = d["defaults"]
    out = {}
    for p in d["panels"]:
        full = copy.deepcopy(base)
        full.update(copy.deepcopy(p))
        full.setdefault("title", "panel." + p["id"])
        full.setdefault("description", "panel.%s.desc" % p["id"])
        full.setdefault("icon", "panel." + p["id"])
        full.setdefault("source", "")
        for m in full["modes"]:
            full["defaults"].setdefault(m, copy.deepcopy(base["defaults"]["classic"]))
        if p["id"] in out:
            raise ValueError("duplicate panel id %r" % p["id"])
        out[p["id"]] = full
    return out


PANELS = _load()


def _load_blocks(path=PATH):
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    base = d["defaults"]
    out = {}
    for b in d.get("blocks", ()):
        if b["id"] in out or b["id"] in PANELS:
            raise ValueError("duplicate block id %r" % b["id"])
        full = copy.deepcopy(base)
        full.update(copy.deepcopy(b))
        full["modes"] = ["classic"]
        full.setdefault("title", "panel." + b["id"])
        full.setdefault("description", "panel.%s.desc" % b["id"])
        full.setdefault("icon", "panel." + b["id"])
        full.setdefault("reads", [])
        full["block"] = True
        out[b["id"]] = full
    return out


BLOCKS = _load_blocks()


def known(pid):
    return pid in PANELS or pid in BLOCKS


def reads(pid):
    """The registry views a layout item shows (package 32): a block's reads, or the panel's own view."""
    return tuple(BLOCKS[pid]["reads"]) if pid in BLOCKS else (pid,)


def get(pid):
    if pid in BLOCKS:
        return BLOCKS[pid]
    if pid not in PANELS:
        raise KeyError("no panel %r" % (pid,))
    return PANELS[pid]


def list_panels(mode):
    return tuple(p for p in PANELS.values() if mode in p["modes"])


def _ref(pid, mode):
    if pid in BLOCKS:
        return None if mode in BLOCKS[pid]["modes"] else (PANEL_NOT_IN_MODE, {"values": (pid, mode), "panel": pid,
                                                                               "mode": mode})
    if pid not in PANELS:
        return UNKNOWN_PANEL, {"values": (pid,), "panel": pid}
    if mode not in PANELS[pid]["modes"]:
        return PANEL_NOT_IN_MODE, {"values": (pid, mode), "panel": pid, "mode": mode}
    return None


def check_item(collection, item, mode):
    """A classic panel item must name a registry panel (field "panel"); a cell or element MAY name one."""
    pid = item.get("panel")
    if collection == "panels" and not pid:
        return PANEL_NEEDED, {"values": ("panel",)}
    return _ref(pid, mode) if pid else None


def check_profile(profile, mode):
    """Warnings (never refusals) for a stored profile: (reason, item id, panel id)."""
    out = []
    for coll in ("panels", "cells", "elements"):
        for item in profile.get(coll, ()):
            pid = item.get("panel")
            if pid:
                bad = _ref(pid, mode)
                if bad:
                    out.append((bad[0], item.get("id", ""), pid))
            elif coll == "panels":
                out.append((PANEL_NEEDED, item.get("id", ""), ""))
    return tuple(out)


def warnings(app):
    """{(mode, profile id): warnings} for every stored profile with a problem (used after loading the settings)."""
    out = {}
    for mode in MODES:
        for p in app.profiles[mode]:
            w = check_profile(p, mode)
            if w:
                out[(mode, p["id"])] = w
    return out
