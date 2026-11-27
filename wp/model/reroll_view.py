"""The rerolls of the character (package 38, owner decision 7; wp/core/rerolls.py).

The carriers: feats (race abilities are feats), items (anywhere on the character), active statuses, quirks that are
not burned, injuries, trainings. A reroll is addressed by ref "<kind>:<carrier id>:<reroll id>".
rows(ch) -> ((ref, source ref, source name, reroll name, left, max, recharge), ...) in carrier order.
find(ch, ref) -> (collection, key, carrier, reroll) or None; put(ch, ref, reroll) -> the character with it.
refill(ch, rules) -> every reroll whose recharge rule is in rules back to max (rests, combat start / end).
"""
from dataclasses import replace

from wp.core import rerolls as rr
from wp.core.effects import is_effective

CARRIERS = (("feat", "feats", "fid"), ("item", "items", "iid"), ("status", "statuses", "sid"),
            ("quirk", "quirks", "kid"), ("injury", "injuries", "jid"), ("training", "trainings", "tid"))


def _name(x):
    return getattr(x, "title", "") or getattr(x, "name", "") or ""


def _shown(kind, x):
    if kind == "status":
        return is_effective(x)
    if kind == "quirk":
        return not x.burned
    return True


def _each(ch, shown_only=True):
    for kind, coll, key in CARRIERS:
        for x in getattr(ch, coll, ()):
            if getattr(x, "rerolls", ()) and (not shown_only or _shown(kind, x)):
                yield kind, coll, key, x


def rows(ch):
    out = []
    for kind, _coll, key, x in _each(ch):
        oid = getattr(x, key)
        for r in x.rerolls:
            out.append(("%s:%s:%s" % (kind, oid, r.rrid), "%s:%s" % (kind, oid), _name(x), r.name or _name(x),
                        int(r.charges_current), int(r.charges_max), r.recharge))
    return tuple(out)


def find(ch, ref):
    kind, _, rest = str(ref).partition(":")
    oid, _, rrid = rest.rpartition(":")
    for k, coll, key, x in _each(ch, shown_only=False):
        if k == kind and getattr(x, key) == oid:
            r = next((r for r in x.rerolls if r.rrid == rrid), None)
            return None if r is None else (coll, key, x, r)
    return None


def put(ch, ref, reroll):
    coll, key, x, _old = find(ch, ref)
    new = replace(x, rerolls=tuple(reroll if r.rrid == reroll.rrid else r for r in x.rerolls))
    return replace(ch, **{coll: tuple(new if getattr(y, key) == getattr(x, key) else y for y in getattr(ch, coll))})


def refill(ch, rules):
    for _kind, coll, key, x in list(_each(ch, shown_only=False)):
        new = replace(x, rerolls=rr.refill(x.rerolls, rules))
        if new != x:
            ch = replace(ch, **{coll: tuple(new if getattr(y, key) == getattr(x, key) else y
                                            for y in getattr(ch, coll))})
    return ch
