"""Manual source rows of sheet numbers (package 34, model/sources.py): source_add(number, name, value),
source_edit(sid, name, value), source_toggle(sid, on), source_remove(sid). Journaled and undoable like every command;
the Session lets them run only in the editor mode (EDITOR_ONLY). A row of a number without an effect target (temp HP)
is refused: that number's sources are read-only. The derived total is never written (the owner corrects a derived
row with a manual row)."""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.model import ids
from wp.model import source_row as sr
from wp.model import sources
from wp.model.source_row import SourceRow

EDITOR_ONLY = ("source_add", "source_edit", "source_toggle", "source_remove")


def _row(ch, sid):
    r = next((x for x in ch.source_rows if x.sid == sid), None)
    if r is None:
        raise CommandError("no source row %r" % (sid,), "not_found", values=("source_rows", sid))
    return r


def _put(ch, row):
    return replace(ch, source_rows=tuple(row if x.sid == row.sid else x for x in ch.source_rows))


@command
def source_add(ch, number="", name="", value=0):
    if not sources.known(ch, number):
        raise CommandError("no sheet number %r" % (number,), "unknown_number", values=(number,))
    if not sr.target_of(number)[0]:
        raise CommandError("the sources of %s are read-only" % number, "sources_read_only", values=(number,))
    if not str(name).strip():
        raise CommandError("a source row needs a name", "source_name_needed")
    sid = ids.make_id(name, (x.sid for x in ch.source_rows))
    row = SourceRow(sid, number, str(name).strip(), int(value), True)
    return commit(replace(ch, source_rows=ch.source_rows + (row,)), "source_add",
                  "%s: %s %+d" % (number, row.name, row.value), {"id": sid})


@command
def source_edit(ch, sid="", name=None, value=None):
    r = _row(ch, sid)
    if name is not None and not str(name).strip():
        raise CommandError("a source row needs a name", "source_name_needed")
    r2 = replace(r, name=r.name if name is None else str(name).strip(), value=r.value if value is None else int(value))
    return commit(_put(ch, r2), "source_edit", "%s: %s %+d" % (r2.number, r2.name, r2.value))


@command
def source_toggle(ch, sid="", on=True):
    r = _row(ch, sid)
    return commit(_put(ch, replace(r, on=bool(on))), "source_toggle", "%s: %s %s" % (r.number, r.name,
                                                                                    "on" if on else "off"))


@command
def source_remove(ch, sid=""):
    r = _row(ch, sid)
    return commit(replace(ch, source_rows=tuple(x for x in ch.source_rows if x.sid != sid)), "source_remove",
                  "%s: %s removed" % (r.number, r.name))
