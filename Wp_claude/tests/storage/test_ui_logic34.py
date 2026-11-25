"""Package 34: the Parameters / AC block logic WITHOUT Qt (wp/ui/params_logic.py). Numbers by hand.
Run: python Wp_claude/tests/storage/test_ui_logic34.py"""
import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.core.pain import PainEntry  # noqa: E402
from wp.app import views as vw  # noqa: E402
from wp.model.character import ABILITIES, Ability, Character, Item  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402
from wp.ui import params_logic as pl  # noqa: E402

S = Suite("test_ui_logic34")
GRID = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]


def hero(**kw):
    base = {"str": 14, "dex": 20}
    return Character(bab=2, abilities={a: Ability(base=base.get(a, 10)) for a in ABILITIES}, **kw)


def views(ch):
    with rd.using(ch):
        return vw.VIEWS["sheet"](ch), vw.VIEWS["items"](ch), vw.VIEWS["defense"](ch)


def cell(ch, nid):
    sh, it, _ = views(ch)
    return pl.number_of(sh, it, nid)


S.case("p-signed", "pkg 34: +4, -1, 0", ("+4", "-1", "0"))(lambda: (pl.signed(4), pl.signed(-1), pl.signed(0)))
S.case("p-attack", "combat.md: melee +4, ranged +7; pain 1 -> +3 / +6; morale 4 only in combat: +4 / +6",
       (("+4", ""), ("+7", ""), ("+3", ""), ("+6", ""), ("+4", ""), ("+6", "")))(
    lambda: (cell(hero(), "attack_melee"), cell(hero(), "attack_ranged"),
             cell(hero(pain=(PainEntry(1),)), "attack_melee"), cell(hero(pain=(PainEntry(1),)), "attack_ranged"),
             cell(hero(morale_scale=4), "attack_melee"), cell(hero(morale_scale=4, in_combat=True), "attack_melee")))
S.case("p-source-switch", "combat.md: melee from Dex + BAB = +7", ("+7", ""))(
    lambda: cell(hero(attack_sources={"melee": "dex"}), "attack_melee"))
S.case("p-stats", "pkg 34: CMD 10 + 2 + 2 + 5 = 19 unsigned; Ref 0 + 5 = +5", (("19", ""), ("+5", "")))(
    lambda: (cell(hero(), "cmd"), cell(hero(), "ref")))
S.case("p-borders", "gear.md: light up to 79, load (heavy) 80..129, overload from 130",
       ("light", "light", "heavy", "heavy", "overload"))(
    lambda: tuple(pl.load_category(w, 79, 129) for w in (0, 79, 80, 129, 130)))


def _load(w):
    return cell(hero(items=(Item("b", "bag", weight_l=w),)), "load")


S.case("p-load-text", "gear.md: 40 -> ('load.of', (40, 129), 'load.light'); 130 -> overload style (red)",
       ((("load.of", (40, 129), "load.light"), ""), (("load.of", (130, 129), "load.overload"), "overload")))(
    lambda: (_load(40), _load(130)))
S.case("p-cells", "pkg 34: the layout item's own cells win; else the default rows", ([["cmd"]], [["a", "b"]]))(
    lambda: (pl.cells_of({"cells": [["cmd"]]}, [["a", "b"]]), pl.cells_of({}, [["a", "b"]])))


def _ac(side):
    from wp.commands import dispatch
    ch = dispatch(hero(items=(Item("sh", "heavy shield", kind="shield", hands=1, shield=2, shield_type="heavy"),)),
                  "equip_hands", iid="sh", side=side).state
    info = pl.ac_cells(views(ch)[2], GRID, "5")
    return sorted(c for c, v in info.items() if v[3]), info["1"][2], info["4"][0], "5" in info


S.case("p-ac-shield", "pkg 24 rules: heavy shield left: the shield cells include 4 (side left), labels ac_cell.<n>, "
       "cell 4 = 10 + Dex 5 + shield 2 = 17; 'you' (5) has no number",
       (True, "ac_cell.1", 17, False))(lambda: (lambda r: ("4" in r[0], r[1], r[2], r[3]))(_ac("left")))
S.case("p-ac-right", "pkg 24 rules: shield right: cell 4 has no shield (15), cell 6 has it",
       (False, True, 15))(lambda: (lambda ch_info: ch_info)(
           (lambda r: ("4" in r[0], "6" in r[0], r[2]))(_ac("right"))))


def _imports(path):
    tree = ast.parse(open(path, encoding="ascii").read())
    return [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)] + \
        [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]


S.case("p-no-qt", "pkg 34: params_logic imports no Qt and nothing of the core", [])(
    lambda: [m for m in _imports(pl.__file__) if m.startswith(("PySide6", "wp."))])

if __name__ == "__main__":
    sys.exit(S.run())
