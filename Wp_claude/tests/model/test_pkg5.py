"""Package 5: owner answers (dodge/Dex, enhancement layer, shields, ids, shield attacks, enchantment).
Run: python Wp_claude/tests/model/test_pkg5.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.core import ac as acm  # noqa: E402
from wp.core import ac_layers as L  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402

S = Suite("test_pkg5")


def layers(mode=acm.FRONT, **kw):
    return dict(acm.parts(acm.AcInput(**kw), mode))


def dodge(v):
    return bo.Bonus(v, bo.DODGE, bo.AC)


def pick(p, *keys):
    return tuple(p[k] for k in keys)


# ---- A: dodge layer = dodge bonuses + Dex mod ----
S.case("a-dex-2-dodge+1", "defense_layers.md [OWNER pkg 5]: Dex -2, dodge +1 -> flat -1, dodge 0", (0, -1))(
    lambda: pick(layers(dex_mod=-2, bonuses=(dodge(1),)), "dodge", "flat"))
S.case("a-dex-2-dodge+1-ff", "defense_layers.md: Dex -2, dodge +1, flat-footed -> flat -2", (0, -2))(
    lambda: pick(layers(acm.FLAT_FOOTED, dex_mod=-2, bonuses=(dodge(1),)), "dodge", "flat"))
S.case("a-dex+2-dodge+1", "defense_layers.md: Dex +2, dodge +1 -> dodge 3", (3, 0))(
    lambda: pick(layers(dex_mod=2, bonuses=(dodge(1),)), "dodge", "flat"))
S.case("a-dex+2-dodge+1-ff", "defense_layers.md: Dex +2, dodge +1, flat-footed -> 0", (0, 0))(
    lambda: pick(layers(acm.FLAT_FOOTED, dex_mod=2, bonuses=(dodge(1),)), "dodge", "flat"))
S.case("a-real-ac", "defense_layers.md: real AC = 10 + sum of layers (Dex -2, dodge +1, armor 3: 12; ff 11)",
       (12, 12, 11, 11))(
    lambda: (lambda i: (acm.ac(i), L.ac_total(acm.parts(i)), acm.ac(i, acm.FLAT_FOOTED),
                        L.ac_total(acm.parts(i, acm.FLAT_FOOTED))))(
        acm.AcInput(dex_mod=-2, armor=3, bonuses=(dodge(1),))))

# ---- B: enhancement goes to the armor layer; other unlisted types go to flat ----
S.case("b-enhancement-armor", "defense_layers.md [OWNER Q26]: enhancement +2 raises the armor layer (4 -> 6)", (6, 0))(
    lambda: pick(layers(armor=4, bonuses=(bo.Bonus(2, bo.ENHANCEMENT, bo.AC),)), "armor", "flat"))
S.case("b-sacred-flat", "defense_layers.md: sacred +2 is not a layer; in AC it goes to flat (assumption)", (0, 2, 12))(
    lambda: (lambda p: (p["armor"], p["flat"], 10 + sum(p.values())))(
        layers(bonuses=(bo.Bonus(2, "sacred", bo.AC),))))
S.case("b-enhancement-touch", "defense.md: touch ignores armor, so its enhancement too", 0)(
    lambda: layers(acm.TOUCH, armor=4, bonuses=(bo.Bonus(2, bo.ENHANCEMENT, bo.AC),))["armor"])

if __name__ == "__main__":
    sys.exit(S.run())
