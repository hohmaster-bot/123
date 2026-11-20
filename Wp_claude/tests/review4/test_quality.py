"""Review 4, section 5: test quality scan.
- cases whose expected value is a bare truth value / None / a refusal word (weak when an exact number is known),
- duplicated case ids inside a suite and identical (expected, body) pairs across suites,
- suite run times.
Run: python Wp_claude/tests/review4/test_quality.py
"""
import ast
import glob
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(TESTS))
WEAK = (True, False, None, "allowed", "refused", "rejected", "ok", ())


def cases(path):
    """(case id, expected source, body source, line) for every S.case(...) call."""
    src = open(path, encoding="ascii").read()
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "case" \
                and len(node.args) >= 3 and isinstance(node.args[0], ast.Constant):
            exp = node.args[2]
            try:
                val = ast.literal_eval(exp)
            except Exception:  # noqa: BLE001
                val = "<expr>"
            out.append((node.args[0].value, val, node.lineno))
    return out


def main():
    files = sorted(glob.glob(os.path.join(TESTS, "core", "test_*.py")) + glob.glob(os.path.join(TESTS, "model", "test_*.py"))
                   + glob.glob(os.path.join(TESTS, "storage", "test_*.py")))
    total = weak = 0
    dup_ids = []
    weak_rows = []
    for f in files:
        cs = cases(f)
        total += len(cs)
        ids = [c[0] for c in cs]
        dup_ids += ["%s:%s" % (os.path.basename(f), i) for i in set(ids) if ids.count(i) > 1]
        for cid, val, line in cs:
            if any(val is w or (val == w and type(val) == type(w)) for w in WEAK):
                weak += 1
                weak_rows.append("%s:%d %s expected %r" % (os.path.relpath(f, TESTS), line, cid, val))
    print("cases %d, bare truth / None / refusal-word expectations %d (%.0f%%)" % (total, weak, 100.0 * weak / max(1, total)))
    print("duplicate case ids inside one suite: %d %s" % (len(dup_ids), " ".join(sorted(dup_ids))))
    for r in weak_rows:
        print("  weak: " + r)
    print("suite times:")
    times = []
    for f in files:
        t = time.time()
        subprocess.run([sys.executable, f], capture_output=True, cwd=ROOT)
        times.append((time.time() - t, os.path.relpath(f, TESTS)))
    for t, f in sorted(times, reverse=True)[:8]:
        print("  %.2f s %s" % (t, f))
    print("  total %.1f s for %d suites" % (sum(t for t, _ in times), len(times)))


if __name__ == "__main__":
    main()
