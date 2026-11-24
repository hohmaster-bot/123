"""AC by cell with variants (RULES/ac_zones.md; packages 23 D, 24 B). Cells and variants are DATA
(wp/rules_data/ac_zones.json); the cell rules are a ZoneRules value built from the rule constants of group ac_zones
and the effects of the character (model/ac_zones_view.py).

cell_variants(inp, cell, shields, rules, parry=None) -> {"variants": [...], "full", "parry", "shield", "dex_loss"}:
- shields: ((shield_type, side, value), ...) of the held shields; a shield counts in the cells its type covers
  (LEFT hand; the right hand mirrors 1<->3, 4<->6, 7<->9), plus / minus the cells of shield_cells effects (absolute
  cell ids); two shields: the larger value per cell (shield bonuses of one type do not add).
- Dex and dodge are lost in the Dex-loss cells (positive parts only, like flat-footed).
- a variant: {"id", "label", "ac", "applies_when" (melee | ranged), "chance_pct" (None, or the chance of this
  alternate value), "parry" (uses the parry layer)}. melee = full AC; melee_parry only in parry cells; ranged: no
  parry while ranged_ignores_parry, the shield while ranged_keeps_shield. In a Dex-loss cell with a cancel chance
  > 0 every variant gets an alternate "<id>_dex" WITH Dex and dodge and that chance. Nothing is rolled.
- parry: {cell: parry layer value} for cell-scoped parry effects (None = inp.parry everywhere).
Cell 2 reproduces FRONT and PARRY, cell 6 FLANK (no shield), cell 8 FLAT_FOOTED (no Dex, no shield).
"""
import io
import json
import os
from dataclasses import dataclass, replace
from typing import Any, FrozenSet

from wp.core import ac as acm
from wp.rules_data import rules as rd

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rules_data", "ac_zones.json")
LEFT = "left"
RIGHT = "right"
MELEE = "melee"
RANGED = "ranged"


def _load(path=PATH):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


TABLE = _load()
CELLS = tuple(sorted(TABLE["cells"], key=int))
VARIANTS = tuple(TABLE["variants"])


@dataclass(frozen=True)
class ZoneRules:
    parry_cells: FrozenSet[str]
    dex_loss_cells: FrozenSet[str]
    shield_cells: Any                  # {shield type: cells of a LEFT-hand shield}
    shield_add: FrozenSet[str] = frozenset()
    shield_remove: FrozenSet[str] = frozenset()
    ranged_ignores_parry: bool = True
    ranged_keeps_shield: bool = True
    dex_loss_chance_pct: int = 0


def cellset(values):
    return frozenset(str(c) for c in values)


def default_rules():
    """The rules from the constants of the active scope (rules.using(ch)) or the table defaults."""
    return ZoneRules(cellset(rd.ref("ac_zones.parry_cells").value), cellset(rd.ref("ac_zones.dex_loss_cells").value),
                     {k: cellset(v) for k, v in rd.ref("ac_zones.shield_cells").value.items()},
                     ranged_ignores_parry=bool(rd.ref("ac_zones.ranged_ignores_parry").value),
                     ranged_keeps_shield=bool(rd.ref("ac_zones.ranged_keeps_shield").value),
                     dex_loss_chance_pct=int(rd.ref("ac_zones.dex_loss_chance_pct").value))


def covered(cell, shield_type="", shield_hand=LEFT, rules=None):
    rules = rules or default_rules()
    cell = str(cell)
    if cell in rules.shield_remove:
        return False
    if cell in rules.shield_add:
        return True
    cells = rules.shield_cells.get(shield_type, rules.shield_cells.get("", frozenset()))
    c = str(TABLE["mirror"][cell]) if shield_hand == RIGHT else cell
    return c in cells


def shield_value(cell, shields, rules):
    return max([v for t, side, v in shields if v > 0 and covered(cell, t, side, rules)] or [0])


def _ac(inp, cell, use_parry, use_shield, lose_dex):
    return acm.BASE_AC + sum(v for _, v in acm.layer_parts(inp, use_parry=use_parry, use_shield=use_shield,
                                                            lose_dex=lose_dex, cell=cell))


def _shield_on(inp, cell, shields, rules):
    """Unscoped shield bonuses count where a held shield covers the cell; with no shield held, in the cells of the
    default ("" type) coverage of the default side (assumption Q162)."""
    if not inp.shield_enabled:
        return False
    if any(v > 0 for _, _, v in shields):
        return shield_value(cell, shields, rules) > 0
    return covered(cell, "", rd.ref("hands.default_shield_side").value, rules)


def cell_variants(inp, cell, shields=(), rules=None, parry=None):
    rules = rules or default_rules()
    cell = str(cell)
    cinp = replace(inp, shield=shield_value(cell, shields, rules),
                   parry=parry.get(cell, inp.parry) if parry else inp.parry)
    on = _shield_on(cinp, cell, shields, rules)
    lose = cell in rules.dex_loss_cells
    can_parry = cell in rules.parry_cells
    chance = int(rules.dex_loss_chance_pct) if lose else 0   # clamped to 0..100 by the model
    out = []
    for v in VARIANTS:
        ranged = bool(v.get("ranged"))
        use_parry = can_parry and (bool(v.get("parry")) or (ranged and not rules.ranged_ignores_parry))
        if v.get("parry") and not can_parry:
            continue
        use_shield = on and (not ranged or rules.ranged_keeps_shield)
        when = RANGED if ranged else MELEE
        out.append({"id": v["id"], "label": v["label"], "ac": _ac(cinp, cell, use_parry, use_shield, lose),
                    "applies_when": when, "chance_pct": None, "parry": use_parry})
        if chance > 0:
            out.append({"id": v["id"] + TABLE["chance_suffix"], "label": TABLE["chance_label"],
                        "ac": _ac(cinp, cell, use_parry, use_shield, False), "applies_when": when,
                        "chance_pct": chance, "parry": use_parry})
    by_id = {x["id"]: x["ac"] for x in out}
    return {"variants": tuple(out), "full": by_id.get(VARIANTS[0]["id"]),
            "parry": by_id.get("melee_parry"), "shield": on and cinp.shield > 0, "dex_loss": lose}


def cell_ac(inp, cell, shield_type="", shield_hand=LEFT):
    """{"full", "parry"} of one cell for one shield of the input (package 23 API)."""
    c = cell_variants(inp, cell, ((shield_type, shield_hand, inp.shield),))
    return {"full": c["full"], "parry": c["parry"]}


def all_cells(inp, shields=(), rules=None, parry=None):
    return {c: cell_variants(inp, c, shields, rules, parry) for c in CELLS}
