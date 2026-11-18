"""Item activation, combat start/end, end of cycle (gear.md, resources.md, buffs.md, narrative.md)."""
from dataclasses import replace

from wp.commands.base import CommandError, Result, command, commit
from wp.core import effects as ef
from wp.model import derived_view as dv
from wp.model import items as itm
from wp.model.character import LogEntry

SHORT = "short"
LONG = "long"
DAY = "day"                # until the end of the SHORT rest
DECADE = "decade"          # until the end of the LONG rest
UNTIL = {DAY: SHORT, DECADE: LONG}
NOT_SET = "activation price not set"


def _put(ch, item):
    return replace(ch, items=tuple(item if it.iid == item.iid else it for it in ch.items))


@command
def damage_item(ch, iid="", amount=0):
    """Damage to an item's HP (gear.md, package 6). Below 0 -> destroyed for good."""
    it = ch.item(iid)
    if it.destroyed:
        raise CommandError("destroyed: %s" % it.name)
    if amount < 0:
        raise CommandError("damage cannot be negative")
    p = dv.picks(ch, it)
    new = itm.damaged(it, amount, p)
    return commit(_put(ch, new), "damage_item", "%s -%d HP -> %d (%s)" % (
        it.name, amount, new.hp_current, itm.state(new, p)))


@command
def set_item_hp(ch, iid="", value=0):
    """Manual item HP (edit mode). A destroyed item cannot be healed; below 0 -> destroyed."""
    it = ch.item(iid)
    if it.destroyed:
        raise CommandError("destroyed: %s" % it.name)
    new = itm.with_hp(it, value)
    return commit(_put(ch, new), "set_item_hp", "%s HP = %d (%s)" % (
        it.name, new.hp_current, itm.state(new, dv.picks(ch, it))))


def _prices(item):
    return {k: v for k, v in ((DAY, item.activation_day), (DECADE, item.activation_decade)) if v > 0}


@command
def activate_item(ch, iid="", kind=None):
    """Activate an item for spirit: "day" (until the short rest) or "decade" (until the long
    rest), each with its own price on the card (gear.md [OWNER]). No price set -> soft refusal
    (the sheet does not change). One price set -> that one works."""
    it = ch.item(iid)
    if it.destroyed:
        raise CommandError("destroyed: %s" % it.name)
    if it.activated:
        raise CommandError("already activated: %s" % it.name)
    prices = _prices(it)
    if kind is None and len(prices) == 1:
        kind = next(iter(prices))
    if kind is not None and kind not in prices:
        prices = {}
    if not prices:
        return Result(state=ch, entry=LogEntry("activate_item", NOT_SET), events=(),
                      info={"refused": NOT_SET})
    if kind is None:
        raise CommandError("%s: choose day or decade" % it.name)
    spirit = prices[kind]
    if ch.spirit_current < spirit:
        raise CommandError("not enough spirit: need %d, have %d" % (spirit, ch.spirit_current))
    on = replace(itm.switch(it, True, dv.picks(ch, it)), active_until=UNTIL[kind])        # enchanted: current HP +N
    new = replace(_put(ch, on), spirit_current=ch.spirit_current - spirit)
    return commit(new, "activate_item", "%s activated for %d spirit (%s)" % (it.name, spirit, kind))


@command
def deactivate_item(ch, iid=""):
    it = ch.item(iid)
    if not it.activated:
        raise CommandError("not activated: %s" % it.name)
    return commit(_put(ch, itm.switch(it, False, dv.picks(ch, it))), "deactivate_item", "%s deactivated" % it.name)


def switch_off_items(ch, rest_kind):
    """Short rest switches off "day" items; long rest switches off all."""
    items = tuple(itm.switch(it, False, dv.picks(ch, it))
                  if it.activated and (rest_kind == LONG or it.active_until == SHORT) else it
                  for it in ch.items)
    return replace(ch, items=items)


@command
def start_combat(ch):
    if ch.in_combat:
        raise CommandError("combat already active")
    return commit(replace(ch, in_combat=True, balance_cap_hits=0), "start_combat", "combat started")


@command
def end_combat(ch):
    """End of combat: temp HP are NOT touched (button temp HP live to the short rest, buff temp HP
    live with the buff; resources.md [OWNER]),
    'until end of combat' statuses removed with their temp HP (buffs.md), overload reset to 0
    (resources.md [OWNER]), morale scale reset to 0 (defense.md [OWNER])."""
    if not ch.in_combat:
        raise CommandError("no combat is active")
    new = replace(ch, in_combat=False, overload=0, morale_scale=0, balance_cap_hits=0,
                  statuses=ef.end_combat(ch.statuses))
    return commit(new, "end_combat", "combat ended")


@command
def end_cycle(ch):
    """End of cycle (narrative.md [OWNER]): adds Attention (1 + levels 3, 6, 9... + drives 4+)
    and burns unspent OV, drops BP above max. Nothing else: it does not run a long rest (separate button)."""
    gain = dv.attention_per_cycle(ch)
    bp = min(ch.bp_current, dv.bp_max(ch))          # BP above max is dropped (package 8 C)
    return commit(replace(ch, attention=ch.attention + gain, ov=0, bp_current=bp), "end_cycle",
                  "attention +%d, OV %d burned" % (gain, ch.ov), {"gain": gain, "burned": ch.ov})


OV_MIN = 2


@command
def convert_attention(ch):
    """Spend 1 Attention -> max(2, Con mod) OV (training.md attention course, option 3)."""
    if ch.attention < 1:
        raise CommandError("no attention")
    gain = max(OV_MIN, dv.ability_mod(ch, "con"))
    return commit(replace(ch, attention=ch.attention - 1, ov=ch.ov + gain), "convert_attention",
                  "attention -1, OV +%d" % gain, {"gain": gain})


@command
def spend_ov(ch, n=1):
    """Spend OV (recipes, narrative)."""
    n = int(n)
    if n < 0 or n > ch.ov:
        raise CommandError("not enough OV: need %d, have %d" % (n, ch.ov))
    return commit(replace(ch, ov=ch.ov - n), "spend_ov", "OV -%d" % n)


@command
def burn_ov(ch):
    """Burn all unspent OV by hand."""
    return commit(replace(ch, ov=0), "burn_ov", "OV %d burned" % ch.ov)
