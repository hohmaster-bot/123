"""Group C: two-weapon fighting (RULES/combat.md). Run: python Wp_claude/tests/model/test_twf.py

Hero: level 5, BAB 5, Str 16 (+3), no mastery nodes (no group bonuses), in combat, morale 0.
Without the combination: sword record to hit 5 + 3 = 8; every off-hand record also 8 (basic group, no penalty).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from dataclasses import replace  # noqa: E402

from wp.catalog import feats_catalog as fc  # noqa: E402
from wp.catalog import weapons_catalog as wc  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import twf  # noqa: E402
from wp.model.character import Ability, AttackRecord, Character, Feat, Item  # noqa: E402

S = Suite("test_twf")
CAT = wc.load_default()


def abil():
    a = dict(Character().abilities)
    a["str"] = Ability(16)
    return a


SWORD = Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("blades",))
DAGGER = replace(wc.make_item(CAT, "dagger", "dg"), in_hands=True)        # finesse = light
CLUB = replace(wc.make_item(CAT, "club", "cl"), in_hands=True)            # not light
# double weapon; the second row is changed to 1d3/1d4 so the test sees which row the off end uses
STAFF = replace(wc.make_item(CAT, "quarterstaff", "qs"), in_hands=True, damage_small2="1d3", damage_medium2="1d4")
TWF_FEAT = Feat("two_weapon_fighting", flags=(twf.TWF_FLAG,))


def hero(off_item, feat=False, statuses=()):
    recs = (AttackRecord("main", "sw", "blades", "one", twf=True, twf_off="off"),
            AttackRecord("off", off_item.iid, "basic_simple", "off"))
    return Character(level=5, bab=5, abilities=abil(), in_combat=True, items=(SWORD, off_item),
                     attacks=recs, feats=(TWF_FEAT,) if feat else (), statuses=statuses)


def hits(ch, rid="main"):
    c = twf.combination(ch, rid)
    return (c.main.to_hit, c.off.to_hit)


# The four table rows (primary / off): 8 - penalty.
S.case("row-normal", "combat.md table: normal -6/-10 -> 8-6, 8-10", (2, -2))(lambda: hits(hero(CLUB)))
S.case("row-light", "combat.md table: off hand light -4/-8", (4, 0))(lambda: hits(hero(DAGGER)))
S.case("row-feat", "combat.md table: TWF feat -4/-4", (4, 4))(lambda: hits(hero(CLUB, feat=True)))
S.case("row-light-feat", "combat.md table: light + TWF feat -2/-2", (6, 6))(lambda: hits(hero(DAGGER, feat=True)))
S.case("penalties-table", "combat.md table as numbers", ((-6, -10), (-4, -8), (-4, -4), (-2, -2)))(
    lambda: tuple(twf.penalties(l, f) for l, f in ((False, False), (True, False), (False, True), (True, True))))


# Unarmed off-hand strike is always light: sword + unarmed -> -4/-8. The unarmed card is made NOT finesse
# here on purpose, so the test proves the rule "unarmed is always light" and not the card flag.
@S.case("unarmed-light", "combat.md: an unarmed strike is always light", (-4, -8, True))
def _unarmed():
    card = replace(wc.make_item(CAT, "unarmed_combat", "unarmed"), finesse=False)
    ch = Character(level=5, bab=5, abilities=abil(), items=(SWORD, card),
                   attacks=(AttackRecord("main", "sw", "blades", "one"), AttackRecord("u", "unarmed", "unarmed_combat", "off")))
    ch = dispatch(ch, "set_twf", rid="main", off="u").state
    c = twf.combination(ch, "main")
    return (c.main_penalty, c.off_penalty, c.light_off)


# Double weapon: the other end counts as light -> -4/-8 without the feat. Main end Str one-hand 3,
# other end off-hand Str 3 * 0.5 = 1, second damage row.
@S.case("double-light", "combat.md: double weapon, off end as light; second row; off-hand Str",
        (-4, -8, 3, 1, ("1d3", "1d4")))
def _double():
    ch = Character(level=5, bab=5, abilities=abil(), items=(STAFF,),
                   attacks=(AttackRecord("q", "qs", "basic_simple", "two"),))
    ch = dispatch(ch, "set_twf", rid="q").state
    c = twf.combination(ch, "q")
    return (c.main_penalty, c.off_penalty, c.main.damage, c.off.damage, c.off.dice)


# Class/race reduction effect: light + feat (-2/-2) with reduction 1 -> -1/-1; reduction 5 -> 0/0 (never a bonus).
def _red(n):
    return Status("trained hands", effects=(Effect(twf.REDUCTION, n),))


S.case("reduction-1", "owner: reduction lowers the penalty", (7, 7))(
    lambda: hits(hero(DAGGER, feat=True, statuses=(_red(1),))))
S.case("reduction-not-bonus", "owner: penalty never below 0, never a bonus", (8, 8))(
    lambda: hits(hero(DAGGER, feat=True, statuses=(_red(5),))))

# A record without the toggle gets no two-weapon penalty: 8.
S.case("no-toggle-no-penalty", "combat.md: no combination -> no penalty", 8)(
    lambda: av.by_record(replace(hero(CLUB), attacks=(AttackRecord("main", "sw", "blades", "one"),)), "main").to_hit)


def rejected(fn):
    try:
        fn()
    except (CommandError, ValueError, KeyError):
        return "rejected"
    return "allowed"


S.case("toggle-needs-two", "combat.md: toggle only with two weapons in the hands or a double weapon", "rejected")(
    lambda: rejected(lambda: dispatch(Character(items=(SWORD,), attacks=(AttackRecord("main", "sw", "blades"),)),
                                      "set_twf", rid="main")))
S.case("marks-main-off", "owner: the view marks the main and the off-hand attack", ("main", "off"))(
    lambda: (lambda c: (c.main.record, c.off.record))(twf.combination(hero(DAGGER), "main")))
S.case("feat-in-catalog", "owner: feat Two-Weapon Fighting in the catalog, 200 by default", (200, ("twf",)))(
    lambda: (lambda t: (t.cost, t.flags))(fc.load_default().get("two_weapon_fighting")))

if __name__ == "__main__":
    sys.exit(S.run())
