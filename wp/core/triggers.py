"""Triggers and their reminders (package 36, owner decision 6; RULES/buffs.md "Triggers").

Any carrier (item, race ability, class ability, feat, spell, status, injury, quirk) may hold triggers. A Trigger fires on
an EVENT the core has (cycle_end, combat_start, combat_end, zero_initiative, level_up, short_rest, long_rest,
hp_below_one) or by hand (manual: a button on the ability card; the owner has no "end of session" button, Q122).
A fired trigger never acts by itself: it becomes a TriggerNote = a reminder text + an optional action button (always
pressed by the player) + a handled mark; unhandled notes stay visible. Actions are a closed vocabulary (ACTIONS); the
command allowlist of run_command and both lists are data (wp/rules_data/triggers.json). Frozen records only.
"""
import io
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict

from wp.core.frozen import freeze_fields

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rules_data", "triggers.json")


def _load(path=PATH):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


TABLE = _load()
EVENTS = tuple(TABLE["events"])
ACTIONS = tuple(TABLE["actions"])
RUN_COMMANDS = tuple(TABLE["run_command_allowlist"])
MANUAL = "manual"


@dataclass(frozen=True)
class Trigger:
    tid: str
    event: str = MANUAL                # one of EVENTS or "manual"
    text: str = ""                     # the reminder text
    action: str = ""                   # "" (a reminder only) or one of ACTIONS
    target: str = ""                   # add_status: a status id; change_resource: a resource id; run_command: a command
    amount: int = 0                    # change_resource / add_pain / reduce_injury_points
    params: Dict[str, Any] = field(default_factory=dict)   # run_command parameters

    def __post_init__(self):
        freeze_fields(self, ("params",))


@dataclass(frozen=True)
class TriggerNote:
    nid: str                           # made by the program
    source: str                        # the carrier: "feat:<id>", "item:<id>", "status:<id>", "injury:<id>", ...
    tid: str
    event: str
    text: str = ""
    action: str = ""
    target: str = ""
    amount: int = 0
    params: Dict[str, Any] = field(default_factory=dict)
    handled: bool = False

    def __post_init__(self):
        freeze_fields(self, ("params",))


def check(trigger):
    """None or (reason id, values) of a trigger that does not fit the vocabulary."""
    if trigger.event not in EVENTS + (MANUAL,):
        return "unknown_event", (trigger.event,)
    if trigger.action and trigger.action not in ACTIONS:
        return "unknown_action", (trigger.action,)
    if trigger.action == "run_command" and trigger.target not in RUN_COMMANDS:
        return "command_not_allowed", (trigger.target,)
    return None
