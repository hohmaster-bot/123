"""Skill catalog vs RULES/skills_list.md. Run: python Wp_claude/tests/model/test_skills_catalog.py
Russian strings are written as \\u escapes (code files are ASCII only)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.catalog import skills_catalog as sc  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.model.factory import new_character  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_skills_catalog")
CAT = sc.load_default()

SMITH = "\u043a\u0443\u0437\u043d\u0435\u0446"
BAKER = "\u043f\u0435\u043a\u0430\u0440\u044c"
NORTH = "\u0421\u0435\u0432\u0435\u0440"
AIR = "\u0432\u043e\u0437\u0434\u0443\u0448\u043d\u043e\u0435"

S.case("count-45", "skills_list.md: 45 templates", 45)(lambda: len(CAT.templates))
S.case("by-stat", "skills_list.md: STR 1, DEX 7, CON 1, INT 22, WIS 6, CHA 8", (1, 7, 1, 22, 6, 8))(
    lambda: tuple(len(CAT.by_stat(s)) for s in ("str", "dex", "con", "int", "wis", "cha")))
S.case("families", "skills_list.md: param families",
       ("piloting", "craft_1", "craft_2", "craft_3", "know_culture", "acting"))(
    lambda: tuple(t.tid for t in CAT.templates if t.param))
S.case("data-not-code", "skills_list.md: default catalog is read from the data file", True)(
    lambda: CAT.get("search").name in open(sc.DEFAULT_PATH, encoding="utf-8").read())


# New character: ONLY perception and search, 0 ranks.
@S.case("new-character", "skills_list.md [OWNER]: new character has only perception and search, 0 ranks",
        (("perception", "wis", 0), ("search", "int", 0)))
def _new():
    return tuple((s.name, s.stat, s.ranks) for s in new_character(CAT).skills)


def add(ch, tid, sub=""):
    return dispatch(ch, "add_skill", catalog=CAT, tid=tid, sub=sub).state


S.case("add-from-catalog", "skills_list.md: a template creates a skill with 0 ranks", ("stealth", 0, True))(
    lambda: (lambda s: (s.name, s.ranks, s.armor_penalty_applies))(add(new_character(CAT), "stealth").skills[-1]))


# Families: "Craft (smith) III" and "Craft (baker) III" at the same time, different ranks.
@S.case("craft-two-subs", "skills_list.md [OWNER]: Craft (smith) III and Craft (baker) III, own ranks",
        (("\u0420\u0435\u043c\u0435\u0441\u043b\u043e (\u043a\u0443\u0437\u043d\u0435\u0446) III", 2),
         ("\u0420\u0435\u043c\u0435\u0441\u043b\u043e (\u043f\u0435\u043a\u0430\u0440\u044c) III", 0)))
def _craft():
    ch = new_character(CAT, level=3)
    ch = add(add(ch, "craft_3", SMITH), "craft_3", BAKER)
    for _ in range(2):
        ch = dispatch(ch, "buy_skill_rank", name=sc.skill_id("craft_3", SMITH)).state
    return tuple((sc.title(CAT, s), s.ranks) for s in ch.skills if s.template == "craft_3")


S.case("culture-title", "skills_list.md [OWNER]: 'Culture knowledge: North'",
       "\u0417\u043d\u0430\u043d\u0438\u0435 (\u043a\u0443\u043b\u044c\u0442\u0443\u0440\u0430): \u0421\u0435\u0432\u0435\u0440")(
    lambda: sc.title(CAT, sc.make_skill(CAT, "know_culture", NORTH)))
S.case("piloting-title", "skills_list.md [OWNER]: 'Piloting: air'",
       "\u041f\u0438\u043b\u043e\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435: \u0432\u043e\u0437\u0434\u0443\u0448\u043d\u043e\u0435")(
    lambda: sc.title(CAT, sc.make_skill(CAT, "piloting", AIR)))


def rejected(fn):
    try:
        fn()
    except (CommandError, ValueError):
        return "rejected"
    return "allowed"


S.case("family-needs-name", "skills_list.md: a family needs a sub-skill name", "rejected")(
    lambda: rejected(lambda: add(new_character(CAT), "craft_3")))
S.case("plain-no-name", "skills_list.md: a plain skill has no sub-skill name", "rejected")(
    lambda: rejected(lambda: add(new_character(CAT), "stealth", "x")))
S.case("no-duplicates", "same skill twice on a sheet is rejected", "rejected")(
    lambda: rejected(lambda: add(new_character(CAT), "search")))


# Own templates (catalog.md: players add their own entries).
@S.case("user-template", "catalog.md: the player adds an own template, then uses it", (46, "user", "my_dance", 0))
def _user():
    cat = sc.add_template(CAT, sc.SkillTemplate("my_dance", "cha", "Dance"))
    ch = dispatch(new_character(cat), "add_skill", catalog=cat, tid="my_dance").state
    return (len(cat.templates), cat.get("my_dance").source, ch.skills[-1].name, ch.skills[-1].ranks)


S.case("user-template-unique", "catalog: template ids stay unique", "rejected")(
    lambda: rejected(lambda: sc.add_template(CAT, sc.SkillTemplate("search", "int", "x"))))


@S.case("save-sub-skills", "D11: sub-skills survive save/load (round trip)", True)
def _save():
    ch = add(add(new_character(CAT), "craft_3", SMITH), "craft_3", BAKER)
    return cio.loads(cio.dumps(ch)) == ch


if __name__ == "__main__":
    sys.exit(S.run())
