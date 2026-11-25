"""Package 33: experience and the level-up cost (A; RULES/progression.md "Level up", narrative.md "Experience") and
"what changes with the level" (D; numbers by hand from RULES, never from the code's output).

A (owner): a level-up needs 1000 xp and spends it; xp is at most 1999; the excess is not counted (a reminder, not a
refusal); the roll counts at least 1; reminders "distribute the drive points" and "you got X training".
D: sample fighter (d10, BAB good = level * 1, fort good = 2 + level / 2, ref / will poor = level / 3,
progression.md "Class system v0"), light armor proficiency (parry 2 + 1 per odd level from 3, defense.md),
attention 1 + 1 per level multiple of 3 (narrative.md), comfort 1 -> 5 + 5 * level training (training.md),
base max 10 * level (training.md), training HP cap die * level (progression.md), formula variables level / lvl
(buffs.md "Formulas"), level-up training 100 * new level, qualification 50 * N (NOT level dependent).
Run: python Wp_claude/tests/model/test_pkg33.py"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import session as sm  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.model import classes as klass  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import experience as xp  # noqa: E402
from wp.model import pool_view as pv  # noqa: E402
from wp.model.character import Character, Item  # noqa: E402
from wp.model.experience import XpEntry  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg33")
TMP = tempfile.mkdtemp(prefix="wp_p33_")


def refusal(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def banked(n, **kw):
    return Character(xp_log=(XpEntry("xp0", n),), **kw)


# ================================================================ A. experience and the level-up cost
S.case("a-1000", "owner: 1000 xp -> level_up -> 0 xp, level 2", (0, 2))(
    lambda: (lambda c: (xp.total(c), c.level))(run(banked(1000), ("level_up", {"hp_roll": 5}))))
S.case("a-1500", "owner: 1500 -> level_up -> 500 (the rest stays)", 500)(
    lambda: xp.total(run(banked(1500), ("level_up", {"hp_roll": 5}))))
S.case("a-999", "owner: 999 -> refused not_enough_experience; nothing changes", ("not_enough_experience", 1))(
    lambda: (refusal(lambda: dispatch(banked(999), "level_up", hp_roll=5)), banked(999).level))
S.case("a-goal", "owner: the goal is always 1000: 1500 -> 100 %, 999 -> 99 %, can_level_up at 1000, not at 999",
       (1000, 100, 99, True, False))(
    lambda: (xp.view(Character())["next_level_at"], xp.progress_pct(banked(1500)), xp.progress_pct(banked(999)),
             xp.can_level_up(banked(1000)), xp.can_level_up(banked(999))))


def _cap():
    r = dispatch(run(Character(), ("add_experience", {"amount": 1700})), "add_experience", amount=500, note="boss")
    e = r.state.xp_log[-1]
    return xp.total(r.state), e.amount, e.entered, e.note, r.info["reminders"]


S.case("a-cap", "owner: 1700 + 500 -> 1999 (counted 1999 - 1700 = 299, entered 500 kept); reminder, no refusal",
       (1999, 299, 500, "boss", (("exp.remind.excess", (500, 299)),)))(_cap)
S.case("a-cap-full", "owner: at 1999 a further +10 counts 0 (the entry keeps 10); a negative entry counts whole",
       (1999, 0, 10, 1949))(
    lambda: (lambda c: (xp.total(c), c.xp_log[-1].amount, c.xp_log[-1].entered,
                        xp.total(run(c, ("add_experience", {"amount": -50})))))(
        run(Character(), ("add_experience", {"amount": 1999}), ("add_experience", {"amount": 10}))))
S.case("a-cap-edit", "pkg 33: editing an entry 300 -> 2500 with 0 elsewhere counts 1999 (the same cap)",
       (1999, 2500))(
    lambda: (lambda c: (xp.total(c), c.xp_log[0].entered))(
        run(Character(), ("add_experience", {"amount": 300}), ("edit_experience_entry", {"xid": "xp1", "amount": 2500}))))
S.case("a-training", "progression.md: level 2 -> 3 gives 100 * 3 = 300 training (1000 -> 1300)", (3, 1300))(
    lambda: (lambda c: (c.level, c.training))(run(banked(1000, level=2, hp_rolls=(8, 5), training=1000),
                                                  ("level_up", {"hp_roll": 4}))))
S.case("a-roll-min", "owner: hp roll 0 -> 1 (the minimum), warning hit_die_min_used; max HP 8 + 1 = 9 (Con 10)",
       ((8, 1), 9, ("hit_die_min_used",)))(
    lambda: (lambda r: (r.state.hp_rolls, dv.hp_max(r.state), r.info["warnings"]))(
        dispatch(banked(1000, hp_rolls=(8,)), "level_up", hp_roll=0)))
S.case("a-reminders", "owner: the two reminders: distribute the drive points; you got 200 training (level 2)",
       (("drive.remind.distribute", ()), ("exp.remind.training", (200,))))(
    lambda: dispatch(banked(1000), "level_up", hp_roll=3).info["reminders"])


def _log():
    c = run(banked(1500), ("level_up", {"hp_roll": 5, "note": "dragon"}))
    e, h = c.xp_log[-1], c.level_history[-1]
    return e.amount, e.kind, e.note, h.level, h.experience_total


S.case("a-log", "owner: the cost is a log entry -1000 of kind level_up with the note; history keeps 1500 (before)",
       (-1000, "level_up", "dragon", 2, 1500))(_log)


def _undo():
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    s.new("Hero", Character())
    s.dispatch("add_experience", amount=1200)
    s.dispatch("level_up", hp_roll=4)
    after = (s.character.level, xp.total(s.character))
    s.undo()
    return after, (s.character.level, xp.total(s.character), len(s.character.level_history))


S.case("a-undo", "pkg 26 behaviour kept: undo of level_up -> level 1, 1200 xp, no history entry",
       ((2, 200), (1, 1200, 0)))(_undo)
S.case("a-retired", "pkg 33: the hand-typed goal is retired: set_next_level_at is an unknown command",
       "unknown_command")(lambda: refusal(lambda: dispatch(Character(), "set_next_level_at", value=5)))
S.case("a-roundtrip", "D11: a capped entry (entered) and a level_up entry (kind) survive save / load", True)(
    lambda: (lambda c: cio.loads(cio.dumps(c)) == c)(
        run(banked(1900), ("level_up", {"hp_roll": 2}), ("add_experience", {"amount": 3000}))))


# ================================================================ D. what changes with the level
def fighter(level):
    rolls = (10,) + (5,) * (level - 1)
    return run(Character(level=level, hp_rolls=rolls, xp_log=(XpEntry("xp0", 1000),), armor_grade="light",
                         training=5000, base_slots=10 * level, comfort_current=1,
                         pools=()), ("set_class", {"class_id": "sample_fighter"}),
               ("add_pool", {"name": "Lv", "max": "level + 2 * lvl"}))


def snap(c):
    with rd.using(c):
        return {"bab": klass.bab(c), "saves": tuple(klass.save_base(c, k) for k in ("fort", "ref", "will")),
                "parry": dv.ac_input(c).parry, "attention": dv.attention_per_cycle(c), "cap": dv.hit_die_cap(c),
                "pool": pv.max_of(c, c.pools[0])}


def up(c):
    return dispatch(c, "level_up", hp_roll=5)


def _pair(level):
    c = fighter(level)
    r = up(c)
    return c, r.state, r.info["training"]


def _numbers(level):
    before, after, gain = _pair(level)
    b, a = snap(before), snap(after)
    return {k: (b[k], a[k]) for k in sorted(b)}, gain


# level 2 -> 3: BAB 2 -> 3; fort 2 + 2 // 2 = 3 -> 2 + 3 // 2 = 3; ref / will 2 // 3 = 0 -> 3 // 3 = 1;
# parry 2 + 0 -> 2 + 1 (level 3 is odd); attention 1 -> 1 + 1 (3 is a multiple of 3); cap 10 * 2 = 20 -> 30;
# pool "level + 2 * lvl" 2 + 4 = 6 -> 3 + 6 = 9; training 100 * 3 = 300.
S.case("d-2-3", "RULES: level 2 -> 3 (fighter d10, light armor): BAB, saves, parry, attention, HP cap, level / lvl, "
       "training", ({"attention": (1, 2), "bab": (2, 3), "cap": (20, 30), "parry": (2, 3), "pool": (6, 9),
                     "saves": ((3, 0, 0), (3, 1, 1))}, 300))(lambda: _numbers(2))
# level 4 -> 5: BAB 4 -> 5; fort 2 + 2 = 4 -> 2 + 5 // 2 = 4; ref / will 4 // 3 = 1 -> 5 // 3 = 1;
# parry 2 + 1 (odd 3) -> 2 + 2 (odd 3, 5); attention 2 -> 2 (5 is not a multiple of 3); cap 40 -> 50;
# pool 4 + 8 = 12 -> 5 + 10 = 15; training 100 * 5 = 500.
S.case("d-4-5", "RULES: level 4 -> 5: parry +1 (odd), attention unchanged (5 is no multiple of 3), saves unchanged",
       ({"attention": (2, 2), "bab": (4, 5), "cap": (40, 50), "parry": (3, 4), "pool": (12, 15),
         "saves": ((4, 1, 1), (4, 1, 1))}, 500))(lambda: _numbers(4))


def _comfort(level):
    before, after, _ = _pair(level)
    gain = lambda c: dispatch(c, "exchange_comfort", n=1).info["training"]     # noqa: E731
    return gain(before), gain(after)


S.case("d-comfort", "training.md: 1 comfort = 5 + 5 * level: 15 -> 20 (2 -> 3), 25 -> 30 (4 -> 5)",
       ((15, 20), (25, 30)))(lambda: (_comfort(2), _comfort(4)))


def _base(level):
    before, after, _ = _pair(level)
    return refusal(lambda: dispatch(before, "buy_base_slot")), dispatch(after, "buy_base_slot").state.base_slots


S.case("d-base", "training.md: max base points 10 * level: 20 full at level 2, the 21st allowed at 3; 40 / 41 at 4 / 5",
       (("base_at_max", 21), ("base_at_max", 41)))(lambda: (_base(2), _base(4)))


def _qualification(level):
    before, after, _ = _pair(level)
    item = Item("rod", "rod", qualification_n=3)
    cost = lambda c: c.training - dispatch(replace_items(c, item), "buy_item_qualification", iid="rod").state.training  # noqa
    return cost(before), cost(after)


def replace_items(c, item):
    from dataclasses import replace
    return replace(c, items=(item,))


S.case("d-qualification", "training.md: qualification 50 * N (N 3 = 150) does NOT change with the level",
       ((150, 150), (150, 150)))(lambda: (_qualification(2), _qualification(4)))

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
