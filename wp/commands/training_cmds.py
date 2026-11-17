"""Purchase commands (training.md): buy_ability, buy_skill_rank, buy_weapon_grade, buy_base_slot.
Only source = training spends training points."""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import skills as sk
from wp.core import training as tr
from wp.core import weapons as wpn


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
def buy_skill_rank(ch, name="", source=tr.TRAINING):
    skills = list(ch.skills)
    i = next((k for k, s in enumerate(skills) if s.name == name), None)
    if i is None:
        raise CommandError("no skill %r" % (name,))
    s = skills[i]
    cost = sk.rank_step_cost(s.tier, s.ranks + 1, ch.level)
    skills[i] = replace(s, ranks=s.ranks + 1)
    new = replace(ch, skills=tuple(skills), training=_pay(ch, cost, source))
    return commit(new, "buy_skill_rank", "%s rank %d for %d" % (name, s.ranks + 1, cost), {"cost": cost})


@command
def buy_weapon_grade(ch, wid="", source=tr.TRAINING):
    catalog = ch.weapon_catalog()
    if wid not in catalog:
        raise CommandError("no weapon %r" % (wid,))
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
