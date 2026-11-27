"""Feat catalog shipped as data (RULES/catalog.md, training.md).

Default feats live in the catalog file wp/catalog/data/feats.json (kind "feats", package 18). A feat copied into a
sheet keeps its flags (e.g. "finesse": attacks with finesse weapons may use Dex).
Feat price: entered by the author, default 200 (training.md); only source
"training" spends training points.
"""
import io
import json
import os
from dataclasses import dataclass, replace
from typing import Tuple

from wp.catalog import store as cs
from wp.core.effects import Effect
from wp.core.formula import validate as validate_formula
from wp.rules_data import rules as rd

KIND = "feats"
DEFAULT_COST = rd.ref("training.feat_default_cost")
FINESSE = "finesse"


@dataclass(frozen=True)
class FeatTemplate:
    fid: str
    name: str
    name_en: str = ""
    desc: str = ""
    cost: int = rd.default("training.feat_default_cost")
    flags: Tuple[str, ...] = ()
    source: str = "default"
    effects: Tuple[Effect, ...] = ()   # copied to the sheet feat (package 11 D)
    granted_maneuvers: Tuple[str, ...] = ()
    is_stance: bool = False


@dataclass(frozen=True)
class FeatCatalog:
    templates: Tuple[FeatTemplate, ...] = ()

    def get(self, fid):
        for t in self.templates:
            if t.fid == fid:
                return t
        raise KeyError("no feat template %r" % (fid,))


EFFECT_KEYS = ("target", "value", "btype", "weapon", "dice", "note", "stat_mod", "multiplier", "block_type",
               "block_scope", "block_stats", "block_actions", "block_resources", "stacks",
               "condition", "situational", "scope", "cells")      # package 38: Endurance is situational


def _effect(d):
    """An effect in the catalog file: {"target": ..., "value": N | "stat_mod": "str", ...}."""
    unknown = set(d) - set(EFFECT_KEYS)
    if unknown:
        raise ValueError("unknown effect fields in the feat catalog: %s" % ", ".join(sorted(unknown)))
    d = {k: tuple(v) if isinstance(v, (list, tuple)) else v for k, v in d.items()}
    e = Effect(**d)
    if isinstance(e.value, str) and e.value != "all":
        validate_formula(e.value)          # a broken formula is refused when the catalog is read (package 14 C)
    return e


def from_entries(entries):
    out = tuple(FeatTemplate(fid=f["id"], name=f["name"], name_en=f.get("name_en", ""),
                             desc=f.get("desc", ""), cost=int(f.get("cost", int(DEFAULT_COST))),
                             flags=tuple(f.get("flags", ())),
                             effects=tuple(_effect(e) for e in f.get("effects", ())),
                             granted_maneuvers=tuple(f.get("granted_maneuvers", ())),
                             is_stance=bool(f.get("is_stance", False))) for f in entries)
    ids = [t.fid for t in out]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate feat ids in the catalog file")
    return FeatCatalog(out)


def parse(text):
    """A feat catalog from the text of a catalog file of kind "feats"."""
    cat = cs.loads(text)
    if cat.kind != KIND:
        raise ValueError("not a WipeFinder feat catalog")
    return from_entries(cat.entries)


def load_default(user_folder=None):
    layers = cs.load_layers(KIND, user_folder) if user_folder else cs.Layers(cs.load_shipped(KIND), cs.Catalog(KIND))
    return from_entries([e for e, _ in cs.merged(layers)])


def add_template(catalog, template):
    if any(t.fid == template.fid for t in catalog.templates):
        raise ValueError("feat id already exists: %r" % (template.fid,))
    return replace(catalog, templates=catalog.templates + (replace(template, source="user"),))


def has_flag(ch, flag):
    """Does any feat on the sheet carry this flag?"""
    return any(flag in f.flags for f in ch.feats)
