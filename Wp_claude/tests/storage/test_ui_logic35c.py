"""Package 35 P4: the rows of the content tabs without Qt (wp/ui/tab_logic.py) and the UI data helpers
(wp/app/ui_data.py). The rows only arrange view values (no game number is computed in the UI).
Run: python Wp_claude/tests/storage/test_ui_logic35c.py"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import ui_data  # noqa: E402
from wp.app import views as vw  # noqa: E402
from wp.app.session import Session  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.injuries import Injury  # noqa: E402
from wp.model.character import Character, Item  # noqa: E402
from wp.ui import tab_logic as tl  # noqa: E402

S = Suite("test_ui_logic35c")
TMP = tempfile.mkdtemp(prefix="wp_l35c_")
INJ = Injury("cut", "light", 2, False, Pool(1, 2), "cut")
HERO = Character(trauma=4, injuries=(INJ,), training=150, comfort_current=3,
                 items=(Item("ring", "ring", weight_l=1, qualification_n=3), Item("rope", "rope", weight_l=10)))

S.case("r-injuries", "injuries.md: one row per injury (id, name, severity, heal rating, permanent, charges 1/2)",
       [("cut", "cut", "light", 2, False, "1/2")])(lambda: tl.injury_rows(vw.VIEWS["injuries"](HERO)))
S.case("r-items", "gear.md: the items with weight, quantity, worn, in hands, state (from the items view)",
       [("ring", "ring", 1, 1, False, False, "ok"), ("rope", "rope", 10, 1, False, False, "ok")])(
    lambda: tl.item_rows(HERO.items, vw.VIEWS["items"](HERO)["items"]))
S.case("r-qualification", "gear.md: only the items that need a qualification: the ring, N 3, not bought",
       [("ring", "ring", 3, False)])(lambda: tl.qualification_rows(HERO.items))
S.case("r-training", "training view: training 150, level 1, comfort 3 of its max (the numbers come from the view)",
       (150, 1, True))(lambda: (lambda t: (t[0], t[1], t[4].startswith("3/")))(
           tl.training_summary(vw.VIEWS["training"](HERO))))
S.case("r-empty", "pkg 35: a hero without skills / feats / drives gives empty rows (the empty state)", ([], [], []))(
    lambda: (tl.skill_rows(vw.VIEWS["skills"](HERO)), tl.feat_rows(vw.VIEWS["sheet"](HERO)),
             tl.drive_rows(vw.VIEWS["notebook"](HERO))))
S.case("r-heavy", "UI_WISHES 9: the heavy tabs get the expand button", ("skills", "inventory", "training", "catalogs"))(
    lambda: tl.HEAVY)


def _catalogs():
    s = Session(os.path.join(TMP, "ch"), os.path.join(TMP, "user"))
    rows = ui_data.catalog_rows(s, "feats")
    return "feats" in ui_data.catalog_kinds(), len(rows), rows[0][2], ui_data.setting_range("font_size"), \
        ui_data.profile_field_range("classic", "quick_cells"), ui_data.background_path(s)


S.case("r-ui-data", "D25: the catalog browser reads the data (3 shipped feats); setting ranges 6-48, quick cells "
       "4-16; no background picture by default", (True, 3, "shipped", (6, 48), (4, 16), ""))(_catalogs)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
