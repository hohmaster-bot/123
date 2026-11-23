"""Build ONE file with all game rules for an independent reviewer (package 20, part 2).

Output: Wp_claude/REVIEW_PACK/RULES_PACK.md. Deterministic (no dates, no network): the same inputs give the same file.
Contents: a cover note with the review task (English, then Russian), a glossary, every RULES/*.md file in the order
of RULES/index.md (each under its own heading; the generated "Sections" block of index.md is left out because it only
repeats headings; draft files go to an appendix with a DRAFT banner), and the data tables that carry rule numbers
(rule constants, damage types, doll slots, weapon qualification levels, effect target names).
No code, no tests, no chat notes. Owner quotes stay as they are (the file is UTF-8; this script is ASCII).
Usage: python Wp_claude/tools/make_review_pack.py
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RULES = os.path.join(ROOT, "Wp_claude", "RULES")
DATA = os.path.join(ROOT, "wp", "catalog", "data")
CONSTANTS = os.path.join(ROOT, "wp", "rules_data", "constants.json")
OUT = os.path.join(ROOT, "Wp_claude", "REVIEW_PACK", "RULES_PACK.md")
DRAFTS = ("ac_zones.md",)              # owner drafts, not built: appendix
SKIP = ("training_costs_draft.md",)    # legacy dumps (not rules)
SECTIONS = re.compile(r"<!-- sections:start.*?<!-- sections:end -->", re.S)

COVER_EN = """# WipeFinder rules pack for an independent review

## What this is
WipeFinder is a character-tracking app for a homebrew tabletop RPG based on Pathfinder 1e with MANY house rules.
The app tracks resources (HP, balance, pain, mana, spirit, comfort...), statuses, abilities, items and training
purchases for one character. It does NOT roll dice and does NOT run the game: the players roll, the app records the
results and computes the derived numbers.

