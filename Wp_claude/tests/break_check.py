"""Deliberate break check (CLAUDE.md "Standard package procedure").

Each registry entry (Wp_claude/tests/breaks/*.py, list ENTRIES) breaks ONE rule in the code and names the
test suites that must fail:
    dict(id="...", file="wp/...", old="exact text", new="broken text", suites=("core/test_x.py", ...), rule="...")
`old` / `new` are written with "\\n"; they are matched with the file's own line endings.
The runner copies wp/, Wp_claude/tests/, Wp_claude/RULES/ and Wp_claude/tools/ to a TEMP directory, checks that
each named suite passes there WITHOUT a break (else the entry proves nothing: "not applied"), applies one break at a time
THERE (the working tree is never touched), runs only the named suites, and reports caught / missed per entry.
Exit code 1 if any entry is missed or does not apply.
Usage: python Wp_claude/tests/break_check.py [id-prefix ...]
"""
import glob
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
COPY = ("wp", os.path.join("Wp_claude", "tests"), os.path.join("Wp_claude", "RULES"), os.path.join("Wp_claude", "tools"),
        os.path.join("Wp_claude", "TRANSLATION_TODO.md"), os.path.join("Wp_claude", "REVIEW_PACK"),
        os.path.join("Wp_claude", "ARCH"))                # view_contract.md (review 5 F30)


def registry():
    out = []
    for f in sorted(glob.glob(os.path.join(HERE, "breaks", "*.py"))):
        if os.path.basename(f).startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location("breaks_" + os.path.basename(f)[:-3], f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out += list(mod.ENTRIES)
    return out


def _copy(tmp):
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    for rel in COPY:
        src = os.path.join(ROOT, rel)
        if os.path.isfile(src):
            os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
            shutil.copy2(src, os.path.join(tmp, rel))
        elif os.path.isdir(src):
            shutil.copytree(src, os.path.join(tmp, rel), ignore=ignore)


def _passes(suite, tmp):
    r = subprocess.run([sys.executable, os.path.join(tmp, "Wp_claude", "tests", suite)], capture_output=True, text=True,
                       cwd=tmp)
    return r.returncode == 0


def _clean_pass(suite, tmp):
    """Does the suite pass on the clean copy? A failure is run once more alone before it counts (package 29 C: a
    timing budget may fail once on a loaded machine); the second result is final."""
    if _passes(suite, tmp):
        return True
    again = _passes(suite, tmp)
    print("%-8s %-40s %s" % ("rerun", suite, "passes on the second run" if again else "fails twice on the clean copy"))
    return again


def check(entry, tmp, clean):
    """'caught', 'missed' or 'not applied (...)' for one entry, run inside the temp copy.
    clean: {suite: passes without any break}; a suite that already fails proves nothing (package 18)."""
    bad = [s for s in entry["suites"] if not clean.setdefault(s, _clean_pass(s, tmp))]
    if bad:
        return "not applied (suite fails without a break: %s)" % ", ".join(bad)
    path = os.path.join(tmp, entry["file"])
    raw = open(path, "rb").read()
    nl = b"\r\n" if b"\r\n" in raw else b"\n"
    old = entry["old"].encode("ascii").replace(b"\n", nl)
    new = entry["new"].encode("ascii").replace(b"\n", nl)
    if raw.count(old) != 1:
        return "not applied (pattern found %d times)" % raw.count(old)
    try:
        open(path, "wb").write(raw.replace(old, new))
        failed = []
        for s in entry["suites"]:
            r = subprocess.run([sys.executable, os.path.join(tmp, "Wp_claude", "tests", s)], capture_output=True,
                               text=True, cwd=tmp)
            if r.returncode != 0:
                failed.append(s)
        return "caught" if failed else "missed"
    finally:
        open(path, "wb").write(raw)


def main(prefixes):
    entries = [e for e in registry() if not prefixes or any(e["id"].startswith(p) for p in prefixes)]
    bad = 0
    tmp = tempfile.mkdtemp(prefix="wp_breaks_")
    try:
        _copy(tmp)
        clean = {}
        for e in entries:
            res = check(e, tmp, clean)
            if res != "caught":
                bad += 1
            print("%-8s %-40s %s" % ("ok" if res == "caught" else "MISSED", e["id"], "" if res == "caught" else res))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("entries %d, caught %d, missed %d" % (len(entries), len(entries) - bad, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
