"""AC cells of a character (packages 23 D, 24 B; RULES/ac_zones.md "Variants and settings").

rules(ch): the cell rules = the character's rule constants of group ac_zones (defaults in constants.json, changed by
set_rule_setting) changed by effects of active sources:
- parry_cells / shield_cells / dex_loss_cells: effect.cells are added (value >= 0) or removed (value < 0); removals
  win over additions (assumption Q163). shield_cells effects name absolute cells (they are not mirrored).
- dex_loss_chance_pct: the constant + the stacked effects of that target, clamped to 0..100.
shields(ch): every held shield with its hand (model/hands.py) and its shield value.
parry_by_cell(ch): the parry layer per cell = the unscoped parry + parry effects scoped to that cell (typed stacking).
cells(ch): {cell: variants...}; display(app): the display hints (app settings: primary, secondary, slash list).
"""
from wp.core import ac as acm
from wp.core import ac_zones as acz
from wp.core import bonuses as bo
from wp.model import blocks as blk
from wp.model import derived_view as dv
from wp.model import hands as hd
from wp.model import records as rec
from wp.model import sheet_targets as stg
from wp.rules_data import rules as rd

SET_TARGETS = {"parry_cells": "ac_zones.parry_cells", "dex_loss_cells": "ac_zones.dex_loss_cells"}
SHIELD_CELLS = "shield_cells"
CHANCE = "dex_loss_chance_pct"
PARRY = "parry"
PCT_MAX = 100                          # a percent


def _changes(ch, target):
    add, remove = set(), set()
    ctx = dv.context(ch)
    for _, e in blk.active_effects(ch):
        if e.target == target and e.cells:
            (remove if e.resolve(ctx) < 0 else add).update(str(c) for c in e.cells)
    return add, remove


def rules(ch):
    sets = {}
    for target, cid in SET_TARGETS.items():
        add, remove = _changes(ch, target)
        sets[target] = frozenset((acz.cellset(rd.const(cid, ch)) | add) - remove)
    add, remove = _changes(ch, SHIELD_CELLS)
    chance = int(rd.const("ac_zones.dex_loss_chance_pct", ch)) + stg.value(ch, CHANCE)
    return acz.ZoneRules(sets["parry_cells"], sets["dex_loss_cells"],
                         {k: acz.cellset(v) for k, v in rd.const("ac_zones.shield_cells", ch).items()},
                         frozenset(add - remove), frozenset(remove),
                         ranged_ignores_parry=bool(rd.const("ac_zones.ranged_ignores_parry", ch)),
                         ranged_keeps_shield=bool(rd.const("ac_zones.ranged_keeps_shield", ch)),
                         dex_loss_chance_pct=max(0, min(PCT_MAX, chance)))


def shield_type(ch):
    return next((it.shield_type for it in ch.items if it.in_hands and rec.is_shield(it)), "")


def shields(ch, hand=None):
    """((shield_type, side, value), ...) of the held shields; hand forces one side for all (tests, previews)."""
    sides = hd.sides(ch)
    out = []
    for it in ch.items:
        if it.in_hands and (rec.is_shield(it) or it.shield):
            out.append((it.shield_type, hand or sides.get(it.iid) or hd.LEFT, dv.shield_value(it, dv.picks(ch, it))))
    return tuple(out)


def parry_by_cell(ch, base):
    """{cell: parry} where a cell-scoped parry effect exists; other cells use the unscoped value."""
    scoped = [b for b in stg.sheet_bonuses(ch) if b.target == PARRY and b.cells]
    if not scoped:
        return None
    unscoped = [b for b in stg.sheet_bonuses(ch) if b.target == PARRY and not b.cells]
    plain = bo.stack(blk.unblocked(ch, unscoped, PARRY))
    out = {}
    for c in acz.CELLS:
        here = unscoped + [b for b in scoped if c in b.cells]
        out[c] = base - plain + bo.stack(blk.unblocked(ch, here, PARRY))
    return out


def cells(ch, shield_enabled=True, hand=None):
    inp = dv.ac_input(ch, shield_enabled=shield_enabled)
    return acz.all_cells(inp, shields(ch, hand), rules(ch), parry_by_cell(ch, inp.parry))


DISPLAY_KEYS = {"primary": "ac_cell_primary", "secondary": "ac_cell_secondary", "slash": "ac_cell_slash"}


def display(app=None):
    """Display hints for the UI (app settings; package 24 B1): the big number, the small one, the slash list."""
    from wp.settings import schema as sch
    from wp.settings import store as st
    out = {}
    for k, key in DISPLAY_KEYS.items():
        out[k] = st.get(app, key) if app is not None else sch.KEYS[key]["default"]
        if isinstance(out[k], list):
            out[k] = tuple(out[k])
    return out


def mode_cells(ch):
    """The cell of each old AC mode (presets of ac_zones.json). Owner (package 27, review 5 F15): flank = the cell of
    the side WITHOUT a shield: cell 6, or its mirror 4 when every held shield is in the right hand."""
    out = {m: str(c) for m, c in acm.MODE_CELL.items()}
    held = shields(ch)
    if held and all(side == hd.RIGHT for _, side, _ in held):
        out[acm.FLANK] = str(acz.TABLE["mirror"][out[acm.FLANK]])
    return out


def modes(ch, the_cells=None):
    """The old modes as their cells show them (owner F15: one number on screen): front, flank and flat_footed = the
    melee number of their cell, parry = the parry number of its cell; touch keeps its own ladder (no cell)."""
    out = dict(acm.all_modes(dv.ac_input(ch)))
    the_cells = the_cells or cells(ch)
    mc = mode_cells(ch)
    for mode in (acm.FRONT, acm.FLANK, acm.FLAT_FOOTED):
        out[mode] = the_cells[mc[mode]]["full"]
    if the_cells[mc[acm.PARRY]]["parry"] is not None:
        out[acm.PARRY] = the_cells[mc[acm.PARRY]]["parry"]
    return out


def view(ch, app=None):
    c = cells(ch)
    return {"cells": c, "display": display(app), "rules": rules(ch), "modes": modes(ch, c)}
