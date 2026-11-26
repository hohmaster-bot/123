"""Package 36 P1.1: every package report of the fixed format (packages 23 and later) holds the five fixed sections
and is not truncated (owner: the package 35 report once held 3 lines only).
Run: python Wp_claude/tests/storage/test_reports.py"""
import glob
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

S = Suite("test_reports")
REPORTS = os.path.join(HERE, "..")
SECTIONS = ("## Done", "## Tests and breaks", "## Changes to old rules", "## Assumptions", "## Open questions")
FIRST_FIXED = 23                       # the five sections are the format since package 23
MIN_LINES = 15                         # a report shorter than this is a truncated file
NL = chr(10)


def reports():
    out = []
    for p in sorted(glob.glob(os.path.join(REPORTS, "PACKAGE*_REPORT.md"))):
        m = re.match(r"PACKAGE(\d+)_REPORT\.md$", os.path.basename(p))
        if m and int(m.group(1)) >= FIRST_FIXED:
            out.append(p)
    return out


def check(path):
    """[(name, "missing", sections) / (name, "short", lines)] of one report."""
    bad = []
    lines = open(path, encoding="utf-8").read().split(NL)
    missing = [h for h in SECTIONS if not any(ln.startswith(h) for ln in lines)]
    if missing:
        bad.append((os.path.basename(path), "missing", missing))
    if len(lines) < MIN_LINES:
        bad.append((os.path.basename(path), "short", len(lines)))
    return bad


def _problems():
    return [b for p in reports() for b in check(p)]


def _truncated():
    p = os.path.join(tempfile.mkdtemp(prefix="wp_rep_"), "PACKAGE99_REPORT.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write(NL + "- Not built on purpose: Lite." + NL)
    return check(p)


S.case("r-sections", "owner (package 36 P1.1): every report of package 23+ has the five sections and is not truncated",
       [])(_problems)
S.case("r-truncated", "the check catches the package 35 accident: a 3-line report misses every section and is short",
       [("PACKAGE99_REPORT.md", "missing", list(SECTIONS)), ("PACKAGE99_REPORT.md", "short", 3)])(_truncated)
S.case("r-found", "the check sees the reports (at least packages 23-35)", True)(lambda: len(reports()) >= 13)

if __name__ == "__main__":
    sys.exit(S.run())
