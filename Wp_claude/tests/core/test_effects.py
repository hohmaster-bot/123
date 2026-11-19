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
    lambda: (bo.total(ef.bonuses_from([RAGE]), "str"), bo.total(ef.bonuses_from([RAGE]), bo.AC)))
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
S.case("duration-expire", "buffs.md [pkg 11 A]: the last tick makes the status inactive, the entry stays", (("x", False, 0),))(
    lambda: tuple((s.name, s.active, s.remaining) for s in ef.tick_all([Status("x", duration=ef.TICKS, remaining=1)])))
S.case("duration-manual", "buffs.md [OWNER]: duration typed by hand", 12)(
    lambda: ef.activate(Status("haste", duration=ef.TICKS), ticks=12).remaining)
S.case("end-of-combat", "buffs.md: until end of combat (pkg 11 A: eoc inactive, entry stays)", (("eoc", False), ("narr", True)))(
    lambda: tuple((s.name, s.active) for s in ef.end_combat([Status("eoc", duration=ef.END_OF_COMBAT),
                                                            Status("narr", duration=ef.INFINITE)])))
S.case("infinite-no-tick", "buffs.md: narrative infinite does not tick", ef.INFINITE)(
    lambda: ef.tick_duration(Status("curse")).duration)
S.case("instant-not-kept", "buffs.md: instant one-shot is not kept", ())(
    lambda: ef.drop_instant([Status("heal", duration=ef.INSTANT)]))

# buffs.md Condition: in combat only / out of combat only.
_TOOLS = Status("tools", effects=(Effect(bo.SKILL, 2, "competence"),))
S.case("no-condition", "buffs.md [OWNER pkg 8]: no combat-only condition, a status works while active", (2, False))(
    lambda: (bo.total(ef.bonuses_from([_TOOLS]), bo.SKILL), hasattr(_TOOLS, "condition")))
S.case("inactive", "effects: switched off -> no bonuses", 0)(
    lambda: bo.total(ef.bonuses_from([ef.set_active(RAGE, False)]), "str"))

# buffs.md Stacking flags: temp HP from statuses may or may not stack.
S.case("temp-hp-no-stack", "buffs.md: temp HP not stacking -> higher value", 5)(
    lambda: ef.apply_temp_hp(3, 5, stacks=False))
S.case("temp-hp-stack", "buffs.md: temp HP stacking flag -> add", 8)(
    lambda: ef.apply_temp_hp(3, 5, stacks=True))

# buffs.md [OWNER]: value from the current overload: attack and damage with natural weapons = overload.
_NAT = Status("feral", effects=(Effect(bo.ATTACK, value_source=ef.OVERLOAD, weapon="natural"),
                                Effect(bo.DAMAGE, value_source=ef.OVERLOAD, weapon="natural")))
S.case("overload-source", "buffs.md [OWNER]: natural weapons attack and damage = current overload",
       (3, 3, 0, 0))(
    lambda: (bo.total(ef.bonuses_from([_NAT], {ef.OVERLOAD: 3}), bo.ATTACK, weapon="natural"),
             bo.total(ef.bonuses_from([_NAT], {ef.OVERLOAD: 3}), bo.DAMAGE, weapon="natural"),
             bo.total(ef.bonuses_from([_NAT], {ef.OVERLOAD: 3}), bo.ATTACK, weapon="sword"),
             bo.total(ef.bonuses_from([_NAT], {ef.OVERLOAD: 0}), bo.ATTACK, weapon="natural")))

# combat.md: effect flag 'ignores iterative penalty'.
S.case("ignores-iterative", "combat.md: effect flag", (True, False))(
    lambda: (ef.ignores_iterative([Status("master", ignores_iterative=True)]),
             ef.ignores_iterative([Status("other")])))

if __name__ == "__main__":
    sys.exit(S.run())
