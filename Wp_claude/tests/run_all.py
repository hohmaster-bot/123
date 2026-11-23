"""Run every test suite of the new code and print ONE summary line.

Suites: Wp_claude/tests/core/test_*.py, model/test_*.py, storage/test_*.py, test_module_size.py,
test_ascii_code.py. The legacy baseline (test_rules_baseline.py) is NOT run here: it has known failures
(BASELINE_REPORT.md) and is run separately.
Prints only failing suites (with their last output lines), then: "suites N, passed P, failed F".
Exit code 1 on any failure.
Usage: python Wp_claude/tests/run_all.py
"""
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TAIL = 15


def suites(base=HERE):
    out = []
    for sub in ("core", "model", "storage", "app", "perf"):
        out += sorted(glob.glob(os.path.join(base, sub, "test_*.py")))
    out += [os.path.join(base, "test_module_size.py"), os.path.join(base, "test_ascii_code.py"),
            os.path.join(base, "test_rule_literals.py"), os.path.join(base, "test_review_pack.py")]
    return out


def run(path, cwd=ROOT):
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, cwd=cwd)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()


def main():
    failed = 0
    files = suites()
    for f in files:
        code, lines = run(f)
        if not lines:                  # an empty or silent suite proves nothing (package 18)
            code, lines = 1, ["suite printed nothing (empty file?)"]
        if code != 0:
            failed += 1
            print("FAILED %s" % os.path.relpath(f, ROOT))
            for ln in lines[-TAIL:]:
                print("    " + ln)
    print("suites %d, passed %d, failed %d" % (len(files), len(files) - failed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
