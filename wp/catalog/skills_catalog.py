"""Skill catalog (RULES/skills_list.md, catalog.md, skills.md).

The default catalog is DATA: the catalog file wp/catalog/data/skills.json (kind "skills", package 18), made from the
owner's text RULES/skills_list.md by Wp_claude/tools/build_catalogs.py skills (a test checks they agree).
Entry fields: id, name, name_en, stat, desc, param (a family: the player names each sub-skill, each has its own
ranks), needs_flight (informational). The player may add own templates (catalog rules).

A new character starts with ONLY perception and search, 0 ranks. Every other skill
is added from the catalog with 0 ranks.
"""
from dataclasses import dataclass, replace
from typing import Tuple

from wp.catalog import store as cs
from wp.core import skills as sk

KIND = "skills"
DEFAULT_PATH = cs.shipped_path(KIND)

STAT_CODES = {"STR": "str", "DEX": "dex", "CON": "con", "INT": "int", "WIS": "wis", "CHA": "cha"}
ARMOR_PENALTY_STATS = ("str", "dex")      # gear.md: armor skill penalty on Str/Dex skills
START_SKILLS = ("perception", "search")
DEFAULT = "default"
USER = "user"



@dataclass(frozen=True)
class SkillTemplate:
    tid: str                  # stable id (ASCII)
    stat: str
    name: str                 # display name (owner text)
    desc: str = ""
    param: bool = False       # family: needs a sub-skill name
    needs_flight: bool = False
    source: str = DEFAULT     # DEFAULT or USER


@dataclass(frozen=True)
class SkillCatalog:
    templates: Tuple[SkillTemplate, ...] = ()

    def get(self, tid):
        for t in self.templates:
            if t.tid == tid:
                return t
        raise KeyError("no skill template %r" % (tid,))

    def by_stat(self, stat):
        return tuple(t for t in self.templates if t.stat == stat)


def from_entries(entries):
    return SkillCatalog(tuple(SkillTemplate(tid=e["id"], stat=e["stat"], name=e["name"], desc=e.get("desc", ""),
                                            param=bool(e.get("param", False)),
                                            needs_flight=bool(e.get("needs_flight", False))) for e in entries))


def load_default(user_folder=None):
    layers = cs.load_layers(KIND, user_folder) if user_folder else cs.Layers(cs.load_shipped(KIND), cs.Catalog(KIND))
    return from_entries([e for e, _ in cs.merged(layers)])


def add_template(catalog, template):
    """Player's own template (source USER). Ids must stay unique."""
    if any(t.tid == template.tid for t in catalog.templates):
        raise ValueError("template id already exists: %r" % (template.tid,))
    if template.stat not in STAT_CODES.values():
        raise ValueError("unknown stat: %r" % (template.stat,))
    return replace(catalog, templates=catalog.templates + (replace(template, source=USER),))


def skill_id(tid, sub=""):
    return "%s:%s" % (tid, sub) if sub else tid


def make_skill(catalog, tid, sub=""):
    """A sheet skill from a template, 0 ranks. Families need a sub-skill name."""
    t = catalog.get(tid)
    sub = sub.strip()
    if t.param and not sub:
        raise ValueError("%s is a family: give the sub-skill a name" % tid)
    if not t.param and sub:
        raise ValueError("%s is not a family: no sub-skill name" % tid)
    return sk.Skill(name=skill_id(tid, sub), stat=t.stat, ranks=0,
                    armor_penalty_applies=t.stat in ARMOR_PENALTY_STATS, template=tid, sub=sub)


PARAM_MARK = "(\u0445)"          # "(x)" in the owner's names


def title(catalog, skill):
    """Display name with the sub-skill, as in the owner's examples:
    'Craft (x) III' -> 'Craft (smith) III'; 'Culture knowledge (x)' -> 'Culture knowledge: North'."""
    t = catalog.get(skill.template) if skill.template else None
    if t is None:
        return skill.name
    if not skill.sub:
        return t.name.replace(PARAM_MARK, "").strip()
    name = t.name.strip()
    if name.endswith(PARAM_MARK):
        return "%s: %s" % (name[: -len(PARAM_MARK)].strip(), skill.sub)
    if PARAM_MARK in name:
        return name.replace(PARAM_MARK, "(%s)" % skill.sub)
    return "%s: %s" % (name, skill.sub)


def start_skills(catalog):
    """A new character has ONLY perception and search, 0 ranks."""
    return tuple(make_skill(catalog, tid) for tid in START_SKILLS)
