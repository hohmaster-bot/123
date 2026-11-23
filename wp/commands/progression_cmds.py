"""Progression and narrative purchases (RULES/progression.md, training.md, injuries.md, narrative.md; package 15):
level_up, exchange_comfort, remove_ot_comfort, remove_ot_attention, raise_heal_rating, buy_attention_course,
buy_reaction, buy_seed, sprout_seed, make_language_native, promote_skill, buy_professionalism.
Only source "training" spends training points; no refunds anywhere."""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import injuries as inj
from wp.core import skills as sk
from wp.core import training as tr
from wp.model import derived_view as dv
from wp.model import ids
from wp.model.character import Seed
from wp.rules_data import rules as rd


def _pay(ch, cost, source):
    try:
        return tr.pay(ch.training, cost, source)
    except ValueError as e:
        raise CommandError(str(e), "rule_refused")


def attention_value(ch, stat):
    """What 1 attention is worth: max(2, stat mod) + the bought attention course (training.md: the course adds to the
    stat bonus; applied to every attention conversion: assumption Q102)."""
    return inj.attention_value(dv.ability_mod(ch, stat)) + ch.attention_course


HIT_DIE_DEFAULT = rd.ref("progression.hit_die_default")
HIT_DIE_DEFAULT_USED = "hit_die_default_used"


@command
def level_up(ch, hp_roll=None):
    """Level +1, +100 * NEW level training (progression.md), and the player's hit-die roll for the new level
    (1..die; edit later with set_hp_roll or edit mode). No level cap (owner, Q103). Without a roll the die counts 1
    and the result carries the warning "hit_die_default_used" ("die not entered, 1 taken", package 17, Q111).
    Max HP grows; the current HP is not healed (Q111)."""
    warnings = ()
    if hp_roll is None:
        hp_roll, warnings = HIT_DIE_DEFAULT, (HIT_DIE_DEFAULT_USED,)
    roll = int(hp_roll)
    if not 1 <= roll <= ch.hit_die:
        raise CommandError("hit-die roll must be 1..%d" % ch.hit_die, "hit_die_roll_must", values=(ch.hit_die,))
    level = ch.level + 1
    gain = tr.level_up_training(level)
    new = replace(ch, level=level, hp_rolls=ch.hp_rolls + (roll,), training=ch.training + gain)
    return commit(new, "level_up", "level %d, training +%d" % (level, gain),
                  {"level": level, "training": gain, "roll": roll, "warnings": warnings})


@command
def exchange_comfort(ch, n=1):
    """n comfort -> n * ((level + 1) * 5 + effects "comfort_rate_bonus") training (training.md "Comfort for training")."""
    n = int(n)
    if n < 1:
        raise CommandError("exchange at least 1 comfort", "exchange_least_1_comfort")
    if ch.comfort_current < n:
        raise CommandError("not enough comfort: have %d, exchange %d" % (ch.comfort_current, n), "not_enough_comfort_have", values=(ch.comfort_current, n))
    gain = n * tr.comfort_rate(ch.level, dv.comfort_rate_bonus(ch))   # effect "comfort_rate_bonus" (package 16 G2)
    return commit(replace(ch, comfort_current=ch.comfort_current - n, training=ch.training + gain), "exchange_comfort",
                  "comfort -%d, training +%d" % (n, gain), {"training": gain})


@command
def remove_ot_comfort(ch, n=1):
    """n comfort -> -3 OT each (injuries.md); OT never below 0."""
    n = int(n)
    if n < 1:
        raise CommandError("spend at least 1 comfort", "spend_least_1_comfort")
    if ch.comfort_current < n:
        raise CommandError("not enough comfort: have %d, spend %d" % (ch.comfort_current, n), "not_enough_comfort_have", values=(ch.comfort_current, n))
    if ch.trauma <= 0:
        raise CommandError("no OT to remove", "no_ot_remove")
    trauma = max(0, ch.trauma - n * inj.COMFORT_OT)
    return commit(replace(ch, comfort_current=ch.comfort_current - n, trauma=trauma), "remove_ot_comfort",
                  "comfort -%d, OT %d -> %d" % (n, ch.trauma, trauma), {"removed": ch.trauma - trauma})


