"""Sheet stats: saves, initiative, CMB, CMD (package 10; RULES defense.md, combat.md, resources.md,
classes_magic.md). Computed on read (D6).

What RULES give and what is an open question (OPEN_QUESTIONS Q55-Q60):
- Save = base (typed by hand from the class table, like BAB) + stat mod + typed bonuses (target "save"
  for all saves, "save:fort" / "save:ref" / "save:will" for one) + pain (resources.md: all rolls)
  + morale (defense.md: saves). The stat of each save is DATA (Character.save_stats), default as in the
  legacy program (classes_magic.md "as in current program"): Fort Con, Ref Dex, Will Wis (Q55).
- Initiative = Dex mod + typed bonuses (target "initiative") + pain + morale (Q56: morale list in
  defense.md does not name initiative; code keeps "ALL rolls").
- CMB = BAB + Str mod (or the better of Str/Dex with the Finesse feat, combat.md) + size CMB mod
  (from Character.size: small -1, medium 0, large +1; package 11 C) + typed bonuses (target "cmb", pain and morale: CMB is a roll).
  Weapon-group bonuses to CMB are not added yet (Q58).
- CMD = 10 + BAB + Str mod + Dex mod + size CMB mod + typed bonuses (target "cmd") (Q59). CMD is not a
  roll: no pain, no morale (resources.md "rolls with a die", defense.md morale list).
"""
from dataclasses import dataclass
from typing import Tuple

from wp.catalog.feats_catalog import FINESSE, has_flag
from wp.core import bonuses as bo
from wp.model import blocks as blk
from wp.model import derived_view as dv

SAVES = ("fort", "ref", "will")
CMD_BASE = 10


@dataclass(frozen=True)
class Stat:
    name: str
    total: int
    lines: Tuple[Tuple[str, int], ...]     # (label, value) breakdown for the UI


def _typed(ch, target, extra_target=None):
    """Typed bonuses for a target, plus bonuses aimed at one sub-target (e.g. "save:fort"), stacked
    together by the normal rules."""
    bs = [b for b in dv.all_bonuses(ch)
          if bo.applies(b, target) or (extra_target is not None and b.target == extra_target
                                       and b.btype not in bo.AC_ONLY_TYPES)]
    return bo.stack(blk.unblocked(ch, bs, target, extra_target))


def _stat(name, parts):
    return Stat(name, sum(v for _, v in parts), tuple(parts))


def save(ch, key):
    if key not in SAVES:
        raise KeyError("no save %r" % (key,))
    stat = ch.save_stats.get(key, "")
    parts = [("base", int(ch.save_base.get(key, 0)))]
    if stat:
        parts.append(("stat:" + stat, dv.ability_mod(ch, stat)))
    parts.append(("bonuses", _typed(ch, bo.SAVE, bo.SAVE_PREFIX + key)))
    return _stat(key, parts)


def saves(ch):
    return {k: save(ch, k) for k in SAVES}


def initiative(ch):
    return _stat("initiative", [("stat:dex", dv.ability_mod(ch, "dex")), ("bonuses", _typed(ch, bo.INITIATIVE))])


def cmb_stat(ch):
    """Str; with the Finesse feat the better of Str/Dex (combat.md "has finesse")."""
    if has_flag(ch, FINESSE):
        return max(("str", "dex"), key=lambda a: (dv.ability_mod(ch, a), a == "dex"))
    return "str"


def cmb(ch):
    st = cmb_stat(ch)
    return _stat("cmb", [("bab", ch.bab), ("stat:" + st, dv.ability_mod(ch, st)), ("size", dv.size_cmb(ch)),
                         ("bonuses", _typed(ch, bo.CMB))])


def cmd(ch):
    return _stat("cmd", [("base", CMD_BASE), ("bab", ch.bab), ("stat:str", dv.ability_mod(ch, "str")),
                         ("stat:dex", dv.ability_mod(ch, "dex")), ("size", dv.size_cmb(ch)),
                         ("bonuses", _typed(ch, bo.CMD))])


def view(ch):
    out = dict(saves(ch))
    out.update(initiative=initiative(ch), cmb=cmb(ch), cmd=cmd(ch))
    return out
