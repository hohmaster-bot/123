"""Package 23 D: AC by cell from the owner's draft (RULES/ac_zones.md), as data (wp/rules_data/ac_zones.json, a sample).
Expected numbers by hand. Run: python Wp_claude/tests/model/test_ac_zones.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.core import ac as acm  # noqa: E402
from wp.core import ac_zones as acz  # noqa: E402
from wp.model import ac_zones_view as zv  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import ABILITIES, Ability, Character, Item  # noqa: E402

S = Suite("test_ac_zones")


def hero(dex=14, shield_type="heavy", armor=4, grade="light", shield=2):
    items = []
    if shield:
        items.append(Item("sh", "shield", kind="shield", hands=1, in_hands=True, shield=shield, shield_type=shield_type))
    if armor:
        items.append(Item("mail", "mail", equipped=True, armor=armor))
    return Character(abilities={a: Ability(base=dex if a == "dex" else 10) for a in ABILITIES}, items=tuple(items),
                     armor_grade=grade, shield_grade="heavy")


def full(c, hand=acz.LEFT):
    return tuple(zv.cells(c, hand=hand)[k]["full"] for k in acz.CELLS)


S.case("z-cells", "ac_zones.md: Dex +2, armor 4, heavy shield 2: cells 1 2 3 4 = 18, 6 = 16 (no shield), 7 = 18, 8 = 14 "
       "(back: no Dex, no shield), 9 = 16", (18, 18, 18, 18, 16, 18, 14, 16))(lambda: full(hero()))
S.case("z-parry-cells", "ac_zones.md: Parry only in cells 1, 2, 3 (parry 2 < armor 4 -> 18); None elsewhere",
       (18, 18, 18, None, None, None, None, None))(
    lambda: tuple(zv.cells(hero())[k]["parry"] for k in acz.CELLS))


def _presets(c):
    inp = dv.ac_input(c)
    cells = zv.cells(c)
    return (cells["2"]["full"] == acm.ac(inp, acm.FRONT), cells["2"]["parry"] == acm.ac(inp, acm.PARRY),
            cells["6"]["full"] == acm.ac(inp, acm.FLANK), cells["8"]["full"] == acm.ac(inp, acm.FLAT_FOOTED))


S.case("z-presets", "pkg 23: cell 2 = front and parry, cell 6 = flank, cell 8 = flat-footed (the old modes unchanged)",
       (True, True, True, True))(lambda: _presets(hero()))
S.case("z-presets-parry", "pkg 23: the same with parry 6 > armor 0 (heavy armor proficiency)", (True, True, True, True))(
    lambda: _presets(hero(armor=0, grade="heavy")))
S.case("z-parry-high", "defense.md: parry 6, no armor, Dex +2, shield 2: full 14, parry 20 in cell 2", (14, 20))(
    lambda: (lambda c: (c["2"]["full"], c["2"]["parry"]))(zv.cells(hero(armor=0, grade="heavy"))))
S.case("z-buckler", "ac_zones.md: a buckler covers 1, 2, 4 only: cell 3 and 7 lose the shield (16)",
       (18, 18, 16, 18, 16, 16, 14, 16))(lambda: full(hero(shield_type="buckler")))
S.case("z-right-hand", "ac_zones.md: a shield in the RIGHT hand mirrors: 4 -> 16, 6 -> 18, 7 -> 16, 9 -> 18",
       (18, 18, 18, 16, 18, 16, 14, 18))(lambda: full(hero(), acz.RIGHT))
S.case("z-shield-off", "defense.md: after an attack with the shield (no shield bonus): cell 2 -> 16", 16)(
    lambda: zv.cells(hero(), shield_enabled=False)["2"]["full"])
S.case("z-dex-minus", "defense.md example: Dex -2, nothing worn: front 8, back (cell 8) 8 (the penalty stays)", (8, 8))(
    lambda: (lambda c: (c["2"]["full"], c["8"]["full"]))(zv.cells(hero(dex=6, armor=0, shield=0))))
S.case("z-data", "ac_zones.md: 8 cells around the character (5 is the character)", ("1", "2", "3", "4", "6", "7", "8", "9"))(
    lambda: acz.CELLS)

if __name__ == "__main__":
    sys.exit(S.run())
