"""Package 18: catalog files (one JSON file per kind), two layers (shipped / user), catalog commands, ids, validation,
atomic save, entry codes, the skill catalog (medicine Int). Expected values by hand from the package text and RULES.
Run: python Wp_claude/tests/storage/test_catalogs.py"""
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import ROOT, Suite  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "Wp_claude", "tools"))
import build_catalogs  # noqa: E402

from wp.catalog import armor_catalog as arm  # noqa: E402
from wp.catalog import catalog_view as cvw  # noqa: E402
from wp.catalog import convert  # noqa: E402
from wp.catalog import schema  # noqa: E402
from wp.catalog import skills_catalog as sc  # noqa: E402
from wp.catalog import store as cs  # noqa: E402
from wp.catalog.catalog_cmds import catalog_dispatch as do  # noqa: E402
from wp.commands import CommandError  # noqa: E402

S = Suite("test_catalogs")
TMP = tempfile.mkdtemp(prefix="wp_cat_")
MECH = "\u041c\u0435\u0447"          # the Cyrillic word "Mech" (sword)


def items(folder=None):
    return cs.load_layers("items", folder or TMP)


def run(layers, *steps):
    for name, params in steps:
        layers = do(layers, name, **params).state
    return layers


def reason(layers, name, /, **kw):
    try:
        do(layers, name, **kw)
    except CommandError as e:
        return e.reason
    return "allowed"


def _err(layers, name, **kw):
    try:
        do(layers, name, **kw)
    except CommandError as e:
        return e
    return None


def fresh():
    d = tempfile.mkdtemp(prefix="wp_cat_", dir=TMP)
    return cs.load_layers("items", d), d


def shipped_text(kind):
    return io.open(cs.shipped_path(kind), encoding="utf-8").read()


# ---------------------------------------------------------------- files and layers
def _round_trip():
    lay, d = fresh()
    lay = run(lay, ("catalog_add_entry", {"fields": {"name": "Torch", "weight_l": 1}}))
    cs.save(lay.user)
    back = cs.load_layers("items", d)
    return back.user.entries == lay.user.entries, cvw.get(back, "torch").fields["weight_l"], cvw.get(back, "torch").layer


S.case("f-round-trip", "pkg 18: load, add, save, load -> the same entries; Torch weight 1, layer user", (True, 1, "user"))(_round_trip)


def _override():
    before = shipped_text("items")
    lay = run(fresh()[0], ("catalog_edit_entry", {"eid": "rope", "weight_l": 20}))
    v = cvw.get(lay, "rope")
    return v.layer, v.fields["weight_l"], shipped_text("items") == before, cvw.get(fresh()[0], "rope").fields["weight_l"]


S.case("f-override", "pkg 18: editing a shipped entry writes an override (weight 20); the shipped file is unchanged (10)",
       ("override", 20, True, 10))(_override)


def _tombstone():
    lay = run(fresh()[0], ("catalog_remove_entry", {"eid": "rope"}))
    hidden = "rope" not in [v.id for v in cvw.list_entries(lay)]
    back = run(lay, ("catalog_reset_entry", {"eid": "rope"}))
    return hidden, lay.user.find("rope")["deleted"], cvw.get(back, "rope").layer, cvw.get(back, "rope").fields["weight_l"]


S.case("f-tombstone-reset", "pkg 18: removing a shipped entry = tombstone (hidden); reset brings the shipped entry back",
       (True, True, "shipped", 10))(_tombstone)
S.case("f-reset-refused", "pkg 18: reset without an override is refused", "no_override")(
    lambda: reason(fresh()[0], "catalog_reset_entry", eid="rope"))


def _ids():
    lay = run(fresh()[0], ("catalog_add_entry", {"fields": {"name": "Rope"}}))
    first = lay.user.entries[-1]["id"]
    lay = run(lay, ("catalog_remove_entry", {"eid": first}), ("catalog_add_entry", {"fields": {"name": "Rope"}}))
    return first, lay.user.entries[-1]["id"], lay.user.retired, lay.user.counter


S.case("f-ids-never-reused", "pkg 18: 'Rope' collides with the shipped rope -> rope_1; deleted rope_1 is retired; next -> rope_2",
       ("rope_1", "rope_2", ("rope_1",), 2))(_ids)
S.case("f-retired", "pkg 18: Torch -> torch; deleted (retired); a new Torch -> torch_1, never torch again", ("torch", "torch_1"))(
    lambda: (lambda lay: (lay.user.retired[0], lay.user.entries[-1]["id"]))(
        run(fresh()[0], ("catalog_add_entry", {"fields": {"name": "Torch"}}), ("catalog_remove_entry", {"eid": "torch"}),
            ("catalog_add_entry", {"fields": {"name": "Torch"}}))))
