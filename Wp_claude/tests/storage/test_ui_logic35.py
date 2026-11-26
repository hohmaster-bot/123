"""Package 35 P1: the Qt-free logic of the dialogs and the tab bar (wp/ui/dialog_logic.py) and the AC variant names
(wp/ui/params_logic.py). Numbers by hand. Run: python Wp_claude/tests/storage/test_ui_logic35.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.ui import dialog_logic as dl  # noqa: E402
from wp.ui import params_logic as pl  # noqa: E402

S = Suite("test_ui_logic35")

ROWS = [{"id": "a", "value": 10}, {"id": "b", "value": 0}, {"id": "c", "value": -2}, {"id": "d", "value": 0}]
S.case("d-zero-rows", "owner review 3: rows of value 0 hidden by default (a, c); show all = all four",
       (["a", "c"], ["a", "b", "c", "d"]))(
    lambda: ([r["id"] for r in dl.visible_rows(ROWS, False)], [r["id"] for r in dl.visible_rows(ROWS, True)]))
S.case("d-show-all-start", "owner review 3: the editor mode starts ON; outside it the saved state",
       (True, True, False, True))(
    lambda: (dl.show_all_start(False, True), dl.show_all_start(True, True), dl.show_all_start(False, False),
             dl.show_all_start(True, False)))
S.case("d-fit", "owner review 4: content 300 x 200 -> 300 x 200; dragged 500 x 400 -> 500 x 400; dragged 3000 x 2000 "
       "on a 1920 x 1040 screen -> 1920 x 1040; content larger than the screen -> clamped",
       ((300, 200), (500, 400), (1920, 1040), (1920, 1040)))(
    lambda: (dl.fit_size((300, 200), None, (1920, 1040)), dl.fit_size((300, 200), [500, 400], (1920, 1040)),
             dl.fit_size((300, 200), [3000, 2000], (1920, 1040)), dl.fit_size((2500, 1500), None, (1920, 1040))))
S.case("d-flow", "owner review 5: widths 50, 50, 50, gap 10: width 120 -> rows [0 1] [2] (50 + 10 + 50 = 110 <= 120, "
       "+ 60 = 170 > 120); width 170 -> one row (170 <= 170); width 100 -> three rows; a too wide item stays alone",
       ([[0, 1], [2]], [[0, 1, 2]], [[0], [1], [2]], [[0], [1]]))(
    lambda: (dl.flow_rows([50, 50, 50], 120, 10), dl.flow_rows([50, 50, 50], 170, 10),
             dl.flow_rows([50, 50, 50], 100, 10), dl.flow_rows([300, 50], 100, 10)))
S.case("d-pinned", "owner review 5: 13 tabs pinned to 2 rows -> 7 + 6; 3 rows -> 5 + 5 + 3; 0 = automatic; 3 tabs in 5 "
       "rows -> 3 rows of one", ([7, 6], [5, 5, 3], [], [1, 1, 1]))(
    lambda: ([len(r) for r in dl.pinned_rows(13, 2)], [len(r) for r in dl.pinned_rows(13, 3)], dl.pinned_rows(13, 0),
             [len(r) for r in dl.pinned_rows(3, 5)]))

DEF = {"cells": {"2": {"variants": ({"id": "melee", "label": "ac_variant.melee", "ac": 13},
                                    {"id": "melee_parry", "label": "ac_variant.melee_parry", "ac": 14})}}}
S.case("d-variants", "pkg 35 AC audit: the small number names its variant (with parry 14); the tooltip lists all",
       ({"melee": "ac_variant.melee", "melee_parry": "ac_variant.melee_parry"},
        (("ac_variant.melee", 13), ("ac_variant.melee_parry", 14)), {}))(
    lambda: (pl.variant_labels(DEF, "2"), pl.variant_list(DEF, "2"), pl.variant_labels(DEF, "9")))

if __name__ == "__main__":
    sys.exit(S.run())
