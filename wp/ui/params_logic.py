"""The Parameters and AC blocks without Qt (package 34): pure functions over the views, tested without PySide6.

signed(n) -> "+4" / "-1" / "0" (a bonus); number_of(view_sheet, view_items, nid) -> (text, values or None, style):
    the text of one Parameters cell from the views (attack_melee / attack_ranged from the sheet view, initiative /
    cmb / cmd / fort / ref / will from sheet.stats, load from items.load); style "overload" for the overloaded load.
load_category(carried, light_max, heavy_max) -> light | heavy | overload (RULES/gear.md "Load display": 0..light =
    light, above light up to the maximum = load (heavy), above the maximum = overload).
ac_cells(defense) -> {cell: (total, label key, shield)}; the shield cells come from the defense view.
cells_of(item, default) -> the rows of the Parameters block (the layout item's own "cells" or the default).
No game rule is computed here (the core gives every number; load_category mirrors the core for the UI tests).
"""
SIGNED = ("attack_melee", "attack_ranged", "initiative", "cmb", "fort", "ref", "will")
STATS = ("initiative", "cmb", "cmd", "fort", "ref", "will")
LIGHT, HEAVY, OVER = "light", "heavy", "overload"


def signed(n):
    n = int(n)
    return "%+d" % n if n else "0"


def load_category(carried, light_max, heavy_max):
    if carried <= light_max:
        return LIGHT
    if carried <= heavy_max:
        return HEAVY
    return OVER


def number_of(sheet, items, nid):
    """(text, style) of one cell: style "" or "overload"; the load text is (key, values) for the i18n call."""
    if nid in ("attack_melee", "attack_ranged"):
        return signed(sheet[nid]["total"]), ""
    if nid in STATS:
        total = sheet["stats"][nid].total
        return (signed(total) if nid in SIGNED else str(total)), ""
    if nid == "load":
        ld = items["load"]
        cat = load_category(ld["carried_l"], ld["light_max_l"], ld["heavy_max_l"])
        return ("load.of", (ld["carried_l"], ld["heavy_max_l"]), "load." + cat), (OVER if cat == OVER else "")
    raise KeyError("no parameter %r" % (nid,))


def cells_of(item, default):
    cells = (item or {}).get("cells")
    return [list(r) for r in (cells or default)]


def variant(cell, vid):
    """The AC of one variant (melee / melee_parry / ranged) of a cell of the defense view; the full AC otherwise."""
    return next((v["ac"] for v in cell.get("variants", ()) if v["id"] == vid), cell.get("full"))


def variant_labels(defense, cell):
    """{variant id: its label key} of one cell of the defense view (package 35: the small number is named)."""
    return {v["id"]: v["label"] for v in dict(defense.get("cells", {})).get(cell, {}).get("variants", ())}


def variant_list(defense, cell):
    """((label key, AC), ...) of every variant of one cell (the cell tooltip; the Sources dialog shows the same)."""
    return tuple((v["label"], v["ac"]) for v in dict(defense.get("cells", {})).get(cell, {}).get("variants", ()))


def ac_cells(defense, grid, you):
    """{cell: (primary AC, secondary AC, label key, shield counts there)} for the grid cells except "you"; primary /
    secondary = the variants of the app setting display (defense["display"])."""
    out = {}
    cells = dict(defense.get("cells", {}))
    disp = dict(defense.get("display", {}))
    labels = dict(defense.get("cell_labels", {}))
    for row in grid:
        for c in row:
            if c != you and c in cells:
                d = cells[c]
                out[c] = (variant(d, disp.get("primary")), variant(d, disp.get("secondary")),
                          labels.get(c, "ac_cell." + c), bool(d.get("shield")))
    return out
