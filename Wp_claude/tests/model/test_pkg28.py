"""Package 28 B: drives (types, levels, quests, buying a level with comfort, reminders). Numbers by hand from the
package text and RULES/narrative.md "Drives (package 28)". Run: python Wp_claude/tests/model/test_pkg28.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.catalog import store as cs  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.commands import notebook_cmds as nbc  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.model.experience import XpEntry  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_pkg28")


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def refusal(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


def drive(level, ch=None, **kw):
    return run(ch or Character(), ("add_drive", dict({"dtype": "growth", "level": level}, **kw)))


def view(ch, i=0):
    with rd.using(ch):
        return nbc.notebook_view(ch)["drives"][i]


FLAGS = ("taboo_required", "principle_missing", "quest_allowed", "quest_mandatory", "quest_missing", "obsessed")


def flags(ch):
    v = view(ch)
    return tuple(v[f] for f in FLAGS) + (v["spirit_bonus"], v["penalty_text"])


S.case("d-level1", "owner: level 1 -> no flags, no spirit bonus, no penalty", (False,) * 6 + (0, ""))(
    lambda: flags(drive(1)))
S.case("d-level2", "owner: level 2 without a principle -> taboo required, principle missing; spirit +1",
       (True, True, False, False, False, False, 1, ""))(lambda: flags(drive(2)))
S.case("d-level3", "owner: level 3 with a principle: a quest allowed (not mandatory); spirit +2; penalty text of 3",
       (True, False, True, False, False, False, 2, "drive_level.3.penalty"))(lambda: flags(drive(3, principle="never lie")))
S.case("d-level4", "owner: level 4 without a quest -> quest mandatory and missing; spirit +3",
       (True, False, True, True, True, False, 3, "drive_level.4.penalty"))(lambda: flags(drive(4, principle="p")))
S.case("d-level5", "owner: level 5 -> obsessed; spirit +4; penalty text of 5",
       (True, False, True, True, True, True, 4, "drive_level.5.penalty"))(lambda: flags(drive(5, principle="p")))
S.case("d-quest-taken", "owner: level 4 with a quest taken -> not missing", False)(
    lambda: view(run(drive(4, principle="p"), ("set_drive_quest", {"did": "growth", "quest": "find", "state": "taken"})))
    ["quest_missing"])


def _attention():
    ch = Character(level=7)
    ch = drive(4, ch)
    ch = run(ch, ("add_drive", {"dtype": "triumph", "level": 5}), ("add_drive", {"dtype": "society", "level": 3}))
    return dispatch(ch, "end_cycle").info["gain"]


S.case("d-attention", "narrative.md: level 7 (3 and 6) and two drives at 4+ -> 1 + 2 + 2 = 5", 5)(_attention)


def _open_quest():
    ch = drive(3, principle="p")
    taken = run(ch, ("set_drive_quest", {"did": "growth", "quest": "q", "state": "taken"}))
    closed = run(taken, ("set_drive_quest", {"did": "growth", "state": "closed", "comfort_received": True}))
    return dispatch(taken, "end_cycle").info["reminders"], dispatch(closed, "end_cycle").info["reminders"]


S.case("d-end-cycle", "owner: level 3 with a quest taken -> the end-of-cycle reminder with its penalty text; "
       "closed -> none", ((("drive.remind.open_quest", ("growth", "drive_level.3.penalty")),), ()))(_open_quest)


def _buy_up():
    ch = drive(2, Character(comfort_current=3))
    up = run(ch, ("drive_buy_up", {"did": "growth"}))
    short = drive(2, Character(comfort_current=2))
    return up.drives[0].level, up.comfort_current, refusal(lambda: dispatch(short, "drive_buy_up", did="growth"))


S.case("d-buy-up", "owner: buy up at comfort 3 -> level 2 -> 3, comfort 0; at comfort 2 -> not_enough_comfort",
       (3, 0, "not_enough_comfort"))(_buy_up)


def _buy_down():
    ch = drive(3, Character(comfort_current=5))
    down = run(ch, ("drive_buy_down", {"did": "growth"}))
    zero = drive(0, Character(comfort_current=5))
    top = drive(5, Character(comfort_current=5))
    return (down.drives[0].level, down.comfort_current, refusal(lambda: dispatch(zero, "drive_buy_down", did="growth")),
            refusal(lambda: dispatch(top, "drive_buy_up", did="growth")))


S.case("d-buy-down", "owner: buy down costs 2 (comfort 5 -> 3, level 3 -> 2); down at 0 and up at 5 -> out_of_range",
       (2, 3, "out_of_range", "out_of_range"))(_buy_down)


def _budget():
    ch = Character()
    for t, lv in (("growth", 5), ("triumph", 5), ("society", 4)):
        ch = run(ch, ("add_drive", {"dtype": t, "level": lv}))
    with rd.using(ch):
        s = nbc.notebook_view(ch)["drive_summary"]
    return s["distributed"], s["start_points"], len(ch.drives)


S.case("d-budget-hint", "owner: 5 + 5 + 4 = 14 of 12 -> no refusal, the hint only", (14, 12, 3))(_budget)


def _reminders():
    ch = run(Character(), ("add_drive", {"dtype": "growth", "level": 2}), ("add_drive", {"dtype": "triumph", "level": 4,
                                                                                         "principle": "p"}),
             ("add_drive", {"dtype": "society", "level": 1}))
    with rd.using(ch):
        return nbc.notebook_view(ch)["drive_summary"]["reminders"]


S.case("d-reminders", "owner: level 2 without a principle -> write the taboo; level 4 without a quest -> take a quest; "
       "level 1 -> nothing", (("drive.remind.principle", ("growth",)), ("drive.remind.quest", ("triumph",))))(_reminders)
S.case("d-level-up", "owner: level_up carries the reminder to distribute drive points (no number)",
       (("drive.remind.distribute", ()),))(lambda: dispatch(Character(xp_log=(XpEntry("xp0", 1000),)), "level_up", hp_roll=4).info["reminders"][:1])
S.case("d-custom", "owner: a custom drive (no type) is allowed; a second growth drive is not forbidden: 3 drives",
       ("", 3))(lambda: (lambda c: (c.drives[0].dtype, len(drive(1, c).drives)))(
           run(Character(), ("add_drive", {"name": "Revenge", "level": 1}), ("add_drive", {"dtype": "growth"}))))
S.case("d-quest-state", "pkg 28: a quest state outside none / taken / closed -> not_allowed", "not_allowed")(
    lambda: refusal(lambda: dispatch(drive(3), "set_drive_quest", did="growth", state="done")))
S.case("d-edit-free", "owner: in edit mode the level changes for free (edit_drive 0 -> 5, comfort untouched)", (5, 0))(
    lambda: (lambda c: (c.drives[0].level, c.comfort_current))(run(drive(0), ("edit_drive", {"did": "growth", "level": 5}))))


def _catalog():
    e = cs.load_shipped("drive_types").entries
    return (tuple(x["id"] for x in e), all(len(x["description"]) > 100 for x in e),
            e[0]["description"].startswith("\u0416\u0435\u043b\u0430\u043d\u0438\u0435"))


S.case("d-types", "owner: the 10 drive types with their Russian descriptions", (
    ("idealism", "growth", "knowledge", "autonomy", "pleasure", "material", "triumph", "success", "society", "decadence"),
    True, True))(_catalog)
S.case("d-constants", "owner: start 12, up 3 comfort, down 2 comfort", (12, 3, 2))(
    lambda: (rd.const("drives.start_points"), rd.const("drives.buy_up_cost"), rd.const("drives.buy_down_cost")))

if __name__ == "__main__":
    sys.exit(S.run())
