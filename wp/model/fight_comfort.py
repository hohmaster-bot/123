"""Comfort per fight (package 38, owner decision 5; RULES/resources.md "Comfort per fight"; closes Q280).

During a combat the program keeps the largest absolute morale (combat pressure) reached: Character.combat_morale_peak,
a stored base value of the combat state, cleared at the combat start and raised after every command while the
combat lasts (commands/base.py dispatch -> track). At the combat end the gain is offered as a reminder with an action
button (never added silently); the player accepts it with the command gain_fight_comfort (journal, undo).
gain = min(comfort.fight_max, max(0, min(|peak|, comfort.fight_cap) - comfort.fight_minus)): |morale| 1 -> 0,
2 -> 1, 5 -> 4, 8 -> 4. The three numbers are rule data, so they are const:<id> targets (the Mordon Wall of Bones adds
fight_minus +1 and fight_max -1: 2 -> 0, 5 -> 3; the buy-out takes both back).
"""
from dataclasses import replace

from wp.rules_data import rules as rd

CAP, MINUS, MAX = "comfort.fight_cap", "comfort.fight_minus", "comfort.fight_max"
SOURCE = "rule:comfort_per_fight"
TID = "fight_comfort"
TEXT = "trigger.fight_comfort"        # i18n key of the reminder text ({amount})
COMMAND = "gain_fight_comfort"


def morale_now(ch):
    from wp.model import formula_vars as fv
    return int(fv.guarded(ch, "morale", fv._morale))


def peak(ch):
    """The largest |morale| of the current (or the last) combat, the current morale included while it lasts."""
    p = int(ch.combat_morale_peak)
    return max(p, abs(morale_now(ch))) if ch.in_combat else p


def gain(ch, value=None):
    """Comfort for a combat whose largest |morale| is value (default: the stored peak)."""
    v = abs(int(peak(ch) if value is None else value))
    v = min(v, int(rd.const(CAP, ch)))
    return max(0, min(int(rd.const(MAX, ch)), v - int(rd.const(MINUS, ch))))


def track(ch):
    """After a command in combat: raise the stored peak to the current |morale| (never lowers it)."""
    if not getattr(ch, "in_combat", False):
        return ch
    p = abs(morale_now(ch))
    return replace(ch, combat_morale_peak=p) if p > ch.combat_morale_peak else ch


def offer(ch):
    """At the combat end (ch still holds the peak): a reminder note with the button "take N comfort" when N > 0."""
    from wp.core import triggers as tg
    from wp.model import trigger_view as tv
    n = gain(ch)
    if n <= 0:
        return ch
    t = tg.Trigger(TID, "combat_end", TEXT, "run_command", COMMAND, n)
    return tv._add(ch, [(SOURCE, t)])
