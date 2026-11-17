"""Tiny test runner for core tests (no pytest needed).

Each case is a function returning the actual value; it is compared with the
expected value. Any mismatch or exception -> FAIL, exit code 1.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


class Suite(object):
    def __init__(self, name):
        self.name = name
        self.cases = []

    def case(self, cid, src, expected):
        def deco(fn):
            self.cases.append((cid, src, expected, fn))
            return fn
        return deco

    def run(self):
        failed = 0
        print("| id | source | expected | got | status |")
        print("|---|---|---|---|---|")
        for cid, src, expected, fn in self.cases:
            try:
                got = fn()
                ok = got == expected
                got_s = repr(got)
            except Exception as e:  # a crash is a failure too
                ok = False
                got_s = "%s: %s" % (type(e).__name__, e)
            if not ok:
                failed += 1
            print("| %s | %s | %r | %s | %s |" % (
                cid, src, expected, got_s, "PASS" if ok else "FAIL"))
        print()
        print("%s: TOTAL %d, PASS %d, FAIL %d" % (
            self.name, len(self.cases), len(self.cases) - failed, failed))
        return 1 if failed else 0
