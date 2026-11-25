"""Package 34 part 1: the sources of every derived number (owner 1A), the attack numbers, the load borders and the AC
zones as the Parameters / AC blocks read them. Numbers by hand from RULES (combat.md "General attack numbers",
gear.md "Load display", resources.md, defense.md, progression.md, narrative.md).
Hero: Str 14 (+2), Dex 20 (+5), Con 12 (+1), Cha 14 (+2), others 10; bab 2 (no class); hp rolls (10,).
Run: python Wp_claude/tests/model/test_pkg34.py"""
import dataclasses
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import session as sm  # noqa: E402
from wp.app import views as vw  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.model import sources as src  # noqa: E402
from wp.model.character import ABILITIES, Ability, Character, Item, ResourcePool  # noqa: E402
from wp.model.source_row import SourceRow  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg34")
TMP = tempfile.mkdtemp(prefix="wp_p34_")


def hero(**kw):
    base = {"str": 14, "dex": 20, "con": 12, "cha": 14}
    return Character(bab=2, hp_rolls=(10,), abilities={a: Ability(base=base.get(a, 10)) for a in ABILITIES}, **kw)


def sv(ch, number):
    with rd.using(ch):
        return src.view(ch, number)


def total(ch, number):
    return sv(ch, number)["total"]


def summed(ch, number):
    return sum(r["value"] for r in sv(ch, number)["rows"] if r["counted"])


def run(ch, *steps):
    for n, p in steps:
        ch = dispatch(ch, n, **p).state
    return ch


