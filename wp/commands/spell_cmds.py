"""Spells (RULES/training.md "Other purchases", progression.md "Spell mastery"; package 15):
learn_spell and buy_spell_upgrade. Only source "training" spends training points; no refunds."""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import magic as mg
from wp.core import training as tr
from wp.model import ids
from wp.model import sheet_targets as stg
from wp.model.character import Spell, SpellUpgrade

CIRCLES = mg.CIRCLES               # circles 0-9 (classes_magic.md, package 16 B)


def _pay(ch, cost, source):
    try:
        return tr.pay(ch.training, cost, source)
    except ValueError as e:
        raise CommandError(str(e), "rule_refused")


@command
def learn_spell(ch, name="", circle=1, discount=None, source=tr.TRAINING):
    """New spell = 20 + 10 * circle^2; discount=True for classes with a book or learning from a teacher or a scroll:
    half price (training.md)."""
    if not name:
        raise CommandError("a spell needs a name", "spell_needs_name")
    if int(circle) not in CIRCLES:
        raise CommandError("circle must be 0..9", "circle_must_0_9")
    if discount is None:               # package 25 B: the class spellbook flag is the default
        from wp.model import classes as klass
        discount = klass.spellbook(ch)
    cost = tr.spell_cost(circle, bool(discount), stg.value(ch, "spell_price_discount"))
    sp = Spell(ids.make_id(name, (s.spid for s in ch.spells)), name, int(circle), source, cost)
    new = replace(ch, spells=ch.spells + (sp,), training=_pay(ch, cost, source))
    return commit(new, "learn_spell", "spell %s (circle %d) for %d" % (sp.spid, sp.circle, cost),
                  {"cost": cost, "spid": sp.spid})


def slots_used(spell):
    return sum(u.slots for u in spell.upgrades)


def upgrade_slots(spell, name, metamagic=0):
    """Slots an upgrade takes (progression.md): metamagic = its circles; otherwise 1, a second identical upgrade 2
    (each further identical one 1 more: assumption Q106)."""
    if metamagic > 0:
        return int(metamagic)
    return 1 + sum(1 for u in spell.upgrades if u.name == name and u.metamagic == 0)


@command
def buy_spell_upgrade(ch, spid="", name="", metamagic=0, source=tr.TRAINING):
    """Spell mastery: one upgrade = 25 * (1 + circle^2); three slots per spell (progression.md)."""
    sp = next((s for s in ch.spells if s.spid == spid), None)
    if sp is None:
        raise CommandError("no spell %r" % (spid,), "no_spell", values=(spid,))
    if not name:
        raise CommandError("an upgrade needs a name", "upgrade_needs_name")
    if int(metamagic) < 0:
        raise CommandError("metamagic circles cannot be negative", "metamagic_circles_cannot_negative")
    need = upgrade_slots(sp, name, int(metamagic))
    if slots_used(sp) + need > tr.MASTERY_SLOTS:
        raise CommandError("not enough slots: %s uses %d of %d, the upgrade needs %d" % (
            spid, slots_used(sp), tr.MASTERY_SLOTS, need), "not_enough_slots_uses", values=(
            spid, slots_used(sp), tr.MASTERY_SLOTS, need))
    cost = tr.mastery_cost(sp.circle)
    up = SpellUpgrade(name, need, int(metamagic))
    spells = tuple(replace(s, upgrades=s.upgrades + (up,)) if s.spid == spid else s for s in ch.spells)
    new = replace(ch, spells=spells, training=_pay(ch, cost, source))
    return commit(new, "buy_spell_upgrade", "%s +%s (%d slots) for %d" % (spid, name, need, cost),
                  {"cost": cost, "slots": need})


SAVE_IDS = ("fort", "ref", "will", "none")


def _damage_types():
    from wp.catalog import store as cs
    return {e["id"] for e in cs.load_shipped("damage_types").entries}


def _component(d):
    from wp.core import formula as fm
    from wp.model.class_types import SpellDamage
    from wp.rules_data import rules as rd
    d = d if isinstance(d, SpellDamage) else SpellDamage(**{k: (str(v) if k in ("dice_count", "flat", "range") else v)
                                                             for k, v in dict(d).items()})
    if d.damage_type not in _damage_types():
        raise CommandError("unknown damage type %r" % (d.damage_type,), "unknown_damage_type", values=(d.damage_type,))
    if d.area not in rd.const("spells.areas"):
        raise CommandError("unknown area %r" % (d.area,), "unknown_area", values=(d.area,))
    if d.save not in SAVE_IDS:
        raise CommandError("save must be fort, ref, will or none", "unknown_save", values=(d.save,))
    if int(d.die_size) < 1:
        raise CommandError("a die has at least 1 side", "bad_die_size", values=(d.die_size,))
    for text in (d.dice_count, d.flat):
        try:
            fm.evaluate(text, {"level": 1})
        except fm.FormulaError as e:
            raise CommandError("bad formula %r: %s" % (text, e), "bad_effect_formula", values=(str(e),))
    return d


@command
def set_spell_damage(ch, spid="", damage=()):
    """The damage components of a learned spell (package 25 F): a list of {dice_count, die_size, flat, damage_type,
    area, range, save, save_effect}; an empty list removes the damage."""
    if not any(s.spid == spid for s in ch.spells):
        raise CommandError("no spell %r" % (spid,), "not_found", values=("spells", spid))
    comps = tuple(_component(d) for d in damage)
    spells = tuple(replace(s, damage=comps) if s.spid == spid else s for s in ch.spells)
    return commit(replace(ch, spells=spells), "set_spell_damage", "%s damage (%d parts)" % (spid, len(comps)))
