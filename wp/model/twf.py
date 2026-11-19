"""Two-weapon fighting (RULES/combat.md "Two-weapon fighting", Pathfinder TWF).

Penalties (primary hand / off hand):
  normal              -6 / -10
  off hand light      -4 / -8
  TWF feat            -4 / -4
  light + TWF feat    -2 / -2
An unarmed strike is always light; the other end of a double weapon counts as light.
Both attacks are ONE combination (one action, one attack tag). Class/race effects
"twf_reduction" lower the penalty, never below 0 (never a bonus).
A double weapon: the main end uses one-hand Str, the other end off-hand Str and the
second damage row.
"""
from dataclasses import dataclass, replace

from wp.catalog.feats_catalog import has_flag
from wp.catalog.weapons_catalog import is_light
from wp.core import effects as ef
from wp.model import attack_view as av
from wp.model import derived_view as dv
from wp.model.character import AttackRecord

TWF_FLAG = "twf"
REDUCTION = "twf_reduction"            # effect target: number that lowers both penalties
BASE = (-6, -10)
LIGHT_RELIEF = 2                       # each penalty
FEAT_RELIEF = (2, 6)                   # primary, off hand


@dataclass(frozen=True)
class TwfView:
    main: av.AttackView                # marked "main"
    off: av.AttackView                 # marked "off"
    main_penalty: int
    off_penalty: int
    light_off: bool
    feat: bool


def penalties(light_off, feat, reduction=0):
    """(primary, off) penalties from the table, then effect reduction; never above 0."""
    main, off = BASE
    if light_off:
        main, off = main + LIGHT_RELIEF, off + LIGHT_RELIEF
    if feat:
        main, off = main + FEAT_RELIEF[0], off + FEAT_RELIEF[1]
    r = max(0, int(reduction))
    return min(0, main + r), min(0, off + r)


def reduction(ch):
    """Sum of twf_reduction effects of active statuses and feats (class / race features)."""
    bonuses = dv.effect_bonuses(ch)
    return sum(b.value for b in bonuses if b.target == REDUCTION)


def _with_penalty(view, pen):
    if not pen:
        return view
    return replace(view, to_hit=view.to_hit + pen, to_hit_lines=view.to_hit_lines + (av.Line("two-weapon", pen),))


def _record(ch, rid):
    for r in ch.attacks:
        if r.rid == rid:
            return r
    raise KeyError("no attack record %r" % (rid,))


def _item(ch, iid):
    if iid == av.UNARMED:
        return next((it for it in ch.items if it.iid == av.UNARMED), None)
    return ch.item(iid)


def combination(ch, rid):
    """The two attacks of a record with the two-weapon toggle on."""
    main_rec = _record(ch, rid)
    if not main_rec.twf:
        raise ValueError("record %s has no two-weapon combination" % rid)
    main_item = _item(ch, main_rec.item)
    if main_rec.twf_off:
        off_rec = _record(ch, main_rec.twf_off)
        off_view = av.attack(ch, off_rec)
        light = is_light(_item(ch, off_rec.item))
        main_view = av.attack(ch, main_rec)
    else:                              # double weapon: the other end
        light = True
        main_view = av.attack(ch, replace(main_rec, grip=av.ONE))
        off_rec = AttackRecord(rid=main_rec.rid + ":off", item=main_rec.item, group=main_rec.group,
                               grip=av.OFF, stat=main_rec.stat)
        off_view = replace(av.attack(ch, off_rec), dice=av.dice_row(main_item, 2))
    feat = has_flag(ch, TWF_FLAG)
    p_main, p_off = penalties(light, feat, reduction(ch))
    return TwfView(main=_with_penalty(main_view, p_main), off=_with_penalty(off_view, p_off),
                   main_penalty=p_main, off_penalty=p_off, light_off=light, feat=feat)


def available(ch, record, off_rid=""):
    """Toggle allowed: a double weapon; two weapons in the hands; or an unarmed off-hand strike
    while at most one hand is used (an unarmed strike is always light)."""
    item = _item(ch, record.item)
    if item is not None and item.double and not off_rid:
        return True
    if off_rid:
        off = next((r for r in ch.attacks if r.rid == off_rid), None)
        if off is not None and off.item == av.UNARMED:
            return dv.hands_used(ch) <= 1
    held = [it for it in ch.items if it.in_hands and it.groups]
    return len(held) >= 2

