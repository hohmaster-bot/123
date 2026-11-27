"""Comfort per fight (package 38, owner decision 5; wp/model/fight_comfort.py, RULES/resources.md).

gain_fight_comfort(): after the combat, add the comfort of that combat (from the stored largest |morale|) and clear
    the peak so it is taken once. It is the action button of the reminder the combat end leaves (the player accepts;
    the program never adds it silently). Comfort may go over its max (resources.md "Over max": spent down by the
    next session), so the gain is not cut at the max.
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.model import fight_comfort as fc


@command
def gain_fight_comfort(ch):
    if ch.in_combat:
        raise CommandError("the combat is still on", "combat_still_active")
    n = fc.gain(ch)
    if n <= 0:
        raise CommandError("no comfort for the last combat", "no_fight_comfort")
    new = replace(ch, comfort_current=ch.comfort_current + n, combat_morale_peak=0)
    return commit(new, "gain_fight_comfort", "comfort +%d for the fight" % n, {"gain": n})
