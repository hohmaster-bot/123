"""Package 20 part 2: the rules pack for an independent reviewer (Wp_claude/REVIEW_PACK/RULES_PACK.md).
It builds, is ONE file, is up to date with RULES and the data, names every RULES file, has no Python code block and
stays under 400 KB. Prints its size and word count.
Run: python Wp_claude/tests/test_review_pack.py"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "core"))
from _runner import ROOT, Suite  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "Wp_claude", "tools"))
import make_review_pack as mrp  # noqa: E402

S = Suite("test_review_pack")
TEXT = mrp.build_text()
LIMIT = 400 * 1024


def _committed():
    if not os.path.exists(mrp.OUT):
        return None
    with io.open(mrp.OUT, encoding="utf-8") as f:
        return f.read()


S.case("r-up-to-date", "pkg 20: the committed pack equals a fresh build (run tools/make_review_pack.py after a RULES change)",
       True)(lambda: _committed() == TEXT)
S.case("r-one-file", "pkg 20: the pack folder holds exactly one file", ["RULES_PACK.md"])(
    lambda: sorted(os.listdir(os.path.dirname(mrp.OUT))))
S.case("r-every-rules-file", "pkg 20: every RULES file name is in the pack", [])(
    lambda: [f for f in os.listdir(mrp.RULES) if f.endswith(".md") and f not in mrp.SKIP and f not in TEXT])
S.case("r-no-python", "pkg 20: no Python code block", False)(lambda: "```python" in TEXT or "```py\n" in TEXT)
S.case("r-size", "pkg 20: under 400 KB", True)(lambda: len(TEXT.encode("utf-8")) < LIMIT)
S.case("r-task", "pkg 20: the cover holds the review task and the answer table", True)(
    lambda: "Your review task" in TEXT and "| id | file / section | type" in TEXT)

if __name__ == "__main__":
    print("RULES_PACK.md: %d bytes, %d words" % (len(TEXT.encode("utf-8")), len(TEXT.split())))
    sys.exit(S.run())
