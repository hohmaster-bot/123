"""Core rest vs RULES/rest.md. Run: python Wp_claude/tests/core/test_rest.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import Suite  # noqa: E402

from wp.core.damage import Pool  # noqa: E402
from wp.core import rest as r  # noqa: E402
from wp.core.pain import PainEntry as PE  # noqa: E402

S = Suite("test_rest")


def st(**kw):
    base = dict(level=3, hp=Pool(1, 20), bp=Pool(2, 5))
    base.update(kw)
    return r.RestState(**base)


# rest.md Short rest 2: +1 BP if below max.
@S.case("free-bp", "rest.md Short rest 2 [OWNER]", (3, 0))
def _free_bp():
    s = r.start_short_rest(st()).state
    return (s.bp.current, s.temp_bp)


# ... +1 temp BP if BP at max.
@S.case("free-temp-bp", "rest.md Short rest 2 [OWNER]", (5, 1))
def _free_temp():
    s = r.start_short_rest(st(bp=Pool(5, 5))).state
    return (s.bp.current, s.temp_bp)


# rest.md Example 7: level 3, HP 1/20: free +5 HP; a second heal costs 1 BP.
@S.case("heal-example", "rest.md Short rest 7 Example [OWNER]", (6, 11, 2))
def _heal():
    rest = r.start_short_rest(st())
    hp_free = rest.state.hp.current
    rest = r.spend(rest, r.OPT_HEAL)
    return (hp_free, rest.state.hp.current, rest.state.bp.current)


@S.case("heal-race-more", "rest.md Short rest 2: larger heal from race/effect wins", 8)
def _heal_more():
    return r.start_short_rest(st(), other_heal=8).free_heal


@S.case("heal-cost", "rest.md table: repeat heal 1 BP", 1)
def _heal_cost():
    return dict(r.options(r.start_short_rest(st())))[r.OPT_HEAL]


# rest.md Short rest 4: only options with something to restore are shown.
@S.case("options-hidden", "rest.md Short rest 4 [OWNER]", ())
def _hidden():
    s = st(hp=Pool(20, 20), stats={"str": Pool(18, 18)})
    return r.options(r.start_short_rest(s))


@S.case("options-shown", "rest.md Short rest 4 [OWNER]",
        (("stat", 1), ("pain", 1)))
def _shown():
    s = st(hp=Pool(20, 20), stats={"str": Pool(17, 18)}, pain=(PE(2),))
    return r.options(r.start_short_rest(s))


@S.case("costs-table", "rest.md Short rest table",
        (("heal", 1), ("charges", 2), ("spirit", 2), ("stat", 1), ("pain", 1),
         ("mana", 0), ("divine", 1)))
def _costs():
    s = st(stats={"con": Pool(10, 12)}, pain=(PE(1),), spirit=Pool(0, 5),
           mana=Pool(0, 6), mana_enabled=True, slots={1: Pool(0, 2)},
           charges=(r.Charge("rage", r.ABILITY, Pool(0, 3)),))
    return r.options(r.start_short_rest(s))


@S.case("mana-free-once", "rest.md table: mana free once, then 1 BP", (0, 1, 4))
def _mana():
    s = st(mana=Pool(0, 6), mana_enabled=True)
    rest = r.start_short_rest(s)
    c1 = r.option_cost(rest, r.OPT_MANA)
    rest = r.spend(rest, r.OPT_MANA, mana_amount=4)
    return (c1, r.option_cost(rest, r.OPT_MANA), rest.state.mana.current)


# stats.md Tests: Str 17/18, short rest 1 BP -> 18/18.
@S.case("stat-restore", "stats.md Tests + rest.md table", (18, 2))
def _stat():
    rest = r.spend(r.start_short_rest(st(stats={"str": Pool(17, 18)})), r.OPT_STAT, stat="str")
    return (rest.state.stats["str"].current, rest.state.bp.current)


@S.case("pain-1bp", "rest.md table: remove 1 pain for 1 BP (pain list)", (1, 2))
def _pain():
    rest = r.spend(r.start_short_rest(st(pain=(PE(2, "overflow"),))), r.OPT_PAIN)
    return (sum(e.amount for e in rest.state.pain), rest.state.bp.current)


@S.case("pain-permanent-hidden", "rest.md: only permanent pain -> 'remove pain' hidden", ())
def _pain_perm():
    return r.options(r.start_short_rest(st(hp=Pool(20, 20), pain=(PE(2, "curse", True),))))


@S.case("not-enough-bp", "rest.md: spend only what you have", "rejected")
def _no_bp():
    rest = r.start_short_rest(st(bp=Pool(0, 5), spirit=Pool(0, 5)))  # 1 BP after free gain
    try:
        r.spend(rest, r.OPT_SPIRIT)
    except ValueError:
        return "rejected"
    return "allowed"


# rest.md Short rest 6: Apply -> excess BP (above max) is lost.
@S.case("apply-excess-lost", "rest.md Short rest 6 [OWNER]", (5, 0))
def _apply():
    rest = r.start_short_rest(st(bp=Pool(5, 5)), extra_temp_bp=2)
    s = r.apply_short_rest(rest)
    return (s.bp.current, s.temp_bp)


@S.case("extra-bp", "rest.md Short rest 5: other BP sources add BP", 5)
def _extra():
    return r.bp_available(r.start_short_rest(st(bp=Pool(2, 5)), extra_bp=1, extra_temp_bp=1))


# rest.md Long rest.
def _long_state():
    return st(hp=Pool(-4, 20), bp=Pool(0, 5), pain=(PE(3, "overflow"), PE(1, "curse", True)),
              spirit=Pool(1, 5), mana=Pool(0, 6), mana_enabled=True,
              slots={1: Pool(0, 2)}, resources={"ki": Pool(0, 4)},
              charges=(r.Charge("rage", r.ABILITY, Pool(0, 3)),
                       r.Charge("wand", r.ITEM, Pool(0, 5), restore_on_long_rest=False),
                       r.Charge("ring", r.ITEM, Pool(0, 2), restore_on_long_rest=True),
                       r.Charge("broken arm", r.INJURY, Pool(1, 2))),
              stats={"str": Pool(17, 18)}, trauma=7, comfort=Pool(4, 10))


@S.case("long-restores", "rest.md Long rest [OWNER]",
        (20, 5, 5, 6, 2, 4))
def _long1():
    s = r.long_rest(_long_state())
    return (s.hp.current, s.bp.current, s.spirit.current, s.mana.current,
            s.slots[1].current, s.resources["ki"].current)


@S.case("long-charges", "rest.md Long rest: ability yes, item by checkbox, injury no",
        (3, 0, 2, 1))
def _long2():
    s = r.long_rest(_long_state())
    return tuple(c.pool.current for c in s.charges)


@S.case("long-pain", "rest.md Long rest: pain gone except permanent", (1, ("curse",)))
def _long3():
    s = r.long_rest(_long_state())
    return (sum(e.amount for e in s.pain), tuple(e.source for e in s.pain))


@S.case("long-keeps", "rest.md / injuries.md: long rest never touches OT, comfort", (7, 4))
def _long4():
    s = r.long_rest(_long_state())
    return (s.trauma, s.comfort.current)


@S.case("long-stats", "rest.md Long rest [OWNER]: stat damage healed, permanent not",
        ((18, 18), (17, 17)))
def _long5():
    from wp.core import injuries as inj
    con = inj.permanent_stat_damage(Pool(18, 18), 1)          # permanent: max 17
    s = r.long_rest(st(stats={"str": Pool(15, 18), "con": inj.damage_stat(con, 2)}))
    return tuple((p.current, p.max) for p in (s.stats["str"], s.stats["con"]))


if __name__ == "__main__":
    sys.exit(S.run())