S.case("f-id-translit", "D7: a Cyrillic name gets a transliterated id: 'Mech' in Cyrillic -> mech", "mech")(
    lambda: do(fresh()[0], "catalog_add_entry", fields={"name": MECH}).info["id"])
S.case("f-rename", "pkg 18: rename keeps the id", ("rope", "Long rope"))(
    lambda: (lambda v: (v.id, v.name))(cvw.get(run(fresh()[0], ("catalog_rename_entry", {"eid": "rope", "name": "Long rope"})), "rope")))
S.case("f-id-fixed", "pkg 18: the id cannot be edited", "id_not_editable")(
    lambda: reason(fresh()[0], "catalog_edit_entry", eid="rope", id="x"))


def _unknown_kept():
    lay, d = fresh()
    lay = run(lay, ("catalog_add_entry", {"fields": {"name": "Lamp", "glow": "blue"}}),
              ("catalog_edit_entry", {"eid": "lamp", "weight_l": 2}))
    cs.save(lay.user)
    e = cs.load_layers("items", d).user.find("lamp")
    return e["glow"], e["weight_l"]


S.case("f-unknown-field-kept", "pkg 18: an unknown entry field is kept on edit and save", ("blue", 2))(_unknown_kept)
S.case("f-unknown-top-dropped", "pkg 18: an unknown top-level field is dropped on load", False)(
    lambda: "zzz" in cs.to_data(cs.loads(json.dumps({"kind": "items", "format": 1, "zzz": 1, "entries": []}))))
S.case("f-duplicate", "pkg 18: duplicate -> a new id, same fields, not a sample", ("ring_of_guard_1", 1, False))(
    lambda: (lambda lay: (lambda e: (e["id"], e["activation_day"], e["sample"]))(lay.user.entries[-1]))(
        run(fresh()[0], ("catalog_duplicate_entry", {"eid": "ring_of_guard"}))))


# ---------------------------------------------------------------- validation
def spells():
    return cs.load_layers("spells", tempfile.mkdtemp(dir=TMP))


S.case("v-allowed", "spells.md: circle 0..9: circle 10 refused (field_not_allowed, field circle)", ("field_not_allowed", "circle"))(
    lambda: (lambda e: (e.reason, e.params["field"]))(_err(spells(), "catalog_add_entry", fields={"name": "X", "circle": 10})))
S.case("v-required", "gear.md: an armor row needs kind and category -> field_required", "field_required")(
    lambda: reason(cs.load_layers("armor_shields", tempfile.mkdtemp(dir=TMP)), "catalog_add_entry", fields={"name": "Mail"}))
S.case("v-type", "weapons.md: hands must be a number -> field_type", "field_type")(
    lambda: reason(cs.load_layers("weapons", tempfile.mkdtemp(dir=TMP)), "catalog_add_entry", fields={"name": "S", "hands": "two"}))
S.case("v-name", "pkg 18: an entry needs a name", "entry_needs_name")(lambda: reason(fresh()[0], "catalog_add_entry", fields={}))
S.case("v-shipped-valid", "pkg 18: every shipped catalog entry passes its schema", [])(
    lambda: [(k, e["id"]) for k in schema.KINDS for e in cs.load_shipped(k).entries if schema.check(k, e)])


# ---------------------------------------------------------------- saving
def _atomic():
    lay, d = fresh()
    lay = run(lay, ("catalog_add_entry", {"fields": {"name": "Torch"}}))
    cs.save(lay.user)
    path = cs.user_path(d, "items")
    old = io.open(path, encoding="utf-8").read()
    lay2 = run(lay, ("catalog_add_entry", {"fields": {"name": "Candle"}}))

    def boom(a, b):
        raise OSError("disk full")
    real, cs._replace = cs._replace, boom
    try:
        cs.save(lay2.user)
        return "saved"
    except cs.CatalogError:
        pass
    finally:
        cs._replace = real
    return io.open(path, encoding="utf-8").read() == old, os.path.exists(path + ".tmp")


S.case("s-atomic", "pkg 18: a failed save leaves the old file and no temp file", (True, False))(_atomic)


def _refused_save(cat):
    try:
        cs.save(cat)
    except cs.CatalogError:
        return "refused"
    return "saved"


S.case("s-shipped-read-only", "pkg 18: the program never writes into the shipped folder", "refused")(
    lambda: _refused_save(cs.load_shipped("items")))


def _create():
    path = os.path.join(tempfile.mkdtemp(dir=TMP), "my_weapons.json")
    lay = do(None, "catalog_create", kind="weapons", path=path, title="My weapons").state
    cs.save(lay.user)
    back = cs.load(path)
    return back.kind, back.title, len(back.entries), reason(None, "catalog_create", kind="weapons", path=path), \
        reason(None, "catalog_create", kind="potatoes", path=path + "2")


