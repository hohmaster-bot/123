"""New character: ONLY perception and search (skills.md), groups Contact + Unarmed combat (weapons.md)."""
from wp.catalog import skills_catalog as sc
from wp.catalog import weapons_catalog as wc
from wp.model.character import Character


def new_character(catalog=None, weapon_catalog=None, **fields):
    """A fresh sheet. Skills: perception and search, 0 ranks; others come from the catalog.
    Weapons: Contact (level 0), the Unarmed combat node (scale 1, level 0) and its card."""
    catalog = catalog or sc.load_default()
    weapon_catalog = weapon_catalog or wc.load_default()
    fields.setdefault("weapons", wc.start_nodes(weapon_catalog))
    fields.setdefault("items", wc.start_items(weapon_catalog))
    return Character(skills=sc.start_skills(catalog), **fields)
