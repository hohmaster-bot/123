"""Purchase commands (training.md): ability, skill rank, weapon grade, base slot,
shield and armor grades, languages.
Only source = training spends training points."""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import skills as sk
from wp.core import training as tr
from wp.core import weapons as wpn
from wp.model import derived_view as dv
from wp.model import ids
from wp.model.character import Language


def _pay(ch, cost, source):
    try:
        return tr.pay(ch.training, cost, source)
    except ValueError as e:
        raise CommandError(str(e))


@command
def buy_ability(ch, name="str", source=tr.TRAINING):
    a = ch.ability(name)
    cost = tr.ability_step_cost(a.base, a.race)
    abilities = dict(ch.abilities)
    abilities[name] = replace(a, base=a.base + 1)
    new = replace(ch, abilities=abilities, training=_pay(ch, cost, source))
    return commit(new, "buy_ability", "%s +1 for %d (%s)" % (name, cost, source), {"cost": cost})


@command
def buy_skill_rank(ch, name="", target=None, source=tr.TRAINING):
    """Raise a skill to a TARGET rank (default: one above the current effective rank).
    Specialized: ranks up to the level are free and follow the level automatically
    (skills.md [OWNER]); only ranks above the level are paid, all in one command."""
    skills = list(ch.skills)
    i = next((k for k, s in enumerate(skills) if s.name == name), None)
    if i is None:
        raise CommandError("no skill %r" % (name,))
    s = skills[i]
    have = sk.effective_ranks(s, ch.level)
    target = have + 1 if target is None else int(target)
    if target <= have:
        raise CommandError("%s already has rank %d" % (name, have))
    cost = sk.ranks_cost(s.tier, have, target, ch.level)
    skills[i] = replace(s, ranks=target)
    new = replace(ch, skills=tuple(skills), training=_pay(ch, cost, source))
    return commit(new, "buy_skill_rank", "%s rank %d -> %d for %d" % (name, have, target, cost), {"cost": cost})


@command
def buy_weapon_grade(ch, wid="", source=tr.TRAINING):
    catalog = ch.weapon_catalog()
    if wid not in catalog:
        raise CommandError("no weapon %r" % (wid,))
    if catalog[wid].basic:
        raise CommandError("group Basic/simple cannot be trained")
    if wpn.level(catalog, wid) >= wpn.MAX_LEVEL:
        raise CommandError("weapon already at level 12")
    cost = wpn.grade_cost(catalog, wid)
    entries = tuple(replace(e, weapon=replace(e.weapon, grades=e.weapon.grades + 1))
                    if e.weapon.name == wid else e for e in ch.weapons)
    new = replace(ch, weapons=entries, training=_pay(ch, cost, source))
    return commit(new, "buy_weapon_grade", "%s +1 grade for %d" % (wid, cost), {"cost": cost})


@command
def buy_base_slot(ch, source=tr.TRAINING):
    cost = tr.base_slot_cost(ch.base_slots, ch.level)
    new = replace(ch, base_slots=ch.base_slots + 1, training=_pay(ch, cost, source))
    return commit(new, "buy_base_slot", "base slot %d for %d" % (ch.base_slots + 1, cost), {"cost": cost})


def _next_grade(grades, current):
    i = grades.index(current)
    if i >= len(grades) - 1:
        raise CommandError("already at max grade")
    return grades[i + 1]


@command
def buy_shield_grade(ch, source=tr.TRAINING):
    """Shield proficiency: 100 per grade (none -> light -> heavy -> tower)."""
    nxt = _next_grade(tr.SHIELD_GRADES, ch.shield_grade)
    cost = tr.shield_grade_cost(ch.shield_grade)
    new = replace(ch, shield_grade=nxt, training=_pay(ch, cost, source))
    return commit(new, "buy_shield_grade", "shield -> %s for %d" % (nxt, cost), {"cost": cost})


@command
def buy_armor_grade(ch, source=tr.TRAINING):
    """Armor proficiency: 250 per grade (none -> light -> medium -> heavy)."""
    nxt = _next_grade(tr.ARMOR_GRADES, ch.armor_grade)
    cost = tr.armor_grade_cost(ch.armor_grade)
    new = replace(ch, armor_grade=nxt, training=_pay(ch, cost, source))
    return commit(new, "buy_armor_grade", "armor -> %s for %d" % (nxt, cost), {"cost": cost})


@command
def buy_language(ch, lid="", title="", native=False, projects=1, source=tr.TRAINING):
    """Language: non-native 30 * projects from the nearest native; native: first free, cheap 50 while natives < Int mod, else 100."""
    if not lid and not title:
        raise CommandError("language needs a name")
    lid = lid or ids.make_id(title, (lang.lid for lang in ch.languages))    # the player never types an id (D7)
    if any(lang.lid == lid for lang in ch.languages):
        raise CommandError("language already known: %r" % (lid,))
    try:
        cost = tr.language_cost(native, dv.natives(ch), dv.ability_mod(ch, "int"), projects)
    except ValueError as e:
        raise CommandError(str(e))
    lang = Language(lid, title or lid, bool(native))
    new = replace(ch, languages=ch.languages + (lang,), training=_pay(ch, cost, source))
    return commit(new, "buy_language", "language %s%s for %d" % (
        lid, " (native)" if native else "", cost), {"cost": cost})
