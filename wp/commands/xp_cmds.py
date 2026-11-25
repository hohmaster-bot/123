"""Experience commands (package 26 C, model/experience.py): add_experience(amount, note, at),
edit_experience_entry(xid, amount, note), remove_experience_entry(xid) (the total is recomputed from the log),
and the level history: level_up writes an entry (add_history) and pays exp.level_cost (spend_for_level);
edit_level_history(lid, note, ...) / remove_level_history(lid) are edit-mode commands. All are journaled and undoable.
Package 33 (owner): the total never passes exp.max_banked: add_experience / edit_experience_entry count only up to it
and the result carries the reminder "exp.remind.excess" (not a refusal); the entry keeps what was entered.
The hand-typed goal (set_next_level_at) is retired: the goal is always exp.level_cost.
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.model import experience as xp
from wp.model.experience import LevelRecord, XpEntry

XP_PREFIX = "xp"
LEVEL_PREFIX = "lv"


def _next_id(ch, prefix):
    n = ch.xp_counter + 1
    return replace(ch, xp_counter=n), "%s%d" % (prefix, n)


def add_history(ch, level, hp_roll, note="", at=""):
    ch, lid = _next_id(ch, LEVEL_PREFIX)
    rec = LevelRecord(lid, int(level), xp.total(ch), int(hp_roll), str(note), str(at))
    return replace(ch, level_history=ch.level_history + (rec,))


EXCESS = "exp.remind.excess"


def _excess(entered, got):
    return ((EXCESS, (entered, got)),) if got != entered else ()


def spend_for_level(ch, note="", at=""):
    """The level-up cost as a log entry (kind "level_up"); the caller checks xp.can_level_up first."""
    new, xid = _next_id(ch, XP_PREFIX)
    cost = int(xp.LEVEL_COST)
    return replace(new, xp_log=new.xp_log + (XpEntry(xid, -cost, str(note), str(at), None, xp.KIND_LEVEL_UP),))


@command
def add_experience(ch, amount=0, note="", at=""):
    amount = int(amount)
    got = xp.counted(xp.total(ch), amount)
    new, xid = _next_id(ch, XP_PREFIX)
    entry = XpEntry(xid, got, str(note), str(at), None if got == amount else amount)
    new = replace(new, xp_log=new.xp_log + (entry,))
    return commit(new, "add_experience", "xp %+d" % got, {"id": xid, "total": xp.total(new), "counted": got,
                                                         "reminders": _excess(amount, got)})


def _entry(ch, xid):
    e = next((x for x in ch.xp_log if x.xid == xid), None)
    if e is None:
        raise CommandError("no experience entry %r" % (xid,), "not_found", values=("xp_log", xid))
    return e


@command
def edit_experience_entry(ch, xid="", amount=None, note=None):
    e = _entry(ch, xid)
    reminders = ()
    if amount is None:
        e2 = replace(e, note=e.note if note is None else str(note))
    else:
        amount = int(amount)
        got = xp.counted(xp.total(ch) - int(e.amount), amount)     # the same cap as add_experience
        reminders = _excess(amount, got)
        e2 = replace(e, amount=got, entered=None if got == amount else amount,
                     note=e.note if note is None else str(note))
    new = replace(ch, xp_log=tuple(e2 if x.xid == xid else x for x in ch.xp_log))
    return commit(new, "edit_experience_entry", "xp %s edited" % xid, {"total": xp.total(new),
                                                                     "reminders": reminders})


@command
def remove_experience_entry(ch, xid=""):
    _entry(ch, xid)
    new = replace(ch, xp_log=tuple(x for x in ch.xp_log if x.xid != xid))
    return commit(new, "remove_experience_entry", "xp %s removed" % xid, {"total": xp.total(new)})


HISTORY_FIELDS = ("level", "experience_total", "hp_roll", "note", "at")


def _history(ch, lid):
    r = next((x for x in ch.level_history if x.lid == lid), None)
    if r is None:
        raise CommandError("no level history entry %r" % (lid,), "not_found", values=("level_history", lid))
    return r


@command
def edit_level_history(ch, lid="", **fields):
    unknown = sorted(set(fields) - set(HISTORY_FIELDS))
    if unknown:
        raise CommandError("unknown fields: %s" % ", ".join(unknown), "unknown_field", values=(", ".join(unknown),))
    r = replace(_history(ch, lid), **fields)
    return commit(replace(ch, level_history=tuple(r if x.lid == lid else x for x in ch.level_history)),
                  "edit_level_history", "level history %s edited" % lid)


@command
def remove_level_history(ch, lid=""):
    _history(ch, lid)
    return commit(replace(ch, level_history=tuple(x for x in ch.level_history if x.lid != lid)),
                  "remove_level_history", "level history %s removed" % lid)
