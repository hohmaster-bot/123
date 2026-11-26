"""Triggers of the character's carriers and their reminders (package 36, owner decision 6; wp/core/triggers.py).

carriers(ch) -> ((source ref, triggers), ...): feats ("feat:<id>", race abilities are feats with source race:<id>),
    items ("item:<id>"), ACTIVE statuses, quirks that are not burned, injuries.
fire(ch, event) -> the character with one new TriggerNote per trigger of that event (never an action by itself).
fire_one(ch, source, tid) -> the same for one manual trigger (the button on the ability card).
notes_view(ch) -> the notes, unhandled first: (nid, source, text, action, target, amount, handled).
EVENT_OF -> the event of a command (end_cycle -> cycle_end ...: data), HP_BELOW_ONE when HP falls below 1.
"""
from dataclasses import replace

from wp.core import triggers as tg
from wp.core.effects import is_effective

EVENT_OF = dict(tg.TABLE["event_of_command"])
HP_BELOW_ONE = "hp_below_one"
NOTE_PREFIX = "tn"


def carriers(ch):
    out = [("feat:" + f.fid, f.triggers) for f in ch.feats]
    out += [("item:" + it.iid, it.triggers) for it in ch.items]
    out += [("status:" + s.sid, s.triggers) for s in ch.statuses if is_effective(s)]
    out += [("quirk:" + q.kid, q.triggers) for q in ch.quirks if not q.burned]
    out += [("injury:" + j.jid, j.triggers) for j in ch.injuries]
    return [(src, tuple(ts)) for src, ts in out if ts]


def _note(ch, src, t, counter):
    return tg.TriggerNote("%s%d" % (NOTE_PREFIX, counter), src, t.tid, t.event, t.text, t.action, t.target, t.amount,
                          dict(t.params))


def _add(ch, pairs):
    counter, notes = ch.trigger_counter, list(ch.trigger_notes)
    for src, t in pairs:
        counter += 1
        notes.append(_note(ch, src, t, counter))
    return replace(ch, trigger_notes=tuple(notes), trigger_counter=counter) if pairs else ch


def fire(ch, event):
    return _add(ch, [(src, t) for src, ts in carriers(ch) for t in ts if t.event == event])


def find_trigger(ch, source, tid):
    for src, ts in carriers(ch):
        if src == source:
            for t in ts:
                if t.tid == tid:
                    return t
    return None


def fire_one(ch, source, tid):
    t = find_trigger(ch, source, tid)
    return None if t is None else _add(ch, [(source, t)])


def note_of(ch, nid):
    return next((n for n in ch.trigger_notes if n.nid == nid), None)


def notes_view(ch):
    rows = [(n.nid, n.source, n.text, n.action, n.target, n.amount, n.handled) for n in ch.trigger_notes]
    return tuple(sorted(rows, key=lambda r: (r[-1], int(r[0][len(NOTE_PREFIX):] or 0))))
