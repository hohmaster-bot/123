"""New character: ONLY perception and search (skills.md), groups Contact + Unarmed combat (weapons.md)."""
from wp.catalog import skills_catalog as sc
from wp.catalog import weapons_catalog as wc
from wp.model.character import Character


def new_character(catalog=None, weapon_catalog=None, **fields):
    """A fresh sheet. Skills: perception and search, 0 ranks; others come from the catalog.
    Weapon groups: Contact (level 0) and its child Unarmed combat (scale 1, level 0)."""
    catalog = catalog or sc.load_default()
    weapon_catalog = weapon_catalog or wc.load_default()
    fields.setdefault("weapons", wc.start_groups(weapon_catalog))
    return Character(skills=sc.start_skills(catalog), **fields)
