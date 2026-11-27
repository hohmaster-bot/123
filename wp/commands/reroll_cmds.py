"""Reroll commands (package 38, owner decision 7; wp/model/reroll_view.py). The program never rolls: it counts.

spend_reroll(ref): one reroll of that grant used (refused when none is left).
restore_reroll(ref): the grant back to its max by hand (a "manual" rule, or the GM gives it back).
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.model import reroll_view as rv


def _find(ch, ref):
    f = rv.find(ch, ref)
    if f is None:
        raise CommandError("no reroll %r" % (ref,), "not_found", values=("rerolls", ref))
    _coll, _key, _carrier, reroll = f
    return reroll


@command
def spend_reroll(ch, ref=""):
    r = _find(ch, ref)
    if r.charges_current < 1:
        raise CommandError("no reroll left: %s" % ref, "no_reroll_left", values=(r.name or ref,))
    new = rv.put(ch, ref, replace(r, charges_current=r.charges_current - 1))
    return commit(new, "spend_reroll", "%s %d -> %d" % (ref, r.charges_current, r.charges_current - 1),
                  {"left": r.charges_current - 1})


@command
def restore_reroll(ch, ref=""):
    r = _find(ch, ref)
    new = rv.put(ch, ref, replace(r, charges_current=max(r.charges_current, r.charges_max)))
    return commit(new, "restore_reroll", "%s -> %d" % (ref, r.charges_max), {"left": r.charges_max})
