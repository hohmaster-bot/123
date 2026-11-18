"""Package 6: item HP (gear.md, weapons.md). Run: python Wp_claude/tests/model/test_pkg6.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import ac as acm  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import items as itm  # noqa: E402
from wp.model.character import SHIELD, Character, Item  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg6")


def sword(**kw):
    base = dict(kind="weapon", hands=1, in_hands=True, groups=("blades",), hp=10, enchant=3, activation_day=1)
    base.update(kw)
    return Item("sw", "sword", **base)


def ch_with(*items, **kw):
    return Character(items=items, spirit_current=5, hp_rolls=(8,), hp_current=8, **kw)


def hp(ch, iid="sw"):
    return dv.item_hp_current(ch.item(iid))


# Owner example: base 10, +3, active 13/13, damage 6 -> 7; off -> 7*10/13 = 5; on -> 8.
@S.case("example-13", "gear.md [OWNER pkg 6]: 13/13 -> damage 6 -> 7 -> off 5 -> on 8", (13, 7, 5, 8))
def _example():
    c = dispatch(ch_with(sword()), "activate_item", iid="sw").state
    a = hp(c)
    c = dispatch(c, "damage_item", iid="sw", amount=6).state
    b = hp(c)
    c = dispatch(c, "deactivate_item", iid="sw").state
    d = hp(c)
    c = dispatch(c, "activate_item", iid="sw").state
    return (a, b, d, hp(c))


S.case("off-not-zero", "gear.md: switching off never rounds a positive HP to 0 (1/13 -> 1, not 0.77 -> 1; 1/23 -> 1)",
       (1, 1))(
    lambda: (itm.scale_off(1, 13, 10), itm.scale_off(1, 23, 10)))
S.case("off-nearest", "gear.md: switching off rounds to NEAREST (9/13 -> 90/13 = 6.92 -> 7; 6/13 -> 4.6 -> 5)", (7, 5))(
    lambda: (itm.scale_off(9, 13, 10), itm.scale_off(6, 13, 10)))
S.case("off-short-rest", "gear.md: the short rest switches a day item off with the same scaling (7/13 -> 5)", 5)(
    lambda: hp(dispatch(ch_with(sword(activated=True, active_until="short", hp_current=7)), "short_rest").state))

# Broken = HP <= 50% of max (and > 0). Max 10 (not activated): 5 broken, 4 broken, 6 not broken; max 100: 51 not.
S.case("broken-50", "gear.md [OWNER pkg 6]: broken at exactly 50% and below, not at 51%",
       ("broken", "broken", "ok", "ok"))(
    lambda: tuple(itm.state(Item("x", "x", hp=m, hp_current=c)) for m, c in ((10, 5), (10, 4), (10, 6), (100, 51))))


def _atk(c):
    c = dispatch(c, "add_attack", iid="sw", group="blades").state
    return av.by_record(c, c.attacks[0].rid)


S.case("broken-sword", "gear.md: broken sword -2 attack and damage; the attack table shows it", (-2, -2, "broken"))(
    lambda: (lambda a: (a.to_hit, a.damage, a.item_state))(_atk(ch_with(sword(enchant=0, hp_current=5)))))


def armor(**kw):
    base = dict(equipped=True, armor=5, hp=20, skill_penalty=-3)
    base.update(kw)
    return Item("ar", "plate", **base)


S.case("broken-armor", "gear.md: broken armor bonus 5 -> 2 (half, down); armor skill penalty x2 (-3 -> -6)", (2, -6))(
    lambda: (lambda c: (dict(acm.parts(dv.ac_input(c)))["armor"], dv.armor_skill_penalty(c)))(
        ch_with(armor(hp_current=10))))
S.case("broken-shield", "gear.md: a shield is broken like armor: shield bonus 3 -> 1", 1)(
    lambda: dv.shield_bonus(ch_with(Item("sh", "shield", kind=SHIELD, hands=1, in_hands=True, shield=3, hp=10,
                                         hp_current=4))))
S.case("hp0-nothing", "gear.md: HP 0 -> the item gives nothing (armor 0, tab off, no dice), state not_working",
       (0, 0, ("", ""), "not_working"))(
    lambda: (dict(acm.parts(dv.ac_input(ch_with(armor(hp_current=0)))))["armor"],
             dv.total(ch_with(armor(hp_current=0, effects_off=(itm_effect(),))), "attack"),
             _atk(ch_with(sword(enchant=0, hp_current=0, damage_medium="1d8"))).dice,
             itm.state(Item("x", "x", hp=10, hp_current=0))))


def itm_effect():
    from wp.core.effects import Effect
    return Effect("attack", 1)


@S.case("hp-1-destroyed", "gear.md: HP -1 -> destroyed; cannot be activated or healed", ("destroyed", "rejected", "rejected"))
def _destroyed():
    c = dispatch(ch_with(sword()), "damage_item", iid="sw", amount=11).state
    out = [itm.state(c.item("sw"))]
    for name, kw in (("activate_item", {"iid": "sw"}), ("set_item_hp", {"iid": "sw", "value": 10})):
        try:
            dispatch(c, name, **kw)
            out.append("accepted")
        except CommandError:
            out.append("rejected")
    return tuple(out)


S.case("set-item-hp", "gear.md: set_item_hp (edit mode) sets the current HP", (4, "broken"))(
    lambda: (lambda c: (hp(c), itm.state(c.item("sw"))))(dispatch(ch_with(sword(enchant=0)), "set_item_hp", iid="sw", value=4).state))
S.case("no-hp-item-ok", "items.py: an item without HP (ring) is not tracked: always ok", "ok")(
    lambda: itm.state(Item("r", "ring")))
S.case("save-load", "D11: current item HP and destroyed survive save/load", True)(
    lambda: (lambda c: cio.loads(cio.dumps(c)) == c)(ch_with(sword(hp_current=-1, destroyed=True))))

if __name__ == "__main__":
    sys.exit(S.run())
