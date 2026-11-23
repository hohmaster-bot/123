"""One-time builder of the package 18 catalog files (ASCII code; the data files are UTF-8).

Reads the old data files (weapons_default.json, armor_set_*.json, feats_default.json, damage_types.json,
doll_slots.json) and RULES/skills_list.md, writes the new single-file catalogs into wp/catalog/data/ and adds the
test samples (items, spells, statuses, a stance feat). Kept in the repo as the record of how the files were made and
for regenerating skills.json from skills_list.md: python Wp_claude/tools/build_catalogs.py skills
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "wp", "catalog", "data")
SKILLS_MD = os.path.join(ROOT, "Wp_claude", "RULES", "skills_list.md")
STAT_CODES = {"STR": "str", "DEX": "dex", "CON": "con", "INT": "int", "WIS": "wis", "CHA": "cha"}
_SECTION = re.compile(r"^##\s.*\((STR|DEX|CON|INT|WIS|CHA)\)\s*$")
_ENTRY = re.compile(r"^-\s+([a-z0-9_]+)\s*(?:\(([a-z_ ,]+)\))?\s*\|\s*(.+?)\s+—\s+(.*)$")


def read(name):
    with io.open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def write(kind, entries, title="", meta=None, note=""):
    data = {"kind": kind, "format": 1, "title": title, "counter": 0, "retired": [], "meta": dict(meta or {}),
            "entries": entries}
    if note:
        data["meta"]["note"] = note
    with io.open(os.path.join(DATA, kind + ".json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1) + "\n")


def skills_entries(md_path=SKILLS_MD):
    out, stat = [], None
    for line in io.open(md_path, encoding="utf-8").read().splitlines():
        m = _SECTION.match(line.strip())
        if m:
            stat = STAT_CODES[m.group(1)]
            continue
        m = _ENTRY.match(line.strip())
        if m and stat:
            flags = {x.strip() for x in (m.group(2) or "").split(",") if x.strip()}
            name = m.group(3).strip()
            out.append({"id": m.group(1), "name": name, "name_en": name, "sample": False, "stat": stat,
                        "desc": m.group(4).strip(), "param": "param" in flags, "needs_flight": "needs_flight" in flags})
    return out


def build_skills():
    write("skills", skills_entries(), "Default skills (RULES/skills_list.md)",
          note="Generated from RULES/skills_list.md by Wp_claude/tools/build_catalogs.py skills.")


def build_all():
    w = read("weapons_default.json")
    groups = [{"id": g["gid"], "name": g["name"], "name_en": g.get("name_en", ""), "sample": False,
               "scale": g["scale"], "difficulty": g["difficulty"], "parents": g["parents"], "basic": g["basic"]}
              for g in w["groups"]]
    write("weapon_groups", groups, "Weapon groups (weapons.md)")
    weapons = []
    for x in w["weapons"]:
        e = {"id": x["wid"], "name": x["name"], "sample": x["wid"] != "unarmed_combat"}
        e.update({k: v for k, v in x.items() if k not in ("wid", "name")})
        weapons.append(e)
    write("weapons", weapons, "Weapon cards (test samples)",
          meta={"qualification_levels": w["qualification_levels"]}, note=w.get("note", ""))
    armor = []
    for name in ("armor_set_1.json", "armor_set_2.json"):
        s = read(name)
        for r in s["rows"]:
            e = {"id": r["id"], "name": r["name"], "sample": True, "set": s["set"], "set_title": s.get("title", s["set"])}
            e.update({k: v for k, v in r.items() if k not in ("id", "name")})
            armor.append(e)
    write("armor_shields", armor, "Armor and shields (two sample sets)", note=read("armor_set_1.json").get("note", ""))
    feats = []
    for f in read("feats_default.json")["feats"]:
        e = {"id": f["fid"], "name": f["name"], "sample": False}
        e.update({k: v for k, v in f.items() if k not in ("fid", "name")})
        feats.append(e)
    feats.append({"id": "me_liquescit", "name": "Me Liquescit", "sample": True, "cost": 200, "is_stance": True,
                  "desc": "Stance (combat.md): no dodge bonus to AC, cannot be flanked.",
                  "effects": [{"target": "block_bonus", "block_type": "dodge", "block_scope": ["ac"]},
                              {"target": "cannot_be_flanked"}]})
    write("feats", feats, "Feats")
    dt = read("damage_types.json")
    write("damage_types", [{"id": t, "name": t, "sample": False, "physical": t in dt["physical"]} for t in dt["types"]],
          "Damage types", meta={"also_physical": [t for t in dt["physical"] if t not in dt["types"]]},
          note="Owner list (packages 16, 17); 'also_physical' = the old code default type.")
    ds = read("doll_slots.json")
    write("doll_slots", [{"id": s, "name": n, "sample": False, "hands": s == ds["hands"]} for s, n in ds["slots"]],
          "Doll slots (doll.md)")
    build_skills()
    write("items", [
        {"id": "rope", "name": "Rope", "sample": True, "kind": "misc", "weight_l": 10, "quantity": 1, "slot": "",
         "base_slot_cost": 1},
        {"id": "healing_potion", "name": "Healing potion", "sample": True, "kind": "misc", "consumable": True,
         "quantity": 3, "weight_l": 1, "on_use_status": "healing", "slot": "belt_pouch"},
        {"id": "ring_of_guard", "name": "Ring of guard", "sample": True, "kind": "misc", "slot": "fingers",
         "activation_day": 1, "effects_off": [], "effects_on": [{"target": "ac", "value": 1, "btype": "deflection"}],
         "ilvl": 1},
    ], "Items (test samples)")
    write("spells", [
        {"id": "light", "name": "Light", "sample": True, "circle": 0, "school": "", "mana_cost": None,
         "description": "Test sample."},
        {"id": "fire_dart", "name": "Fire dart", "sample": True, "circle": 2, "school": "", "mana_cost": None,
         "description": "Test sample (no damage engine: spells.md BETA)."},
    ], "Spells (test samples)")
    write("statuses", [
        {"id": "rage", "name": "Rage", "sample": True, "duration": "ticks", "full_ticks": 3, "charges_max": 3,
         "effects": [{"target": "attack", "value": 2, "btype": "morale"}]},
        {"id": "ki_aura", "name": "Ki aura", "sample": True, "duration": "ticks", "full_ticks": 3,
         "charge_source": "ki", "charge_per_round": 1, "effects": [{"target": "ac", "value": 1, "btype": "deflection"}]},
        {"id": "cursed_darkness", "name": "Cursed darkness", "sample": True, "duration": "infinite",
         "charges_max": 9, "charge_source": "own", "charge_per_round": 3, "effects": []},
    ], "Statuses (test samples from buffs.md)")


if __name__ == "__main__":
    if sys.argv[1:] == ["skills"]:
        build_skills()
    else:
        build_all()
    print("catalogs written")
