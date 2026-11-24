"""Class commands (package 25 B, model/classes.py): set_class(class_id, catalog) takes a snapshot of the catalog entry
(catalog kind "classes"; catalog = a loaded catalog or its merged layers, None = the shipped file); "" removes the
class (everything typed by hand as before). set_bab_override / set_save_override: hand values that win over the class
(value None clears it).
"""
from dataclasses import replace

from wp.commands.base import CommandError, command, commit
from wp.core.frozen import FrozenDict
from wp.model.class_types import GOOD, MEDIUM, POOR, SAVES, ClassInfo

GROWTHS = (GOOD, MEDIUM, POOR)
PROGRESSIONS = (GOOD, POOR)


def _entries(catalog):
    if catalog is None:
        from wp.catalog import store as cs
        catalog = cs.load_shipped("classes")
    if isinstance(catalog, dict):
        return dict(catalog)
    if hasattr(catalog, "entries"):
        return {e["id"]: e for e in catalog.entries}
    from wp.catalog import store as cs           # layers (shipped, user)
    return {e["id"]: e for e, _ in cs.merged(catalog)}


def class_info(entry):
    saves = {k: entry.get("saves", {}).get(k, POOR) for k in SAVES}
    if entry.get("bab_growth", MEDIUM) not in GROWTHS or any(v not in PROGRESSIONS for v in saves.values()):
        raise CommandError("bad class progression in %r" % entry.get("id"), "bad_class_progression",
                           values=(entry.get("id", ""),))
    return ClassInfo(cid=entry["id"], name=entry.get("name", ""), hit_die=int(entry.get("hit_die", 0)),
                     bab_growth=entry.get("bab_growth", MEDIUM), saves=saves,
                     class_skills=tuple(entry.get("class_skills", ())), spellbook=bool(entry.get("spellbook", False)),
                     divine=bool(entry.get("divine", False)),
                     spell_failure_mode=entry.get("spell_failure_mode", ""),
                     own_professionalism=bool(entry.get("own_professionalism", False)), notes=entry.get("notes", ""))


@command
def set_class(ch, class_id="", catalog=None):
    if not class_id:
        return commit(replace(ch, class_id="", class_info=None), "set_class", "no class")
    entries = _entries(catalog)
    if class_id not in entries:
        raise CommandError("no class %r" % (class_id,), "not_found", values=("classes", class_id))
    ci = class_info(entries[class_id])
    return commit(replace(ch, class_id=class_id, class_info=ci), "set_class", "class %s" % class_id)


@command
def set_bab_override(ch, value=None):
    return commit(replace(ch, bab_override=None if value is None else int(value)), "set_bab_override",
                  "bab override %s" % value)


@command
def set_save_override(ch, save="", value=None):
    if save not in SAVES:
        raise CommandError("save must be fort, ref or will", "unknown_save", values=(save,))
    over = {k: v for k, v in ch.save_override.items() if k != save}
    if value is not None:
        over[save] = int(value)
    return commit(replace(ch, save_override=FrozenDict(over)), "set_save_override", "save %s override %s" % (save, value))
