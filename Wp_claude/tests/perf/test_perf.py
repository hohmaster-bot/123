"""Package 23 B: performance budgets of the heavy character (wp/app/data/perf_budgets.json; they depend on the
hardware, with a margin) and the read cache: cached results equal uncached ones for random commands, and no cache
survives a command. Run: python Wp_claude/tests/perf/test_perf.py"""
import os
import random
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import ROOT, Suite  # noqa: E402

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "Wp_claude", "tools"))
import bench  # noqa: E402
import heavy  # noqa: E402

from wp.app import views as vw  # noqa: E402
from wp.app.session import Session  # noqa: E402
from wp.commands import dispatch  # noqa: E402
from wp.model import cache  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_perf")
B = bench.budgets()
BEST_OF = 3                            # package 29 C: a budget never fails from one slow run
M = bench.measure(repeat=BEST_OF)


def slow_views():
    return sorted(name for name, v in M["views_ms"].items() if v > B["view_ms"])


S.case("b-views", "pkg 23: every panel view of the heavy character under the view budget", [])(slow_views)
S.case("b-dispatch", "pkg 23: one command + all views under the budget", True)(lambda: M["dispatch_all_views_ms"] < B["dispatch_all_views_ms"])
S.case("b-load", "pkg 23: opening the heavy character under the budget", True)(lambda: M["load_ms"] < B["load_ms"])

STEPS = (("take_damage", {"amount": 3}), ("tick", {}), ("start_combat", {}), ("restore", {"resource": "hp", "amount": 2}),
         ("activate_status", {"sid": "s5"}), ("set_rule_setting", {"key": "training.ability_step", "value": 100}),
         ("end_combat", {}), ("spend_bp", {"n": 1}), ("use_attack", {"rid": "r0"}), ("delete_status", {"sid": "s7"}))


def _views(ch):
    with rd.using(ch):
        return {name: repr(fn(ch)) for name, fn in vw.VIEWS.items()}


def _property():
    rng = random.Random(23)
    ch = heavy.heavy()
    bad = []
    for i in range(12):
        name, params = STEPS[rng.randrange(len(STEPS))]
        try:
            ch = dispatch(ch, name, **params).state
        except Exception:
            continue
        cached = _views(ch)
        with cache.disabled():
            plain = _views(ch)
        bad += ["%d %s %s" % (i, name, v) for v in cached if cached[v] != plain[v]]
    return bad


S.case("c-equal", "pkg 23: cached views equal uncached views after random commands", [])(_property)


def _cleared():
    ch = heavy.heavy()
    with rd.using(ch):
        vw.VIEWS["attacks"](ch)
    box = cache._STORE.get(id(ch))
    dispatch(ch, "take_damage", amount=1)
    return box is not None, cache._STORE.get(id(ch)) is not box


S.case("c-cleared", "pkg 23: a command drops the cache entries made before it (the command may compute new ones)",
       (True, True))(_cleared)


def _override_not_mixed():
    ch = heavy.heavy()
    c2 = dispatch(ch, "set_rule_setting", key="ac.base", value=12).state
    with rd.using(c2):
        a = vw.VIEWS["defense"](c2)["modes"]["front"]
    b = vw.VIEWS["defense"](c2)["modes"]["front"]     # outside its scope: the table defaults
    return a - b


S.case("c-scope", "pkg 23: a value computed under other rule constants is never reused (AC base 12 vs 10)", 2)(_override_not_mixed)


def _mod_scope():
    from wp.model import derived_view as dv
    from wp.model.character import ABILITIES, Ability, Character
    ch = Character(abilities={a: Ability(base=14 if a == "dex" else 10) for a in ABILITIES})
    c2 = dispatch(ch, "set_rule_setting", key="ability.mod_base", value=12).state
    with rd.using(c2):
        a = dv.ability_mod(c2, "dex")                 # (14 - 12) // 2 = 1
    return a, dv.ability_mod(c2, "dex")               # outside the scope: (14 - 10) // 2 = 2


S.case("c-scope-cached", "pkg 23: a cached function (ability_mod) keyed by the rule scope: Dex 14 with base 12 -> 1, "
       "with the default 10 -> 2", (1, 2))(_mod_scope)

def _journal_save():
    """Package 27 E (review 5 F29): the heavy character with a 50 000-line journal, opened by the Session (journal_mode
    full: the old lines go into the archive at once), then one command and a save: under the save budget."""
    import time
    from dataclasses import replace
    from wp.model.character import LogEntry
    d = tempfile.mkdtemp(prefix="wp_perf_j_")
    try:
        ch = heavy.heavy()
        log = tuple(LogEntry(seq=i + 1, command="take_damage", kind="damage", params={"amount": 3},
                             at="20260101-000000-000") for i in range(JOURNAL_LINES))
        ch = replace(ch, log=log, log_seq=JOURNAL_LINES)
        s = Session(os.path.join(d, "ch"), os.path.join(d, "user"))
        s.new("heavy", ch)
        s.dispatch("add_experience", amount=1)
        best = None
        for _ in range(BEST_OF):
            t = time.perf_counter()
            s.save()
            ms = (time.perf_counter() - t) * 1000.0
            best = ms if best is None else min(best, ms)
        return best < B["save_journal_ms"], len(s.full_log())
    finally:
        shutil.rmtree(d, ignore_errors=True)


JOURNAL_LINES = 50000
S.case("b-save-journal", "pkg 27 E: save of the heavy character with a 50 000-line journal (archived) under the budget; "
       "the full log keeps 50 001 lines", (True, 50001))(_journal_save)

if __name__ == "__main__":
    print("load %.1f ms, dispatch + views %.1f ms, slowest view %.1f ms" % (
        M["load_ms"], M["dispatch_all_views_ms"], max(M["views_ms"].values())))
    sys.exit(S.run())
