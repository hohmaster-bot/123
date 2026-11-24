"""Benchmark of the heavy character (package 23 B): load, one dispatch, every panel view, save; --profile prints the
cProfile top 10 of computing all views. Budgets: wp/app/data/perf_budgets.json (they depend on the hardware).
Usage: python Wp_claude/tools/bench.py [--profile]"""
import cProfile
import io
import json
import os
import pstats
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "Wp_claude", "tests", "perf"))
import heavy  # noqa: E402

from wp.app import views as vw  # noqa: E402
from wp.model import cache  # noqa: E402
from wp.app.session import Session  # noqa: E402

BUDGETS = os.path.join(ROOT, "wp", "app", "data", "perf_budgets.json")


def budgets():
    with io.open(BUDGETS, encoding="utf-8") as f:
        return json.load(f)


def ms(fn, repeat=1):
    """Best of `repeat` runs, the read cache cleared before every run (a fresh computation each time)."""
    best = None
    for _ in range(repeat):
        cache.clear()
        t = time.perf_counter()
        fn()
        d = (time.perf_counter() - t) * 1000.0
        best = d if best is None else min(best, d)
    return best


def measure(repeat=3):
    d = tempfile.mkdtemp(prefix="wp_bench_")
    try:
        s = Session(os.path.join(d, "ch"), os.path.join(d, "user"))
        s.new("Heavy", heavy.heavy())
        out = {"load_ms": ms(lambda: s.open("Heavy"), repeat)}
        out["views_ms"] = {name: ms(lambda name=name: s.view(name), repeat) for name in vw.VIEWS}

        def dispatch_and_refresh():
            s.dispatch("take_damage", amount=1)
            for name in vw.VIEWS:
                s.view(name)
        out["dispatch_all_views_ms"] = ms(dispatch_and_refresh, repeat)
        out["save_ms"] = ms(s.save, repeat)

        def dispatch_undo_redo():                 # package 25 A: the undo stack keeps states, no copies
            s.dispatch("take_damage", amount=1)
            s.undo()
            s.redo()
        out["undo_redo_ms"] = ms(dispatch_undo_redo, repeat)
        return out
    finally:
        shutil.rmtree(d, ignore_errors=True)


def profile():
    d = tempfile.mkdtemp(prefix="wp_bench_")
    try:
        s = Session(os.path.join(d, "ch"), os.path.join(d, "user"))
        s.new("Heavy", heavy.heavy())
        pr = cProfile.Profile()
        pr.enable()
        for name in vw.VIEWS:
            s.view(name)
        pr.disable()
        buf = io.StringIO()
        pstats.Stats(pr, stream=buf).sort_stats("cumulative").print_stats(10)
        return buf.getvalue()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main(argv):
    m = measure()
    b = budgets()
    print("load %.1f ms (budget %d)" % (m["load_ms"], b["load_ms"]))
    for name, v in sorted(m["views_ms"].items(), key=lambda kv: -kv[1]):
        print("view %-10s %.1f ms (budget %d)" % (name, v, b["view_ms"]))
    print("dispatch + all views %.1f ms (budget %d)" % (m["dispatch_all_views_ms"], b["dispatch_all_views_ms"]))
    print("save %.1f ms" % m["save_ms"])
    print("dispatch + undo + redo %.1f ms" % m["undo_redo_ms"])
    if "--profile" in argv:
        print(profile())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
