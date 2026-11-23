"""Sheet editing commands: add a skill (skills_list.md) or a feat (feats catalog)."""
from dataclasses import replace

from wp.catalog import skills_catalog as sc
from wp.commands.base import CommandError, command, commit
from wp.core import derived as dvc
from wp.core import training as tr
from wp.model.character import Feat
from wp.rules_data import rules as rd


@command
def add_skill(ch, catalog=None, tid="", sub=""):
    """Add a skill from a catalog template with 0 ranks. A family (param) needs a
    sub-skill name; several sub-skills of one family may exist, each with own ranks."""
    if catalog is None:
        raise CommandError("no skill catalog given", "no_skill_catalog_given")
    skill = sc.make_skill(catalog, tid, sub)
    if any(s.name == skill.name for s in ch.skills):
        raise CommandError("skill already on the sheet: %s" % sc.title(catalog, skill), "skill_already_sheet", values=sc.title(catalog, skill))
    new = replace(ch, skills=ch.skills + (skill,))
    return commit(new, "add_skill", "skill %s added" % skill.name)


@command
def add_feat(ch, catalog=None, fid="", source="training"):
    """Take a feat from the catalog. The price is the catalog's (feat price is set by its author and
    cannot be changed on purchase, training.md); only source 'training' spends training points."""
    if catalog is None:
        raise CommandError("no feat catalog given", "no_feat_catalog_given")
    t = catalog.get(fid)
    if any(f.fid == fid for f in ch.feats):
        raise CommandError("feat already on the sheet: %s" % fid, "feat_already_sheet", values=(fid,))
    price = t.cost
    try:
        left = tr.pay(ch.training, price, source)
    except ValueError as e:
        raise CommandError(str(e), "rule_refused")
    feat = Feat(fid=fid, title=t.name, flags=t.flags, source=source, cost=price, effects=t.effects,
                granted_maneuvers=t.granted_maneuvers, is_stance=t.is_stance)
    new = replace(ch, feats=ch.feats + (feat,), training=left)
    return commit(new, "add_feat", "feat %s (%s, %d)" % (fid, source, price), {"cost": price})


@command
def set_size(ch, size="medium"):
    """Race size: small / medium / large only (combat.md "Size and speed")."""
    if size not in dvc.SIZES:
        raise CommandError("size must be one of %s" % ", ".join(dvc.SIZES), "size_must_one", values=", ".join(dvc.SIZES))
    return commit(replace(ch, size=size), "set_size", "size %s" % size)


@command
def set_base_speed(ch, feet=None):
    """Race base speed in feet (default: the rule constant speed.base_ft)."""
    feet = rd.const("speed.base_ft", ch) if feet is None else feet
    if int(feet) < 0:
        raise CommandError("speed cannot be negative", "speed_cannot_negative")
    return commit(replace(ch, base_speed=int(feet)), "set_base_speed", "base speed %d ft" % int(feet))


@command
def remove_feat(ch, fid=""):
    """Remove a feat from the sheet; its effects go with it. No training refund (the rules give none)."""
    if not any(f.fid == fid for f in ch.feats):
        raise CommandError("no feat %r on the sheet" % (fid,), "no_feat_sheet", values=(fid,))
    stance = None if ch.active_stance == fid else ch.active_stance       # removing the active stance clears it
    return commit(replace(ch, feats=tuple(f for f in ch.feats if f.fid != fid), active_stance=stance),
                  "remove_feat", "feat %s removed" % fid)


@command
def set_active_stance(ch, fid=None):
    """Choose the active stance (a stance feat the character owns), or None for no stance (combat.md, Q74)."""
    if fid is None:
        return commit(replace(ch, active_stance=None), "set_active_stance", "no stance")
    feat = next((f for f in ch.feats if f.fid == fid), None)
    if feat is None:
        raise CommandError("feat %r is not on the sheet" % (fid,), "feat_not_sheet", values=(fid,))
    if not feat.is_stance:
        raise CommandError("feat %s is not a stance" % (feat.title or fid), "feat_not_stance", values=(feat.title or fid,))
    return commit(replace(ch, active_stance=fid), "set_active_stance", "stance %s" % (feat.title or fid))
