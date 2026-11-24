"""Effect targets of sheet numbers (package 16 A2, owner: EVERY sheet number has an effect target).

The list of targets is data: wp/catalog/data/sheet_targets.json (id -> meaning; ids ending with ":" take an id).
value(ch, target) = the typed bonuses of active statuses, owned feats, injuries, templates and the acting tab of
worn / held items aimed at exactly this target, stacked by the normal rules (bonuses.stack: same type -> larger
wins, flat / dodge add), after block_bonus effects. Morale and pain are roll bonuses and never count here.
Ability scores (target "stat:<id>") are read with the context of the STORED scores (base_context): an effect value
taken from a stat modifier or a formula does not see the other stat effects (no loops, assumption Q118).
"""
import io
import json
import os

from wp.core import bonuses as bo
from wp.core import derived as cdv
from wp.core import effects as ef
from wp.model import blocks as blk
from wp.model import classes as klass
from wp.model import derived_view as dv
from wp.model.cache import cached

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "catalog", "data", "sheet_targets.json")
STAT = "stat:"
SLOTS = "slots:"
POOL_MAX = "pool_max:"
RESIST = "resist:"
EXTRA_DICE = "extra_hit_dice"


def load_targets(path=PATH):
    with io.open(path, encoding="utf-8") as f:
        return dict(json.load(f)["targets"])


TARGETS = load_targets()


def known(target):
    """True for a target of this list (an id after ':' is not checked here)."""
    return target in TARGETS or any(t.endswith(":") and target.startswith(t) for t in TARGETS)


def raw_mod(ch, name):
    """Modifier of the STORED current score (no effects), with block_stat_bonus."""
    m = cdv.ability_mod(ch.ability(name).current)
    return min(0, m) if m > 0 and blk.stat_blocked(ch, name) else m


def base_context(ch):
    ctx = {ef.OVERLOAD: ch.overload, "level": ch.level, "bab": klass.bab(ch)}
    for name in ch.abilities:
        ctx[ef.stat_mod_key(name)] = raw_mod(ch, name)
        ctx["%s_mod" % name] = ctx[ef.stat_mod_key(name)]
    return ctx


def sheet_bonuses(ch, ctx=None):
    ctx = dv.context(ch) if ctx is None else ctx
    return tuple(dv.effect_bonuses(ch, ctx)) + tuple(dv.item_effects(ch, ctx))


def _has(ch, target):
    """Cheap check: does any active source carry an effect with this target (exact or as a prefix)?"""
    return any(e.target == target for _, e in blk.active_effects(ch))


def stack_of(ch, bonuses, target):
    """Unscoped bonuses only: an effect with AC cells counts in its cells (ac_zones_view, package 24 B2)."""
    bs = [b for b in bonuses if b.target == target and b.btype not in bo.AC_ONLY_TYPES and not b.cells]
    return bo.stack(blk.unblocked(ch, bs, target))


@cached
def value(ch, target):
    if not _has(ch, target):
        return 0
    ctx = base_context(ch) if target.startswith(STAT) else None
    return stack_of(ch, sheet_bonuses(ch, ctx), target)


def stat_bonus(ch, name):
    return value(ch, STAT + name)


def entries(ch, target):
    """(source, value, note) of every active effect with this target (defense view: DR bypass texts)."""
    out = []
    ctx = dv.context(ch)
    for src, e in blk.active_effects(ch):
        if e.target == target:
            out.append((src, e.resolve(ctx), e.note))
    return tuple(out)


@cached
def item_bonuses(ch, iid):
    """ItemBonus records for one item from statuses, feats, injuries, quirks and templates (NOT from items: an item's
    HP must not depend on item tabs, which depend on item HP). Values are read without stat modifiers (no loops,
    assumption Q127); normal typed stacking per target; block effects are not applied here."""
    from wp.core import weapons as wpn
    from wp.model import stance_view as stv
    effects = [e for s in ch.statuses if ef.is_effective(s) for e in s.effects]
    effects += [e for f in ch.feats if stv.feat_applies(ch, f) for e in f.effects]
    effects += [e for j in ch.injuries for e in j.effects]
    effects += [e for _, es in dv.other_sources(ch) for e in es]
    ctx = {ef.OVERLOAD: ch.overload, "level": ch.level, "bab": klass.bab(ch)}
    out = ()
    for kind in (wpn.ITEM_HP, wpn.ITEM_HARDNESS):
        bs = [bo.Bonus(e.resolve(ctx), e.btype if e.btype not in bo.AC_ONLY_TYPES else bo.FLAT, kind)
              for e in effects if e.target == kind and (e.weapon is None or e.weapon == iid)]
        if bs:
            out += (wpn.ItemBonus(kind, bo.stack(bs)),)
    return out
