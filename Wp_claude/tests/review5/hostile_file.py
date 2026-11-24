"""Review 5 / area 5: hostile character FILES (a valid save edited by hand) through cio.loads.
Run: python Wp_claude/tests/review5/hostile_file.py"""
import json

from common import rich
from wp.storage import character_io as cio

BASE = json.loads(cio.dumps(rich()))


def t(title, mut=None, raw=None):
    d = json.loads(json.dumps(BASE))
    c = d["character"]
    if mut:
        mut(c)
    txt = json.dumps(d, allow_nan=True)
    if raw:
        txt = raw(txt)
    try:
        ch = cio.loads(txt)
        from common import temp_session, all_views, drop
        s = temp_session(ch)
        v = all_views(s)
        bad = sorted(k for k, x in v.items() if isinstance(x, tuple) and x and x[0] == "RAISED")
        drop(s)
        print("%-34s -> LOADED level=%r hp=%r items=%d; views raising: %d %s" % (
            title, ch.level, ch.hp_current, len(ch.items), len(bad), bad[:3]))
    except cio.StorageError as e:
        print("%-34s -> StorageError %s" % (title, str(e)[:80]))
    except Exception as e:  # noqa: BLE001
        print("%-34s -> RAISED %s %s" % (title, type(e).__name__, str(e)[:80]))


t("valid")
t("extra field (dropped, D1)", lambda c: c.update(zzz=1))
t("level huge int", lambda c: c.update(level=10 ** 30))
t("hp_current NaN", lambda c: c.update(hp_current=float("nan")))
t("hp_current inf", lambda c: c.update(hp_current=float("inf")))
t("level string", lambda c: c.update(level="5"))
t("level bool", lambda c: c.update(level=True))
t("level float", lambda c: c.update(level=5.5))
t("level negative", lambda c: c.update(level=-3))
t("hp_current null", lambda c: c.update(hp_current=None))
t("duplicate key", raw=lambda s: s.replace('"level":', '"level": 99, "level":', 1))
t("items wrong type", lambda c: c.update(items="x"))
t("dup item ids", lambda c: c.update(items=c["items"] + c["items"][:1]))
t("unknown nested field", lambda c: c["items"][0].update(qqq=1))
t("item hp string", lambda c: c["items"][0].update(hp="ten"))
t("abilities wrong type", lambda c: c.update(abilities=3))
t("deep nesting 5000", raw=lambda s: s[:-1] + ', "zz": ' + "[" * 5000 + "]" * 5000 + "}")
t("log params NaN", lambda c: c.update(log=[{"seq": 1, "command": "x", "params": {"a": float("nan")}}]))
