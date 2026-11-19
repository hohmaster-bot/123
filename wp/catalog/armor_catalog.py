"""Armor and shield catalogs shipped as DATA sets (package 9 K, RULES/gear.md, catalog.md).

Every file wp/catalog/data/armor_set_*.json is one selectable data set (tables from a game; rules may
differ per game, so nothing here is a hard rule). Row fields: id, name, kind (armor | shield),
category (armor: light / medium / heavy; shield: light / heavy / tower), weight (L), price (text as
written), access_class (or null), ac_bonus, touch_bonus, max_dex (or null), skill_penalty (a POSITIVE
number meaning a penalty), speed_penalty_ft, spell_penalty_mana, spell_failure_pct, special, hardness,
hp, durable. Weight in the source: "L" = 1 L, a number N = N * 10 L (already converted in the files).
"""
import glob
import io
import json
import os
from dataclasses import dataclass
from typing import Optional, Tuple

from wp.model.character import SHIELD, Item

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PATTERN = "armor_set_*.json"
FORMAT = "wipefinder.armor"
ARMOR = "armor"
KINDS = (ARMOR, SHIELD)
CATEGORIES = {ARMOR: ("light", "medium", "heavy"), SHIELD: ("light", "heavy", "tower")}


@dataclass(frozen=True)
class ArmorTemplate:
    aid: str
    name: str
    kind: str
    category: str
    weight_l: int = 0
    price: str = ""
    access_class: Optional[int] = None
    ac_bonus: int = 0
    touch_bonus: int = 0
    max_dex: Optional[int] = None
    skill_penalty: int = 0             # positive = penalty (the item stores it negative)
    speed_penalty_ft: int = 0
    spell_penalty_mana: int = 0
    spell_failure_pct: int = 0
    special: bool = False              # "+" column of set 2 (meaning kept as data)
    hardness: int = 0
    hp: int = 0
    durable: bool = True


@dataclass(frozen=True)
class ArmorSet:
    sid: str
    title: str
    rows: Tuple[ArmorTemplate, ...] = ()

    def row(self, aid):
        for r in self.rows:
            if r.aid == aid:
                return r
        raise KeyError("no armor %r in set %s" % (aid, self.sid))


def _row(d):
    kind = d["kind"]
    if kind not in KINDS:
        raise ValueError("unknown kind %r for %s" % (kind, d.get("id")))
    if d["category"] not in CATEGORIES[kind]:
        raise ValueError("unknown category %r for %s" % (d["category"], d.get("id")))
    return ArmorTemplate(
        aid=d["id"], name=d["name"], kind=kind, category=d["category"], weight_l=int(d.get("weight", 0)),
        price=str(d.get("price", "")), access_class=d.get("access_class"), ac_bonus=int(d.get("ac_bonus", 0)),
        touch_bonus=int(d.get("touch_bonus", 0)), max_dex=d.get("max_dex"),
        skill_penalty=int(d.get("skill_penalty", 0)), speed_penalty_ft=int(d.get("speed_penalty_ft", 0)),
        spell_penalty_mana=int(d.get("spell_penalty_mana", 0)), spell_failure_pct=int(d.get("spell_failure_pct", 0)),
        special=bool(d.get("special", False)), hardness=int(d.get("hardness", 0)), hp=int(d.get("hp", 0)),
        durable=bool(d.get("durable", True)))


def parse(text):
    data = json.loads(text)
    if data.get("format") != FORMAT:
        raise ValueError("not a WipeFinder armor catalog")
    rows = tuple(_row(d) for d in data.get("rows", ()))
    ids = [r.aid for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate armor id in set %s" % data.get("set"))
    return ArmorSet(sid=data["set"], title=data.get("title", data["set"]), rows=rows)


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return parse(f.read())


def load_sets(folder=DATA_DIR):
    """{set id: ArmorSet} for every armor_set_*.json in the folder."""
    out = {}
    for path in sorted(glob.glob(os.path.join(folder, PATTERN))):
        s = load(path)
        out[s.sid] = s
    return out


def make_item(row, iid):
    """An Item from a catalog row: armor is worn gear, a shield goes to the hands (1 hand)."""
    common = dict(iid=iid, name=row.name, weight_l=row.weight_l, max_dex=row.max_dex,
                  skill_penalty=-abs(row.skill_penalty), spell_penalty_mana=row.spell_penalty_mana,
                  spell_failure_pct=row.spell_failure_pct, speed_penalty_ft=row.speed_penalty_ft,
                  durability=row.hardness, hp=row.hp, durable=row.durable)
    if row.kind == SHIELD:
        return Item(kind=SHIELD, hands=1, shield=row.ac_bonus, shield_type=row.category, **common)
    return Item(armor=row.ac_bonus, armor_type=row.category, touch_bonus=row.touch_bonus, **common)
