"""Standing reminders from effects (package 38, owner decision 4): an effect with the target reminder:<key> makes the
reminder "reminder.<key>" (a text key of wp/i18n) stand while the sum of the active reminder:<key> effects is above
0. A condition makes an effect count only while it holds (status_tag:bleeding: while a bleeding status is active);
a source that takes the reminder away adds -1 (the Mordon buy-out). Nothing is computed from it: it is a text.
reminders(ch) -> (("reminder.<key>", ()), ...) in key order.
"""
from wp.model import blocks as blk
from wp.model import derived_view as dv

PREFIX = "reminder:"
TEXT = "reminder."


def totals(ch):
    ctx = dv.context(ch)
    out = {}
    for _src, e in blk.active_effects(ch):
        if e.target.startswith(PREFIX):
            key = e.target[len(PREFIX):]
            out[key] = out.get(key, 0) + int(e.resolve(ctx))
    return out


def reminders(ch):
    return tuple((TEXT + key, ()) for key, n in sorted(totals(ch).items()) if n > 0)
