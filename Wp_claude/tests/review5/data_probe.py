"""Review 5 / area 4 + 5: catalogs (ids never reused, tombstones, hostile codes), i18n coverage of reason ids, the
formula evaluator with hostile input, huge formula values through every view, and a sweep over EVERY rule constant
(perturb it on the rich character: does any view change? does anything raise?).
Run: python Wp_claude/tests/review5/data_probe.py"""
import base64
import json
import os
import re
import zlib

from common import CONSTS, ROOT, all_views, bad_numbers, drop, temp_session
from wp.catalog import catalog_cmds as cc
from wp.catalog import store as cs
from wp.commands import CommandError
from wp.core import formula as fm
from wp.i18n import i18n


def catalogs():
    lay = cs.load_layers("feats", os.path.join(ROOT, "Wp_claude", "tests", "review5", "_none_"))
    first = cs.merged(lay)[0][0]["id"]
    ids_seen = set(e["id"] for e, _ in cs.merged(lay))
    r = cc.catalog_dispatch(lay, "catalog_add_entry", fields={"name": "Zork"})
    lay, zid = r.state, r.info["id"]
    lay = cc.catalog_dispatch(lay, "catalog_remove_entry", eid=zid).state
    r2 = cc.catalog_dispatch(lay, "catalog_add_entry", fields={"name": "Zork"})
    print("catalog: add Zork -> %s, remove, add Zork again -> %s (must differ)" % (zid, r2.info["id"]))
    lay = cc.catalog_dispatch(lay, "catalog_remove_entry", eid=first).state
    r3 = cc.catalog_dispatch(lay, "catalog_reset_entry", eid=first)
    print("catalog: tombstone shipped %s then reset -> visible again: %s" % (
        first, any(e["id"] == first for e, _ in cs.merged(r3.state))))
    # hostile entry codes
    def code(obj, raw=None):
        raw = raw if raw is not None else json.dumps(obj).encode()
        return cs.CODE_PREFIX + base64.urlsafe_b64encode(zlib.compress(raw)).decode("ascii")
    bomb = code(None, b"[" + b"0," * 20000000 + b"0]")   # 40 MB of JSON from a ~40 KB code
    for title, c in (("not a dict", code([1, 2])), ("no kind", code({"entry": {"name": "x"}})),
                     ("entry list", code({"kind": "feats", "entry": [1]})), ("garbage", cs.CODE_PREFIX + "!!!"),
                     ("not a string", 5), ("zip bomb (40 MB inflated, code %d KB)" % (len(bomb) // 1024), bomb),
                     ("huge name", code({"kind": "feats", "entry": {"name": "x" * 100000}}))):
        try:
            res = cc.catalog_dispatch(lay, "catalog_import_entry", code=c)
            print("catalog import %-40s -> accepted id %s" % (title, str(res.info.get("id"))[:30]))
        except CommandError as e:
            print("catalog import %-40s -> refused %s" % (title, e.reason))
        except Exception as e:  # noqa: BLE001
            print("catalog import %-40s -> RAISED %s %s" % (title, type(e).__name__, str(e)[:50]))


def reasons():
    found = set()
    pat = re.compile(r"CommandError\([^()]*?(?:\([^()]*\)[^()]*?)*?,\s*\"([a-z0-9_]+)\"", re.S)
    pat2 = re.compile(r"refuse\(\(\"([a-z0-9_]+)\"")
    pat3 = re.compile(r"reason=\"([a-z0-9_]+)\"")
    for base, _, fs in os.walk(os.path.join(ROOT, "wp")):
        for f in fs:
            if f.endswith(".py"):
                t = open(os.path.join(base, f), encoding="utf-8").read()
                found |= set(pat.findall(t)) | set(pat2.findall(t)) | set(pat3.findall(t))
    found |= {"nothing_to_undo", "nothing_to_redo", "no_character", "unknown_view"}
    ru, en = i18n.load("ru"), i18n.load("en")
    miss_ru = sorted(r for r in found if "reason." + r not in ru)
    miss_en = sorted(r for r in found if "reason." + r not in en)
    print("i18n: %d reason ids found in code; without ru text %d %s; without en text %d %s" % (
        len(found), len(miss_ru), miss_ru[:12], len(miss_en), miss_en[:12]))
    same = sorted(k for k in ru if k.startswith("reason.") and ru[k] == en.get(k))
    print("i18n: reason texts where ru == en (not translated): %d of %d" % (
        len(same), sum(1 for k in ru if k.startswith("reason."))))


def formulas():
    cases = {"huge number": "9" * 199, "repeated mult": "*".join(["999999999"] * 20),
             "deep parens": "(" * 99 + "1" + ")" * 99, "deep unary": "-" * 199 + "1", "div by zero": "1/0",
             "div by expr zero": "1/(level-level)", "string": "'a'", "attr": "level.__class__",
             "dunder": "__import__", "call outside": "pow(2, 100)", "nested funcs": "max(" * 30 + "1" + ")" * 30,
             "float exp": "1e308", "too long": "1+" * 150 + "1", "comma top": "1,2", "empty call": "max()",
             "floor 2 args": "floor(1, 2)", "decimal": "0.5 * 3", "unicode digit": "\u0663"}
    for k, f in cases.items():
        try:
            v = fm.evaluate(f, {"level": 3})
            print("formula %-16s -> %s" % (k, str(v)[:30] + ("... (%d digits)" % len(str(v)) if len(str(v)) > 30 else "")))
        except fm.FormulaError as e:
            print("formula %-16s -> FormulaError %s" % (k, str(e)[:50]))
        except Exception as e:  # noqa: BLE001
            print("formula %-16s -> RAISED %s %s" % (k, type(e).__name__, str(e)[:50]))


def huge_values():
    """A pool with max = a 199-digit formula; a status effect of 10**18 to hp_max: do all views survive?"""
    from wp.core import effects as ef
    s = temp_session()
    out = []
    out.append(("add_pool 9*199", s.dispatch("add_pool", name="big", max="9" * 199).ok))
    st = ef.Status("huge", sid="huge", effects=(ef.Effect("hp_max", 10 ** 18),), active=True)
    out.append(("status hp_max 1e18", s.dispatch("add_status", status=st, active=True).ok))
    st2 = ef.Status("hugef", sid="hugef", effects=(ef.Effect("attack", "9" * 150),), active=True)
    out.append(("status attack formula 1e150", s.dispatch("add_status", status=st2, active=True).ok))
    v = all_views(s)
    raised = {k: x for k, x in v.items() if isinstance(x, tuple) and x and x[0] == "RAISED"}
    nan = {k: bad_numbers(x)[:2] for k, x in v.items() if bad_numbers(x)}
    for cmd, kw in (("take_damage", {"amount": 5}), ("tick", {}), ("long_rest", {}), ("short_rest", {})):
        try:
            out.append((cmd, s.dispatch(cmd, **kw).ok))
        except Exception as e:  # noqa: BLE001
            out.append((cmd, "RAISED %s %s" % (type(e).__name__, str(e)[:40])))
    try:
        s.save()
        s.open(s.name)
        out.append(("save/open", True))
    except Exception as e:  # noqa: BLE001
        out.append(("save/open", "RAISED %s" % type(e).__name__))
    print("huge values: %s; views raised: %s; NaN/inf: %s" % (out, {k: x[1:] for k, x in raised.items()}, nan))
    drop(s)


def constants_sweep():
    s = temp_session()
    s.dispatch("start_combat")
    s.dispatch("take_damage", amount=9)
    s.dispatch("activate_status", sid="rage")
    base = all_views(s)
    dead, raised, refused = [], [], []
    for c in CONSTS:
        v = c["value"]
        if c["type"] == "int":
            new = v + 3
        elif c["type"] == "float":
            new = v * 2 + 1
        else:
            continue
        snap = s.character
        res = s.dispatch("set_rule_setting", key=c["id"], value=new)
        if not res.ok:
            refused.append((c["id"], res.reason))
            continue
        after = all_views(s)
        r = [k for k, x in after.items() if isinstance(x, tuple) and x and x[0] == "RAISED"]
        if r:
            raised.append((c["id"], r))
        changed = [k for k in after if k not in ("log", "settings") and after[k] != base[k]]
        # also run the rule-heavy commands once
        if not changed:
            probe = s.character
            outs = []
            for cmd, kw in (("tick", {}), ("take_damage", {"amount": 6}), ("short_rest", {}), ("long_rest", {}),
                            ("cast_spell", {"circle": 1}), ("level_up", {"hp_roll": 5})):
                a = s.dispatch(cmd, **kw)
                outs.append((a.ok, s.character))
                s.character = probe
            s.character = snap
            outs0 = []
            for cmd, kw in (("tick", {}), ("take_damage", {"amount": 6}), ("short_rest", {}), ("long_rest", {}),
                            ("cast_spell", {"circle": 1}), ("level_up", {"hp_roll": 5})):
                a = s.dispatch(cmd, **kw)
                outs0.append((a.ok, s.character))
                s.character = snap
            from dataclasses import replace as rp
            same = all((x[0] == y[0]) and rp(x[1], log=(), log_seq=0, rules_settings=snap.rules_settings) ==
                       rp(y[1], log=(), log_seq=0) for x, y in zip(outs, outs0))
            if same:
                dead.append(c["id"])
        s.character = snap
    n = sum(1 for c in CONSTS if c["type"] in ("int", "float"))
    print("constants: %d int/float constants perturbed; refused %d %s; views raised %d %s" % (
        n, len(refused), refused[:6], len(raised), raised[:6]))
    print("constants with NO visible effect on the rich character (views + 6 commands): %d: %s" % (len(dead), dead))
    drop(s)


if __name__ == "__main__":
    catalogs()
    reasons()
    formulas()
    huge_values()
    constants_sweep()
