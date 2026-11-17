"""Sheet editing commands: add a skill (skills_list.md) or a feat (feats catalog)."""
from dataclasses import replace

from wp.catalog import skills_catalog as sc
from wp.commands.base import CommandError, command, commit
from wp.core import training as tr
from wp.model.character import Feat


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


@command
def add_feat(ch, catalog=None, fid="", source="training"):
    """Take a feat from the catalog. The price is the catalog's (feat price is set by its author and
    cannot be changed on purchase, training.md); only source 'training' spends training points."""
    if catalog is None:
        raise CommandError("no feat catalog given")
    t = catalog.get(fid)
    if any(f.fid == fid for f in ch.feats):
        raise CommandError("feat already on the sheet: %s" % fid)
    price = t.cost
    try:
        left = tr.pay(ch.training, price, source)
    except ValueError as e:
        raise CommandError(str(e))
    feat = Feat(fid=fid, title=t.name, flags=t.flags, source=source, cost=price)
    new = replace(ch, feats=ch.feats + (feat,), training=left)
    return commit(new, "add_feat", "feat %s (%s, %d)" % (fid, source, price), {"cost": price})
