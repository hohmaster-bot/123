"""Package 27 D (review 5 F2, F16): the declared topics of every command cover every panel view that really changed;
every change of the character is visible in some panel view other than the log.
Same method as tests/review5/topics_probe.py (kept): random parameters (tests/review5/common.py) on a rich character,
25 tries per command, seeds 5 and 6; on each success all views are compared before / after.
Run: python Wp_claude/tests/app/test_topics.py"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "review5"))
from _runner import Suite  # noqa: E402

from common import REGISTRY, all_views, drop, rand_params, temp_session, sess  # noqa: E402

S = Suite("test_topics")
TRIES = 25
_RUNS = {}


def probe(seed):
    if seed in _RUNS:
        return _RUNS[seed]
    r = random.Random(seed)
    missing, blind = {}, {}
    for cmd in sorted(REGISTRY):
        if cmd.startswith("p27_test_"):
            continue
        topics = sess.topics_of(cmd)
        s = temp_session()
        for _ in range(TRIES):
            before_views, before_ch = all_views(s), s.character
            res = s.dispatch(cmd, **rand_params(r, cmd, s.character))
            if not res.ok:
                continue
            after = all_views(s)
            changed = {k for k in after if after[k] != before_views[k]}
            if before_ch != s.character:
                blind.setdefault(cmd, []).append(changed <= {"log"})
            if "all" not in topics:
                for p in changed - set(topics):
                    missing.setdefault(cmd, set()).add(p)
            s.dispatch("tick")
        drop(s)
    _RUNS[seed] = ({c: sorted(p) for c, p in missing.items()}, sorted(c for c, v in blind.items() if v and all(v)))
    return _RUNS[seed]


for _seed in (5, 6):
    S.case("t-cover-%d" % _seed, "F2: every changed panel is in the command's topics (seed %d)" % _seed, {})(
        lambda sd=_seed: probe(sd)[0])
    S.case("t-visible-%d" % _seed, "F16: no command changes the character with only the log showing it (seed %d)" % _seed,
           [])(lambda sd=_seed: probe(sd)[1])

def _damage():
    """A deterministic case (package 30): take_damage 12 on the rich character (pain changes the rolls)."""
    s = temp_session()
    before = all_views(s)
    s.dispatch("take_damage", amount=12)
    after = all_views(s)
    changed = {k for k in after if after[k] != before[k]}
    drop(s)
    return sorted(changed - set(sess.topics_of("take_damage")))


S.case("t-damage", "F2: take_damage 12: every changed panel is in its topics", [])(_damage)

if __name__ == "__main__":
    sys.exit(S.run())
