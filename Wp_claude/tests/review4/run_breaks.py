"""Review 4: run my own breaks (breaks_review4.py) against the WHOLE test set on a temp copy.
Uses the copy / apply logic of Wp_claude/tests/break_check.py; the working tree is never touched.
For every entry the full run_all.py runs in the temp copy; "caught" = it exits 1.
Run: python Wp_claude/tests/review4/run_breaks.py [id-prefix ...]
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
sys.path.insert(0, TESTS)
import break_check as bc  # noqa: E402


def entries():
    spec = importlib.util.spec_from_file_location("breaks_review4", os.path.join(HERE, "breaks_review4.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ENTRIES


def main(prefixes):
    es = [e for e in entries() if not prefixes or any(e["id"].startswith(p) for p in prefixes)]
    tmp = tempfile.mkdtemp(prefix="wp_review4_")
    missed = []
    try:
        bc._copy(tmp)
        for e in es:
            e = dict(e, suites=("run_all.py",))
            res = bc.check(e, tmp)
            if res != "caught":
                missed.append((e["id"], res, e["rule"]))
            print("%-8s %-32s %s" % ("ok" if res == "caught" else "MISSED", e["id"], "" if res == "caught" else res))
            sys.stdout.flush()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("entries %d, caught %d, missed %d" % (len(es), len(es) - len(missed), len(missed)))
    for m in missed:
        print("MISSED %s (%s): %s" % m)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
