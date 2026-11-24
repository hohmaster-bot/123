"""Review 5 / area 2: do the declared topics of a command cover every panel whose view really changed?
For every command of the registry: random parameters on a rich character (many tries), on each success compare
all views before / after. Prints commands whose changed panels are NOT in their topics (stale UI panels).
Run: python Wp_claude/tests/review5/topics_probe.py [tries_per_command]"""
import random
import sys

from common import REGISTRY, all_views, drop, rand_params, temp_session, sess

TRIES = int(sys.argv[1]) if len(sys.argv) > 1 else 40


def main():
    r = random.Random(5)
    missing = {}
    invisible = {}
    tried = ok_cmds = 0
    for cmd in sorted(REGISTRY):
        topics = sess.topics_of(cmd)
        s = temp_session()
        s.app = s.app  # noqa
        ok_any = False
        for i in range(TRIES):
            before_views = all_views(s)
            before_ch = s.character
            params = rand_params(r, cmd, s.character)
            try:
                res = s.dispatch(cmd, **params)
            except Exception:  # noqa: BLE001  (other exceptions are the fuzzer's job)
                continue
            tried += 1
            if not res.ok:
                continue
            ok_any = True
            after = all_views(s)
            changed = {k for k in after if after[k] != before_views[k]}
            if before_ch is not s.character and before_ch != s.character:
                invisible.setdefault(cmd, []).append(changed <= {"log"})
            extra = set() if "all" in topics else changed - set(topics)
            for p in extra:
                missing.setdefault(cmd, {}).setdefault(p, params)
            # step a few random warm-up commands so the next try sees another state
            try:
                s.dispatch("tick")
            except Exception:  # noqa: BLE001
                s.character = before_ch
        ok_cmds += ok_any
        drop(s)
    print("commands with own topic list: %d, succeeded at least once: %d, tries: %d" % (
        sum(1 for c in REGISTRY if "all" not in sess.topics_of(c)), ok_cmds, tried))
    for cmd in sorted(missing):
        print("UNDER-DECLARED %-26s declared=%s changed-but-missing=%s example=%r" % (
            cmd, ",".join(sess.topics_of(cmd)), ",".join(sorted(missing[cmd])),
            list(missing[cmd].values())[0]))
    print("under-declared commands: %d" % len(missing))
    blind = sorted(c for c, v in invisible.items() if v and all(v))
    print("commands that changed the character but NO panel view (only the log) shows it: %d %s" % (len(blind), blind))


if __name__ == "__main__":
    main()
