"""Sheet editing commands: add a skill from the catalog (skills_list.md)."""
from dataclasses import replace

from wp.catalog import skills_catalog as sc
from wp.commands.base import CommandError, command, commit


@command
def add_skill(ch, catalog=None, tid="", sub=""):
    """Add a skill from a catalog template with 0 ranks. A family (param) needs a
    sub-skill name; several sub-skills of one family may exist, each with own ranks."""
    if catalog is None:
        raise CommandError("no skill catalog given")
    skill = sc.make_skill(catalog, tid, sub)
    if any(s.name == skill.name for s in ch.skills):
        raise CommandError("skill already on the sheet: %s" % sc.title(catalog, skill))
    new = replace(ch, skills=ch.skills + (skill,))
    return commit(new, "add_skill", "skill %s added" % skill.name)
