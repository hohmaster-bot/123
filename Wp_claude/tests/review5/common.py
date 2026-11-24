"""Review 5 helpers: a rich character, a Session in a temp folder, all views, a generic random parameter maker for
EVERY command of the registry (valid and hostile values). Not part of the product; never imported by it."""
import inspect
import math
import os
import random
import shutil
import sys
import tempfile
from dataclasses import fields, is_dataclass, replace

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "Wp_claude", "tests", "review4"))

from fuzz import rich as rich4  # noqa: E402
from wp.app import session as sess  # noqa: E402
from wp.app import views as vw  # noqa: E402
from wp.commands import REGISTRY  # noqa: E402
from wp.model import cache  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.model.doll import SLOT_IDS  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402

import json  # noqa: E402

CONSTS = json.load(open(os.path.join(ROOT, "wp", "rules_data", "constants.json"), encoding="utf-8"))["constants"]
CONST_IDS = tuple(c["id"] for c in CONSTS)


def rich():
    return rich4()


def temp_session(ch=None, name="hero", clock=None):
    d = tempfile.mkdtemp(prefix="wp_r5_")
    chars, user = os.path.join(d, "chars"), os.path.join(d, "user")
    os.makedirs(chars)
    os.makedirs(user)
    t = [1000.0]
    s = sess.Session(chars, user, clock=clock or (lambda: t[0]))
    s.new(name, ch if ch is not None else rich())
    s._tmp = d
    return s


def drop(s):
    shutil.rmtree(s._tmp, ignore_errors=True)


def all_views(s):
    out = {}
    for name in sorted(vw.VIEWS):
        try:
            out[name] = s.view(name)
        except Exception as e:  # noqa: BLE001
            out[name] = ("RAISED", type(e).__name__, str(e)[:80])
    return out


def ids_of(ch):
    return {
        "iid": [i.iid for i in ch.items], "sid": [x.sid for x in ch.statuses], "rid": [a.rid for a in ch.attacks],
        "fid": [f.fid for f in ch.feats], "pid": [p.pid for p in ch.pools], "mid": [m.mid for m in ch.maneuvers],
        "did": [d.did for d in getattr(ch, "drives", ())], "wid": [w.weapon.wid if hasattr(w.weapon, "wid") else
                                                                    w.weapon.name for w in ch.weapons],
        "injury_id": [j.jid for j in ch.injuries], "tid": [t.tid for t in ch.templates],
        "kid": [q.kid for q in ch.quirks], "spid": [sp.spid for sp in getattr(ch, "spells", ())],
    }


HOSTILE = (None, -1, -10 ** 9, 10 ** 18, 2.5, float("nan"), float("inf"), "", "x" * 300, "../../etc", True, [], {},
           ("a",), "\u0436\u0443\u043a", -0.0)
STR_NAMES = ("name", "title", "text", "principle", "tag", "group", "grip", "stat", "kind", "dtype", "severity",
             "to_tier", "source", "collection", "save", "size", "resource", "target", "owner_kind", "lid", "sub")
CHOICES = {
    "resource": ("hp", "balance", "spirit", "bp", "comfort", "mana", "nope"),
    "dtype": ("physical", "fire", "cold", "nope"), "severity": ("light", "medium", "heavy", "x"),
    "source": ("training", "free", "zzz"), "side": ("", "left", "right", "middle"),
    "owner_kind": ("item", "feat", "status", "x"), "save": ("fort", "ref", "will", "x"),
    "size": ("small", "medium", "large", "x"), "to_tier": ("advanced", "specialized", "normal"),
    "grip": ("one", "two", "off", "x"), "kind": (None, "day", "decade", "x"), "collection": ("quirks", "templates",
                                                                                       "spells", "x"),
    "target": ("item", "status", None), "group": ("blades", "rules.ac_zones", "rules.pain", "x"),
}


def rand_value(r, pname, default, ch, hostile=0.15):
    if r.random() < hostile:
        return r.choice(HOSTILE)
    ids = ids_of(ch)
    if pname in ids:
        pool = ids[pname] + ["nope"]
        return r.choice(pool)
    if pname == "owner_id":
        return r.choice(sum(ids.values(), []) + ["nope"])
    if pname == "hid":
        hs = [h.hid for it in ch.items for h in getattr(it, "hidden_properties", ())]
        return r.choice(hs + ["nope"])
    if pname in ("slot", "a", "b"):
        return r.choice(SLOT_IDS + ("left_hand", "right_hand", "nope"))
    if pname == "key":
        return r.choice(CONST_IDS + ("autosave", "nope"))
    if pname == "seed_id":
        return r.choice([s.sid for s in getattr(ch, "seeds", ())] + ["nope"]) if hasattr(ch, "seeds") else "nope"
    if pname in CHOICES:
        return r.choice(CHOICES[pname])
    if pname == "name":
        return r.choice(("climb", "lore", "str", "dex", "con", "new thing", ""))
    if isinstance(default, bool):
        return r.random() < 0.5
    if isinstance(default, int) or pname in ("n", "amount", "value", "level", "max", "current", "ticks",
                                             "remaining", "hp_roll", "circle", "delta", "feet", "metamagic",
                                             "projects", "class_skill_points", "min_qualification", "damage",
                                             "other_heal", "extra_bp", "penalty_balance"):
        return r.choice((0, 1, 2, 3, 5, 8, 12, -1, r.randint(0, 20)))
    if isinstance(default, str):
        return r.choice(("", "a", "nope"))
    return default


def rand_params(r, cmd, ch):
    sig = inspect.signature(REGISTRY[cmd])
    out = {}
    for name, p in list(sig.parameters.items())[1:]:
        if p.kind == p.VAR_KEYWORD:
            if r.random() < 0.5:
                fname = r.choice(("name", "level", "hp_current", "to_hit", "current", "max", "bogus_field",
                                  "abilities", "base", "title", "restore"))
                out[fname] = rand_value(r, fname, 0, ch)
            continue
        if p.kind == p.VAR_POSITIONAL:
            continue
        d = p.default if p.default is not p.empty else None
        if r.random() < 0.85:
            out[name] = rand_value(r, name, d if not isinstance(d, rd.Ref) else 1, ch)
    return out


def bad_numbers(obj, path="", out=None):
    """Paths of float NaN / inf anywhere in a view (dataclasses, dicts, tuples)."""
    if out is None:
        out = []
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            out.append(path)
    elif is_dataclass(obj) and not isinstance(obj, type):
        for f in fields(obj):
            bad_numbers(getattr(obj, f.name), path + "." + f.name, out)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            bad_numbers(v, path + "[%r]" % (k,), out)
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            bad_numbers(v, path + "[%d]" % i, out)
    return out
