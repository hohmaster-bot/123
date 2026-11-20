"""Spell casting penalties of armor and shields (RULES/gear.md "Armor", classes_magic.md, package 9 I).
Computed on read (D6).

- Item fields: spell_penalty_mana (extra mana cost, >= 0) and spell_failure_pct (0..100).
- Sources: worn items + shields held in a hand that work (HP 0 = taken off, gives nothing).
- Sum of the sources, then plus the effects of target "spell_penalty_mana" / "spell_failure_pct"
  (normal bonus entries: a feat with value -2 lowers the penalty by 2; a large negative value
  ignores it); floor 0; the failure chance is capped at 100.
- Mana casters: the extra cost is added to every mana spell (circle 1+), paid in any mix of mana and
  balance. Mana level = the character's level (package 10, Q49): one spell (its cost + the armor
  penalty) can cost at most that much mana; above it the spell cannot be cast (clear refusal).
- Failure chance: slot casters always have it; mana casters only when the chance is > 0.
  The program rolls no dice: the player reports the roll (command resolve_spell_failure).
- Failure mode: "cancel" (the spell is not cast) or "zero_balance" (the spell works, balance -> 0
  as an extra cost). Default: divine casters (Character.divine_slots) zero_balance, others cancel.
"""
from dataclasses import dataclass

from wp.core import magic as mg
from wp.model import derived_view as dv
from wp.model import records as rec

TARGET_MANA = "spell_penalty_mana"
TARGET_FAILURE = "spell_failure_pct"
CANCEL = "cancel"
ZERO_BALANCE = "zero_balance"
MODES = (CANCEL, ZERO_BALANCE)
MAX_PCT = 100


@dataclass(frozen=True)
class SpellView:
    mana_penalty: int                  # extra mana per mana spell (after reductions)
    mana_penalty_items: int            # sum of the items before reductions
    failure_pct: int                   # chance shown to the player (0 when it does not apply)
    failure_items: int                 # sum of the items before reductions
    failure_applies: bool
    failure_mode: str
    sources: tuple                     # item ids that give a penalty


def _sources(ch):
    worn = [it for it in ch.items if it.equipped and dv.works(ch, it)]
    held = [it for it in ch.items if it.in_hands and not it.equipped and rec.is_shield(it) and dv.works(ch, it)]
    return worn + held


def mana_penalty(ch):
    items = sum(max(0, it.spell_penalty_mana) for it in _sources(ch))
    return max(0, items + dv.total(ch, TARGET_MANA))


def failure_pct_raw(ch):
    items = sum(max(0, it.spell_failure_pct) for it in _sources(ch))
    return min(MAX_PCT, max(0, items + dv.total(ch, TARGET_FAILURE)))


def failure_applies(ch):
    if ch.caster == mg.SLOTS:
        return True
    return ch.caster == mg.MAGE and failure_pct_raw(ch) > 0


def failure_mode(ch):
    if ch.spell_failure_mode:
        return ch.spell_failure_mode
    return ZERO_BALANCE if ch.divine_slots else CANCEL


def view(ch):
    src = _sources(ch)
    applies = failure_applies(ch)
    return SpellView(mana_penalty=mana_penalty(ch),
                     mana_penalty_items=sum(max(0, it.spell_penalty_mana) for it in src),
                     failure_pct=failure_pct_raw(ch) if applies else 0,
                     failure_items=sum(max(0, it.spell_failure_pct) for it in src),
                     failure_applies=applies, failure_mode=failure_mode(ch),
                     sources=tuple(it.iid for it in src if it.spell_penalty_mana > 0 or it.spell_failure_pct > 0))


def mana_level(ch):
    """The most one spell may cost in mana, penalty included = the character's level (Q49) + effects "mana_level"
    (package 17)."""
    from wp.model import sheet_targets as stg
    return int(ch.level) + stg.value(ch, "mana_level")


def over_limit(ch, mana_cost, extra):
    """None if the cast fits the mana level, else the refusal text (no silent cut)."""
    lvl = mana_level(ch)
    if mana_cost > lvl:
        return "cannot cast: spell cost %d is above the mana level %d" % (mana_cost, lvl)
    if mana_cost + extra > lvl:
        return "cannot cast: spell cost %d + armor penalty %d is above the mana level %d" % (mana_cost, extra, lvl)
    return None
