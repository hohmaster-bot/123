"""Item activation, combat start/end, end of cycle (gear.md, resources.md, buffs.md, narrative.md)."""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import effects as ef
from wp.model import derived_view as dv

SHORT = "short"
LONG = "long"
SHORT_REST_COST = 1        # 1 spirit: active until the end of the SHORT rest
LONG_REST_COST = 5         # 5 spirit: active until the end of the LONG rest


def active_until(cost):
    """1 spirit -> until short rest; 5 (and any other X) -> until long rest (OPEN_QUESTIONS Q14)."""
    return SHORT if int(cost) == SHORT_REST_COST else LONG


def _replace_item(ch, iid, **changes):
    found = False
    items = []
    for it in ch.items:
        if it.iid == iid:
            it = replace(it, **changes)
            found = True
        items.append(it)
    if not found:
        raise CommandError("no item with id %r" % (iid,))
    return replace(ch, items=tuple(items))


@command
def activate_item(ch, iid="", cost=None):
    """Activate an item for spirit (its 'activated' tab acts instead of the other)."""
    it = ch.item(iid)
    if it.activated:
        raise CommandError("already activated: %s" % it.name)
    spirit = it.activation_cost if cost is None else int(cost)
    if spirit <= 0:
        raise CommandError("item is not activatable: %s" % it.name)
    if ch.spirit_current < spirit:
        raise CommandError("not enough spirit: need %d, have %d" % (spirit, ch.spirit_current))
    new = replace(_replace_item(ch, iid, activated=True, active_until=active_until(spirit)),
                  spirit_current=ch.spirit_current - spirit)
    return commit(new, "activate_item", "%s activated for %d spirit (until %s rest)" % (
        it.name, spirit, active_until(spirit)))


@command
def deactivate_item(ch, iid=""):
    it = ch.item(iid)
    if not it.activated:
        raise CommandError("not activated: %s" % it.name)
    return commit(_replace_item(ch, iid, activated=False, active_until=""), "deactivate_item",
                  "%s deactivated" % it.name)


def switch_off_items(ch, rest_kind):
    """Short rest switches off 1-spirit items; long rest switches off all."""
    items = tuple(replace(it, activated=False, active_until="")
                  if it.activated and (rest_kind == LONG or it.active_until == SHORT) else it
                  for it in ch.items)
    return replace(ch, items=items)


@command
def start_combat(ch):
    if ch.in_combat:
        raise CommandError("combat already active")
    return commit(replace(ch, in_combat=True), "start_combat", "combat started")


@command
def end_combat(ch):
    """End of combat: temp HP gone (resources.md: usually lasts to end of combat),
    'until end of combat' statuses removed (buffs.md), morale ignored again.
    Overload and the morale scale are NOT touched (OPEN_QUESTIONS Q12, Q13)."""
    if not ch.in_combat:
        raise CommandError("no combat is active")
    new = replace(ch, in_combat=False, temp_hp=0, statuses=ef.end_combat(ch.statuses))
    return commit(new, "end_combat", "combat ended")


@command
def end_cycle(ch):
    """End of cycle: only adds attention (narrative.md), nothing else."""
    gain = dv.attention_per_cycle(ch)
    return commit(replace(ch, attention=ch.attention + gain), "end_cycle",
                  "attention +%d" % gain, {"gain": gain})
