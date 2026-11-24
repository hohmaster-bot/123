"""Spell damage as data (package 25 F, RULES/combat.md "Spells damage", "Damage roll and pain"). No dice are rolled.

component(ch, d, level): the dice count and the flat part evaluated for the caster level (formulas of
wp/core/formula.py with the variable level; a broken formula counts 0, never below 0 dice), the die size, the type,
area, range, save. The damage roll is a die roll: the pain penalty and morale apply to it like to an attack roll,
so the view returns them (pain, morale, roll_modifier) next to the dice. The caster level is the character level
(assumption Q170).
"""
from wp.core import formula as cf
from wp.core import pain as pn
from wp.model import derived_view as dv


def _value(text, level):
    try:
        return cf.evaluate(str(text), {"level": level})
    except (cf.FormulaError, TypeError, ValueError):
        return 0


def component(d, level):
    return {"dice_count": max(0, _value(d.dice_count, level)), "die_size": d.die_size, "flat": _value(d.flat, level),
            "damage_type": d.damage_type, "area": d.area, "range": d.range, "save": d.save,
            "save_effect": d.save_effect}


def roll_modifiers(ch):
    pain = pn.penalty_bonus(dv.pain_total(ch), dv.pain_profile(ch)).value
    morale = dv.morale_bonus(ch)
    return {"pain": pain, "morale": morale, "roll_modifier": pain + morale}


def spell_damage(ch, spell, level=None):
    level = ch.level if level is None else int(level)
    return {"spid": spell.spid, "level": level, "components": tuple(component(d, level) for d in spell.damage),
            **roll_modifiers(ch)}


def view(ch):
    return tuple(spell_damage(ch, s) for s in ch.spells if s.damage)
