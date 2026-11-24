"""Actions as a resource (package 26 A, RULES/combat.md "Actions"; owner: base 3 per turn).

max = the constant actions.base + effects "actions_max" (spells, abilities, items, statuses; typed stacking like
every sheet target), never below 0; current = Character.actions_current (None = full). The zero-initiative tick and
the end of combat bring them back to max (like reactions). Nothing is spent automatically: cost_actions on attack
records, maneuvers, quick buttons and spells is shown, the player presses spend_actions. The combat.md costs
(shift 1, move 1, standard 2, full round 3, complete round 4) are the presets of the constant actions.cost_presets.
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import damage as dm
from wp.model import sheet_targets as stg
from wp.rules_data import rules as rd

TARGET = "actions_max"
NOT_ENOUGH = "not_enough_actions"


def actions_max(ch):
    return max(0, int(rd.const("actions.base", ch)) + stg.value(ch, TARGET))


def actions_current(ch):
    mx = actions_max(ch)
    return mx if ch.actions_current is None else max(0, ch.actions_current)


def actions_pool(ch):
    return dm.Pool(actions_current(ch), actions_max(ch))


def preset_cost(name, ch=None):
    """The action cost of a combat.md preset (shift, move, standard, full_round, complete_round)."""
    presets = rd.const("actions.cost_presets", ch)
    if name not in presets:
        raise CommandError("unknown action cost %r" % (name,), "unknown_action_cost", values=(name,))
    return int(presets[name])


def refill(ch):
    return replace(ch, actions_current=None)


def actions_view(ch):
    """current / max and the sources for a tooltip: (source, value, note) of the base and every actions_max effect."""
    p = actions_pool(ch)
    return {"current": p.current, "max": p.max,
            "sources": (("base", int(rd.const("actions.base", ch)), ""),) + stg.entries(ch, TARGET)}


@command
def spend_actions(ch, n=1):
    n = int(n)
    if n < 0:
        raise CommandError("cannot spend a negative number of actions", "cannot_spend_negative_amount")
    have = actions_current(ch)
    if have < n:
        raise CommandError("not enough actions: need %d, have %d" % (n, have), NOT_ENOUGH, values=(n, have))
    new = replace(ch, actions_current=have - n)
    return commit(new, "spend_actions", "actions -%d" % n, {"left": have - n})


@command
def restore_actions(ch):
    return commit(refill(ch), "restore_actions", "actions to max")
