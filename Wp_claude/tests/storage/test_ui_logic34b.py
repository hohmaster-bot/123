"""Package 34 part 2: the statuses block and the combat tab logic WITHOUT Qt (wp/ui/combat_logic.py). Numbers by hand.
Run: python Wp_claude/tests/storage/test_ui_logic34b.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import views as vw  # noqa: E402
from wp.commands import dispatch  # noqa: E402
from wp.core.effects import Status  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.ui import combat_logic as cl  # noqa: E402

S = Suite("test_ui_logic34b")
CH = Character(statuses=(Status("Rage", sid="rage", duration="ticks", remaining=3, active=True),
                         Status("Bless", sid="bless", active=False, favorite=True),
                         Status("Hidden", sid="hid", active=True, hidden=True, favorite=True)))
ENTRIES = vw.VIEWS["statuses"](CH)["container"].entries


def ids(mode):
    return [e.eid for e in cl.filter_entries(ENTRIES, mode)]


S.case("f-filters", "UI_WISHES 8: All = every entry; Active = rage (hidden left out); Favorites = bless (hidden out)",
       (["rage", "bless", "hid"], ["rage"], ["bless"]))(lambda: (ids("all"), ids("active"), ids("favorites")))
S.case("f-text", "buffs.md: rage 3 rounds left; bless inactive -> off; an endless active buff -> no end",
       (("statuses.rounds", (3,)), ("statuses.off", ()), ("statuses.infinite", ())))(
    lambda: tuple(cl.entry_text(e) for e in ENTRIES))


def _squares(spent):
    c = dispatch(Character(), "spend_actions", n=spent).state if spent else Character()
    return vw.VIEWS["combat"](c)["action_squares"]


S.case("q-smallest", "combat.md (owner): 3 actions; the next spend takes 1, then 2, then 3; all spent -> None",
       (1, 2, 3, None))(lambda: tuple(cl.next_square(_squares(n)) for n in (0, 1, 2, 3)))
S.case("q-core-order", "combat.md: after spending 2 the squares 1 and 2 are spent (smallest first), 3 is free",
       ((1, True), (2, True), (3, False)))(lambda: _squares(2))
S.case("g-grid", "UI_WISHES 9: 8 cells in 4 columns -> 2 rows; 3 -> 4 (minimum); 20 -> 16 (maximum); 0 columns -> 1; "
       "columns above the cells -> the cells", ((8, 4, 2), (4, 4, 1), (16, 4, 4), (8, 1, 8), (4, 4, 1)))(
    lambda: (cl.grid_shape(8, 4, 4, 16), cl.grid_shape(3, 4, 4, 16), cl.grid_shape(20, 4, 4, 16),
             cl.grid_shape(8, 0, 4, 16), cl.grid_shape(4, 9, 4, 16)))
S.case("g-tabs", "UI_WISHES 9: the layout item's own tabs win; else the data list", (["combat", "rest"], ["a"]))(
    lambda: (cl.tab_list({"tabs": ["combat", "rest"]}, ["a"]), cl.tab_list({}, ["a"])))

if __name__ == "__main__":
    sys.exit(S.run())
