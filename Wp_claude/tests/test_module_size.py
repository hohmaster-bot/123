"""Every module in wp/ has at most 500 lines (CLAUDE.md, START.md).
Run: python Wp_claude/tests/test_module_size.py   (exit 1 if any file is too big)"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO = os.path.dirname(ROOT)
LIMIT = 500


def sizes():
    out = []
    for folder, dirs, files in os.walk(os.path.join(REPO, "wp")):
        dirs[:] = [x for x in dirs if x != "__pycache__"]
        for name in files:
            if name.endswith(".py"):
                path = os.path.join(folder, name)
                with open(path, encoding="utf-8") as f:
                    out.append((os.path.relpath(path, REPO), sum(1 for _ in f)))
    return sorted(out)


def main():
    files = sizes()
    big = [(p, n) for p, n in files if n > LIMIT]
    for p, n in big:
        print("TOO BIG: %s has %d lines (limit %d)" % (p, n, LIMIT))
    top = max(files, key=lambda x: x[1])
    print("test_module_size: %d files, largest %s (%d lines), over limit %d" % (
        len(files), top[0], top[1], len(big)))
    return 1 if big else 0


if __name__ == "__main__":
    sys.exit(main())
