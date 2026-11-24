"""Narrative notebook and template commands (RULES/narrative.md, package 16 F, G6).

Play commands with the notebook rules: add_note(kind, name, **fields) (a lens starts at 1 of max, clamped 0..max;
a drive level 0..5; court level / tier >= 0), change_lens(lid, delta) (clamped 0..max: 0 red, max green),
set_drive_level(did, level), burn_quirk(kid, burned) (reversible). Changing or deleting any field without limits:
edit_entry / remove_entry (edit mode, edit_cmds).
Templates: add_template(template) copies its feats / pools / statuses (source "template:<tid>"); remove_template(tid)
removes the template and every record with that source.
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.model import formulas as fx
from wp.model import ids
from wp.model import notebook as nb
from wp.model import template as tpl
from wp.core import formula as fm


def _kind(kind):
    if kind not in nb.KINDS:
        raise CommandError("note kind must be one of %s" % ", ".join(sorted(nb.KINDS)), "unknown_note_kind",
                           values=(kind,))
    return nb.KINDS[kind]


def _check(rec):
    if isinstance(rec, nb.Drive) and not 0 <= rec.level <= nb.DRIVE_MAX:
        raise CommandError("a drive level is 0..%d" % nb.DRIVE_MAX, "drive_level_range", values=(rec.level,))
    if isinstance(rec, nb.Court) and (rec.level < 0 or rec.tier < 0):
        raise CommandError("court level and tier cannot be negative", "court_negative", values=(rec.level, rec.tier))
    if isinstance(rec, nb.Lens) and rec.max < 1:
        raise CommandError("a lens needs a max of 1 or more", "lens_max_range", values=(rec.max,))
    if isinstance(rec, nb.Quirk):
        try:
            fx.validate_effects(rec.effects)
        except fm.FormulaError as e:
            raise CommandError("bad effect formula: %s" % e, "bad_effect_formula", values=(str(e),))
    return rec


@command
def add_note(ch, kind="", name="", **fields):
    coll, cls, key = _kind(kind)
    if not name:
        raise CommandError("a note needs a name", "note_needs_name")
    rec = cls(**{key: ids.make_id(name, (getattr(r, key) for r in getattr(ch, coll))), "name": name}, **fields)
    if isinstance(rec, nb.Lens) and "value" not in fields:
        rec = replace(rec, value=min(nb.LENS_START, rec.max))
    if isinstance(rec, nb.Lens):
        rec = replace(rec, value=nb.clamp_lens(rec.value, max(1, rec.max)))
    _check(rec)
    return commit(replace(ch, **{coll: getattr(ch, coll) + (rec,)}), "add_note", "%s %s" % (kind, getattr(rec, key)),
                  {"id": getattr(rec, key)})


def _get(ch, coll, key, oid):
    rec = next((r for r in getattr(ch, coll) if getattr(r, key) == oid), None)
    if rec is None:
        raise CommandError("no %s %r" % (coll, oid), "not_found", values=(coll, oid))
    return rec


def _put(ch, coll, key, rec):
    oid = getattr(rec, key)
    return replace(ch, **{coll: tuple(rec if getattr(r, key) == oid else r for r in getattr(ch, coll))})


@command
def change_lens(ch, lid="", delta=0):
    """Only the player moves a lens, by hand; the counter is clamped to 0..max (narrative.md)."""
    lens = _get(ch, "lenses", "lid", lid)
    new = replace(lens, value=nb.clamp_lens(lens.value + int(delta), lens.max))
    return commit(_put(ch, "lenses", "lid", new), "change_lens", "lens %s %d/%d" % (lid, new.value, new.max),
                  {"value": new.value, "state": nb.lens_state(new)})


@command
def set_drive_level(ch, did="", level=0):
    d = _check(replace(_get(ch, "drives", "did", did), level=int(level)))
    return commit(_put(ch, "drives", "did", d), "set_drive_level", "drive %s level %d" % (did, d.level))


def drive_view(ch, d):
    """A drive for the panel (package 25 C): the level, the note of every level, the principle and the reminder
    principle_missing (level >= narrative.principle_min_level and no principle; never a block)."""
    from wp.rules_data import rules as rd
    need = d.level >= int(rd.const("narrative.principle_min_level", ch))
    return {"did": d.did, "name": d.name, "level": d.level, "level_notes": dict(d.level_notes),
            "note": d.level_notes.get(str(d.level), ""), "principle": d.principle,
            "principle_missing": need and not d.principle.strip()}


def _level_key(level):
    level = int(level)
    if not 0 <= level <= nb.DRIVE_MAX:
        raise CommandError("a drive level is 0..%d" % nb.DRIVE_MAX, "drive_level_range", values=(level,))
    return str(level)


@command
def add_drive(ch, name="", level=0, principle="", level_notes=None, text=""):
    if not name:
        raise CommandError("a note needs a name", "note_needs_name")
    notes = {_level_key(k): str(v) for k, v in dict(level_notes or {}).items()}
    d = _check(nb.Drive(ids.make_id(name, (x.did for x in ch.drives)), name, int(level), text, notes, principle))
    return commit(replace(ch, drives=ch.drives + (d,)), "add_drive", "drive %s" % d.did, {"id": d.did})


DRIVE_FIELDS = ("name", "level", "text", "level_notes", "principle")


@command
def edit_drive(ch, did="", **fields):
    unknown = sorted(set(fields) - set(DRIVE_FIELDS))
    if unknown:
        raise CommandError("unknown drive fields: %s" % ", ".join(unknown), "unknown_field", values=(", ".join(unknown),))
    if "level_notes" in fields:
        fields["level_notes"] = {_level_key(k): str(v) for k, v in dict(fields["level_notes"]).items()}
    if "level" in fields:
        fields["level"] = int(fields["level"])
    d = _check(replace(_get(ch, "drives", "did", did), **fields))
    return commit(_put(ch, "drives", "did", d), "edit_drive", "drive %s edited" % did)


@command
def remove_drive(ch, did=""):
    _get(ch, "drives", "did", did)
    return commit(replace(ch, drives=tuple(x for x in ch.drives if x.did != did)), "remove_drive", "drive %s removed" % did)


@command
def set_drive_level_note(ch, did="", level=0, text=""):
    d = _get(ch, "drives", "did", did)
    notes = dict(d.level_notes)
    if text:
        notes[_level_key(level)] = str(text)
    else:
        notes.pop(_level_key(level), None)
    return commit(_put(ch, "drives", "did", replace(d, level_notes=notes)), "set_drive_level_note",
                  "drive %s level %s note" % (did, level))


@command
def set_drive_principle(ch, did="", text=""):
    d = _get(ch, "drives", "did", did)
    return commit(_put(ch, "drives", "did", replace(d, principle=str(text))), "set_drive_principle",
                  "drive %s principle" % did)


@command
def burn_quirk(ch, kid="", burned=True):
    """Burn = grey, status destroyed, its effects stop; reversible by hand (burned=False). Delete: remove_entry."""
    q = replace(_get(ch, "quirks", "kid", kid), burned=bool(burned))
    return commit(_put(ch, "quirks", "kid", q), "burn_quirk", "quirk %s %s" % (kid, "burned" if burned else "restored"))


@command
def add_template(ch, template=None):
    if template is None or not template.name:
        raise CommandError("no template given", "no_template")
    tid = ids.make_id(template.name, (t.tid for t in ch.templates)) if not template.tid else template.tid
    if any(t.tid == tid for t in ch.templates):
        raise CommandError("template %r is already on the sheet" % (tid,), "id_taken", values=("templates", tid))
    try:
        fx.validate_effects(template.effects)
    except fm.FormulaError as e:
        raise CommandError("bad effect formula: %s" % e, "bad_effect_formula", values=(str(e),))
    src = tpl.source_of(tid)
    have = {f.fid for f in ch.feats}
    clash = [f.fid for f in template.feats if f.fid in have]
    if clash:
        raise CommandError("the sheet already has the feats %s" % ", ".join(clash), "feat_already_sheet",
                           values=(", ".join(clash),))
    feats = tuple(replace(f, source=src) for f in template.feats)
    pools, taken = [], [p.pid for p in ch.pools]
    for p in template.pools:
        pid = ids.make_id(p.name or "pool", taken)
        taken.append(pid)
        pools.append(replace(p, pid=pid, source=src))
    statuses, taken = [], [s.sid for s in ch.statuses]
    for s in template.statuses:
        sid = ids.make_id(s.name, taken)
        taken.append(sid)
        statuses.append(replace(s, sid=sid, source=src))
    stored = replace(template, tid=tid, feats=(), pools=(), statuses=())
    new = replace(ch, templates=ch.templates + (stored,), feats=ch.feats + feats, pools=ch.pools + tuple(pools),
                  statuses=ch.statuses + tuple(statuses))
    return commit(new, "add_template", "template %s" % tid, {"id": tid})


@command
def remove_template(ch, tid=""):
    """Removes the template and ALL its contributions: its effects and hit dice, and every feat / pool / status
    with source "template:<tid>" (package 16 G6)."""
    _get(ch, "templates", "tid", tid)
    src = tpl.source_of(tid)
    feats = tuple(f for f in ch.feats if f.source != src)
    new = replace(ch, templates=tuple(t for t in ch.templates if t.tid != tid), feats=feats,
                  pools=tuple(p for p in ch.pools if p.source != src),
                  statuses=tuple(s for s in ch.statuses if s.source != src))
    if ch.active_stance and ch.active_stance not in {f.fid for f in feats}:
        new = replace(new, active_stance=None)
    return commit(new, "remove_template", "template %s removed" % tid)


def notebook_view(ch):
    """Lenses with their end state (red / green), courts with their label, quirks with their state."""
    return {"lenses": tuple((x.lid, x.value, x.max, nb.lens_state(x)) for x in ch.lenses),
            "courts": tuple((x.cid, x.label()) for x in ch.courts),
            "quirks": tuple((x.kid, nb.quirk_state(x)) for x in ch.quirks),
            "drives": tuple(drive_view(ch, x) for x in ch.drives),
            "quests": tuple((x.qid, x.done) for x in ch.quests), "stories": tuple(x.stid for x in ch.stories)}