def ref(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


BLESS = Status("bless", sid="bless", effects=(Effect("hp_max", 3), Effect("save", 1, "morale"),
                                              Effect("save", 2, "morale")), active=True)
SAMPLE = hero(statuses=(BLESS,), pools=(ResourcePool("ki", "Ki", "level + 2", 1),),
              source_rows=(SourceRow("mage", "mana_max", "Mage", 8), SourceRow("old", "hp_max", "Old", 5, False),
                           SourceRow("ward", "ac:1", "Ward", 2), SourceRow("trained", "attack_melee", "Drill", 1)))

# ---------------------------------------------------------------- 1A totals = the sum of the counted sources
# hp: die 10 + Con 1 = 11, bless +3, "Old" off -> 14; mana: base 0 + Mage 8 = 8; spirit 5 + 5 x 2 = 15;
# melee 2 + 2 + Drill 1 = 5; ranged 2 + 5 = 7; fort 0 + 1 + morale max(1, 2) = 3 (morale bonuses do not stack);
# pool Ki: level 1 + 2 = 3; AC cell 1: 10 + Dex 5 + Ward 2 = 17, cell 2: 15; speed 30 base (Character default);
# attention 1; load Str mod 2.
EXPECT = {"hp_max": 14, "mana_max": 8, "spirit_max": 15, "attack_melee": 5, "attack_ranged": 7, "fort": 3,
          "ref": 7, "will": 2, "initiative": 5, "cmb": 4, "cmd": 19, "pool:ki": 3, "ac:1": 17, "ac:2": 15,
          "attention": 1, "load": 2, "balance_max": 0, "temp_hp": 0}
S.case("s-totals", "owner 1A: hand totals of the sample (hp 11 + 3 = 14, mana 8, spirit 15, melee 5, fort 3, AC 17 / "
       "15 ...)", EXPECT)(lambda: {n: total(SAMPLE, n) for n in EXPECT})
S.case("s-no-remainder", "pkg 34: no hidden remainder rows (ac_other / speed_other / floor) in the sample",
       [])(lambda: [(n, r["id"]) for n in src.NUMBERS + ("pool:ki", "ac:1", "ac:4", "ac:8") for r in sv(SAMPLE, n)["rows"]
                    if r["id"] in ("ac_other", "speed_other", "floor")])
S.case("s-sum", "owner 1A: for EVERY number the counted rows add up to the total (also speed and every AC cell)",
       [])(lambda: [n for n in src.NUMBERS + ("pool:ki",) + tuple("ac:%d" % c for c in (1, 2, 3, 4, 6, 7, 8, 9))
                    if summed(SAMPLE, n) != total(SAMPLE, n)])
S.case("s-real", "owner 1A: the total is the sheet's own number (resources view hp max 14, mana max 8, sheet melee 5)",
       (14, 8, 5))(lambda: (lambda r, sh: (r["hp"]["max"], r["mana"]["max"], sh["attack_melee"]["total"]))(
           *[vw.VIEWS[v](SAMPLE) for v in ("resources", "sheet")]))
S.case("s-rows", "owner 1A: rows name their kind; a derived row names its rule; the off row is shown, not counted",
       (("hit_dice", "rule", True, "progression.md"), ("bless", "effect", False), ("old", "manual", False, False)))(
    lambda: (lambda rows: ((rows[0]["id"], rows[0]["kind"], rows[0]["derived"], rows[0]["rule"]),
                           (rows[3]["id"], rows[3]["kind"], rows[3]["derived"]),
                           (rows[4]["id"], rows[4]["kind"], rows[4]["on"], rows[4]["counted"])))(
        sv(SAMPLE, "hp_max")["rows"]))
S.case("s-stacking", "buffs.md: two morale bonuses to saves: only +2 counts (+1 shown as not counted)",
       [(1, False), (2, True)])(
    lambda: [(r["value"], r["counted"]) for r in sv(SAMPLE, "fort")["rows"] if r["id"] == "bless"])


# ---------------------------------------------------------------- 1A editing: commands, journal, undo, read-only
def _edit():
    c = hero()
    a = run(c, ("source_add", {"number": "hp_max", "name": "Toughness", "value": 3}))
    b = run(a, ("source_edit", {"sid": "toughness", "value": 5}))
    off = run(b, ("source_toggle", {"sid": "toughness", "on": False}))
    gone = run(b, ("source_remove", {"sid": "toughness"}))
    return (total(c, "hp_max"), total(a, "hp_max"), total(b, "hp_max"), total(off, "hp_max"), total(gone, "hp_max"),
            [e.command for e in run(c, ("source_add", {"number": "hp_max", "name": "T", "value": 1})).log][-1:])


S.case("e-commands", "owner 1A: hp 11; add +3 -> 14; edit to 5 -> 16; switched off -> 11; removed -> 11; a journal line",
       (11, 14, 16, 11, 11, ["source_add"]))(_edit)


def _session():
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    s.new("Hero", hero())
    refused = s.dispatch("source_add", number="mana_max", name="Mage", value=8)
    s.set_editor_mode(True)
    s.dispatch("source_add", number="mana_max", name="Mage", value=8)
    on = s.view("resources")["mana"]["max"], s.view("sources", number="mana_max")["editable"]
    s.undo()
    s.set_editor_mode(False)
    return refused.reason, on, s.view("resources")["mana"]["max"], s.view("sources", number="mana_max")["editable"]


S.case("e-session", "owner 1A: outside the editor mode the edit is refused; in it mana 0 -> 8 (editable); undo -> 0; "
       "read-only again", ("editor_mode_needed", (8, True), 0, False))(_session)
S.case("e-refusals", "pkg 34: temp HP sources are read-only; an unknown number, an empty name, an unknown row refused",
       ("sources_read_only", "unknown_number", "source_name_needed", "not_found"))(
    lambda: (ref(lambda: dispatch(hero(), "source_add", number="temp_hp", name="x", value=1)),
             ref(lambda: dispatch(hero(), "source_add", number="luck", name="x", value=1)),
             ref(lambda: dispatch(hero(), "source_add", number="hp_max", name=" ", value=1)),
             ref(lambda: dispatch(hero(), "source_edit", sid="zz", value=1))))
S.case("e-not-stored", "owner 1A: the derived total is never stored: a row stores only its own value; save / load "
       "keeps the rows", (False, True))(
    lambda: ("hp_max" in {f.name for f in dataclasses.fields(Character)},
             cio.loads(cio.dumps(SAMPLE)) == SAMPLE))
S.case("e-mana-q224", "owner (Q224 closed): mana max is never typed: no plain-number command, only source rows",
       ("unknown_command", "unknown_command"))(
    lambda: (ref(lambda: dispatch(hero(), "set_max", resource="mana", value=8)),
             ref(lambda: dispatch(hero(), "set_mana_max", value=8))))
S.case("e-derived-override", "owner 1A: a derived row is corrected by a manual row: spirit 15 + (-5) = 10",
       10)(lambda: total(run(hero(), ("source_add", {"number": "spirit_max", "name": "Curse", "value": -5})),
                         "spirit_max"))


# ---------------------------------------------------------------- 1B attack numbers (combat.md)
def att(ch, kind):
    with rd.using(ch):
        return vw.VIEWS["sheet"](ch)["attack_" + kind]["total"]


S.case("a-numbers", "combat.md: melee 2 + 2 = 4, ranged 2 + 5 = 7; pain 1 -> 3 / 6; morale 4 out of combat 4, in "
       "combat 4 + 2 = 6", (4, 7, 3, 6, 4, 6))(
    lambda: (att(hero(), "melee"), att(hero(), "ranged"), att(hero(pain=(PainEntry(1),)), "melee"),
             att(hero(pain=(PainEntry(1),)), "ranged"), att(hero(morale_scale=4), "melee"),
             att(hero(morale_scale=4, in_combat=True), "melee")))
S.case("a-source", "combat.md: melee from Dex + BAB -> 7; a manual row +1 on melee -> 8, switched off -> 7",
       (7, 8, 7))(
    lambda: (lambda c: (att(c, "melee"),
                        att(run(c, ("source_add", {"number": "attack_melee", "name": "x", "value": 1})), "melee"),
                        att(run(c, ("source_add", {"number": "attack_melee", "name": "x", "value": 1}),
                                ("source_toggle", {"sid": "x", "on": False})), "melee")))(
        run(hero(), ("set_attack_source", {"kind": "melee", "source": "dex"}))))


# ---------------------------------------------------------------- 1B load borders (gear.md: Str 14 -> 79 / 129 L)
def _cat(weight):
    with rd.using(hero()):
        return vw.VIEWS["items"](hero(items=(Item("b", "bag", weight_l=weight),)))["load"]["category"]


S.case("l-borders", "gear.md: 79 light, 80 load (heavy), 129 load, 130 overload", ("light", "heavy", "heavy",
                                                                                  "overload"))(
    lambda: tuple(_cat(w) for w in (79, 80, 129, 130)))
S.case("l-sources", "pkg 34: load sources: Str mod 2 + a manual load_mod row 1 = 3 -> limits of Str mod 3",
       (3, True))(
    lambda: (lambda c: (total(c, "load"), vw.VIEWS["items"](c)["load"]["heavy_max_l"] >
                        vw.VIEWS["items"](hero())["load"]["heavy_max_l"]))(
        run(hero(), ("source_add", {"number": "load", "name": "Belt", "value": 1}))))

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
