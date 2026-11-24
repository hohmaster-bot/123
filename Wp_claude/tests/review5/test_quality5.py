"""Review 5 / area 6: static scan of the newer suites.
- expected values that are NOT literals (computed by a call: a possible tautology, the code checks itself);
- expected values that are weak (True / False / None / () / refusal words) where a number could be checked;
- the same case body evaluated twice as both sides ("lambda: f(x)" with expected f(x));
- suites without any S.case and without assert / raise SystemExit (they can pass without checking);
- suites whose case count is 0 when run (prints the summary line only).
Run: python Wp_claude/tests/review5/test_quality5.py"""
import ast
import glob
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
NEW = (["model/test_pkg16a.py", "model/test_pkg16b.py", "model/test_pkg17.py", "model/test_pkg20.py",
        "model/test_pkg22.py", "model/test_pkg24.py", "model/test_pkg25.py", "app/test_session.py",
        "perf/test_perf.py", "model/test_ac_zones.py", "storage/test_settings.py", "storage/test_catalogs.py",
        "storage/test_i18n.py", "storage/test_themes_panels.py", "test_rule_literals.py", "test_review_pack.py",
        "app/test_view_contract.py"])
WEAK = (True, False, None, (), "ok", "refused", "allowed")


def src_of(text, node):
    return ast.get_source_segment(text, node) or ""


def scan(rel):
    path = os.path.join(TESTS, rel)
    if not os.path.exists(path):
        return None
    text = open(path, encoding="ascii").read()
    tree = ast.parse(text)
    n = weak = computed = 0
    comp_examples = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "case" \
                and len(node.args) >= 3:
            n += 1
            exp = node.args[2]
            try:
                val = ast.literal_eval(exp)
                if val in WEAK or (isinstance(val, tuple) and val and all(v in (True, False) for v in val)):
                    weak += 1
            except (ValueError, TypeError, SyntaxError):
                calls = [c for c in ast.walk(exp) if isinstance(c, ast.Call)]
                names = {src_of(text, c.func) for c in calls}
                if calls and not names <= {"tuple", "list", "dict", "set", "frozenset", "range", "sorted", "len",
                                           "str", "int", "max", "min", "sum", "FrozenDict", "Pool"}:
                    computed += 1
                    if len(comp_examples) < 3:
                        comp_examples.append("line %d: %s" % (node.lineno, src_of(text, exp)[:70]))
    asserts = sum(isinstance(x, ast.Assert) for x in ast.walk(tree)) + text.count("SystemExit") + \
        text.count("sys.exit")
    return n, weak, computed, comp_examples, asserts


def main():
    print("| suite | cases | weak expected | computed expected | asserts/exits |")
    tot = Counter()
    for rel in NEW:
        r = scan(rel)
        if r is None:
            print("| %s | MISSING FILE | | | |" % rel)
            continue
        n, weak, computed, ex, asserts = r
        tot.update(cases=n, weak=weak, computed=computed)
        print("| %s | %d | %d | %d | %d |" % (rel, n, weak, computed, asserts))
        for e in ex:
            print("|  | | | %s | |" % e)
        if n == 0 and asserts == 0:
            print("|  | NO CHECKS AT ALL | | | |")
    print("total cases %(cases)d, weak %(weak)d, computed (possible tautology) %(computed)d" % tot)


if __name__ == "__main__":
    main()
