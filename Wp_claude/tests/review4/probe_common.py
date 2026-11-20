"""Review 4 probes, shared helpers (case registry, run, refused, abil, hero). The cases are in probe_a.py and
probe_b.py; run them with probe_rules.py."""
import os
import sys
from dataclasses import replace

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import ac as acm  # noqa: E402
from wp.core import ac_layers as acl  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import damage as dm  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core import magic as mg  # noqa: E402
from wp.core import rest as rs  # noqa: E402
from wp.core import skills as sk  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.core.skills import Skill  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import container_view as cv  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import maneuver_view as mv  # noqa: E402
from wp.model import pool_view as pv  # noqa: E402
from wp.model import stats_view as stv  # noqa: E402
from wp.model.character import (Ability, AttackRecord, Character, Feat, Item, Maneuver, ResourcePool,  # noqa: E402
                                RulesSettings, Usage, WeaponEntry)

RESULTS = []


def case(ref, what, expected, severity="breaks rule"):
    def deco(fn):
        try:
            got = fn()
        except Exception as e:          # a crash is a finding too
            got = "%s: %s" % (type(e).__name__, e)
        RESULTS.append((ref, what, expected, got, got == expected, severity))
        return fn
    return deco


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def refused(fn):
    try:
        fn()
    except CommandError:
        return "refused"
    return "allowed"


def abil(**s):
    out = {a: Ability() for a in ("str", "dex", "con", "int", "wis", "cha")}
    for k, v in s.items():
        out[k] = Ability(base=v)
    return out


def hero(**kw):
    base = dict(hp_rolls=(20,), hit_die=20, hp_current=20, bp_current=5, balance_current=10, balance_bonus=5,
                spirit_current=10)
    base.update(kw)
    return Character(**base)


def sword(**kw):
    base = dict(kind="weapon", hands=1, in_hands=True, groups=("blades",))
    base.update(kw)
    return Item("sw", "sword", **base)


def rec_view(ch, rid="r"):
    return next(v for v in av.all_records(ch) if v.record == rid)
