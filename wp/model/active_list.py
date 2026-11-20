"""Active list for the UI (package 13 E; data only). Computed on read (D6).

Sections:
  - attacks: available attack records (weapons in the hands + the unarmed attack);
  - activated_items: worn / held items that are activated now;
  - item_charges: charges of worn / held items (Item.usage, package 14 B, Q94);
  - statuses: active statuses, with the hidden flag (hidden = display only);
  - consumables: consumable items with their quantity and the spent flag.
"""
from dataclasses import dataclass
from typing import Optional, Tuple

from wp.model import attack_view as av
from wp.model import derived_view as dv
from wp.model import items as itm


@dataclass(frozen=True)
class ActiveAttack:
    record: str
    weapon: str
    to_hit: int
    damage: int


@dataclass(frozen=True)
class ActiveCharge:
    iid: str
    name: str
    current: int
    max: int


@dataclass(frozen=True)
class ActiveStatus:
    sid: str
    name: str
    remaining: int
    charges: Optional[Tuple[int, int]]
    hidden: bool


@dataclass(frozen=True)
class ActiveConsumable:
    iid: str
    name: str
    quantity: int
    spent: bool


@dataclass(frozen=True)
class ActiveList:
    attacks: Tuple[ActiveAttack, ...]
    activated_items: Tuple[str, ...]
    item_charges: Tuple[ActiveCharge, ...]
    statuses: Tuple[ActiveStatus, ...]
    consumables: Tuple[ActiveConsumable, ...]


def active_list(ch):
    attacks = tuple(ActiveAttack(a.record, a.weapon, a.to_hit, a.damage) for a in av.all_attacks(ch) if a.available)
    activated = tuple(it.iid for it in ch.items if (it.equipped or it.in_hands) and dv.item_active(it))
    charges = tuple(ActiveCharge(it.iid, it.name, it.usage.charges_current, it.usage.charges_max) for it in ch.items
                    if (it.equipped or it.in_hands) and it.usage is not None and it.usage.charges_max > 0)
    statuses = tuple(ActiveStatus(s.sid, s.name, s.remaining,
                                  (s.charges.current, s.charges.max) if s.charges is not None else None, s.hidden)
                     for s in ch.statuses if s.active)
    consumables = tuple(ActiveConsumable(it.iid, it.name, it.quantity, itm.spent(it)) for it in ch.items if it.consumable)
    return ActiveList(attacks, activated, charges, statuses, consumables)
