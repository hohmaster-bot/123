"""Package 38 P5 (owner decision 9, D37; closes Q276): the effect editor, Qt-free. A character carrier changes only by
the commands effect_add / effect_change / effect_remove (journal, undo); a catalog entry is saved to its user file
with its module tag; invalid input is never saved. Numbers by hand: hero every stat 10, level 1.
Run: python Wp_claude/tests/model/test_pkg38c.py"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import effect_editor as ee  # noqa: E402
from wp.app import views as vw  # noqa: E402
from wp.app.session import Session  # noqa: E402
from wp.catalog import store as cs  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import effect_form as ef  # noqa: E402
from wp.model.character import Character, Feat, Item  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_pkg38c")
TMP = tempfile.mkdtemp(prefix="wp38c_")


def hero():
    return Character(feats=(Feat("brave", "Brave"),), items=(Item("ring", "Ring"),))


def run(ch, *steps):
    for n, p in steps:
        ch = dispatch(ch, n, **p).state
    return ch


def ref(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "no refusal"


def attack(ch):
    with rd.using(ch):
        return dv.total(ch, bo.ATTACK)


def comfort_max(ch):
    with rd.using(ch):
        return dv.comfort_pool(ch).max


PLUS2 = {"target": "attack", "value": "2"}
add2 = ("effect_add", {"collection": "feats", "oid": "brave", "form": PLUS2})

# attack bonus 0 -> +2 -> back to 0
S.case("add-remove", "decision 9: +2 attack added to a feat: attack bonus 0 -> 2; removed -> 0",
       (0, 2, 0))(lambda: (attack(hero()), attack(run(hero(), add2)),
                           attack(run(hero(), add2, ("effect_remove", {"collection": "feats", "oid": "brave",
                                                                       "index": 0})))))
# comfort max = base 5 + 5 x level 1 = 10; base replaced by 20 -> 20 + 5 = 25
S.case("replace-const", "decision 9: replace a rule constant: comfort max base 5 -> 20: max 10 -> 25", (10, 25))(
    lambda: (comfort_max(hero()), comfort_max(run(hero(), ("effect_add", {
        "collection": "feats", "oid": "brave",
        "form": {"target": "const:training.comfort_max_base", "value": "20", "mode": "replace"}})))))
S.case("change", "decision 9: change the effect +2 -> formula level + 3 = 4 at level 1", 4)(
    lambda: attack(run(hero(), add2, ("effect_change", {"collection": "feats", "oid": "brave", "index": 0,
                                                        "form": {"target": "attack", "value": "level + 3"}}))))
S.case("item-tab", "decision 9: an item effect goes to the chosen tab (activated)", ((), 1))(
    lambda: (lambda c: (c.items[0].effects_off, len(c.items[0].effects_on)))(
        run(hero(), ("effect_add", {"collection": "items", "oid": "ring", "field": "effects_on", "form": PLUS2}))))


def _refusals():
    c = hero()
    out = []
    for form in ({"target": "attack", "value": "2 +"}, {"target": "nowhere", "value": "1"},
                 {"target": "attack", "value": ""}, {"target": "attack", "value": "1", "mode": "replace"},
                 {"target": "attack", "value": "1", "scope": "melee"}, {"target": "attack", "value": "1",
                                                                       "condition": "full_moon"},
                 {"target": "attack", "value": "1", "btype": "magic"}, {"target": "const:no.such", "value": "1"}):
        out.append(ref(lambda f=form: dispatch(c, "effect_add", collection="feats", oid="brave", form=f)))
    return out


S.case("refused", "decision 9: invalid input is refused with a reason and nothing is saved",
       ["bad_effect_formula", "unknown_effect_target", "effect_value_needed", "replace_const_only",
        "scope_not_allowed", "unknown_condition", "unknown_bonus_type", "unknown_effect_target"])(_refusals)
S.case("accepted-kinds", "decision 9: a scope on damage_per_pain, a prefix target with its id, an existing condition "
       "kind and a situational note are accepted", ("melee", "stat:str", "pressure_ge:3&in_combat", "vs giants"))(
    lambda: (ef.build({"target": "damage_per_pain", "value": "1", "scope": "melee"}).scope,
             ef.build({"target": "stat:str", "value": "2"}).target,
             ef.build({"target": "attack", "value": "1", "condition": "pressure_ge:3&in_combat"}).condition,
             ef.build({"target": "save", "value": "2", "situational": "vs giants"}).situational))
S.case("targets", "decision 9: the target list is the view effect_targets: the core roll targets, the sheet targets, "
       "every rule constant; searchable", (True, True, True, ("const:comfort.fight_cap",)))(
    lambda: (lambda t: ("attack" in t, "hp_max" in t, len([x for x in t if x.startswith("const:")]) ==
                        len(rd.numeric_ids()), ef.search("FIGHT_CAP")))(vw.effect_targets(hero())))


def _undo():
    d = tempfile.mkdtemp(dir=TMP)
    s = Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    s.new("Hero", hero())
    r = ee.apply(s, "add", "feats", "brave", form=PLUS2)
    after = attack(s.character), s.character.log[-1].command
    s.undo()
    return r.ok, after, attack(s.character)


S.case("undo", "decision 9: the change is a journaled command; undo -> attack 2 back to 0", (True, (2, "effect_add"), 0))(
    _undo)


def _catalog():
    d = tempfile.mkdtemp(dir=TMP)
    s = Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    bad = ee.catalog_apply(s, "feats", "toughness", "add", form={"target": "attack", "value": "1 +"})
    ok = ee.catalog_apply(s, "feats", "toughness", "add", form={"target": "save:fort", "value": "1"})
    s2 = Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    effects = [(e.target, e.value) for e in ee.catalog_effects(s2, "feats", "toughness")]
    path = cs.user_path(os.path.join(d, "user", "catalogs"), "feats")
    saved = next(e for e in json.load(open(path, encoding="utf-8"))["entries"] if e["id"] == "toughness")
    shipped = [e for e in cs.load_shipped("feats").entries if e["id"] == "toughness"][0]
    return (bad.ok, bad.reason, ok.ok, effects, saved.get("module"), len(shipped["effects"]))


S.case("catalog", "decision 9: a catalog edit round trip: a bad formula refused (nothing saved); +1 Fort added to the "
       "Toughness entry, saved to the user file with its module tag, read back after a restart; the shipped file is "
       "unchanged", (False, "bad_effect_formula", True, [("hp_max", "max(3, level)"), ("save:fort", 1)], "core", 1))(
    _catalog)

if __name__ == "__main__":
    sys.exit(S.run())