## What you get
- Every rule file of the project (the owner's rules; the text is the truth, the app follows it), in a fixed order.
- A glossary of the house terms.
- The data tables that hold rule numbers (each number can be changed per character in the app's settings).
Owner quotes in Russian are kept verbatim; the English text around them is the working translation.
Tags: [OWNER] = stated by the owner; [?] = unclear; [BETA] = unfinished; "package N" = the work step that added it;
"Qnn" = a question that was asked and answered (the answer is written next to it).

## What this is NOT
Not a play-test report, not the program code, not the test suite, not a design document of the screens.

## Your review task
1. Find contradictions between files and inside a file.
2. Find ambiguous rules that two readers would implement differently: quote the line and give both readings.
3. Find missing rules: a mechanic that is mentioned but has no numbers or no owner decision.
4. Find rules that are likely to cause bad play or exploits (stacking, resource loops, the balance cap, free actions)
   and say why.
5. Find unnecessary complexity: rules that could be merged or dropped without losing the intent.
6. Rate each domain 1-10 for clarity: combat, defense, resources, rest, gear, training, skills, spells, narrative;
   then give a top-10 list of fixes.

Please answer in one table:

| id | file / section | type (contradiction / ambiguity / missing / balance / complexity) | quote | suggested fix |
|---|---|---|---|---|

then the domain ratings and the top-10 list.
"""

COVER_RU = """## Kratko po-russki
""".replace("Kratko po-russki", "\u041a\u0440\u0430\u0442\u043a\u043e \u043f\u043e-\u0440\u0443\u0441\u0441\u043a\u0438")

RU_TEXT = ("\u042d\u0442\u043e \u043f\u043e\u043b\u043d\u044b\u0439 \u043d\u0430\u0431\u043e\u0440 \u043f\u0440\u0430\u0432\u0438\u043b WipeFinder "
           "\u0434\u043b\u044f \u043d\u0435\u0437\u0430\u0432\u0438\u0441\u0438\u043c\u043e\u0439 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438. "
           "\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u0432\u0435\u0434\u0451\u0442 \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u0436\u0430 "
           "(\u0440\u0435\u0441\u0443\u0440\u0441\u044b, \u0441\u0442\u0430\u0442\u0443\u0441\u044b, \u0441\u043f\u043e\u0441\u043e\u0431\u043d\u043e\u0441\u0442\u0438) "
           "\u0438 \u043d\u0435 \u0431\u0440\u043e\u0441\u0430\u0435\u0442 \u043a\u0443\u0431\u0438\u043a\u0438. "
           "\u0417\u0430\u0434\u0430\u0447\u0430 \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u044e\u0449\u0435\u0433\u043e: \u043d\u0430\u0439\u0442\u0438 "
           "\u043f\u0440\u043e\u0442\u0438\u0432\u043e\u0440\u0435\u0447\u0438\u044f, \u043d\u0435\u044f\u0441\u043d\u043e\u0441\u0442\u0438, \u043f\u0440\u043e\u0431\u0435\u043b\u044b, "
           "\u0434\u044b\u0440\u044b \u0432 \u0431\u0430\u043b\u0430\u043d\u0441\u0435 \u0438 \u043b\u0438\u0448\u043d\u044e\u044e \u0441\u043b\u043e\u0436\u043d\u043e\u0441\u0442\u044c, "
           "\u043e\u0446\u0435\u043d\u0438\u0442\u044c \u043a\u0430\u0436\u0434\u0443\u044e \u043e\u0431\u043b\u0430\u0441\u0442\u044c \u043e\u0442 1 \u0434\u043e 10 "
           "\u0438 \u0434\u0430\u0442\u044c \u0441\u043f\u0438\u0441\u043e\u043a \u0438\u0437 10 \u0433\u043b\u0430\u0432\u043d\u044b\u0445 \u043f\u0440\u0430\u0432\u043e\u043a. "
           "\u041e\u0442\u0432\u0435\u0442 \u2014 \u0432 \u0442\u0430\u0431\u043b\u0438\u0446\u0435 \u0432\u044b\u0448\u0435.")

GLOSSARY = [
    ("Balance", "a second bar next to HP, lost together with HP; regenerates every round (zero-initiative tick)."),
    ("Balance cap", "the balance max taken at the start of combat; each hit lowers it by 1 until the end of combat."),
    ("BP", "pain threshold points (cur / max); spent in the short rest; can be above max (overcap)."),
    ("OT", "trauma points: damage that went past the balance; removed by injuries, comfort, attention."),
    ("Pain", "a counter; -1 to all rolls per pain (default); death at the death cap (default 8)."),
    ("Temp HP", "absorb damage first; 'by button' temp HP last to the short rest, a buff's temp HP last with the buff."),
    ("Spirit", "pays item activations ('day' = until the short rest, 'decade' = until the long rest)."),
    ("Overload", "a counter from spell casting; blocks the balance regen while above 0; -1 per tick."),
    ("Comfort", "a resource exchanged for training or for removing OT."),
    ("Attention", "a narrative resource from the end of a cycle; converted into OV, training, base points, OT removal."),
    ("OV", "time points (narrative); burn at the end of a cycle."),
    ("Zero-initiative tick", "the end of a round: durations -1, balance regen, damage over time, overload -1."),
    ("Status", "a buff / debuff / situation with effects, duration, charges; active or not."),
    ("Effect", "a typed bonus on a target (any sheet number); same type: the larger wins; flat and dodge add."),
    ("AC ladder / layers", "AC is built in layers (base, flat, armor/parry, natural, shield, dodge...); the layer an "
                           "attack roll landed in decides what happens."),
    ("Parry", "an AC layer from proficiency (armor grades, odd levels, tower shields) and weapon mastery."),
    ("Weapon mastery", "grades 0-12 per weapon group; picks at specialist (5-7), expert (8-11) and master (12)."),
    ("Training", "points spent on purchases (stats, skills, weapon grades, feats, spells...)."),
    ("Base", "a home with slots for items and blessings; items at the base give effects."),
    ("Doll", "22 equipment slots; one item per slot; the hands slot holds up to 2 hands of items."),
    ("Court", "a narrative parameter 'Name LtT' (level, tier)."),
    ("Lens", "a narrative goal counter 0..X; 0 = red end, X = green end."),
    ("Drive", "a narrative motive, level 0..5; drives at 4+ give attention at the end of a cycle."),
    ("Quirk / seed", "a narrative ability (may carry effects); a seed is bought and later sprouted into a quirk."),
    ("Template", "a race / class-like package of effects, hit dice, feats, pools, statuses."),
    ("Pool", "a character resource such as Ki (max may be a formula)."),
    ("Iterative penalty", "each further attack in a round: -5 (data), reset every round."),
    ("Package N / Qnn", "the work step that added a rule / a question the owner answered."),
]


def _read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def order():
    """RULES files in the order of the index table, then any file the table misses (alphabetical)."""
    index = _read(os.path.join(RULES, "index.md"))
    listed = re.findall(r"^\|\s*([a-z0-9_]+\.md)\s*\|", index, re.M)
    names = sorted(f for f in os.listdir(RULES) if f.endswith(".md"))
    out = ["index.md"] + [n for n in listed if n in names and n not in SKIP and n != "index.md"]
    out += [n for n in names if n not in out and n not in SKIP]
    return out


def _shift(text):
    """Headings of a rule file go two levels down (its own title becomes ###)."""
    return re.sub(r"^(#+)", lambda m: "##" + m.group(1), text, flags=re.M)


def _table(rows, head):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |")
    return "\n".join(out)


def data_tables():
    c = json.loads(_read(CONSTANTS))
    parts = ["## Data tables with rule numbers", "",
             "### Rule constants (wp/rules_data/constants.json)",
             "Every number can be changed per character (rules_settings). Values as shipped.", "",
             _table([(x["id"], json.dumps(x["value"], ensure_ascii=False), x.get("unit", ""), x.get("description", ""))
                     for x in c["constants"]], ("id", "value", "unit", "meaning"))]
    dt = json.loads(_read(os.path.join(DATA, "damage_types.json")))
    parts += ["", "### Damage types (damage_types.json)", "",
              _table([(e["id"], "yes" if e.get("physical") else "") for e in dt["entries"]], ("type", "physical (DR works)"))]
    ds = json.loads(_read(os.path.join(DATA, "doll_slots.json")))
    parts += ["", "### Doll slots (doll_slots.json)", "",
              _table([(e["id"], e["name"]) for e in ds["entries"]], ("slot id", "name"))]
    w = json.loads(_read(os.path.join(DATA, "weapons.json")))
    levels = w["meta"].get("qualification_levels", {})
    parts += ["", "### Weapon qualification levels (weapons.json)", "",
              _table(sorted(levels.items(), key=lambda kv: kv[1]), ("owner word", "grade"))]
    st = json.loads(_read(os.path.join(DATA, "sheet_targets.json")))
    parts += ["", "### Effect targets of sheet numbers (sheet_targets.json)", "",
              _table(sorted(st["targets"].items()), ("target", "meaning"))]
    return "\n".join(parts)


def build_text():
    files = order()
    rules = [f for f in files if f not in DRAFTS]
    drafts = [f for f in files if f in DRAFTS]
    out = [COVER_EN, COVER_RU, RU_TEXT, "",
           "## Contents", ""] + ["- %s" % f for f in rules] + ["- Appendix (drafts, not built): %s" % ", ".join(drafts),
                                                               "- Data tables", ""]
    out += ["## Glossary", "", _table(GLOSSARY, ("term", "meaning")), ""]
    for f in rules:
        text = _read(os.path.join(RULES, f))
        if f == "index.md":
            text = SECTIONS.sub("", text)
        out += ["## File: %s" % f, "", _shift(text).strip(), ""]
    for f in drafts:
        out += ["## Appendix: %s (DRAFT, not built; review optional)" % f, "", _shift(_read(os.path.join(RULES, f))).strip(), ""]
    out += [data_tables(), ""]
    return "\n".join(out)


def main():
    text = build_text()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    size = os.path.getsize(OUT)
    print("%s: %d bytes (%.1f KB), %d words" % (os.path.relpath(OUT, ROOT), size, size / 1024.0, len(text.split())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
