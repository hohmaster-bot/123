"""Group E: defense ladder (RULES/defense_layers.md). Run: python Wp_claude/tests/core/test_ac_layers.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core import ac as acm  # noqa: E402
from wp.core import ac_layers as L  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402

S = Suite("test_ac_layers")


def plus_one_each():
    """+1 of every type: size 1, Dex 1 (dodge layer), insight, morale, competence, luck, circumstance,
    deflection, shield 1, armor 1, natural 1 -> AC 10 + 11 = 21."""
    b = tuple(bo.Bonus(1, t, bo.AC) for t in ("insight", bo.MORALE, "competence", "luck", "circumstance", bo.DEFLECTION))
    return acm.parts(acm.AcInput(dex_mod=1, armor=1, natural=1, shield=1, size_mod=1, bonuses=b))


# Owner example (flat 0 -> empty, skipped): 1-9 position, 10 size, 11 dodge, 12 insight, 13 morale, 14 competence, 15 luck,
# 16 circumstance, 17 deflection, 18 shield, 19 armor, 20 natural, 21 exact, 22+ hit.
S.case("example-ladder", "defense_layers.md Example [OWNER]: +1 of every type",
       (("position", None, 9), ("size", 10, 10), ("dodge", 11, 11), ("insight", 12, 12), ("morale", 13, 13),
        ("competence", 14, 14), ("luck", 15, 15), ("circumstance", 16, 16), ("deflection", 17, 17),
        ("shield", 18, 18), ("armor", 19, 19), ("natural", 20, 20), ("exact", 21, 21), ("hit", 22, None)))(
    lambda: tuple((r.layer, r.lo, r.hi) for r in L.ladder(plus_one_each())))
S.case("example-rolls", "defense_layers.md Example: rolls 5, 10, 15, 20, 21, 25",
       ("position", "size", "luck", "natural", "exact", "hit"))(
    lambda: tuple(L.layer_for_roll(plus_one_each(), r)[0] for r in (5, 10, 15, 20, 21, 25)))
S.case("ladder-equals-ac", "defense_layers.md: AC = 10 + layers (same as ac.py)", (21, 21))(
    lambda: (L.ac_total(plus_one_each()),
             acm.ac(acm.AcInput(dex_mod=1, armor=1, natural=1, shield=1, size_mod=1, bonuses=tuple(
                 bo.Bonus(1, t, bo.AC) for t in ("insight", bo.MORALE, "competence", "luck", "circumstance", bo.DEFLECTION))))))


# Zero layers are skipped: Dex 2, armor 4 only -> 10-11 dodge, 12-15 armor, 16 exact, 17+ hit.
S.case("zero-skipped", "defense_layers.md: a layer with a zero bonus has an empty range",
       (("position", None, 9), ("dodge", 10, 11), ("armor", 12, 15), ("exact", 16, 16), ("hit", 17, None)))(
    lambda: tuple((r.layer, r.lo, r.hi) for r in L.ladder(acm.parts(acm.AcInput(dex_mod=2, armor=4)))))

# Parry goes into the armor layer: armor 2, parry 5 -> parry mode armor layer 5 wide: 10-14, exact 15.
S.case("parry-in-armor", "defense_layers.md: parry counts in the armor layer (max armor/parry)",
       (("armor", 10, 14), 15))(
    lambda: (lambda lad: ((lad[1].layer, lad[1].lo, lad[1].hi), lad[2].lo))(
        L.ladder(acm.parts(acm.AcInput(armor=2, parry=5), acm.PARRY))))

S.case("roll-equals-ac", "defense_layers.md: roll == AC -> hit just barely", ("exact", 16, 16))(
    lambda: (lambda r: (r[0], r[1].lo, r[1].hi))(L.layer_for_roll(acm.parts(acm.AcInput(dex_mod=2, armor=4)), 16)))
S.case("roll-below-10", "defense_layers.md: below 10 -> no position", ("position", "position"))(
    lambda: (L.layer_for_roll(plus_one_each(), 9)[0], L.layer_for_roll(plus_one_each(), 1)[0]))
S.case("texts-by-type", "defense_layers.md: texts are data by layer type; deflection given, flat not yet", (15, True, ""))(
    lambda: (lambda t: (len(t), bool(t["deflection"]), t["flat"]))(L.texts()))

if __name__ == "__main__":
    sys.exit(S.run())
