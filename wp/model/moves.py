"""Movement modes (package 36, owner decision 10): the speed cell shows the land speed; the other modes (fly with a
quality text, swim, climb ...) come from effects with the target move:<mode> (value in FEET, note = the quality).
Per mode the largest value counts (a better flight replaces the first one). Feet only (the program has no metres).
"""
from wp.model import blocks as blk
from wp.model import derived_view as dv

PREFIX = "move:"


def moves(ch):
    """((mode, feet, quality, source), ...) sorted by mode."""
    ctx = dv.context(ch)
    best = {}
    for src, e in blk.active_effects(ch):
        if e.target.startswith(PREFIX) and e.applies(ctx):
            mode, feet = e.target[len(PREFIX):], int(e.resolve(ctx))
            if mode not in best or feet > best[mode][1]:
                best[mode] = (mode, feet, e.note, src)
    return tuple(best[m] for m in sorted(best))
