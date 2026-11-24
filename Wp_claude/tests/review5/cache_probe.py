"""Review 5 / area 3: the read cache never changes a result.
For random command sequences (all registry commands, plus undo / redo, rule overrides, class changes) the views
read with the cache (twice: cold and warm) must EQUAL the views read with cache.disabled() at every step.
Also: views read OUTSIDE rd.using after a rule override, then inside (scope part of the key).
Run: python Wp_claude/tests/review5/cache_probe.py [seeds] [steps]"""
import random
import sys

from common import CONST_IDS, REGISTRY, all_views, cache, drop, rand_params, temp_session, rd
from wp.model import derived_view as dv

SEEDS = int(sys.argv[1]) if len(sys.argv) > 1 else 6
STEPS = int(sys.argv[2]) if len(sys.argv) > 2 else 150
CMDS = sorted(REGISTRY)


def main():
    diffs = []
    steps = 0
    for seed in range(SEEDS):
        r = random.Random(100 + seed)
        s = temp_session()
        for i in range(STEPS):
            x = r.random()
            if x < 0.05:
                s.undo()
            elif x < 0.08:
                s.redo()
            elif x < 0.12:
                s.dispatch("set_rule_setting", key=r.choice(CONST_IDS), value=r.choice((0, 1, 2, 5)))
            else:
                cmd = r.choice(CMDS)
                try:
                    s.dispatch(cmd, **rand_params(r, cmd, s.character))
                except Exception:  # noqa: BLE001
                    continue
            steps += 1
            cold = all_views(s)
            warm = all_views(s)
            with cache.disabled():
                plain = all_views(s)
            for k in plain:
                if cold[k] != plain[k] or warm[k] != plain[k]:
                    diffs.append((seed, i, k))
        drop(s)
    print("cache: %d steps x 18 views, differences cached vs uncached: %d %s" % (steps, len(diffs), diffs[:8]))
    # scope: a value read outside rd.using must not be reused inside it (and back)
    s = temp_session()
    s.dispatch("set_rule_setting", key="pain.per_hp_lost" if "pain.per_hp_lost" in CONST_IDS else CONST_IDS[0],
               value=1)
    ch = s.character
    out1 = dv.hp_max(ch)
    with rd.using(ch):
        in1 = dv.hp_max(ch)
    with cache.disabled():
        out2 = dv.hp_max(ch)
        with rd.using(ch):
            in2 = dv.hp_max(ch)
    print("scope: hp_max outside %s / %s, inside %s / %s (cached / uncached)" % (out1, out2, in1, in2))
    drop(s)


if __name__ == "__main__":
    main()
