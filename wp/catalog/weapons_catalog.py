"""Weapon groups and weapon cards shipped as data (RULES/weapons.md, combat.md, catalog.md).

A weapon group is a list of weapons sharing bonuses created by mastery. A weapon may
be in any number of groups. Groups are mastery nodes (wp.core.weapons.Weapon).
Group "Basic/simple" is special (no qualification, cannot be trained).
"Unarmed combat" is an ordinary weapon card in group "Contact"; its own mastery node
(scale 1, parent Contact) carries its bonuses. A new character gets the Contact node,
the Unarmed combat node and the Unarmed combat card (item id "unarmed").
Qualification is written with the owner's words; the data file maps them to levels.
"""
from dataclasses import dataclass
from typing import Optional, Tuple

from wp.catalog import store as cs
from wp.core.weapons import Weapon
from wp.model.character import Item, WeaponEntry

WEAPONS = "weapons"                # catalog kinds (package 18): wp/catalog/data/weapons.json, weapon_groups.json
GROUPS = "weapon_groups"
CONTACT = "contact"
UNARMED_COMBAT = "unarmed_combat"
UNARMED_ITEM = "unarmed"
BASIC = "basic_simple"

ITEM_FIELDS = ("attack_kind", "kind", "groups", "required_level", "finesse", "price_sp", "damage_small",
               "damage_medium", "crit_range", "crit_mult", "range_ft", "dmg_type", "hands",
               "weight_l", "durability", "hp", "quantity", "armor", "shield", "max_dex", "skill_penalty",
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


def from_entries(group_entries, weapon_entries, levels):
    """A WeaponCatalog from catalog entries (store.merged of the two kinds) and the qualification levels."""
    groups = tuple(GroupTemplate(gid=g["id"], name=g["name"], name_en=g.get("name_en", ""),
                                 scale=int(g.get("scale", 1)), difficulty=int(g.get("difficulty", 1)),
                                 parents=tuple(g.get("parents", ())), basic=bool(g.get("basic", False)))
                   for g in group_entries)
    weapons = []
    for w in weapon_entries:
        fields = []
        for k in ITEM_FIELDS:
            if k in w:
                v = w[k]
                fields.append((k, tuple(v) if isinstance(v, list) else v))
        if "qualification" in w:
            q = w["qualification"]
            if q not in levels:
                raise ValueError("unknown qualification %r for %s" % (q, w["id"]))
            fields += [("qualification", q), ("required_level", int(levels[q]))]
        node = None
        if "node" in w:
            n = w["node"]
            node = GroupTemplate(gid=w["id"], name=w["name"], name_en=w.get("name_en", ""),
                                 scale=int(n.get("scale", 1)), difficulty=int(n.get("difficulty", 1)),
                                 parents=tuple(n.get("parents", ())))
        weapons.append(WeaponTemplate(wid=w["id"], name=w["name"], fields=tuple(fields), node=node))
    return WeaponCatalog(groups, tuple(weapons))


def load_default(user_folder=None):
    """Shipped weapon and group catalogs (+ the user layer from user_folder, package 18)."""
    def entries(kind):
        layers = cs.load_layers(kind, user_folder) if user_folder else cs.Layers(cs.load_shipped(kind), cs.Catalog(kind))
        return [e for e, _ in cs.merged(layers)], layers
    groups, _ = entries(GROUPS)
    weapons, wl = entries(WEAPONS)
    levels = dict((wl.shipped.meta if wl.shipped else {}).get("qualification_levels", {}))
    levels.update(dict(wl.user.meta).get("qualification_levels", {}))
    return from_entries(groups, weapons, levels)


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
