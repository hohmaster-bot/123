"""Package 20 (D23): no game-rule number is written in code.

- The review 4 scan (tests/review4/hardcoded.py: module-level NAME = number, numbers inside functions other than
  0 / 1 / -1) finds nothing outside the allowlist of wp/rules_data/constants.json.
- No rule reference (rules.Ref) is a default of a saved record (records must hold plain values).
- Every constant of the table is read somewhere in wp/ (no dead or misspelled ids).
Run: python Wp_claude/tests/test_rule_literals.py"""
import dataclasses
import glob
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "core"))
from _runner import ROOT, Suite  # noqa: E402

from wp.rules_data import rules as rd  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_rule_literals")
spec = importlib.util.spec_from_file_location("hardcoded", os.path.join(HERE, "review4", "hardcoded.py"))
hc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hc)


def files():
    return sorted(p for p in glob.glob(os.path.join(ROOT, "wp", "**", "*.py"), recursive=True) if "__pycache__" not in p)


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def _violations():
    allow = rd.ALLOWLIST
    out = []
    for p in files():
        named, inline = hc.scan(p)
        r = rel(p)
        ok_named = allow.get("named", {}).get(r, {})
        ok_inline = allow.get("inline", {}).get(r, {})
        out += ["%s:%d %s" % (r, ln, name) for ln, name, _ in named if name not in ok_named]
        out += ["%s:%d %r" % (r, ln, v) for ln, v in inline if str(v) not in ok_inline and repr(v) not in ok_inline]
    return out


S.case("l-no-rule-literals", "D23: no rule number in code outside the allowlist", [])(_violations)


def _ref_defaults():
    bad = []
    for name, cls in cio._TYPES.items():
        for f in dataclasses.fields(cls):
            d = f.default if f.default is not dataclasses.MISSING else None
            if isinstance(d, rd.Ref) or (isinstance(d, tuple) and any(isinstance(x, rd.Ref) for x in d)):
                bad.append("%s.%s" % (name, f.name))
    return bad


S.case("l-no-ref-in-records", "D23: saved records hold plain numbers (rd.default), never a lazy reference", [])(_ref_defaults)


def _unused():
    text = "".join(open(p, encoding="ascii").read() for p in files())
    return sorted(cid for cid in rd.TABLE if '"%s"' % cid not in text)


S.case("l-every-constant-used", "D23: every constant of the table is read in wp/", [])(_unused)

if __name__ == "__main__":
    sys.exit(S.run())
