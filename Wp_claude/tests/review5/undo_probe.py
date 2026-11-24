"""Review 5 / area 2: undo / redo properties.
1) random valid sequences: undo all -> state (without journal) equals the start; redo all -> equals the end;
2) a non-undoable command (set_char_setting) between undoable ones: undo of the earlier command must keep it;
3) the journal after undo / redo: undo lines kept? log seq numbers reused?
4) memory of 500 steps on the heavy character.
Run: python Wp_claude/tests/review5/undo_probe.py"""
import os
import random
import sys
import tracemalloc
from dataclasses import replace

from common import ROOT, drop, rand_params, temp_session, REGISTRY

sys.path.insert(0, os.path.join(ROOT, "Wp_claude", "tests", "perf"))
from heavy import heavy  # noqa: E402

SAFE = sorted(c for c in REGISTRY if c not in ("set_char_setting", "reset_char_setting"))


def nolog(ch):
    return replace(ch, log=(), log_seq=0)


def prop(seeds=30, steps=40):
    bad = []
    for seed in range(seeds):
        r = random.Random(seed)
        s = temp_session()
        orig = s.setting
        s.setting = lambda k, orig=orig: 1000 if k == "undo_depth" else orig(k)
        start = s.character
        done = 0
        for _ in range(steps):
            cmd = r.choice(SAFE)
            try:
                res = s.dispatch(cmd, **rand_params(r, cmd, s.character, ))
            except Exception:  # noqa: BLE001
                continue
            done += res.ok
        end = s.character
        n = len(s._undo)
        while s.can_undo():
            s.undo()
        if nolog(s.character) != nolog(start):
            bad.append(("undo-all != start", seed))
        while s.can_redo():
            s.redo()
        if nolog(s.character) != nolog(end):
            bad.append(("redo-all != end", seed))
        if seed == 0:
            print("seed 0: %d ok commands, undo stack %d (depth setting %s)" % (done, n, s.setting("undo_depth")))
        drop(s)
    print("property: %d seeds, violations %d %s" % (seeds, len(bad), bad[:5]))


def non_undoable_kept():
    s = temp_session()
    s.dispatch("restore", resource="hp", amount=0)
    s.dispatch("take_damage", amount=3)
    from wp.settings import schema
    char_keys = [k for k in schema.keys_of("character")] if hasattr(schema, "keys_of") else []
    res = None
    for k in char_keys:
        f = schema.FIELDS.get(k) if hasattr(schema, "FIELDS") else None
        for v in ("img1", "", True, 1):
            res = s.dispatch("set_char_setting", key=k, value=v)
            if res.ok:
                break
        if res and res.ok:
            break
    if not (res and res.ok):
        print("non-undoable: could not set any char setting (keys %r)" % (char_keys[:5],))
        return
    after_set = s.character.char_settings
    s.undo()        # undoes take_damage, the setting was made AFTER it
    print("non-undoable: set_char_setting %s=%r then undo of the earlier take_damage -> setting kept: %s" % (
        k, v, s.character.char_settings == after_set))
    drop(s)


def journal_after_undo():
    s = temp_session()
    s.dispatch("take_damage", amount=1)
    s.dispatch("take_damage", amount=2)
    s.dispatch("take_damage", amount=3)
    seqs_before = [e.seq for e in s.character.log]
    s.undo()
    s.undo()
    log = s.character.log
    print("journal: after 3 commands + 2 undo: lines=%s, 'undo' lines=%d (expected 2), last seq=%d, seqs used "
          "before=%s" % ([e.command for e in log][-4:], sum(1 for e in log if e.command == "undo"), log[-1].seq,
                         seqs_before[-3:]))
    s.redo()
    log = s.character.log
    print("journal: after redo: lines=%s" % ([e.command for e in log][-5:],))
    drop(s)


def memory(steps=500):
    s = temp_session(heavy())
    s.app = s.app
    tracemalloc.start()
    base = tracemalloc.get_traced_memory()[0]
    for i in range(steps):
        s.dispatch("take_damage", amount=1) if i % 2 else s.dispatch("restore", resource="hp", amount=1)
    cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print("memory: heavy character, %d commands, undo stack %d (depth %s): +%.1f MB now, peak +%.1f MB" % (
        steps, len(s._undo), s.setting("undo_depth"), (cur - base) / 1e6, (peak - base) / 1e6))
    drop(s)


if __name__ == "__main__":
    prop()
    non_undoable_kept()
    journal_after_undo()
    memory()
