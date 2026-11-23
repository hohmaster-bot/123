"""Code files are ASCII only (CLAUDE.md hard rule, D4).
Checks every .py in wp/, Wp_claude/tests/ and Wp_claude/tools/. Legacy files at the repo root are
reference only and are not checked. Non-ASCII text belongs in locale or data files;
in code write it as escape codes.
Run: python Wp_claude/tests/test_ascii_code.py   (exit 1 if any file has a non-ASCII byte)"""
import os
import sys

TESTS = os.path.abspath(os.path.dirname(__file__))
REPO = os.path.dirname(os.path.dirname(TESTS))
ROOTS = (os.path.join(REPO, "wp"), TESTS, os.path.join(REPO, "Wp_claude", "tools"))  # tools: package 20


def py_files():
    for root in ROOTS:
        for folder, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for name in files:
                if name.endswith(".py"):
                    yield os.path.join(folder, name)


def bad_lines(path):
    """(line number, column) of every non-ASCII byte."""
    out = []
    with open(path, "rb") as f:
        for n, line in enumerate(f, 1):
            for col, byte in enumerate(line, 1):
                if byte > 127:
                    out.append((n, col))
                    break
    return out


def main():
    files = list(py_files())
    bad = 0
    for path in files:
        hits = bad_lines(path)
        if hits:
            bad += 1
            rel = os.path.relpath(path, REPO)
            print("NOT ASCII: %s line %d col %d (%d lines)" % (rel, hits[0][0], hits[0][1], len(hits)))
    print("test_ascii_code: %d files, non-ASCII %d" % (len(files), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
