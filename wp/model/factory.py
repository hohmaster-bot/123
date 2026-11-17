"""New character (skills.md / skills_list.md): starts with ONLY perception and search."""
from wp.catalog import skills_catalog as sc
from wp.model.character import Character


def new_character(catalog=None, **fields):
    """A fresh sheet. Skills: perception and search, 0 ranks; others come from the catalog."""
    catalog = catalog or sc.load_default()
    return Character(skills=sc.start_skills(catalog), **fields)
