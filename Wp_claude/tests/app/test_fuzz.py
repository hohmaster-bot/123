"""Package 27 B (review 5 F4 F5 F13 F14 F21): a permanent fuzz of EVERY command through Session.dispatch.
The random valid / hostile parameters come from tests/review5/common.py (kept untouched, as is tests/review5/fuzz5.py).
60 sequences x 50 steps = 3000 steps, seeds 1..60 (fixed: the run is the same every time). After every step:
- no exception other than a refusal leaves Session.dispatch; a refusal keeps the state;
- no panel view raises and no view holds NaN / inf;
- the review 4 invariants hold (resources >= 0 ...) except "pool read out of bounds": a pool above its max is
  allowed (owner, package 27 F28: the view flags over_max);
- save -> load -> save gives the same text (no NaN in the file).
Run: python Wp_claude/tests/app/test_fuzz.py"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "review5"))
from _runner import Suite  # noqa: E402

from common import REGISTRY, all_views, bad_numbers, drop, rand_params, temp_session  # noqa: E402
import fuzz as f4  # noqa: E402
from wp.commands import CHANGED  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_fuzz")
SEQUENCES, STEPS = 60, 50
ALLOWED = ("pool read out of bounds",)


class _R(object):
    def __init__(self, changed):
        self.events = (CHANGED,) if changed else ()


def _run():
    found = {}
    cmds = sorted(REGISTRY)
    for seed in range(1, SEQUENCES + 1):
        r = random.Random(seed)
        s = temp_session()
        for i in range(STEPS):
            before = s.character
            cmd = r.choice(cmds)
            params = rand_params(r, cmd, before)
            try:
                res = s.dispatch(cmd, **params)
            except Exception as e:  # noqa: BLE001
                found.setdefault("exception %s in %s" % (type(e).__name__, cmd), (seed, i))
                continue
            after = s.character
            kinds = f4.invariants(before, after, _R(len(after.log) > len(before.log)), cmd) if res.ok else []
            if not res.ok and after is not before:
                kinds.append("state changed on a refusal")
            for k, x in all_views(s).items():
                if isinstance(x, tuple) and x and x[0] == "RAISED":
                    kinds.append("view %s raised %s" % (k, x[1]))
                elif bad_numbers(x):
                    kinds.append("view %s has NaN/inf" % k)
            try:
                t1 = cio.dumps(after)
                if t1 != cio.dumps(cio.loads(t1)):
                    kinds.append("save -> load -> save not stable")
            except Exception as e:  # noqa: BLE001
                kinds.append("save raised %s" % type(e).__name__)
            for k in kinds:
                if k not in ALLOWED:
                    found.setdefault("%s (%s)" % (k, cmd), (seed, i))
        drop(s)
    return sorted("%s at seed %d step %d" % (k, a, b) for k, (a, b) in found.items())


S.case("fz-no-crash", "pkg 27 B: 3000 random steps over all commands: no exception, no view raising, no NaN, "
       "invariants hold, save / load stable", [])(_run)

if __name__ == "__main__":
    sys.exit(S.run())