@command
def remove_ot_attention(ch, n=1):
    """n attention -> -(max(2, Str mod) + attention course) OT each (injuries.md); OT never below 0."""
    n = int(n)
    if n < 1:
        raise CommandError("spend at least 1 attention", "spend_least_1_attention")
    if ch.attention < n:
        raise CommandError("not enough attention: have %d, spend %d" % (ch.attention, n), "not_enough_attention_have", values=(ch.attention, n))
    if ch.trauma <= 0:
        raise CommandError("no OT to remove", "no_ot_remove")
    trauma = max(0, ch.trauma - n * attention_value(ch, "str"))
    return commit(replace(ch, attention=ch.attention - n, trauma=trauma), "remove_ot_attention",
                  "attention -%d, OT %d -> %d" % (n, ch.trauma, trauma), {"removed": ch.trauma - trauma})


@command
def raise_heal_rating(ch, injury_id=""):
    """1 attention -> the injury's RL + (max(2, Str mod) + attention course) (injuries.md "Healing rating")."""
    j = next((x for x in ch.injuries if x.jid == injury_id), None)
    if j is None:
        raise CommandError("no injury with id %r" % (injury_id,), "no_injury_id", values=(injury_id,))
    if ch.attention < 1:
        raise CommandError("no attention", "no_attention")
    up = attention_value(ch, "str")
    injuries = tuple(replace(x, heal_rating=x.heal_rating + up) if x.jid == injury_id else x for x in ch.injuries)
    return commit(replace(ch, attention=ch.attention - 1, injuries=injuries), "raise_heal_rating",
                  "%s RL +%d" % (injury_id, up), {"rl": j.heal_rating + up})


@command
def buy_attention_course(ch, source=tr.TRAINING):
    """Attention course +1 for 200 (training.md): adds to the stat bonus of attention conversions."""
    new = replace(ch, attention_course=ch.attention_course + 1, training=_pay(ch, tr.ATTENTION_COURSE_COST, source))
    return commit(new, "buy_attention_course", "attention course %d" % new.attention_course,
                  {"cost": tr.ATTENTION_COURSE_COST})


@command
def buy_reaction(ch, source=tr.TRAINING):
    """+1 reaction = 200 * the new number of reactions (training.md)."""
    cost = tr.reaction_cost(ch.reactions)
    new = replace(ch, reactions=ch.reactions + 1, training=_pay(ch, cost, source))
    return commit(new, "buy_reaction", "reactions %d for %d" % (new.reactions, cost), {"cost": cost})


@command
def buy_seed(ch, name="", source=tr.TRAINING):
    """A new seed for 200 (training.md "Seeds"); the id is made from the name."""
    if not name:
        raise CommandError("a seed needs a name", "seed_needs_name")
    seed = Seed(ids.make_id(name, (s.sid for s in ch.seeds)), name)
    new = replace(ch, seeds=ch.seeds + (seed,), training=_pay(ch, tr.SEED_COST, source))
    return commit(new, "buy_seed", "seed %s" % seed.sid, {"cost": tr.SEED_COST, "sid": seed.sid})


@command
def sprout_seed(ch, seed_id="", source=tr.TRAINING):
    """Sprout a seed for 200 (training.md); the quirk itself is obtained narratively (not modelled)."""
    seed = next((s for s in ch.seeds if s.sid == seed_id), None)
    if seed is None:
        raise CommandError("no seed %r" % (seed_id,), "no_seed", values=(seed_id,))
    if seed.sprouted:
        raise CommandError("seed %s has already sprouted" % seed_id, "seed_has_already_sprouted", values=(seed_id,))
    seeds = tuple(replace(s, sprouted=True) if s.sid == seed_id else s for s in ch.seeds)
    new = replace(ch, seeds=seeds, training=_pay(ch, tr.SPROUT_COST, source))
    return commit(new, "sprout_seed", "seed %s sprouted" % seed_id, {"cost": tr.SPROUT_COST})


@command
def make_language_native(ch, lid="", source=tr.TRAINING):
    """Make a known language native: the first native free, 50 while natives < Int mod, else 100 (training.md)."""
    lang = next((x for x in ch.languages if x.lid == lid), None)
    if lang is None:
        raise CommandError("no language %r" % (lid,), "no_language", values=(lid,))
    if lang.native:
        raise CommandError("%s is already native" % lid, "already_native", values=(lid,))
    cost = tr.native_language_cost(dv.natives(ch), dv.ability_mod(ch, "int"))
    langs = tuple(replace(x, native=True) if x.lid == lid else x for x in ch.languages)
    new = replace(ch, languages=langs, training=_pay(ch, cost, source))
    return commit(new, "make_language_native", "%s native for %d" % (lid, cost), {"cost": cost})


