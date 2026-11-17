"""Core AC vs RULES/defense.md, gear.md. Run: python Wp_claude/tests/core/test_ac.py

defense.md has no numeric AC examples, so one sample character is built from the
rule text: Dex +3, armor 4, parry 6, natural 2, shield 2, deflection 1 (effect).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core import ac as a  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402

S = Suite("test_ac")


def sample(**kw):
    base = dict(dex_mod=3, armor=4, parry=6, natural=2, shield=2,
                bonuses=(bo.Bonus(1, bo.DEFLECTION, bo.AC),))
    base.update(kw)
    return a.AcInput(**base)


S.case("front", "defense.md Front: full AC (10+3+4+2+2+1)", 22)(lambda: a.ac(sample(), a.FRONT))
S.case("flank", "defense.md Flank: shield ignored", 20)(lambda: a.ac(sample(), a.FLANK))
S.case("flat-footed", "defense.md Flat-footed: no Dex, no shield", 17)(
    lambda: a.ac(sample(), a.FLAT_FOOTED))
S.case("flat-footed-shield-side", "defense.md Flat-footed: shield only from shield side", 19)(
    lambda: a.ac(sample(), a.FLAT_FOOTED, from_shield_side=True))
S.case("flat-footed-no-dodge", "defense.md [OWNER]: flat-footed loses Dex and ALL dodge", 17)(
    lambda: a.ac(sample(bonuses=(bo.Bonus(1, bo.DEFLECTION, bo.AC), bo.Bonus(3, bo.DODGE, bo.AC))),
                 a.FLAT_FOOTED))
S.case("parry","defense.md Parry: max(armor 4, parry 6) in the armor slot", 24)(
    lambda: a.ac(sample(), a.PARRY))
S.case("parry-armor-bigger", "defense.md Parry: armor bigger -> armor stays", 22)(
    lambda: a.ac(sample(parry=3), a.PARRY))
S.case("touch", "defense.md Touch: no natural, shield, parry, armor", 14)(
    lambda: a.ac(sample(), a.TOUCH))
S.case("shield-off", "defense.md: shield bonus can be switched off", 20)(
    lambda: a.ac(sample(shield_enabled=False), a.FRONT))
S.case("overload-cap", "gear.md Overload: Dex + dodge capped at +2", 21)(
    lambda: a.ac(sample(overloaded=True, bonuses=(bo.Bonus(1, bo.DEFLECTION, bo.AC),
                                                  bo.Bonus(2, bo.DODGE, bo.AC))), a.FRONT))
S.case("dodge-stacks-in-ac", "defense.md: dodge stacks (Dex 3 + dodge 1 + dodge 1)", 24)(
    lambda: a.ac(sample(bonuses=(bo.Bonus(1, bo.DEFLECTION, bo.AC), bo.Bonus(1, bo.DODGE, bo.AC),
                                 bo.Bonus(1, bo.DODGE, bo.AC))), a.FRONT))
S.case("armor-effect-highest", "defense.md: armor item 4 + armor effect 3 -> highest 4", 22)(
    lambda: a.ac(sample(bonuses=(bo.Bonus(1, bo.DEFLECTION, bo.AC), bo.Bonus(3, bo.ARMOR, bo.AC))),
                 a.FRONT))
S.case("max-dex", "armor max Dex caps Dex", 21)(lambda: a.ac(sample(max_dex=2), a.FRONT))
S.case("stance-defensive-ac", "combat.md Stances Example: +2 dodge on AC", 24)(
    lambda: a.ac(sample(bonuses=(bo.Bonus(1, bo.DEFLECTION, bo.AC), bo.Bonus(2, bo.DODGE, bo.AC))),
                 a.FRONT))
S.case("morale-not-ac", "defense.md Morale: rolls only, not AC", 22)(
    lambda: a.ac(sample(bonuses=(bo.Bonus(1, bo.DEFLECTION, bo.AC), bo.morale(3))), a.FRONT))

if __name__ == "__main__":
    sys.exit(S.run())
