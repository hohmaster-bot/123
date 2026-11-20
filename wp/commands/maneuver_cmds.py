"""Character-level maneuver list (RULES/combat.md "Maneuver list", package 12 B).

add_maneuver / edit_maneuver (set any field) / remove_maneuver. Costs are RECORD ONLY (nothing is
spent automatically). Unknown future keys go to `extra` and are never interpreted.
"""
import dataclasses
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core import formula as fm
from wp.model import formulas as fx
from wp.model import ids
from wp.model.character import Maneuver

TAG_MODES = ("any", "all")
TAGS = ("none", "combat_only", "out_of_combat_only")
_TUPLES = ("required_tags", "effects")
_FIELDS = tuple(f.name for f in dataclasses.fields(Maneuver) if f.name != "mid")


def _check(m):
    if not m.name:
        raise CommandError("a maneuver needs a name")
    if m.tag_mode not in TAG_MODES:
        raise CommandError("tag_mode must be any or all")
    if m.condition_tag not in TAGS:
        raise CommandError("condition_tag must be one of %s" % ", ".join(TAGS))
    try:
        fx.validate_effects(m.effects)      # formula values are checked when added / edited (package 14 C)
    except fm.FormulaError as e:
        raise CommandError("bad effect formula in %s: %s" % (m.name, e))
    for n in ("to_hit", "damage", "cost_actions", "cost_balance", "cost_spirit"):
        if not isinstance(getattr(m, n), int) or isinstance(getattr(m, n), bool):
            raise CommandError("%s must be a whole number" % n)
    return m


def _clean(fields):
    unknown = set(fields) - set(_FIELDS)
    if unknown:
        raise CommandError("unknown maneuver fields: %s (put future keys into extra)" % ", ".join(sorted(unknown)))
    out = dict(fields)
    for n in _TUPLES:
        if n in out:
            out[n] = tuple(out[n])
    if "extra" in out:
        out["extra"] = dict(out["extra"])
    return out


@command
def add_maneuver(ch, name="", **fields):
    """New maneuver; the id is made from the name (D7)."""
    m = _check(Maneuver(mid=ids.make_id(name or "maneuver", (x.mid for x in ch.maneuvers)), name=name, **_clean(fields)))
    return commit(replace(ch, maneuvers=ch.maneuvers + (m,)), "add_maneuver", "maneuver %s added" % m.name,
                  {"mid": m.mid})


def _find(ch, mid):
    m = next((x for x in ch.maneuvers if x.mid == mid), None)
    if m is None:
        raise CommandError("no maneuver %r" % (mid,))
    return m


@command
def edit_maneuver(ch, mid="", **fields):
    """Set any field of a maneuver (not its id)."""
    m = _check(replace(_find(ch, mid), **_clean(fields)))
    return commit(replace(ch, maneuvers=tuple(m if x.mid == mid else x for x in ch.maneuvers)), "edit_maneuver",
                  "maneuver %s: %s" % (m.name, ", ".join(sorted(fields)) or "no change"))


@command
def remove_maneuver(ch, mid=""):
    m = _find(ch, mid)
    return commit(replace(ch, maneuvers=tuple(x for x in ch.maneuvers if x.mid != mid)), "remove_maneuver",
                  "maneuver %s removed" % m.name)