@command
def promote_skill(ch, name="", to_tier=sk.ADVANCED, source=tr.TRAINING):
    """Normal -> advanced (40 + 20 * other advanced or specialized), advanced -> specialized (200 + 50 * other
    specialized); normal -> specialized pays both (skills.md)."""
    if to_tier not in (sk.ADVANCED, sk.SPECIALIZED):
        raise CommandError("to_tier must be advanced or specialized", "tier_must_advanced_specialized")
    s = next((x for x in ch.skills if x.name == name), None)
    if s is None:
        raise CommandError("no skill %r" % (name,), "no_skill", values=(name,))
    if sk.TIERS.index(to_tier) <= sk.TIERS.index(s.tier):
        raise CommandError("%s is already %s" % (name, s.tier), "already_promoted", values=(name, s.tier))
    try:
        cost = sk.tier_cost(ch.skills, name, to_tier)
    except ValueError as e:
        raise CommandError(str(e), "rule_refused")
    skills = tuple(replace(x, tier=to_tier) if x.name == name else x for x in ch.skills)
    new = replace(ch, skills=skills, training=_pay(ch, cost, source))
    return commit(new, "promote_skill", "%s -> %s for %d" % (name, to_tier, cost), {"cost": cost})


@command
def buy_professionalism(ch, skills=(), class_skill_points=0, source=tr.TRAINING):
    """Professionalism 300 (training.md, Q29): 1 / 2 / 3 / 4 class skills become specialized for classes with 2+ / 4+ /
    6+ / 8+ skill points; only for classes WITHOUT their own professionalism (not checkable yet: no class data,
    Q104). Bought once (assumption Q105). The class skill list is not checked (no class data)."""
    if ch.professionalism_bought:
        raise CommandError("professionalism is already bought", "professionalism_already_bought")
    n = tr.professionalism_skills(class_skill_points)
    if n == 0:
        raise CommandError("professionalism needs a class with at least 2 skill points", "professionalism_needs_class_least")
    skills = tuple(skills)
    if len(skills) != n or len(set(skills)) != n:
        raise CommandError("choose exactly %d different skills (class skill points %d)" % (n, int(class_skill_points)), "choose_exactly_different_skills", values=(n, int(class_skill_points)))
    have = {x.name: x for x in ch.skills}
    for name in skills:
        if name not in have:
            raise CommandError("no skill %r" % (name,), "no_skill", values=(name,))
        if have[name].tier == sk.SPECIALIZED:
            raise CommandError("%s is already specialized" % name, "already_specialized", values=(name,))
    new_skills = tuple(replace(x, tier=sk.SPECIALIZED) if x.name in skills else x for x in ch.skills)
    new = replace(ch, skills=new_skills, professionalism_bought=True,
                  training=_pay(ch, tr.PROFESSIONALISM_COST, source))
    return commit(new, "buy_professionalism", "professionalism: %s" % ", ".join(skills), {"cost": tr.PROFESSIONALISM_COST})


def _spend_attention(ch, n):
    n = int(n)
    if n < 1:
        raise CommandError("spend at least 1 attention", "spend_least_1_attention")
    if ch.attention < n:
        raise CommandError("not enough attention: have %d, spend %d" % (ch.attention, n), "not_enough_attention_have",
                           values=(ch.attention, n))
    return n


@command
def attention_to_training(ch, n=1):
    """Attention option 2 (training.md): per attention, training as if spending comfort = Dex mod / 2 (min 1, tenths).
    The attention course adds to the stat (Q102: (Dex mod + course) / 2). Training = floor(comfort * comfort rate)
    (assumption Q114)."""
    n = _spend_attention(ch, n)
    comfort = tr.attention_comfort_equivalent(dv.ability_mod(ch, "dex") + ch.attention_course)
    rate = tr.comfort_rate(ch.level, dv.comfort_rate_bonus(ch))
    gain = int(round(comfort * 10)) * rate * n // 10
    return commit(replace(ch, attention=ch.attention - n, training=ch.training + gain), "attention_to_training",
                  "attention -%d, training +%d" % (n, gain), {"training": gain, "comfort": comfort})


@command
def attention_to_base_points(ch, n=1):
    """Attention option 4 (training.md): 0.2 * Int mod base points per attention (min 0.4), fractions kept in
    Character.base_points_tenths; whole points add base slots (derived_view.base_slots). The attention course adds to
    the stat (Q102)."""
    n = _spend_attention(ch, n)
    gain = tr.attention_base_tenths(n, dv.ability_mod(ch, "int") + ch.attention_course)
    return commit(replace(ch, attention=ch.attention - n, base_points_tenths=ch.base_points_tenths + gain),
                  "attention_to_base_points", "attention -%d, base points +%d tenths" % (n, gain), {"tenths": gain})
