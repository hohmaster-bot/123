"""Package 23 C: ARCH/view_contract.md is up to date (regenerate: python Wp_claude/tools/make_view_contract.py),
names every panel of the registry and every command of the topics table.
Run: python Wp_claude/tests/app/test_view_contract.py"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import ROOT, Suite  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "Wp_claude", "tools"))
import make_view_contract as mvc  # noqa: E402

from wp.app import session as sm  # noqa: E402
from wp.panels import registry  # noqa: E402

S = Suite("test_view_contract")
TEXT = mvc.build_text()


def _on_disk():
    with io.open(mvc.OUT, encoding="utf-8") as f:
        return f.read()


S.case("vc-up-to-date", "pkg 23 C: the file equals the generator output (run tools/make_view_contract.py)", True)(
    lambda: _on_disk() == TEXT)
S.case("vc-deterministic", "pkg 23 C: two runs give the same text", True)(lambda: mvc.build_text() == TEXT)
S.case("vc-panels", "pkg 23 C: a section for every registry panel", [])(
    lambda: sorted(p for p in registry.PANELS if "\n## %s\n" % p not in TEXT))
S.case("vc-commands", "pkg 23 C: every command of the topics table is named", [])(
    lambda: sorted(c for c in sm.TOPICS if "`%s" % c not in TEXT))

if __name__ == "__main__":
    sys.exit(S.run())
