"""Feat catalog shipped as data (RULES/catalog.md, training.md).

Default feats live in wp/catalog/data/feats_default.json. A feat copied into a
sheet keeps its flags (e.g. "finesse": attacks with finesse weapons may use Dex).
Feat price: entered by the author, default 200 (training.md); only source
"training" spends training points.
"""
import io
import json
import os
from dataclasses import dataclass, replace
from typing import Tuple

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "feats_default.json")
FORMAT = "wipefinder.feats"
DEFAULT_COST = 200
FINESSE = "finesse"


@dataclass(frozen=True)
class FeatTemplate:
    fid: str
    name: str
    name_en: str = ""
    desc: str = ""
    cost: int = DEFAULT_COST
    flags: Tuple[str, ...] = ()
    source: str = "default"


@dataclass(frozen=True)
class FeatCatalog:
    templates: Tuple[FeatTemplate, ...] = ()

    def get(self, fid):
        for t in self.templates:
            if t.fid == fid:
                return t
        raise KeyError("no feat template %r" % (fid,))


def parse(text):
    data = json.loads(text)
    if data.get("format") != FORMAT:
        raise ValueError("not a WipeFinder feat catalog")
    out = tuple(FeatTemplate(fid=f["fid"], name=f["name"], name_en=f.get("name_en", ""),
                             desc=f.get("desc", ""), cost=int(f.get("cost", DEFAULT_COST)),
                             flags=tuple(f.get("flags", ()))) for f in data["feats"])
    ids = [t.fid for t in out]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate feat ids in the catalog file")
    return FeatCatalog(out)


def load_default(path=DEFAULT_PATH):
    with io.open(path, encoding="utf-8") as f:
        return parse(f.read())


def add_template(catalog, template):
    if any(t.fid == template.fid for t in catalog.templates):
        raise ValueError("feat id already exists: %r" % (template.fid,))
    return replace(catalog, templates=catalog.templates + (replace(template, source="user"),))


def has_flag(ch, flag):
    """Does any feat on the sheet carry this flag?"""
    return any(flag in f.flags for f in ch.feats)
