"""Catalog trainings (package 37, owner decision 2; RULES/training.md "Catalog trainings").

An entry of the catalog kind trainings: id, name (name_i18n), module, price per unit in training points (a number or a
formula), repeatable (bool), limit (units, a number or a formula; none = no limit), effects of one unit, unlock: what
makes it available ("feat:<id>" an ability, "race:<id>", "quirk:<id>", "tag:<tag>" an item with that tag, "" = every
character). unlocked(ch, entry) -> (True, None) or (False, (reason key, values)); price / limit evaluate formulas over
the sheet numbers (wp/model/formula_vars). rows(ch, entries) -> the Training tab rows.
"""
from wp.core import formula as fm
from wp.model import derived_view as dv


def taken(ch, tid):
    return next((t for t in ch.trainings if t.tid == tid), None)


def units(ch, tid):
    t = taken(ch, tid)
    return t.units if t is not None else 0


def number(ch, value, default=None):
    """A price / limit: a number, a formula (over the sheet numbers) or None (default)."""
    if value is None or value == "":
        return default
    if isinstance(value, str):
        try:
            return fm.evaluate(value, dv.context(ch))
        except fm.FormulaError:
            return default
    return int(value)


def unlocked(ch, entry):
    u = str(entry.get("unlock") or "")
    if not u:
        return True, None
    kind, _, oid = u.partition(":")
    if kind == "feat":
        ok = any(f.fid == oid for f in ch.feats)
    elif kind == "race":
        ok = ch.race_id == oid
    elif kind == "quirk":
        ok = any(q.kid == oid and not q.burned for q in ch.quirks)
    elif kind == "tag":
        ok = any(oid in tuple(it.tags) for it in ch.items)
    else:
        ok = False
    return (True, None) if ok else (False, ("training.locked." + kind, (oid,)))


def limit(ch, entry):
    if not entry.get("repeatable", True):
        return 1
    return number(ch, entry.get("limit"))


def price(ch, entry):
    return number(ch, entry.get("price"), 0)


def rows(ch, entries):
    """((id, name, module, price, units, limit, unlocked, reason), ...) for the Training tab."""
    out = []
    for e in entries:
        ok, why = unlocked(ch, e)
        out.append((e["id"], e.get("name", e["id"]), e.get("module", ""), price(ch, e), units(ch, e["id"]),
                    limit(ch, e), ok, why))
    return tuple(out)
