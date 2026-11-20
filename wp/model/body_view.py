"""Pain, morale, size and speed of a character (RULES/resources.md, defense.md, combat.md). Computed on read
(D6). Split out of derived_view (module size); derived_view re-exports these names."""
import math
from dataclasses import replace
from fractions import Fraction

from wp.core import bonuses as bo
from wp.core import derived as dv
from wp.core import pain as pn
from wp.model import derived_view as dvw


def pain_total(ch):
    return pn.total_pain(ch.pain, ch.hp_current)


def pain_profile(ch):
    """The pain profile with the rule switch ignore_pain applied: it REUSES PainProfile.no_penalty (pain gives no
    penalty, the pain count and death stay; package 14 G)."""
    if ch.rules_settings.ignore_pain and not ch.pain_profile.no_penalty:
        return replace(ch.pain_profile, no_penalty=True)
    return ch.pain_profile


def pain_penalty(ch):
    return pn.penalty(pain_total(ch), pain_profile(ch))


def is_dead(ch):
    return pn.is_dead(pain_total(ch), ch.pain_profile)


def morale_bonus(ch):
    """ignore_negative_morale (rule switch, package 14 G): a negative scale counts as 0."""
    scale = ch.morale_scale
    if ch.rules_settings.ignore_negative_morale:
        scale = max(0, scale)
    return dv.morale_bonus(scale, ch.in_combat)


def size_mod(ch):
    """Size to attack and AC: small +1, medium 0, large -1 (combat.md)."""
    return dv.size_mod(ch.size)


def size_cmb(ch):
    """Size to CMB and CMD: small -1, medium 0, large +1 (opposite sign, combat.md)."""
    return dv.size_cmb(ch.size)


def armor_slowdown(ch):
    """Slowdown of the worn armor (on the doll and working, the same items as the armor bonus; the largest
    one counts, like the armor bonus), minus effects "armor_slowdown_reduction" (value "all" = none left)."""
    pen = max([it.speed_penalty_ft for it in dvw._equipped(ch)] or [0])
    return dv.armor_slowdown(pen, dvw.total(ch, bo.SLOWDOWN_REDUCTION))


def speed(ch):
    """Speed in feet = race base speed + typed bonuses (target "speed": items, abilities, statuses,
    feats) - armor slowdown + overload -10 ft (gear.md); then * speed_multiplier, rounded down (rule switch, pkg 14 G)."""
    s = dv.speed(ch.base_speed, dvw.total(ch, bo.SPEED), dvw.overloaded(ch), armor_slowdown(ch))
    return int(math.floor(s * Fraction(str(ch.rules_settings.speed_multiplier))))
