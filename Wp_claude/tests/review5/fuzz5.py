"""Review 5 / area 5: fuzz of EVERY command of the registry through Session.dispatch with random valid and hostile
parameters (common.rand_params). After every step: no exception other than a refusal result; the review 4
invariants (resources >= 0, journal +1 only on a change, no journal line for a no-op, views work, save/load round
trip); every panel view works and has no NaN / inf; ids unique per collection and never reused after removal;
save -> load -> save gives the same text. At the end: a save that fails in the middle keeps the old file.
Run: python Wp_claude/tests/review5/fuzz5.py [sequences] [steps] [first_seed]"""
import os
import random
import sys
from collections import Counter

from common import REGISTRY, all_views, bad_numbers, drop, rand_params, temp_session
import fuzz as f4
from wp.commands import CHANGED
from wp.storage import character_io as cio

CMDS = sorted(REGISTRY)
COLL = (("items", "iid"), ("statuses", "sid"), ("attacks", "rid"), ("feats", "fid"), ("pools", "pid"),
        ("maneuvers", "mid"), ("injuries", "jid"), ("templates", "tid"), ("quirks", "kid"), ("drives", "did"),
        ("spells", "spid"))


class _R(object):
    def __init__(self, changed):
        self.events = (CHANGED,) if changed else ()


def id_state(ch):
    out = {}
    for coll, key in COLL:
        out[coll] = [getattr(x, key, None) for x in getattr(ch, coll, ())]
    return out


def main(n_seq=400, n_steps=50, first=1):
    seen = {}
    used = Counter()
    ok = steps = 0
    for seed in range(first, first + n_seq):
        r = random.Random(seed)
        s = temp_session()
        ever = {c: set() for c, _ in COLL}
        gone = {c: set() for c, _ in COLL}
        for c, ids in id_state(s.character).items():
            ever[c] |= set(ids)
        for i in range(n_steps):
            before = s.character
            if r.random() < 0.04:
                res = s.undo() if r.random() < 0.6 else s.redo()
                cmd, params = "undo/redo", {}
            else:
                cmd = r.choice(CMDS)
                params = rand_params(r, cmd, before)
                try:
                    res = s.dispatch(cmd, **params)
                except Exception as e:  # noqa: BLE001
                    kind = "EXCEPTION %s in %s: %s" % (type(e).__name__, cmd, str(e)[:70])
                    seen.setdefault(kind, (seed, i, cmd, params))
                    continue
            steps += 1
            used[cmd] += 1
            after = s.character
            ok += res.ok
            if cmd == "undo/redo":
                continue
            kinds = f4.invariants(before, after, _R(len(after.log) > len(before.log)), cmd) if res.ok else []
            if not res.ok and after is not before:
                kinds.append("state changed on a refusal")
            v = all_views(s)
            for k, x in v.items():
                if isinstance(x, tuple) and x and x[0] == "RAISED":
                    kinds.append("view %s raised %s" % (k, x[1]))
                elif bad_numbers(x):
                    kinds.append("view %s has NaN/inf at %s" % (k, bad_numbers(x)[0]))
            ids = id_state(after)
            for c, lst in ids.items():
                if len(lst) != len(set(lst)):
                    kinds.append("duplicate ids in %s" % c)
                now = set(lst)
                back = (now & gone[c]) - set(id_state(before)[c])
                if back:
                    kinds.append("id reused in %s" % c)
                gone[c] |= (set(id_state(before)[c]) - now)
                ever[c] |= now
            try:
                t1 = cio.dumps(after)
                t2 = cio.dumps(cio.loads(t1))
                if t1 != t2:
                    kinds.append("save -> load -> save not stable")
            except Exception as e:  # noqa: BLE001
                kinds.append("save raised %s" % type(e).__name__)
            for k in kinds:
                seen.setdefault(k if "[" not in k else k, (seed, i, cmd, params))
        drop(s)
    print("fuzz5: sequences %d, steps %d, ok %d, commands used %d of %d, distinct findings %d" % (
        n_seq, steps, ok, len([c for c in used if c != "undo/redo"]), len(CMDS), len(seen)))
    for k, (seed, i, cmd, params) in sorted(seen.items()):
        print("- %s | seed %d step %d | %s %r" % (k, seed, i, cmd, {a: (str(b)[:30]) for a, b in params.items()}))
    never = [c for c in CMDS if used[c] == 0]
    if never:
        print("never called: %s" % never)


def partial_write():
    """A save that dies in the middle (fsync raises) must keep the old file intact and leave no .tmp."""
    s = temp_session()
    p = os.path.join(s.characters_dir, s.name + ".json")
    old = open(p, encoding="utf-8").read()
    s.dispatch("take_damage", amount=5)
    real = os.fsync

    def boom(fd):
        raise OSError("disk full (simulated)")
    os.fsync = boom
    try:
        s.save()
        out = "save did not fail"
    except Exception as e:  # noqa: BLE001
        out = "%s %s" % (type(e).__name__, getattr(e, "reason", ""))
    finally:
        os.fsync = real
    print("partial write: %s; old file intact: %s; tmp files left: %s" % (
        out, open(p, encoding="utf-8").read() == old, [f for f in os.listdir(s.characters_dir) if ".tmp" in f]))
    drop(s)


if __name__ == "__main__":
    main(*[int(x) for x in sys.argv[1:4]])
    partial_write()
