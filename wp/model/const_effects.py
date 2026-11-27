"""Effects on rule constants (package 37, owner decision 1): every numeric constant of wp/rules_data/constants.json is
an effect target const:<id>. An effect adds its value (several add up) or, with the note "replace", replaces it (the
last replacing source wins; the adds come on top). Values are numbers or formulas over the level (no other sheet
number: a constant is read while those are computed). A condition or a situational text makes the effect not count
here (conservative: a constant has no context). Unknown ids are ignored (the Sources view warns).
changes(ch) -> {id: (mode, number)}; installed as rules.EFFECTS on import (wp/model/__init__ or the first use).
"""
from wp.core import formula as fm
from wp.model.cache import cached
from wp.rules_data import rules as rd

REPLACE = "replace"
_BUSY = []


def _value(e, level):
    if isinstance(e.value, str):
        try:
            return fm.evaluate(e.value, {"level": level})
        except fm.FormulaError:
            return 0
    return e.value if rd.numeric(e.value) else 0


def entries(ch):
    """((source, id, mode, number), ...) of every const:<id> effect of an active source."""
    if id(ch) in _BUSY:
        return ()
    _BUSY.append(id(ch))
    try:
        from wp.model import blocks as blk
        out = []
        for src, e in blk.active_effects(ch):
            if e.target.startswith(rd.PREFIX) and not e.condition and not e.situational:
                out.append((src, e.target[len(rd.PREFIX):], REPLACE if e.note == REPLACE else "add",
                            _value(e, ch.level)))
        return tuple(out)
    finally:
        _BUSY.remove(id(ch))


@cached
def changes(ch):
    adds, repl = {}, {}
    for _src, cid, mode, n in entries(ch):
        if cid not in rd.DEFAULTS:
            continue
        if mode == REPLACE:
            repl[cid] = n
        else:
            adds[cid] = adds.get(cid, 0) + n
    out = {cid: ("replace", n + adds.get(cid, 0)) for cid, n in repl.items()}
    out.update({cid: ("add", n) for cid, n in adds.items() if cid not in repl})
    return out


def install():
    rd.EFFECTS = changes


install()
