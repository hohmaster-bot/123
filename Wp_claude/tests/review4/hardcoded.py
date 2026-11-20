"""Review 4: count numeric literals in wp/ (rule constants written in code instead of data).
Module-level NAME = number lines are "named constants" (still code, not rules_settings); inline literals other
than 0 and 1 inside functions are "scattered literals". Run: python Wp_claude/tests/review4/hardcoded.py
"""
import ast
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
WP = os.path.join(ROOT, "wp")
SKIP_VALUES = {0, 1, -1}


def scan(path):
    tree = ast.parse(open(path, encoding="ascii").read())
    named, inline = [], []
    top = {id(n) for n in tree.body}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            nums = [n.value for n in ast.walk(node.value) if isinstance(n, ast.Constant)
                    and isinstance(n.value, (int, float)) and not isinstance(n.value, bool)]
            if nums and node.targets[0].id.isupper():
                named.append((node.lineno, node.targets[0].id, nums[:6]))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef,)):
            for n in ast.walk(node):
                if (isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool)
                        and n.value not in SKIP_VALUES):
                    inline.append((n.lineno, n.value))
    return named, inline


def main():
    tot_named = tot_inline = 0
    rows = []
    for folder, dirs, files in os.walk(WP):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in sorted(files):
            if f.endswith(".py"):
                p = os.path.join(folder, f)
                named, inline = scan(p)
                tot_named += len(named)
                tot_inline += len(inline)
                if named or inline:
                    rows.append((os.path.relpath(p, ROOT), named, inline))
    for rel, named, inline in rows:
        print("%s: named %d, inline %d" % (rel, len(named), len(inline)))
        for ln, name, nums in named:
            print("    L%d %s = %s" % (ln, name, nums))
        if inline:
            print("    inline: %s" % ", ".join("L%d:%s" % x for x in inline[:25]))
    print("TOTAL named constants %d, inline literals %d" % (tot_named, tot_inline))


if __name__ == "__main__":
    sys.exit(main())
