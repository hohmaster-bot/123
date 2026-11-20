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
def learn_spell(ch, name="", circle=1, discount=False, source=tr.TRAINING):
    """New spell = 20 + 10 * circle^2; discount=True for classes with a book or learning from a teacher or a scroll:
    half price (training.md)."""
    if not name:
        raise CommandError("a spell needs a name", "spell_needs_name")
    if int(circle) not in CIRCLES:
        raise CommandError("circle must be 0..9", "circle_must_0_9")
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
