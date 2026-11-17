"""Core effect system vs RULES/buffs.md. Run: python Wp_claude/tests/core/test_effects.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Effect, OneShot, Status  # noqa: E402

S = Suite("test_effects")

# buffs.md: one-shot temp HP AND a timed part (+4 Str for 8 rounds); penalties possible (-2 AC).
RAGE = Status("rage", effects=(Effect("str", 4, bo.MORALE), Effect(bo.AC, -2)),
              one_shot=(OneShot(ef.TEMP_HP, 5),), duration=ef.TICKS, remaining=8,
              charges=Pool(3, 3))

S.case("timed-part", "buffs.md: timed +4 Str and -2 AC", (4, -2))(
    lambda: (bo.total(ef.bonuses_from([RAGE], True), "str"), bo.total(ef.bonuses_from([RAGE], True), bo.AC)))
S.case("one-shot", "buffs.md: one-shot temp HP applied once", 5)(lambda: ef.apply_one_shot(RAGE, 0))

# buffs.md Charges: rage 2/3; no charges left -> cannot activate.
S.case("charges", "buffs.md: activating spends a charge (3 -> 2)", 2)(
    lambda: ef.activate(RAGE).charges.current)


@S.case("no-charges", "buffs.md: no charges left -> cannot activate", "rejected")
def _no_charges():
    try:
        ef.activate(Status("rage", charges=Pool(0, 3)))
    except ValueError:
        return "rejected"
    return "allowed"


# buffs.md Duration: drops by 1 each zero-initiative phase; manual number.
S.case("duration-tick", "buffs.md: duration -1 per tick", 7)(lambda: ef.tick_duration(RAGE).remaining)
S.case("duration-expire", "buffs.md: last tick removes the status", ())(
    lambda: ef.tick_all([Status("x", duration=ef.TICKS, remaining=1)]))
S.case("duration-manual", "buffs.md [OWNER]: duration typed by hand", 12)(
    lambda: ef.activate(Status("haste", duration=ef.TICKS), ticks=12).remaining)
S.case("end-of-combat", "buffs.md: until end of combat", ("narr",))(
    lambda: tuple(s.name for s in ef.end_combat([Status("eoc", duration=ef.END_OF_COMBAT),
                                                 Status("narr", duration=ef.INFINITE)])))
S.case("infinite-no-tick", "buffs.md: narrative infinite does not tick", ef.INFINITE)(
    lambda: ef.tick_duration(Status("curse")).duration)
S.case("instant-not-kept", "buffs.md: instant one-shot is not kept", ())(
    lambda: ef.drop_instant([Status("heal", duration=ef.INSTANT)]))

# buffs.md Condition: in combat only / out of combat only.
_OUT = Status("tools", effects=(Effect(bo.SKILL, 2, "competence"),), condition=ef.OUT_OF_COMBAT)
S.case("condition", "buffs.md: out-of-combat bonus", (0, 2))(
    lambda: (bo.total(ef.bonuses_from([_OUT], True), bo.SKILL),
             bo.total(ef.bonuses_from([_OUT], False), bo.SKILL)))
S.case("inactive", "effects: switched off -> no bonuses", 0)(
    lambda: bo.total(ef.bonuses_from([ef.set_active(RAGE, False)], True), "str"))

# buffs.md Stacking flags: temp HP from statuses may or may not stack.
S.case("temp-hp-no-stack", "buffs.md: temp HP not stacking -> higher value", 5)(
    lambda: ef.apply_temp_hp(3, 5, stacks=False))
S.case("temp-hp-stack", "buffs.md: temp HP stacking flag -> add", 8)(
    lambda: ef.apply_temp_hp(3, 5, stacks=True))

# combat.md: effect flag 'ignores iterative penalty'.
S.case("ignores-iterative", "combat.md: effect flag", (True, False))(
    lambda: (ef.ignores_iterative([Status("master", ignores_iterative=True)], True),
             ef.ignores_iterative([Status("other")], True)))

if __name__ == "__main__":
    sys.exit(S.run())
