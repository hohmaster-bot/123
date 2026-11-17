"""Weapon groups and weapon cards shipped as data (RULES/weapons.md, combat.md, catalog.md).

A weapon group is a list of weapons sharing bonuses created by mastery. A weapon may
be in any number of groups. Groups are mastery nodes (wp.core.weapons.Weapon).
Group "Basic/simple" is special (no qualification, cannot be trained).
New characters get "Contact" (level 0) and its child "Unarmed combat" (scale 1, level 0).
Weapon stats come from the owner's table (not in the default file yet).
"""
import io
import json
import os
from dataclasses import dataclass
from typing import Tuple

from wp.core.weapons import Weapon
from wp.model.character import Item, WeaponEntry

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "weapons_default.json")
FORMAT = "wipefinder.weapons"
CONTACT = "contact"
UNARMED_COMBAT = "unarmed_combat"
BASIC = "basic_simple"
START_GROUPS = (CONTACT, UNARMED_COMBAT)

ITEM_FIELDS = ("kind", "groups", "required_level", "finesse", "price_sp", "damage_small",
               "damage_medium", "crit_range", "crit_mult", "range_ft", "dmg_type", "hands",
               "weight_l", "durability", "hp", "count", "armor", "shield", "max_dex", "skill_penalty")


@dataclass(frozen=True)
class GroupTemplate:
    gid: str
    name: str
    name_en: str = ""
    scale: int = 1
    difficulty: int = 1
    parents: Tuple[str, ...] = ()
    basic: bool = False


@dataclass(frozen=True)
class WeaponTemplate:
    wid: str
    name: str
    fields: Tuple[Tuple[str, object], ...] = ()   # Item field values from the card


@dataclass(frozen=True)
class WeaponCatalog:
    groups: Tuple[GroupTemplate, ...] = ()
    weapons: Tuple[WeaponTemplate, ...] = ()

    def group(self, gid):
        for g in self.groups:
            if g.gid == gid:
                return g
        raise KeyError("no weapon group %r" % (gid,))

    def weapon(self, wid):
        for w in self.weapons:
            if w.wid == wid:
                return w
        raise KeyError("no weapon %r" % (wid,))


def parse(text):
    data = json.loads(text)
    if data.get("format") != FORMAT:
        raise ValueError("not a WipeFinder weapon catalog")
    groups = tuple(GroupTemplate(gid=g["gid"], name=g["name"], name_en=g.get("name_en", ""),
                                 scale=int(g.get("scale", 1)), difficulty=int(g.get("difficulty", 1)),
                                 parents=tuple(g.get("parents", ())), basic=bool(g.get("basic", False)))
                   for g in data.get("groups", ()))
    weapons = []
    for w in data.get("weapons", ()):
        fields = []
        for k in ITEM_FIELDS:
            if k in w:
                v = w[k]
                fields.append((k, tuple(v) if isinstance(v, list) else v))
        weapons.append(WeaponTemplate(wid=w["wid"], name=w["name"], fields=tuple(fields)))
    return WeaponCatalog(groups, tuple(weapons))


def load_default(path=DEFAULT_PATH):
    with io.open(path, encoding="utf-8") as f:
        return parse(f.read())


def group_entry(catalog, gid):
    """A mastery node at level 0 for a group from the catalog."""
    g = catalog.group(gid)
    return WeaponEntry(Weapon(g.gid, g.scale, g.difficulty, parents=g.parents, basic=g.basic), g.name)


def start_groups(catalog):
    """New character: Contact (level 0) and Unarmed combat (scale 1, level 0)."""
    return tuple(group_entry(catalog, gid) for gid in START_GROUPS)


def make_item(catalog, wid, iid):
    """An Item from a weapon card."""
    w = catalog.weapon(wid)
    return Item(iid=iid, name=w.name, **dict(w.fields))
