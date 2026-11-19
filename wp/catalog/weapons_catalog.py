"""Weapon groups and weapon cards shipped as data (RULES/weapons.md, combat.md, catalog.md).

A weapon group is a list of weapons sharing bonuses created by mastery. A weapon may
be in any number of groups. Groups are mastery nodes (wp.core.weapons.Weapon).
Group "Basic/simple" is special (no qualification, cannot be trained).
"Unarmed combat" is an ordinary weapon card in group "Contact"; its own mastery node
(scale 1, parent Contact) carries its bonuses. A new character gets the Contact node,
the Unarmed combat node and the Unarmed combat card (item id "unarmed").
Qualification is written with the owner's words; the data file maps them to levels.
"""
import io
import json
import os
from dataclasses import dataclass
from typing import Optional, Tuple

from wp.core.weapons import Weapon
from wp.model.character import Item, WeaponEntry

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "weapons_default.json")
FORMAT = "wipefinder.weapons"
CONTACT = "contact"
UNARMED_COMBAT = "unarmed_combat"
UNARMED_ITEM = "unarmed"
BASIC = "basic_simple"

ITEM_FIELDS = ("kind", "groups", "required_level", "finesse", "price_sp", "damage_small",
               "damage_medium", "crit_range", "crit_mult", "range_ft", "dmg_type", "hands",
               "weight_l", "durability", "hp", "count", "armor", "shield", "max_dex", "skill_penalty",
               "damage_text", "variable", "damage_small2", "damage_medium2", "double", "no_parry")


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
    node: Optional[GroupTemplate] = None           # own mastery node (e.g. Unarmed combat, scale 1)


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
    levels = dict(data.get("qualification_levels", {}))
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
        if "qualification" in w:
            q = w["qualification"]
            if q not in levels:
                raise ValueError("unknown qualification %r for %s" % (q, w["wid"]))
            fields += [("qualification", q), ("required_level", int(levels[q]))]
        node = None
        if "node" in w:
            n = w["node"]
            node = GroupTemplate(gid=w["wid"], name=w["name"], name_en=w.get("name_en", ""),
                                 scale=int(n.get("scale", 1)), difficulty=int(n.get("difficulty", 1)),
                                 parents=tuple(n.get("parents", ())))
        weapons.append(WeaponTemplate(wid=w["wid"], name=w["name"], fields=tuple(fields), node=node))
    return WeaponCatalog(groups, tuple(weapons))


def load_default(path=DEFAULT_PATH):
    with io.open(path, encoding="utf-8") as f:
        return parse(f.read())


def _node_template(catalog, gid):
    for g in catalog.groups:
        if g.gid == gid:
            return g
    for w in catalog.weapons:
        if w.wid == gid and w.node is not None:
            return w.node
    raise KeyError("no weapon group or weapon node %r" % (gid,))


def group_entry(catalog, gid):
    """A mastery node at level 0 for a group (or a weapon's own node) from the catalog."""
    g = _node_template(catalog, gid)
    return WeaponEntry(Weapon(g.gid, g.scale, g.difficulty, parents=g.parents, basic=g.basic), g.name)


def group_weapons(catalog, gid):
    """Weapon ids listed in a group, in file order."""
    return tuple(w.wid for w in catalog.weapons if gid in dict(w.fields).get("groups", ()))


def start_nodes(catalog):
    """New character: Contact (level 0) and the Unarmed combat node (scale 1, level 0)."""
    return (group_entry(catalog, CONTACT), group_entry(catalog, UNARMED_COMBAT))


def start_items(catalog):
    """New character: the Unarmed combat card (always available, not held in the hands)."""
    return (make_item(catalog, UNARMED_COMBAT, UNARMED_ITEM),)


def is_light(item):
    """Light and finesse are ONE flag (column "F."); an unarmed strike is always light (owner)."""
    if item is None or item.iid == UNARMED_ITEM:
        return True
    return bool(item.finesse)


def make_item(catalog, wid, iid):
    """An Item from a weapon card."""
    w = catalog.weapon(wid)
    return Item(iid=iid, name=w.name, wkind=wid, **dict(w.fields))
