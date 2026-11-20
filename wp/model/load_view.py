"""Carried weight, bag and load (RULES/gear.md "Weight", "Bag"). Computed on read (D6).
Split out of derived_view (module size); derived_view re-exports these names."""
from dataclasses import dataclass

from wp.core import derived as cdv
from wp.model import derived_view as dv
from wp.model import items as itm


def in_bag(it):
    """Bag = carried, not worn, not in the hands, not a weapon (gear.md "Bag")."""
    return it.carried and not it.equipped and not it.in_hands and it.kind != "weapon"


def bag_weight_l(ch):
    return sum(itm.weight_l(it) for it in ch.items if in_bag(it))


def carried_weight_l(ch):
    """Carried weight; the bag counts unless ignore_bag_weight is on (package 8 E)."""
    return sum(itm.weight_l(it) for it in ch.items
               if it.carried and not (ch.ignore_bag_weight and in_bag(it)))


@dataclass(frozen=True)
class WeightView:
    carried_l: int
    bag_l: int
    ignore_bag_weight: bool
    load: str


def condition_tags(ch):
    """Display-only condition tags (package 9 E) for the UI icons; no calculation reads them."""
    return {"items": {it.iid: it.condition_tag for it in ch.items},
            "statuses": {s.sid: s.condition_tag for s in ch.statuses},
            "feats": {f.fid: f.condition_tag for f in ch.feats}}


def weight_view(ch):
    return WeightView(carried_l=carried_weight_l(ch), bag_l=bag_weight_l(ch),
                      ignore_bag_weight=ch.ignore_bag_weight, load=load_status(ch))


def load_status(ch):
    return cdv.load_status(carried_weight_l(ch), dv.ability_mod(ch, "str"))


def overloaded(ch):
    return load_status(ch) == cdv.LOAD_OVER
