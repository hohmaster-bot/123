"""Drives (RULES/narrative.md "Drives (package 28)", owner). Story power is narrative and kept outside the program:
no story-power number here, the penalties are text keys only (wp/i18n: drive_level.<n>.penalty).

A drive = a type (catalog drive_types, or a custom one) + level 0..5 + principle (taboo) + quest + level notes.
Levels of different drives are never summed for a rule; the summary only shows "distributed X of
drives.start_points" as a hint (nothing is blocked). Thresholds are constants: the taboo from
narrative.principle_min_level (2), a quest allowed from drives.quest_allowed_level (3), mandatory from
drives.quest_mandatory_level (4), obsessed at narrative.drive_max (5); the spirit hint drives.spirit_bonus.
Reminders are (text key, values) pairs for the UI; they never block.
Commands: drive_buy_up / drive_buy_down (comfort drives.buy_up_cost 3 / buy_down_cost 2, level stays 0..5),
set_drive_quest (quest text, state none / taken / closed, comfort_received by hand).
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.commands import notebook_cmds as nbc
from wp.model import notebook as nb
from wp.rules_data import rules as rd

TAKEN = "taken"
CLOSED = "closed"
NONE = "none"
REMIND_PRINCIPLE = "drive.remind.principle"
REMIND_QUEST = "drive.remind.quest"
REMIND_DISTRIBUTE = "drive.remind.distribute"
REMIND_OPEN = "drive.remind.open_quest"


def _c(key, ch):
    return rd.const(key, ch)


def penalty_key(level, ch=None):
    return "drive_level.%d.penalty" % level if level >= int(_c("drives.quest_allowed_level", ch)) else ""


def drive_view(ch, d):
    taboo = d.level >= int(_c("narrative.principle_min_level", ch))
    allowed = d.level >= int(_c("drives.quest_allowed_level", ch))
    mandatory = d.level >= int(_c("drives.quest_mandatory_level", ch))
    return {"did": d.did, "name": d.name, "type": d.dtype, "level": d.level, "level_notes": dict(d.level_notes),
            "note": d.level_notes.get(str(d.level), ""), "principle": d.principle,
            "taboo_required": taboo, "principle_missing": taboo and not d.principle.strip(),
            "quest": d.quest, "quest_state": d.quest_state, "comfort_received": d.comfort_received,
            "quest_allowed": allowed, "quest_mandatory": mandatory,
            "quest_missing": mandatory and d.quest_state == NONE,
            "obsessed": d.level >= int(nb.DRIVE_MAX),
            "spirit_bonus": int(dict(_c("drives.spirit_bonus", ch)).get(str(d.level), 0)),
            "obligation_text": "drive_level.%d.obligation" % d.level, "penalty_text": penalty_key(d.level, ch)}


def reminders(ch):
    out = []
    for d in ch.drives:
        v = drive_view(ch, d)
        if v["principle_missing"]:
            out.append((REMIND_PRINCIPLE, (d.name,)))
        if v["quest_missing"]:
            out.append((REMIND_QUEST, (d.name,)))
    return tuple(out)


def summary(ch):
    return {"distributed": sum(d.level for d in ch.drives), "start_points": int(_c("drives.start_points", ch)),
            "reminders": reminders(ch), "text": "drive.points"}


def open_quests(ch):
    """End of cycle: (REMIND_OPEN, (name, penalty key)) for every drive at the quest level with a taken quest."""
    return tuple((REMIND_OPEN, (d.name, penalty_key(d.level, ch))) for d in ch.drives
                 if d.level >= int(_c("drives.quest_allowed_level", ch)) and d.quest_state == TAKEN)


def _buy(ch, did, step, cost_key, command_name):
    d = nbc._get(ch, "drives", "did", did)
    level = d.level + step
    if not 0 <= level <= int(nb.DRIVE_MAX):
        raise CommandError("a drive level is 0..%d" % int(nb.DRIVE_MAX), "out_of_range",
                           values=(level, 0, int(nb.DRIVE_MAX)), min=0, max=int(nb.DRIVE_MAX))
    cost = int(_c(cost_key, ch))
    if ch.comfort_current < cost:
        raise CommandError("not enough comfort: need %d, have %d" % (cost, ch.comfort_current), "not_enough_comfort",
                           values=(cost, ch.comfort_current))
    new = nbc._put(ch, "drives", "did", replace(d, level=level))
    return commit(replace(new, comfort_current=ch.comfort_current - cost), command_name,
                  "drive %s level %d for %d comfort" % (did, level, cost), {"level": level, "cost": cost})


@command
def drive_buy_up(ch, did=""):
    return _buy(ch, did, 1, "drives.buy_up_cost", "drive_buy_up")


@command
def drive_buy_down(ch, did=""):
    return _buy(ch, did, -1, "drives.buy_down_cost", "drive_buy_down")


@command
def set_drive_quest(ch, did="", quest=None, state=None, comfort_received=None):
    """The quest of a drive: its text, its state (none / taken / closed), the comfort flag (entered by hand)."""
    d = nbc._get(ch, "drives", "did", did)
    fields = {k: v for k, v in (("quest", quest), ("quest_state", state), ("comfort_received", comfort_received))
              if v is not None}
    d = nbc._check(replace(d, **fields))
    return commit(nbc._put(ch, "drives", "did", d), "set_drive_quest", "drive %s quest %s" % (did, d.quest_state))
