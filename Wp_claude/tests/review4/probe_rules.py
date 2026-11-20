"""Independent review 4: RULES examples and normative sentences run through the REAL commands.
Expected numbers are computed by hand from the RULES text (file:line in each case), never from the code.
The cases are in probe_a.py and probe_b.py (helpers in probe_common.py).
Run: python Wp_claude/tests/review4/probe_rules.py   (prints a table; exit 0 always: this is a probe, not a gate)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_a  # noqa: E402,F401  (registers its cases)
import probe_b  # noqa: E402,F401
from probe_common import RESULTS  # noqa: E402


def main():
    bad = [r for r in RESULTS if not r[4]]
    print("| rule | what | expected | actual | ok | severity |")
    print("|---|---|---|---|---|---|")
    for ref, what, exp, got, ok, sev in RESULTS:
        print("| %s | %s | %r | %r | %s | %s |" % (ref, what, exp, got, "ok" if ok else "MISMATCH", "" if ok else sev))
    print()
    print("probes %d, ok %d, mismatch %d" % (len(RESULTS), len(RESULTS) - len(bad), len(bad)))


if __name__ == "__main__":
    main()
