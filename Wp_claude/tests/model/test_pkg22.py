"""Package 22: manual mana restore, reactions as a resource, balance cap in combat, the most favourable tick order,
paired attacks. Expected numbers by hand from the owner's examples. Run: python Wp_claude/tests/model/test_pkg22.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.commands import reaction_cmds as rc  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.statuses import DYING  # noqa: E402
from wp.core.weapons import Weapon  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import maneuver_view as mv  # noqa: E402
from wp.model.character import AttackRecord, Character, Item, Maneuver, WeaponEntry  # noqa: E402

S = Suite("test_pkg22")


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def reason(ch, name, /, **kw):
    try:
        dispatch(ch, name, **kw)
    except CommandError as e:
        return e.reason
    return "allowed"


def hero(**kw):
    base = dict(hp_rolls=(8,), hp_current=8, spirit_current=5, balance_current=5, bp_current=5, training=1000)
    base.update(kw)
    return Character(**base)


# ---------------------------------------------------------------- A1 mana restore
def mage(cur=2, **kw):
    return hero(mana=Pool(cur, 10), mana_enabled=True, **kw)


S.case("a1-restore", "classes_magic.md [OWNER pkg 22]: mana 2/10 +5 -> 7; +20 -> 10 (the max); 12/10 stays 12",
       (7, 10, 12))(
    lambda: tuple(run(mage(c), ("restore_mana", {"amount": a})).mana.current for c, a in ((2, 5), (2, 20), (12, 3))))
S.case("a1-blocked", "buffs.md block_restore mana: refused", "restoring_blocked")(
    lambda: reason(mage(statuses=(Status("curse", sid="c", effects=(Effect("block_restore", block_resources=("mana",)),)),)),
                   "restore_mana", amount=3))
S.case("a1-logged", "resources.md journal: the restore is logged (kind heal)", "heal")(
    lambda: run(mage(), ("restore_mana", {"amount": 1})).log[-1].kind)

# ---------------------------------------------------------------- A2 reactions
S.case("a2-start", "training.md: a new character has 1 reaction (1/1)", (1, 1))(
    lambda: (lambda p: (p.current, p.max))(rc.reactions_pool(hero())))
S.case("a2-spend-refused", "pkg 22: spend 1 -> 0; spending at 0 is refused", (0, "not_enough_reactions"))(
    lambda: (lambda c: (rc.reactions_current(c), reason(c, "spend_reaction")))(run(hero(), ("spend_reaction", {}))))
S.case("a2-tick", "pkg 22: the zero-initiative tick (a new round) brings the reactions back", 1)(
    lambda: rc.reactions_current(run(hero(), ("spend_reaction", {}), ("tick", {}))))
S.case("a2-two", "training.md: +1 reaction costs 200 * 2 = 400 -> 2/2; spend 2 -> 0; end of combat -> 2",
       (600, 2, 0, 2))(
    lambda: (lambda c: (c.training, rc.reactions_current(c), rc.reactions_current(run(c, ("spend_reaction", {"n": 2}))),
                        rc.reactions_current(run(c, ("start_combat", {}), ("spend_reaction", {"n": 2}), ("end_combat", {})))))(
        run(hero(), ("buy_reaction", {}))))
S.case("a2-restore", "pkg 22: restore_reactions (manual) -> max", 1)(
    lambda: rc.reactions_current(run(hero(), ("spend_reaction", {}), ("restore_reactions", {}))))


def armed(**rec):
    return hero(items=(Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("g",)),),
                attacks=(AttackRecord("r1", "sw", "g", **rec),), weapons=(WeaponEntry(Weapon("g")),))


S.case("a2-attack-cost", "pkg 22: an attack of opportunity record (cost 1 reaction): used -> 0; again refused",
       (0, "not_enough_reactions"))(
    lambda: (lambda c: (rc.reactions_current(c), reason(c, "use_attack", rid="r1")))(
        run(armed(cost_reactions=1), ("use_attack", {"rid": "r1"}))))
S.case("a2-maneuver-cost", "pkg 22: a maneuver costing 1 reaction is not available at 0 reactions",
       (True, False, ("not_enough_reactions",)))(
    lambda: (lambda c: (mv.view_one(c, c.maneuvers[0]).available,
                        mv.view_one(run(c, ("spend_reaction", {})), c.maneuvers[0]).available,
                        mv.view_one(run(c, ("spend_reaction", {})), c.maneuvers[0]).reasons))(
        armed().__class__(**dict(armed().__dict__, maneuvers=(Maneuver("trip", "Trip", cost_reactions=1),)))))

# ---------------------------------------------------------------- A3 balance cap in combat
S.case("a3-clamped", "resources.md [OWNER pkg 22]: in combat the balance never goes above the cap 5 (set 9 -> 5); "
       "out of combat 9 stays (overcap)", (5, 9))(
    lambda: (run(hero(balance_current=3), ("start_combat", {}), ("set_value", {"resource": "balance", "value": 9})).balance_current,
             run(hero(balance_current=3), ("set_value", {"resource": "balance", "value": 9})).balance_current))
S.case("a3-restore-cap", "pkg 22: a restore in combat stops at the cap: 3 + 10 -> 5", 5)(
    lambda: run(hero(balance_current=3), ("start_combat", {}), ("restore", {"resource": "balance", "amount": 10})).balance_current)


# ---------------------------------------------------------------- A4 tick order
def bleed(n, sid="bleed"):
    return Status(sid, sid=sid, per_tick_hp=-n, duration=ef.INFINITE, active=True)


def tick(ch):
    c = run(ch, ("tick", {}))
    return c.balance_current, c.trauma, sum(p.amount for p in c.pain), c.hp_current


S.case("a4-owner-example", "pkg 22 [OWNER]: balance 5/5, dying -2, bleeding -4, regen +1: best order -2, +1, -4 -> 0, "
       "no OT, no pain; HP -1 -2 -4 = -7", (0, 0, 0, -7))(
    lambda: tick(hero(hp_current=-1, negative_state=DYING, statuses=(bleed(4),))))
S.case("a4-overflow-first", "pkg 22 [OWNER]: balance 3 (cap 5), regen +1, damage -4: regen first 4 -> 0 (no OT), "
       "not damage first -1 -> overflow (Q150)", (0, 0, 0, 4))(
    lambda: tick(hero(balance_current=3, statuses=(bleed(4),))))
S.case("a4-cap", "pkg 22: at the cap with nothing to lose the regen does not exceed the cap: 5 -> 5", 5)(
    lambda: run(hero(), ("tick", {})).balance_current)
S.case("a4-plain", "pkg 22: no DoT: plain regen 2 -> 3", 3)(lambda: run(hero(balance_current=2), ("tick", {})).balance_current)
S.case("a4-greedy", "pkg 22: 7 bleeds of 1 + regen (8 items, greedy): balance 3 + 1 against 7 -> OT 3, pain 3, balance 0",
       (0, 3, 3))(
    lambda: tick(hero(balance_current=3, statuses=tuple(bleed(1, "b%d" % i) for i in range(7))))[:3])

# ---------------------------------------------------------------- A5 paired attack


def twf_pair():
    items = (Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("g",)),
             Item("dg", "dagger", kind="weapon", hands=1, in_hands=True, groups=("g",), finesse=True))
    attacks = (AttackRecord("r1", "sw", "g", twf=True, twf_off="r2"), AttackRecord("r2", "dg", "g", grip="off"))
    return hero(items=items, attacks=attacks, weapons=(WeaponEntry(Weapon("g")),))


S.case("a5-paired-one-use", "combat.md [OWNER pkg 22]: a two-weapon combination is ONE use: count 1; the next attack -5, "
       "not -10", (1, -5))(
    lambda: (lambda c: (c.iterative_count, av.attack(c, c.attacks[1]).iterative))(run(twf_pair(), ("use_attack", {"rid": "r1"}))))

if __name__ == "__main__":
    sys.exit(S.run())
