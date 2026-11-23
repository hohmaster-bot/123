"""AC by cell (RULES/ac_zones.md, the owner's draft; package 23 D). The table is DATA: wp/rules_data/ac_zones.json.

cell_ac(inp, cell, shield_type="", shield_hand="left") -> {"full": AC, "parry": AC or None}:
- full: the ladder of ac.layer_parts with the cell's flags: Dex and dodge only where dex_dodge is true (cell 8, the
  back, loses the positive parts like flat-footed); the shield bonus only in the cells its type covers (left hand;
  the right hand mirrors 1<->3, 4<->6, 7<->9) and while the shield is enabled; no parry.
- parry: the same with the armor layer = max(armor, parry), only in the parry cells (1, 2, 3); None elsewhere.
Cell 2 reproduces the FRONT and PARRY modes, cell 6 the FLANK mode (shield dropped), cell 8 FLAT_FOOTED (no shield).
"""
import io
import json
import os

from wp.core import ac as acm

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rules_data", "ac_zones.json")
LEFT = "left"
RIGHT = "right"


def _load(path=PATH):
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d


TABLE = _load()
CELLS = tuple(sorted(TABLE["cells"], key=int))


def covered(cell, shield_type="", shield_hand=LEFT):
    cells = TABLE["shield_cells"].get(shield_type, TABLE["shield_cells"][""])
    c = int(cell)
    if shield_hand == RIGHT:
        c = int(TABLE["mirror"][str(c)])
    return c in cells


def cell_ac(inp, cell, shield_type="", shield_hand=LEFT):
    spec = TABLE["cells"][str(cell)]
    use_shield = inp.shield_enabled and inp.shield > 0 and covered(cell, shield_type, shield_hand)
    lose_dex = not spec["dex_dodge"]
    full = acm.BASE_AC + sum(v for _, v in acm.layer_parts(inp, use_shield=use_shield, lose_dex=lose_dex))
    parry = None
    if spec["parry"]:
        parry = acm.BASE_AC + sum(v for _, v in acm.layer_parts(inp, use_parry=True, use_shield=use_shield,
                                                                lose_dex=lose_dex))
    return {"full": full, "parry": parry}


def all_cells(inp, shield_type="", shield_hand=LEFT):
    return {c: cell_ac(inp, c, shield_type, shield_hand) for c in CELLS}
