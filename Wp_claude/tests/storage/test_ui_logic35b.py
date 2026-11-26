"""Package 35 P2: the bottom strip and the journal filter without Qt (wp/ui/strip_logic.py). Numbers by hand.
Run: python Wp_claude/tests/storage/test_ui_logic35b.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.model.character import LogEntry  # noqa: E402
from wp.ui import strip_logic as sl  # noqa: E402

S = Suite("test_ui_logic35b")
DATA = {"bottom_strip": ["ot", "pain", "morale", "speed", "load"], "second_strip": ["temp_hp", "attention"]}
RES = {"ot": 2, "pain": 1}
OUT = {"in_combat": False, "morale_scale": 4}
IN = {"in_combat": True, "morale_scale": 4}
SHEET = {"speed": 30}
ITEMS = {"load": {"carried_l": 40, "light_max_l": 86, "heavy_max_l": 129}}
HEAVY = {"load": {"carried_l": 100, "light_max_l": 86, "heavy_max_l": 129}}
OVER = {"load": {"carried_l": 130, "light_max_l": 86, "heavy_max_l": 129}}

S.case("b-strips", "UI_WISHES 10: the main strip from data; the profile strips add a second one (empty by default)",
       ([["ot", "pain", "morale", "speed", "load"]], [["ot", "pain", "morale", "speed", "load"], ["temp_hp"]]))(
    lambda: (sl.strips({"strips": []}, DATA), sl.strips({"strips": [["temp_hp"], []]}, DATA)))
S.case("b-cells", "UI_WISHES 10: OT 2, pain 1, morale hidden out of combat and +4 in combat (+6 with a sources total 6), "
       "speed 30", (("2", "", ""), ("1", "", ""), None, ("+4", "", ""), ("30", "", ""), ("+6", "", "")))(
    lambda: (sl.cell("ot", RES, OUT, SHEET, ITEMS), sl.cell("pain", RES, OUT, SHEET, ITEMS),
             sl.cell("morale", RES, OUT, SHEET, ITEMS), sl.cell("morale", RES, IN, SHEET, ITEMS),
             sl.cell("speed", RES, OUT, SHEET, ITEMS), sl.cell("morale", RES, IN, SHEET, ITEMS, {"morale": 6})))
S.case("b-load", "gear.md: 40 of 129 light (limits 86 / 129); 100 -> load; 130 -> overload in the danger style",
       ((("load.of", (40, 129)), ("load.limits", (86, 129), "load.light"), ""), "load.heavy", ("load.overload", "overload")))(
    lambda: (sl.cell("load", RES, OUT, SHEET, ITEMS), sl.cell("load", RES, OUT, SHEET, HEAVY)[1][2],
             (sl.cell("load", RES, OUT, SHEET, OVER)[1][2], sl.cell("load", RES, OUT, SHEET, OVER)[2])))
S.case("b-sources", "pkg 35: every strip cell opens its sources number; other sheet numbers show their sources total",
       (["ot", "pain", "morale", "speed", "load"], sl.OTHER, None))(
    lambda: ([sl.number_of(n) for n in DATA["bottom_strip"]], sl.cell("attention", RES, OUT, SHEET, ITEMS),
             sl.cell("unknown", RES, OUT, SHEET, ITEMS)))

LOG = (LogEntry(seq=1, command="take_damage", kind="damage", params={"amount": 5}, result={"hp": 11}),
       LogEntry(seq=2, command="add_status", kind="status", params={"status": "rage"}),
       LogEntry(seq=3, command="journal_note", kind="note", params={"text": "Met the Duke"}),
       LogEntry(seq=4, command="take_damage", kind="damage", params={"amount": 2}))
S.case("j-filter", "pkg 35 journal: newest first; kind damage -> 4, 1; text 'duke' -> 3 (case-insensitive); text "
       "'rage' -> 2; both filters together", ([4, 3, 2, 1], [4, 1], [3], [2], [1]))(
    lambda: ([e.seq for e in sl.journal_lines(LOG)], [e.seq for e in sl.journal_lines(LOG, "damage")],
             [e.seq for e in sl.journal_lines(LOG, "", "duke")], [e.seq for e in sl.journal_lines(LOG, "", "RAGE")],
             [e.seq for e in sl.journal_lines(LOG, "damage", "amount=5")]))
S.case("j-text", "pkg 35 journal: a line names seq, command, params and result (ids and numbers only)",
       "1. take_damage (amount=5) -> hp=11")(lambda: sl.line_text(LOG[0]))

if __name__ == "__main__":
    sys.exit(S.run())