S.case("s-create", "pkg 18: a new empty catalog file of a kind; an existing file / unknown kind refused",
       ("weapons", "My weapons", 0, "catalog_exists", "unknown_kind"))(_create)


# ---------------------------------------------------------------- codes
def _code():
    ring = cvw.get(fresh()[0], "ring_of_guard").fields
    code = cs.export_entry("items", ring)
    lay = run(fresh()[0], ("catalog_import_entry", {"code": code}))
    e = lay.user.entries[-1]
    same = {k: v for k, v in e.items() if k != "id"} == {k: v for k, v in ring.items() if k != "id"}
    return code.startswith("WFC1:"), code.isascii(), e["id"], same, reason(spells(), "catalog_import_entry", code=code)


S.case("c-entry-code", "gear.md item codes: export -> ASCII code; import -> a new entry ring_of_guard_1 with the same fields; "
       "into another kind refused", (True, True, "ring_of_guard_1", True, "wrong_kind"))(_code)


def _file_export():
    lay = run(fresh()[0], ("catalog_add_entry", {"fields": {"name": "Torch"}}))
    path = os.path.join(tempfile.mkdtemp(dir=TMP), "share.json")
    cs.save(lay.user, path)
    return cs.load(path).entries == lay.user.entries


S.case("c-file-export", "catalog.md sharing: a whole catalog file exported and imported back is the same", True)(_file_export)

# ---------------------------------------------------------------- views, kinds, samples
S.case("w-list", "pkg 18: list filtered by text 'ring' -> ring_of_guard; sorted by name",
       (("ring_of_guard",), ("healing_potion", "ring_of_guard", "rope")))(
    lambda: (tuple(v.id for v in cvw.list_entries(items(), "ring")), tuple(v.id for v in cvw.list_entries(items()))))
S.case("w-kinds", "pkg 18: one shipped file per kind", ("armor_shields", "damage_types", "doll_slots", "feats", "items", "skills",
                                                        "spells", "statuses", "weapon_groups", "weapons"))(
    lambda: tuple(sorted(k for k in schema.KINDS if os.path.exists(cs.shipped_path(k)))))
S.case("w-samples", "pkg 18 [OWNER]: shipped weapon (except unarmed), armor, item, spell, status rows are samples", [])(
    lambda: [(k, e["id"]) for k in ("weapons", "armor_shields", "items", "spells", "statuses")
             for e in cs.load_shipped(k).entries if not e.get("sample") and e["id"] != "unarmed_combat"])
S.case("w-armor-sets", "catalog.md: the two armor sets keep their rows: set_1 8, set_2 15; moss garment AC 1 hardness 3",
       (8, 15, 1, 3))(lambda: (lambda s: (len(s["set_1"].rows), len(s["set_2"].rows), s["set_1"].row("moss_garment").ac_bonus,
                                          s["set_1"].row("moss_garment").hardness))(arm.load_sets()))


def _armor_override():
    d = tempfile.mkdtemp(dir=TMP)
    lay = run(cs.load_layers("armor_shields", d), ("catalog_edit_entry", {"eid": "moss_garment", "ac_bonus": 9}))
    cs.save(lay.user)
    return arm.load_sets(d)["set_1"].row("moss_garment").ac_bonus


S.case("w-user-layer-loader", "pkg 18: the program's loaders read the user layer too (armor override AC 9)", 9)(_armor_override)
S.case("w-convert", "pkg 18: catalog -> sheet: healing potion consumable x3; rage status 3/3 charges, inactive",
       ((True, 3, "belt_pouch"), (3, 3, False)))(
    lambda: ((lambda it: (it.consumable, it.quantity, it.slot))(convert.item_from_entry(cs.load_shipped("items").find("healing_potion"), "p")),
             (lambda st: (st.charges.current, st.charges.max, st.active))(convert.status_from_entry(cs.load_shipped("statuses").find("rage"), "rage"))))

# ---------------------------------------------------------------- skills
S.case("k-counts", "skills_list.md [OWNER pkg 18]: Int 23, Wis 5, Str 1, Dex 7, Con 1, Cha 8 = 45", (23, 5, 1, 7, 1, 8, 45))(
    lambda: (lambda c: tuple(len(c.by_stat(s)) for s in ("int", "wis", "str", "dex", "con", "cha")) + (len(c.templates),))(sc.load_default()))
S.case("k-medicine", "pkg 18 [OWNER]: medicine is an Int skill", "int")(lambda: sc.load_default().get("medicine").stat)
S.case("k-md-agrees", "pkg 18: skills.json is the same as RULES/skills_list.md", True)(
    lambda: build_catalogs.skills_entries() == [dict(e) for e in json.load(io.open(cs.shipped_path("skills"), encoding="utf-8"))["entries"]])

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
