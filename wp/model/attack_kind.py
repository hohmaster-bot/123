"""Attack kinds melee / ranged / thrown (RULES/combat.md "Attack kinds", package 17, owner).

Kind: AttackRecord.kind if set, else the weapon card's Item.attack_kind (default melee).
Defaults are DATA (rules_settings): ranged = attack with Dex, no stat to damage; thrown = attack with Dex, Str to
damage x1; melee unchanged (Str by grip x1 / x0.5 / x1.5, Finesse rule for the attack).
Overrides on the record: stat (= the attack stat), damage_stat ("none" or a stat id), damage_mult (a number).
A positive stat modifier is multiplied and rounded down; a negative one counts once, as is (like the grip rule).
"""
import math
from fractions import Fraction

MELEE = "melee"
RANGED = "ranged"
THROWN = "thrown"
KINDS = (MELEE, RANGED, THROWN)
NONE = "none"


def kind(record, item):
    if record.kind:
        return record.kind
    return item.attack_kind if item is not None and item.attack_kind else MELEE


def default_attack_stat(ch, k):
    rs = ch.rules_settings
    return {RANGED: rs.ranged_attack_stat, THROWN: rs.thrown_attack_stat}.get(k)


def scaled(mod, mult):
    mod = int(mod)
    if mod <= 0:
        return mod
    return int(math.floor(mod * Fraction(str(mult))))


def damage_part(ch, record, item, ability_mod, grip_damage):
    """(label, value) of the stat part of the damage. grip_damage(mod, grip) = the melee grip rule."""
    k = kind(record, item)
    rs = ch.rules_settings
    if k == MELEE and record.damage_stat is None and record.damage_mult is None:
        return "str:" + record.grip, grip_damage(ability_mod(ch, "str"), record.grip)
    stat = record.damage_stat
    if stat is None:
        stat = {RANGED: rs.ranged_damage_stat, THROWN: rs.thrown_damage_stat}.get(k, "str")
    if stat == NONE:
        return "damage stat: none", 0
    mult = record.damage_mult
    if mult is None:
        if k == MELEE:
            return "%s:%s" % (stat, record.grip), grip_damage(ability_mod(ch, stat), record.grip)
        mult = {RANGED: rs.ranged_damage_mult, THROWN: rs.thrown_damage_mult}.get(k, 1)
    return "%s:x%s" % (stat, mult), scaled(ability_mod(ch, stat), mult)
