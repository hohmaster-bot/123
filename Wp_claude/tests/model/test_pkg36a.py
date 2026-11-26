"""Package 36 P1.2 (owner decision 17, closes Q245): an unknown bonus type is untyped (it stacks with everything) and
the AC / attack / save views never raise; P1.4 the notebook commands the Narrative tab uses.
Hero: Dex 14 (+2), others 10; bab 0. AC = 10 + Dex 2 = 12. Run: python Wp_claude/tests/model/test_pkg36a.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import views as vw  # noqa: E402
from wp.commands import dispatch  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.model.character import ABILITIES, Ability, Character, Feat  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_pkg36a")


def hero(**kw):
    return Character(abilities={a: Ability(base=14 if a == "dex" else 10) for a in ABILITIES}, **kw)


def views(ch, *names):
    with rd.using(ch):
        return {n: vw.VIEWS[n](ch) for n in names}


TYPO = Status("Typo", sid="typo", active=True, effects=(Effect("ac", 1, "moral"), Effect("ac", 2, "moral"),
                                                        Effect("save", 3, "untyped"), Effect("attack_melee", 1, "magic")))


def _status():
    ch = dispatch(hero(), "add_status", status=TYPO, active=True).state
    v = views(ch, "defense", "sheet", "attacks")
    return v["defense"]["cells"]["2"]["full"], v["sheet"]["stats"]["fort"].total, v["sheet"]["attack_melee"]["total"]


S.case("u-status", "decision 17: 'moral' / 'untyped' / 'magic' are untyped: AC 12 + 1 + 2 = 15 (both count), Fort 0 + 3 "
       "= 3, melee 0 + 1 = 1; no exception", (15, 3, 1))(_status)


def _entry():
    feat = Feat("lucky", "Lucky", effects=(Effect("ac", 1, "luk"), Effect("ac", 1, "luk")))
    ch = dispatch(hero(), "add_entry", collection="feats", record=feat).state
    return views(ch, "defense")["defense"]["cells"]["2"]["full"]


S.case("u-entry", "decision 17: a feat added by add_entry with the typo 'luk' twice: untyped, both count: 12 + 2 = 14",
       14)(_entry)


def _narrative():
    c = hero()
    c = dispatch(c, "add_note", kind="court", name="Court of Ash").state
    cid = c.courts[0].cid
    c = dispatch(c, "add_note", kind="quest", name="Find the bell", text="North tower", giver=cid).state
    qid = c.quests[0].qid
    c = dispatch(c, "edit_entry", collection="quests", oid=qid, done=True).state
    c = dispatch(c, "add_note", kind="quirk", name="Ash eyes", text="sees embers").state
    c = dispatch(c, "burn_quirk", kid=c.quirks[0].kid, burned=True).state
    return c.quests[0].done, c.quests[0].giver == cid, c.quests[0].text, c.quirks[0].burned


S.case("n-commands", "narrative.md: a court quest (giver = the court) is added, closed by edit_entry; a quirk burned",
       (True, True, "North tower", True))(_narrative)

if __name__ == "__main__":
    sys.exit(S.run())
