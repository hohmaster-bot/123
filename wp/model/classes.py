"""Class system v0 (package 25 B; RULES/progression.md "Class system v0"). One class, no multiclass.

Without a class (class_id "") everything is as before: Character.bab, save_base, hit_die, divine_slots typed by hand.
With a class (Character.class_info, a snapshot of the catalog entry):
- BAB = level * class.bab_factor[growth], rounded down; Character.bab_override wins when set.
- base save = good: class.save_good_base + level // class.save_good_divisor; poor: level // class.save_poor_divisor;
  Character.save_override[save] wins when set (ASSUMPTION formulas, Q167).
- hit die = the class die (level_up cap and level 1 HP); 0 in the class = Character.hit_die.
- spellbook: the default discount of learn_spell; divine / spell_failure_mode: the failure mode default.
- professionalism: a class with its own professionalism refuses the 300 option; picks must be class skills.
"""
import math

from wp.model.class_types import GOOD, POOR
from wp.rules_data import rules as rd


def info(ch):
    return ch.class_info if ch.class_id and ch.class_info is not None else None


def class_bab(ci, level, ch=None):
    factor = rd.const("class.bab_factor", ch).get(ci.bab_growth, 0)
    return int(math.floor(level * float(factor)))


def class_save(ci, key, level, ch=None):
    if ci.saves.get(key, POOR) == GOOD:
        return int(rd.const("class.save_good_base", ch)) + level // int(rd.const("class.save_good_divisor", ch))
    return level // int(rd.const("class.save_poor_divisor", ch))


def bab(ch):
    ci = info(ch)
    if ci is None:
        return ch.bab
    return ch.bab_override if ch.bab_override is not None else class_bab(ci, ch.level, ch)


def save_base(ch, key):
    ci = info(ch)
    if ci is None:
        return int(ch.save_base.get(key, 0))
    if key in ch.save_override:
        return int(ch.save_override[key])
    return class_save(ci, key, ch.level, ch)


def hit_die(ch):
    ci = info(ch)
    return ci.hit_die if ci is not None and ci.hit_die > 0 else ch.hit_die


def divine(ch):
    ci = info(ch)
    return ci.divine if ci is not None else ch.divine_slots


def failure_mode_default(ch):
    """"" = decide by the divine flag (spell_view)."""
    ci = info(ch)
    return ci.spell_failure_mode if ci is not None else ""


def spellbook(ch):
    ci = info(ch)
    return bool(ci.spellbook) if ci is not None else False


def own_professionalism(ch):
    ci = info(ch)
    return bool(ci.own_professionalism) if ci is not None else False


def class_skills(ch):
    ci = info(ch)
    return ci.class_skills if ci is not None else None
