"""Package 38 P3 (owner decisions 6, 7): rerolls as a resource-like list. Any carrier grants reroll charges with a
recharge rule; the view lists name, source, left / max; spend_reroll spends one (journal, undo); rests and combat
events refill by the rule. Mordon type 5: its own reroll charge (1, long rest), separate from the -4 counter (5).
Numbers by hand from the owner decisions (RULES/buffs.md "Rerolls"). Hero: every stat 10, training 2000.
Run: python Wp_claude/tests/model/test_pkg38b.py"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import session as sm  # noqa: E402
from wp.app import views as vw  # noqa: E402
from wp.catalog import store as cs  # noqa: E402
from wp.catalog.convert import item_from_entry, status_from_entry  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core.rerolls import Reroll, from_data  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.model.notebook import Quirk  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg38b")
TMP = tempfile.mkdtemp(prefix="wp38b_")
RACES = {e["id"]: json.loads(json.dumps(e)) for e in cs.load_shipped("races").entries}
REF = "feat:goddess_of_humanity:ally_reroll"


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


def mordon5():
    c = run(Character(training=2000), ("take_race", {"race": RACES["mordon"]}))
    return run(c, ("buy_race_ability", {"aid": "goddess_of_humanity"}))


def left(ch, r=REF):
    return next(row[4] for row in vw.rerolls(ch) if row[0] == r)


def counter(ch):
    f = next(f for f in ch.feats if f.fid == "goddess_of_humanity")
    return f.usage.charges_current, f.usage.charges_max


# ---------------------------------------------------------------- Mordon type 5 (decision 6)
S.case("m5-row", "decision 6: Mordon type 5 has its own reroll: 1 of 1, long rest, from the history ability",
       (REF, "feat:goddess_of_humanity", 1, 1, "long_rest"))(
    lambda: (lambda row: (row[0], row[1], row[4], row[5], row[6]))(vw.rerolls(mordon5())[0]))


def _spend():
    c = mordon5()
    used = run(c, ("spend_reroll", {"ref": REF}))
    short = run(used, ("short_rest", {}))
    long_ = run(used, ("long_rest", {}))
    fight = run(used, ("start_combat", {}))
    return (left(used), counter(used), ref(lambda: dispatch(used, "spend_reroll", ref=REF)), left(short),
            left(long_), left(fight))


# spend 1 -> 0 left; the -4 counter stays 5 / 5; a second spend refused; the short rest keeps 0; the long rest -> 1;
# a combat start does not refill it (its rule is the long rest)
S.case("m5-spend", "decision 6: spend -> 0 left, the -4 counter untouched (5 of 5); none left -> refused; short rest "
       "keeps 0; long rest -> 1; combat start keeps 0", (0, (5, 5), "no_reroll_left", 0, 1, 0))(_spend)


def _counter_apart():
    c = run(mordon5(), ("start_combat", {}), ("spend_charge", {"owner_kind": "feat", "owner_id": "goddess_of_humanity"}))
    return counter(c), left(c)


S.case("m5-apart", "decision 6: spending the -4 counter (5 -> 4) leaves the reroll at 1", ((4, 5), 1))(_counter_apart)


# ---------------------------------------------------------------- any carrier (decision 7)
ITEM = {"id": "lucky_coin", "name": "Lucky coin", "kind": "misc",
        "rerolls": [{"id": "coin", "name": "Coin flip", "charges": 2, "recharge": "short_rest"}]}


def _item():
    c = Character(items=(item_from_entry(ITEM, "coin1"),))
    row = vw.rerolls(c)[0]
    used = run(c, ("spend_reroll", {"ref": row[0]}), ("spend_reroll", {"ref": row[0]}))
    return row[:6], left(used, row[0]), left(run(used, ("short_rest", {})), row[0])


S.case("item-source", "decision 7: a reroll from an item shows its source: Coin flip from Lucky coin, 2 of 2; two spent "
       "-> 0; the short rest -> 2", (("item:coin1:coin", "item:coin1", "Lucky coin", "Coin flip", 2, 2), 0, 2))(_item)


def _carriers():
    st = status_from_entry({"id": "fortune", "name": "Fortune", "rerolls": [{"charges": 1, "recharge": "manual"}]},
                           sid="fortune")
    q = Quirk("lucky", "Lucky", rerolls=from_data([{"id": "q", "charges": 1, "recharge": "combat_start"}]))
    c = Character(quirks=(q,))
    off = run(c, ("add_status", {"status": st}))
    on = run(c, ("add_status", {"status": st, "active": True}))
    return [r[0] for r in vw.rerolls(off)], [r[0] for r in vw.rerolls(on)]


S.case("carriers", "decision 7: a quirk and an ACTIVE status carry rerolls too (an inactive status shows none)",
       (["quirk:lucky:q"], ["status:fortune:reroll_1", "quirk:lucky:q"]))(_carriers)


def _manual():
    c = Character(quirks=(Quirk("gm", "GM gift", rerolls=(Reroll("g", "Gift", 1, 1, "manual"),)),))
    used = run(c, ("spend_reroll", {"ref": "quirk:gm:g"}))
    rested = run(used, ("long_rest", {}), ("start_combat", {}), ("end_combat", {}))
    return left(used, "quirk:gm:g"), left(rested, "quirk:gm:g"), \
        left(run(rested, ("restore_reroll", {"ref": "quirk:gm:g"})), "quirk:gm:g")


S.case("manual", "decision 7: a manual reroll comes back only by hand: 0 after rests and a combat, restore -> 1",
       (0, 0, 1))(_manual)
def _bad():
    try:
        from_data([{"recharge": "sunday"}])
    except ValueError:
        return "ValueError"
    return "accepted"


S.case("bad-rule", "decision 7: a recharge rule must come from the existing list", "ValueError")(_bad)


S.case("unknown-ref", "decision 7: an unknown reroll is refused (not_found)", "not_found")(
    lambda: ref(lambda: dispatch(mordon5(), "spend_reroll", ref="feat:goddess_of_humanity:nope")))


def _undo():
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    s.new("Hero", mordon5())
    s.dispatch("spend_reroll", ref=REF)
    after = left(s.character), s.character.log[-1].command
    s.undo()
    return after, left(s.character)


S.case("undo", "decision 7: spend_reroll is journaled; undo -> 0 back to 1", ((0, "spend_reroll"), 1))(_undo)


def _roundtrip():
    used = run(mordon5(), ("spend_reroll", {"ref": REF}))
    p = os.path.join(TMP, "m5.json")
    cio.save(used, p)
    return left(cio.load(p))


S.case("save-load", "decision 7: the count left is a stored base value: 0 survives save / load", 0)(_roundtrip)

if __name__ == "__main__":
    sys.exit(S.run())
