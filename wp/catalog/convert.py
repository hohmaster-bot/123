"""Catalog entry -> sheet record (package 18): items and statuses (weapons, armor, feats, skills have their own modules).
Fields kept only in the catalog (no sheet field): items ignore_bag_weight (a character flag). ilvl -> Item.ilvl (Q133)."""
from wp.core.damage import Pool
from wp.core.effects import Effect, Status
from wp.model.character import Item

ITEM_FIELDS = ("kind", "hands", "slot", "weight_l", "quantity", "consumable", "activation_day", "activation_decade",
               "on_use_status", "qualification_n", "base_slot_cost", "hp", "durability", "ilvl")


def effect(d):
    return Effect(**{k: tuple(v) if isinstance(v, (list, tuple)) else v for k, v in dict(d).items()})


def item_from_entry(entry, iid):
    fields = {k: entry[k] for k in ITEM_FIELDS if k in entry}
    return Item(iid=iid, name=entry["name"], effects_off=tuple(effect(e) for e in entry.get("effects_off", ())),
                effects_on=tuple(effect(e) for e in entry.get("effects_on", ())), source="catalog:" + entry["id"],
                **fields)


def status_from_entry(entry, sid=""):
    n = int(entry.get("charges_max", 0))
    return Status(entry["name"], sid=sid, effects=tuple(effect(e) for e in entry.get("effects", ())),
                  duration=entry.get("duration", "infinite"), full_ticks=int(entry.get("full_ticks", 0)),
                  charges=Pool(n, n) if n else None, charge_source=entry.get("charge_source", "own"),
                  charge_per_round=int(entry.get("charge_per_round", 0)),
                  cooldown_rounds=int(entry.get("cooldown_rounds", 0)), per_tick_hp=int(entry.get("per_tick_hp", 0)),
                  temp_hp_stacks=bool(entry.get("temp_hp_stacks", False)),
                  ignores_iterative=bool(entry.get("ignores_iterative", False)), active=False,
                  tags=tuple(str(t) for t in entry.get("tags", ())),
                  source="catalog:" + entry["id"])
