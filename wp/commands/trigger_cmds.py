"""Trigger, condition and link commands (package 36, owner decisions 6, 7, 14).

fire_trigger(source, tid): a manual trigger (the button on the ability card) -> its reminder note.
run_trigger_action(nid): the player presses the action button of a note: the action runs (closed vocabulary,
    wp/core/triggers.py) and the note is marked handled. set_trigger_handled(nid, handled): the handled mark by hand.
set_manual_condition(text, on): ticks / unticks a manual effect condition ("manual:<text>").
set_held_kept(collection, oid, kept): the manual kept / lost checkbox of a text holder (held_by "text:...").
The events fire by themselves in dispatch (commands/base.py: end_cycle -> cycle_end, ..., HP below 1).
"""
from dataclasses import replace

from wp.commands.base import REGISTRY, CommandError, command, commit
from wp.core import pain as pn
from wp.core import triggers as tg
from wp.model import trigger_view as tv

HOLDER_COLLECTIONS = {"feats": "fid", "statuses": "sid", "quirks": "kid", "trainings": "tid"}


@command
def fire_trigger(ch, source="", tid=""):
    new = tv.fire_one(ch, source, tid)
    if new is None:
        raise CommandError("no trigger %s of %s" % (tid, source), "not_found", values=("triggers", tid))
    return commit(new, "fire_trigger", "%s %s" % (source, tid), {"id": new.trigger_notes[-1].nid})


def _note(ch, nid):
    n = tv.note_of(ch, nid)
    if n is None:
        raise CommandError("no trigger note %r" % (nid,), "not_found", values=("trigger_notes", nid))
    return n


def _mark(ch, nid, handled):
    return replace(ch, trigger_notes=tuple(replace(n, handled=bool(handled)) if n.nid == nid else n
                                           for n in ch.trigger_notes))


def _run(ch, n):
    a = n.action
    if a == "add_status":
        return REGISTRY["activate_status"](ch, sid=n.target).state
    if a == "change_resource":
        return REGISTRY["adjust_value"](ch, resource=n.target, delta=int(n.amount)).state
    if a == "add_reminder":
        return tv._add(ch, [(n.source, tg.Trigger(n.tid + "_reminder", n.event, n.target or n.text))])
    if a == "add_pain":
        return replace(ch, pain=pn.add(ch.pain, int(n.amount), n.source))
    if a == "reduce_injury_points":      # injury points = OT (RULES/injuries.md), never below 0
        return replace(ch, trauma=max(0, ch.trauma - int(n.amount)))
    if a == "run_command":
        if n.target not in tg.RUN_COMMANDS:
            raise CommandError("%s is not allowed in a trigger" % n.target, "command_not_allowed", values=(n.target,))
        return REGISTRY[n.target](ch, **dict(n.params)).state
    raise CommandError("the note %s has no action" % n.nid, "no_action", values=(n.nid,))


@command
def run_trigger_action(ch, nid=""):
    n = _note(ch, nid)
    if n.handled:
        raise CommandError("the note %s is already handled" % nid, "already_handled", values=(nid,))
    new = _mark(_run(ch, n), nid, True)
    return commit(new, "run_trigger_action", "%s %s" % (nid, n.action), {"action": n.action})


@command
def set_trigger_handled(ch, nid="", handled=True):
    _note(ch, nid)
    return commit(_mark(ch, nid, handled), "set_trigger_handled", "%s %s" % (nid, bool(handled)))


@command
def set_manual_condition(ch, text="", on=True):
    text = str(text).strip()
    if not text:
        raise CommandError("a manual condition needs its text", "condition_text_needed")
    have = tuple(c for c in ch.manual_conditions if c != text)
    return commit(replace(ch, manual_conditions=have + ((text,) if on else ())), "set_manual_condition",
                  "%s %s" % (text, bool(on)))


@command
def set_held_kept(ch, collection="", oid="", kept=True):
    key = HOLDER_COLLECTIONS.get(collection)
    if key is None:
        raise CommandError("no holder links in %s" % collection, "unknown_collection", values=(collection,))
    rows = getattr(ch, collection)
    if not any(getattr(r, key) == oid for r in rows):
        raise CommandError("no %s %r" % (collection, oid), "not_found", values=(collection, oid))
    new = tuple(replace(r, held_kept=bool(kept)) if getattr(r, key) == oid else r for r in rows)
    return commit(replace(ch, **{collection: new}), "set_held_kept", "%s %s %s" % (collection, oid, bool(kept)))


@command
def set_held_by(ch, collection="", oid="", holder=""):
    """Link a dependent to its holder (package 37, owner decision 5): holder = feat:<id> / item:<id> / quirk:<id> /
    status:<id> / training:<id> / text:<what>; "" removes the link. The holder must exist (a text holder always
    does) and cannot be the dependent itself."""
    from wp.model import links
    key = HOLDER_COLLECTIONS.get(collection)
    if key is None:
        raise CommandError("no holder links in %s" % collection, "unknown_collection", values=(collection,))
    rows = getattr(ch, collection)
    if not any(getattr(r, key) == oid for r in rows):
        raise CommandError("no %s %r" % (collection, oid), "not_found", values=(collection, oid))
    holder = str(holder or "")
    if holder and not holder.startswith(links.PREFIXES):
        raise CommandError("a holder is feat: / item: / quirk: / status: / training: / text:", "bad_holder",
                           values=(holder,))
    if holder and not holder.startswith(links.TEXT) and not links.holder_present(ch, holder):
        raise CommandError("no holder %s" % holder, "not_found", values=("holders", holder))
    if holder == links.REF[collection] + oid:
        raise CommandError("an entry cannot hold itself", "bad_holder", values=(holder,))
    new = tuple(replace(r, held_by=holder, held_kept=True) if getattr(r, key) == oid else r for r in rows)
    return commit(replace(ch, **{collection: new}), "set_held_by", "%s %s <- %s" % (collection, oid, holder or "-"))
