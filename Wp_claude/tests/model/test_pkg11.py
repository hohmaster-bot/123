"""Package 11: status container, stat-mod effect values, race size and speed, feat effects.
Run: python Wp_claude/tests/model/test_pkg11.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.injuries import Injury  # noqa: E402
from wp.model import container_view as cv  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import Character, Item  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg11")


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def refused(ch, name, **kw):
    try:
        dispatch(ch, name, **kw)
    except CommandError as e:
        return "refused: " + str(e).split(":")[0]
    return "allowed"


def hero(**kw):
    base = dict(hp_rolls=(20,), hp_current=20, spirit_current=5, balance_current=5, bp_current=5)
    base.update(kw)
    return Character(**base)


ATK2 = (Effect(bo.ATTACK, 2),)


def rage(cur=2, mx=3, **kw):
    return Status("Rage", sid="rage", effects=ATK2, duration=ef.TICKS, full_ticks=5, charges=Pool(cur, mx), **kw)


def haste(**kw):
    return Status("Haste", sid="haste", effects=ATK2, duration=ef.TICKS, full_ticks=3, **kw)


def st(ch, sid):
    return next(s for s in ch.statuses if s.sid == sid)


def added(*statuses, **kw):
    ch = hero(**kw)
    for s in statuses:
        ch = run(ch, ("add_status", {"status": s}))
    return ch


# ---- A: container ----
S.case("a-add-inactive", "buffs.md [OWNER pkg 11 A]: a new entry starts inactive: no charge spent, no bonus",
       (False, 2, 0))(
    lambda: (lambda c: (st(c, "rage").active, st(c, "rage").charges.current, dv.total(c, bo.ATTACK)))(added(rage())))
S.case("a-activate-charges", "buffs.md: activate with charges: one spent, full duration per charge, bonus +2",
       (True, 1, 5, 2))(
    lambda: (lambda c: (st(c, "rage").active, st(c, "rage").charges.current, st(c, "rage").remaining,
                        dv.total(c, bo.ATTACK)))(run(added(rage()), ("activate_status", {"sid": "rage"}))))
S.case("a-activate-no-charges", "buffs.md: an entry without charges just becomes active (full duration 3)", (True, 3))(
    lambda: (lambda s: (s.active, s.remaining))(st(run(added(haste()), ("activate_status", {"sid": "haste"})), "haste")))
S.case("a-add-active", "buffs.md: add with active=True starts it at once (charge spent)", (True, 1))(
    lambda: (lambda s: (s.active, s.charges.current))(
        st(run(hero(), ("add_status", {"status": rage(), "active": True})), "rage")))
S.case("a-refuse-no-charge", "buffs.md: no charge left -> refused", "refused: no charges left")(
    lambda: refused(added(rage(cur=0)), "activate_status", sid="rage"))
S.case("a-refuse-active", "buffs.md: already active -> refused", "refused: status Haste is already active")(
    lambda: refused(run(added(haste()), ("activate_status", {"sid": "haste"})), "activate_status", sid="haste"))
S.case("a-refuse-cost", "buffs.md: the cost cannot be paid (2 spirit, have 1) -> refused",
       "refused: cannot pay 2 spirit for Haste (have 1)")(
    lambda: refused(added(haste(cost_resource="spirit", cost_amount=2), spirit_current=1), "activate_status", sid="haste"))
S.case("a-cost-paid", "buffs.md: activation pays the cost (spirit 5 -> 3)", 3)(
    lambda: run(added(haste(cost_resource="spirit", cost_amount=2)), ("activate_status", {"sid": "haste"})).spirit_current)
S.case("a-remove-early", "buffs.md: remove_status ends it now: inactive, time cleared, entry stays, bonus gone",
       (False, 0, 1, 0))(
    lambda: (lambda c: (st(c, "haste").active, st(c, "haste").remaining, len(c.statuses), dv.total(c, bo.ATTACK)))(
        run(added(haste()), ("activate_status", {"sid": "haste"}), ("remove_status", {"sid": "haste"}))))
S.case("a-remove-inactive", "buffs.md: removing an inactive status is refused", "refused: status Haste is not active")(
    lambda: refused(added(haste()), "remove_status", sid="haste"))


def _run_ticks(ch, n):
    out = []
    for _ in range(n):
        ch = run(ch, ("tick", {}))
        out.append((st(ch, "haste").active, dv.total(ch, bo.ATTACK)))
    return out


S.case("a-full-duration", "buffs.md: 3 ticks: bonus while active, inactive after the 3rd tick, entry stays",
       [(True, 2), (True, 2), (False, 0), (False, 0)])(
    lambda: _run_ticks(run(added(haste()), ("activate_status", {"sid": "haste"})), 4))
S.case("a-inactive-no-tick", "buffs.md: an inactive status does not tick and gives nothing (remaining 4 stays)", (4, 0))(
    lambda: (lambda c: (st(c, "haste").remaining, dv.total(c, bo.ATTACK)))(
        run(hero(statuses=(haste(active=False, remaining=4),)), ("tick", {}))))
S.case("a-hidden", "buffs.md: hidden is display only: still gives the bonus and ticks (3 -> 2)", (True, 2, 2))(
    lambda: (lambda c: (st(c, "haste").hidden, dv.total(c, bo.ATTACK), st(c, "haste").remaining))(
        run(added(haste()), ("activate_status", {"sid": "haste"}), ("set_status_hidden", {"sid": "haste", "value": True}),
            ("tick", {}))))
S.case("a-favorite", "buffs.md: favorite flag -> container favorites list", ("haste",))(
    lambda: cv.container_view(run(added(haste(), rage()), ("set_status_favorite", {"sid": "haste"}))).favorites)
S.case("a-delete", "buffs.md: delete_status removes the entry from the container", ("rage",))(
    lambda: tuple(s.sid for s in run(added(haste(), rage()), ("delete_status", {"sid": "haste"})).statuses))
S.case("a-charges-long-rest", "rest.md (unchanged): the long rest restores status charges (1/3 -> 3/3)", 3)(
    lambda: st(run(added(rage()), ("activate_status", {"sid": "rage"}), ("long_rest", {})), "rage").charges.current)
S.case("a-charges-short-rest", "rest.md (unchanged): the short rest does not restore status charges (1 stays)", 1)(
    lambda: st(run(added(rage()), ("activate_status", {"sid": "rage"}), ("short_rest", {})), "rage").charges.current)
S.case("a-container-kinds", "buffs.md: the container lists statuses, injuries and item effects",
       (("status", "rage", True), ("injury", "injury:0", False), ("item", "ring", False)))(
    lambda: tuple((e.kind, e.eid, e.manageable) for e in cv.container_view(hero(
        statuses=(rage(),), injuries=(Injury("cut", "light", 2),),
        items=(Item("ring", "ring", equipped=True, effects_off=ATK2),))).entries))
S.case("a-temp-hp-ends", "resources.md: temp HP of a status go when it ends early (5 -> 0, stored 0)", (5, 0, 0))(
    lambda: (lambda c: (dv.temp_hp_total(c), dv.temp_hp_total(run(c, ("remove_status", {"sid": "aid"}))),
                        st(run(c, ("remove_status", {"sid": "aid"})), "aid").temp_hp_left))(
        run(hero(), ("add_status", {"active": True, "status": Status(
            "aid", sid="aid", one_shot=(ef.OneShot(ef.TEMP_HP, 5),), duration=ef.TICKS, full_ticks=3)}))))


def _old_save():
    """A save written before package 11: statuses without the new fields still load."""
    d = json.loads(cio.dumps(hero(statuses=(haste(),))))
    for s in d["character"]["statuses"]:
        for k in ("full_ticks", "cost_resource", "cost_amount", "hidden", "favorite"):
            s.pop(k, None)
    return cio.loads(json.dumps(d)).statuses[0].full_ticks


S.case("a-old-save", "D11: an old save without the new status fields loads (defaults)", 0)(_old_save)

if __name__ == "__main__":
    sys.exit(S.run())
