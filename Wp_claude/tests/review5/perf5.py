"""Review 5 / area 7: performance on the heavy character and on bigger ones (x3 items / statuses / skills, journal
50,000 lines), memory, the slowest views, growth factor per view (x1 -> x3: ~3 = linear, ~9 = quadratic).
Run: python Wp_claude/tests/review5/perf5.py"""
import os
import sys
import time
import tracemalloc
from dataclasses import replace

from common import ROOT, cache, drop, temp_session
from wp.app import views as vw
from wp.model.character import LogEntry

sys.path.insert(0, os.path.join(ROOT, "Wp_claude", "tests", "perf"))
from heavy import heavy  # noqa: E402


def scaled(k, log_lines=5000):
    h = heavy()

    def many(seq, key):
        out = []
        for i in range(k):
            for x in seq:
                out.append(replace(x, **{key: "%s_%d" % (getattr(x, key), i)}) if i else x)
        return tuple(out)
    items = many(h.items, "iid")
    statuses = many(h.statuses, "sid")
    log = tuple(LogEntry(seq=i + 1, command="tick", kind="combat", params={}, result={"n": i}) for i in range(log_lines))
    return replace(h, items=items, statuses=statuses, log=log, log_seq=log_lines)


def ms(fn):
    best = None
    for _ in range(3):
        cache.clear()
        t = time.perf_counter()
        fn()
        d = (time.perf_counter() - t) * 1000.0
        best = d if best is None else min(best, d)
    return best


def measure(ch):
    s = temp_session(ch)
    out = {"load": ms(lambda: s.open(s.name)), "save": ms(s.save)}
    out["views"] = {n: ms(lambda n=n: s.view(n)) for n in vw.VIEWS}

    def all_views():
        s.dispatch("take_damage", amount=1)
        for n in vw.VIEWS:
            s.view(n)
    out["dispatch_all"] = ms(all_views)
    size = os.path.getsize(os.path.join(s.characters_dir, s.name + ".json"))
    tracemalloc.start()
    s.open(s.name)
    for n in vw.VIEWS:
        s.view(n)
    out["peak_mb"] = tracemalloc.get_traced_memory()[1] / 1e6
    tracemalloc.stop()
    out["file_kb"] = size / 1024
    drop(s)
    return out


def main():
    r1 = measure(scaled(1))
    r3 = measure(scaled(3))
    rj = measure(scaled(1, 50000))
    print("%-22s %10s %10s %8s %12s" % ("", "heavy", "x3", "factor", "journal 50k"))
    for k in ("load", "save", "dispatch_all", "peak_mb", "file_kb"):
        print("%-22s %10.1f %10.1f %8.2f %12.1f" % (k, r1[k], r3[k], r3[k] / max(r1[k], 1e-6), rj[k]))
    print("slowest views (ms):")
    for n in sorted(vw.VIEWS, key=lambda n: -r3["views"][n])[:8]:
        print("  %-12s %8.2f %8.2f  x%.2f  journal50k %8.2f" % (n, r1["views"][n], r3["views"][n],
                                                                 r3["views"][n] / max(r1["views"][n], 1e-3),
                                                                 rj["views"][n]))
    worst = [n for n in vw.VIEWS if r1["views"][n] > 1 and r3["views"][n] / r1["views"][n] > 5]
    print("views growing faster than linear (x3 data -> > x5 time): %s" % worst)


if __name__ == "__main__":
    main()
