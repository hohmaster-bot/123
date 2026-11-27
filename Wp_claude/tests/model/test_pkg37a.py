"""Package 37 P1: the universal mechanisms (owner decisions 1, 2, 5): rule constants as effect targets const:<id>,
catalog trainings (kind trainings), the held-by links both ways and the link command, the level offsets of the comfort
exchange and Attention, damage_per_pain with a scope, BP restored only by the long rest. Numbers by hand from RULES
(training.md: comfort rate 5 + 5 x level; narrative.md: Attention 1 + level / 3) and the owner decisions.
Hero: every stat 10, level 1, training 2000. Run: python Wp_claude/tests/model/test_pkg37a.py"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import session as sm  # noqa: E402
from wp.app import views as vw  # noqa: E402
from wp.catalog import store as cs  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core.effects import Effect  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import body_view as bv  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import links  # noqa: E402
from wp.model import sources as src  # noqa: E402
from wp.model.character import AttackRecord, Character, Feat, Item  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_pkg37a")
TMP = tempfile.mkdtemp(prefix="wp_p37a_")
RATE = "training.comfort_rate_base"


def hero(**kw):
    base = dict(training=2000, comfort_current=5)
    base.update(kw)
    return Character(**base)


def feat(fid, *effects, **kw):
    return Feat(fid, fid.title(), effects=tuple(effects), **kw)


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


def gain(ch):
    return run(ch, ("exchange_comfort", {"n": 1})).training - ch.training


# ---------------------------------------------------------------- 1.1 const:<id> (decision 1)
def _const():
    plain = hero()
    add = hero(feats=(feat("x", Effect("const:" + RATE, 50)),))
    repl = hero(feats=(feat("y", Effect("const:" + RATE, 3, note="replace")),))
    gone = run(add, ("remove_entry", {"collection": "feats", "oid": "x"}))
    v = src.view(add, "const:" + RATE)
    typo = hero(feats=(feat("z", Effect("const:training.comfort_rat_base", 50)),))
    return (gain(plain), gain(add), gain(repl), gain(gone), (v["total"], [(r["id"], r["value"]) for r in v["rows"]]),
            (gain(typo), src.view(typo, "const:training.comfort_rat_base")["warning"]))


# comfort rate at level 1 = 5 + 5 x 1 = 10; base 5 + 50 = 55 -> 60; replaced by 3 -> 3 + 5 = 8; removed -> 10
S.case("k-const", "decision 1: comfort rate 5 + 5 = 10 training per comfort; +50 to the base -> 60; base replaced by 3 "
       "-> 8; the source removed -> 10; the Sources view lists the table value and the effect; a typo id changes "
       "nothing and the view warns", (10, 60, 8, 10, (55, [("const_default", 5), ("const:x", 50)]),
                                      (10, "unknown_constant")))(_const)


def _manual():
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    s.new("Hero", hero())
    s.set_editor_mode(True)
    r = s.dispatch("source_add", number="const:" + RATE, name="House rule", value=7)
    return r.ok, rd.const(RATE, s.character), s.view("sources", number="const:" + RATE)["editable"]


S.case("k-manual", "decision 1: a manual source row on a constant (editor mode): 5 + 7 = 12", (True, 12, True))(_manual)
S.case("k-targets", "decision 1: the effect targets list is generated from the rule data (every numeric constant)",
       (True, True))(lambda: (lambda t: ("const:" + RATE in t, len([x for x in t if x.startswith("const:")]) ==
                                         len(rd.numeric_ids())))(vw.VIEWS["effect_targets"](hero())))

# ---------------------------------------------------------------- 1.2 catalog trainings (decision 2)
RACES = {e["id"]: json.loads(json.dumps(e)) for e in cs.load_shipped("races").entries}
TRAIN = {e["id"]: json.loads(json.dumps(e)) for e in cs.load_shipped("trainings").entries}
LIMITED = dict(TRAIN["ragmal_mana"], id="limited", limit=2, unlock="")


def _ragmal():
    r = run(hero(), ("take_race", {"race": RACES["ragmal"]}))
    a = run(r, ("buy_training", {"training": TRAIN["ragmal_mana"], "units": 3}))
    v = src.view(a, "mana_max")
    row = [(x["id"], x["value"]) for x in v["rows"] if x["id"].startswith("training")]
    return (dv.mana_pool(r).max, dv.mana_pool(a).max, 2000 - a.training, a.trainings[0].units, row,
            ref(lambda: dispatch(hero(), "buy_training", training=TRAIN["ragmal_mana"])))


# 3 units x 200 = 600 training; mana 6 + 3 = 9; one source row "training:ragmal_mana" +3
S.case("t-ragmal", "decision 2: Ragmal mana training (unlocked by Magic body): 3 units = 600 training, mana 6 -> 9, one "
       "source row +3; a hero without the ability: locked", (6, 9, 600, 3, [("training:ragmal_mana", 3)],
                                                            "training_locked"))(_ragmal)
S.case("t-limit", "decision 2: limit 2: 2 units allowed, a third refused (training_limit)", (2, "training_limit"))(
    lambda: (lambda a: (a.trainings[0].units, ref(lambda: dispatch(a, "buy_training", training=LIMITED))))(
        run(hero(), ("buy_training", {"training": LIMITED, "units": 2}))))


def _undo():
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    s.new("Hero", hero())
    s.dispatch("take_race", race=RACES["ragmal"])
    s.dispatch("buy_training", training=TRAIN["ragmal_mana"], units=3)
    after = s.character.training, dv.mana_pool(s.character).max
    s.undo()
    rows = [(r[0], r[6]) for r in s.view("trainings")]
    return after, (s.character.training, dv.mana_pool(s.character).max), rows


S.case("t-undo", "decision 2: undo the purchase: training 1400 -> 2000, mana 9 -> 6; the view lists the training as "
       "open for the Ragmal", ((1400, 9), (2000, 6), [("ragmal_mana", True)]))(_undo)


# ---------------------------------------------------------------- 1.3 links both ways (decision 5)
def _links():
    c = hero(items=(Item("ring", "golden ring"),),
             feats=(feat("parent"), feat("child", held_by="feat:parent"), feat("gem", held_by="item:ring")))
    v = links.view(c)
    gone = run(c, ("remove_entry", {"collection": "feats", "oid": "parent"}))
    relinked = run(gone, ("set_held_by", {"collection": "feats", "oid": "child", "holder": "item:ring"}))
    return ([n for _c, _o, n in v["feat:parent"]["holds"]], [n for _c, _o, n in v["item:ring"]["holds"]],
            links.view(gone)["feat:child"]["backed"], links.view(relinked)["feat:child"]["backed"],
            sorted(n for _c, _o, n in links.view(relinked)["item:ring"]["holds"]),
            ref(lambda: dispatch(c, "set_held_by", collection="feats", oid="child", holder="feat:nobody")),
            ref(lambda: dispatch(c, "set_held_by", collection="feats", oid="child", holder="feat:child")))


S.case("l-both-ways", "decision 5: the parent holds Child, the ring holds Gem; the parent removed -> Child not backed; "
       "relinked to the ring -> backed, the ring holds Child and Gem; a missing holder and self are refused",
       (["Child"], ["Gem"], False, True, ["Child", "Gem"], "not_found", "bad_holder"))(_links)


# ---------------------------------------------------------------- 1.4 the missing targets
def _lomit():
    c = hero(level=2, hp_rolls=(8, 8))
    a = hero(level=2, hp_rolls=(8, 8), feats=(feat("adaptation", Effect("const:training.comfort_exchange_level_offset", 1),
                                                    Effect("const:attention.level_offset", 1)),))
    return gain(c), gain(a), dv.attention_per_cycle(c), dv.attention_per_cycle(a)


# level 2: rate 5 + 5 x 2 = 15; one level higher: 5 + 5 x 3 = 20; Attention 1 + 2 / 3 = 1; one level higher: 1 + 3 / 3 = 2
S.case("x-lomit", "Lomit Adaptation: comfort exchange at level 2 = 15, counted one level higher = 20; Attention 1 -> 2",
       (15, 20, 1, 2))(_lomit)


def _rage():
    c = hero(pain=(PainEntry(3, "wound"),), attacks=(AttackRecord("u", "unarmed", "unarmed"),),
             feats=(feat("rage", Effect("damage_per_pain", 1, scope="melee")),))
    lines = dict((x.label, x.value) for x in av.attack(c, c.attacks[0]).damage_lines)
    return bv.damage_per_pain(c, "melee"), bv.damage_per_pain(c, "ranged"), dv.pain_profile(c).damage_per_pain, \
        lines.get("pain: race bonus")


S.case("x-rage", "Ulstanger Rage melee only: +1 per pain for melee, 0 for ranged; the unarmed (melee) attack with pain 3 "
       "gets +3", (1, 0, 0, 3))(_rage)


def _adrenaline():
    c = hero(bp_current=2)
    spent = run(c, ("spend_bp", {"n": 2, "restore_only": "long_rest"}))
    short = run(spent, ("short_rest", {}))
    plain = run(run(c, ("spend_bp", {"n": 2})), ("short_rest", {}))
    long_ = run(spent, ("long_rest", {}))
    return dv.bp_pool(c).max, spent.bp_long_rest_only, short.bp_current, plain.bp_current, \
        (long_.bp_current, long_.bp_long_rest_only)


# BP max 2: 2 spent for adrenaline; the short rest gives +1 to others but not these (0); a plain spend: 0 + 1 = 1
S.case("x-adrenaline", "Adrenaline: 2 BP spent with restore_only long_rest: the short rest leaves them (0, a plain "
       "spend gets 1 back); the long rest restores all (2) and clears the mark", (2, 2, 0, 1, (2, 0)))(_adrenaline)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
