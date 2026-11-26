"""Package 14: per-round pay at activation, charges and cooldown, formulas, injury effects, per-round examples,
action / restore blocks, restore by effect, rule switches, long journal.
Run: python Wp_claude/tests/model/test_pkg14.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.core import effects as ef  # noqa: E402
from wp.core import formula as cf  # noqa: E402
from wp.core import magic as mg  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Effect, OneShot, Status  # noqa: E402
from wp.core.injuries import Injury  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.model import active_list as al  # noqa: E402
from wp.model import blocks as blk  # noqa: E402
from wp.model import container_view as cv  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import pool_view as pv  # noqa: E402
from wp.model.character import (ABILITIES, Ability, AttackRecord, Character, Feat, Item, Maneuver,  # noqa: E402
                                ResourcePool, RulesSettings, Usage)
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg14")


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def refused(ch, name, /, **kw):
    try:
        dispatch(ch, name, **kw)
    except CommandError as e:
        return "refused: " + str(e)
    return "allowed"


def abil(**scores):
    return {a: Ability(base=scores.get(a, 10)) for a in ABILITIES}


def hero(**kw):
    base = dict(hp_rolls=(20,), hp_current=20, spirit_current=5, balance_current=5, bp_current=5)
    base.update(kw)
    return Character(**base)


def pool(pid, mx, cur=None, restore="manual"):
    return ResourcePool(pid, pid, max=mx, current=mx if cur is None else cur, restore=restore)


def per_round(sid, source, n, **kw):
    return Status(sid, sid=sid, charge_source=source, charge_per_round=n, active=False, **kw)


def ticks(ch, n, pid=None, sid=None):
    out = []
    for _ in range(n):
        ch = run(ch, ("tick", {}))
        out.append((ch.statuses[0].active if sid is None else next(s for s in ch.statuses if s.sid == sid).active,
                    pv.current(ch, ch.pools[0]) if ch.pools else None))
    return out


# ================================================================ A. owner answers
S.case("a-exact-3-rounds", "buffs.md [OWNER pkg 14 A, Q83]: pool 3 at 1 per round gives EXACTLY 3 rounds",
       (2, [(True, 1), (True, 0), (False, 0)]))(
    lambda: (lambda c: (c.pools[0].current, ticks(c, 3)))(
        run(hero(pools=(pool("ki", 3),), statuses=(per_round("aura", "ki", 1),)), ("activate_status", {"sid": "aura"}))))
S.case("a-refuse-activation", "buffs.md: the source cannot pay at activation -> refused (pool 1, 2 per round)",
       "refused: not enough ki for aura: need 2 per round, have 1")(
    lambda: refused(hero(pools=(pool("ki", 1),), statuses=(per_round("aura", "ki", 2),)), "activate_status", sid="aura"))
S.case("a-own-instead", "buffs.md [Q91]: source own, 3 per round, charges 3: activation spends 3 (no extra charge) -> 0",
       0)(lambda: run(hero(statuses=(per_round("b", ef.OWN, 3, charges=Pool(3, 3)),)),
                      ("activate_status", {"sid": "b"})).statuses[0].charges.current)


def _old_count():
    d = json.loads(cio.dumps(hero(items=(Item("b", "bolts", quantity=10),))))
    d["character"]["items"][0]["count"] = 10
    return cio.loads(json.dumps(d)).items[0].quantity


S.case("a-count-dropped", "gear.md [OWNER Q86]: the old field count is dropped on load; quantity stays", 10)(_old_count)
S.case("a-long-rest-short-pools", "resources.md [OWNER Q88]: a long rest restores short_rest and long_rest pools, not "
       "combat_start / manual", (3, 3, 0, 0))(
    lambda: tuple(p.current for p in run(hero(pools=(pool("a", 3, 0, "short_rest"), pool("b", 3, 0, "long_rest"),
                                                     pool("c", 3, 0, "combat_start"), pool("d", 3, 0))),
                                          ("long_rest", {})).pools))

# ================================================================ B. charges and cooldown
WAND = Item("wand", "wand", in_hands=True, hands=1, usage=Usage(charges_max=3, charges_current=3, recharge="long_rest",
                                                               cooldown_rounds=2))


def _chg(ch, kind="item", oid="wand"):
    from wp.model import usage as us
    o = us.find(ch, kind, oid)
    return (us.charges(kind, o)[0], us.cooldown(kind, o)[0])


S.case("b-spend", "gear.md [OWNER pkg 14 B]: spend 1 of 3 -> 2, cooldown 2 starts", (2, 2))(
    lambda: _chg(run(hero(items=(WAND,)), ("spend_charge", {"owner_kind": "item", "owner_id": "wand"}))))
S.case("b-cooldown-refuse", "gear.md: spending during the cooldown is refused",
       "refused: item wand is on cooldown (2 rounds left)")(
    lambda: refused(run(hero(items=(WAND,)), ("spend_charge", {"owner_kind": "item", "owner_id": "wand"})),
                    "spend_charge", owner_kind="item", owner_id="wand"))
S.case("b-cooldown-ticks", "gear.md: the tick lowers the cooldown 2 -> 1 -> 0; then spending works again (1 left)",
       ((2, 1), (2, 0), (1, 2)))(
    lambda: (lambda c: (_chg(run(c, ("tick", {}))), _chg(run(c, ("tick", {}), ("tick", {}))),
                        _chg(run(c, ("tick", {}), ("tick", {}), ("spend_charge", {"owner_kind": "item", "owner_id": "wand"})))))(
        run(hero(items=(WAND,)), ("spend_charge", {"owner_kind": "item", "owner_id": "wand"}))))
S.case("b-below-zero", "gear.md: spending more than there is -> refused", "refused: not enough charges: have 3, spend 4")(
    lambda: refused(hero(items=(WAND,)), "spend_charge", owner_kind="item", owner_id="wand", n=4))
S.case("b-no-charges", "gear.md: an owner without charges -> refused", "refused: item ring has no charges")(
    lambda: refused(hero(items=(Item("ring", "ring"),)), "spend_charge", owner_kind="item", owner_id="ring"))


def _rule(rule, step):
    it = Item("x", "x", usage=Usage(charges_max=2, charges_current=0, recharge=rule))
    return run(hero(items=(it,)), step).items[0].usage.charges_current


S.case("b-recharge-rules", "gear.md: recharge: short rest -> short_rest; long rest -> long_rest and short_rest; start_combat "
       "-> combat_start; manual never", ((2, 0, 0, 0), (2, 2, 0, 0), (0, 0, 2, 0)))(
    lambda: tuple(tuple(_rule(r, step) for r in ("short_rest", "long_rest", "combat_start", "manual"))
                  for step in (("short_rest", {}), ("long_rest", {}), ("start_combat", {}))))
S.case("b-owners", "gear.md: feat, attack record, maneuver and status charges (2 -> 1 each); set and restore work",
       (1, 1, 1, 1, 0, 2))(
    lambda: (lambda c: (_chg(run(c, ("spend_charge", {"owner_kind": "feat", "owner_id": "f"})), "feat", "f")[0],
                        _chg(run(c, ("spend_charge", {"owner_kind": "attack", "owner_id": "r"})), "attack", "r")[0],
                        _chg(run(c, ("spend_charge", {"owner_kind": "maneuver", "owner_id": "m"})), "maneuver", "m")[0],
                        _chg(run(c, ("spend_charge", {"owner_kind": "status", "owner_id": "s"})), "status", "s")[0],
                        _chg(run(c, ("set_charges", {"owner_kind": "feat", "owner_id": "f", "value": 0})), "feat", "f")[0],
                        _chg(run(c, ("spend_charge", {"owner_kind": "feat", "owner_id": "f"}),
                                 ("restore_charges", {"owner_kind": "feat", "owner_id": "f"})), "feat", "f")[0]))(
        hero(feats=(Feat("f", usage=Usage(2, 2)),), attacks=(AttackRecord("r", "unarmed", "unarmed_combat", usage=Usage(2, 2)),),
             maneuvers=(Maneuver("m", "M", usage=Usage(2, 2)),), statuses=(Status("s", sid="s", charges=Pool(2, 2)),))))
S.case("b-status-cooldown", "gear.md: a status cooldown starts on spend and ticks down", (1, 3, 2))(
    lambda: (lambda c: (_chg(c, "status", "s")[0], _chg(c, "status", "s")[1], _chg(run(c, ("tick", {})), "status", "s")[1]))(
        run(hero(statuses=(Status("s", sid="s", charges=Pool(2, 2), cooldown_rounds=3, active=False),)),
            ("spend_charge", {"owner_kind": "status", "owner_id": "s"}))))
S.case("b-active-list-follows", "pkg 14 B (Q94): item charges in the active list only while the item is worn / held",
       ((("wand", 3, 3),), ()))(
    lambda: tuple(tuple((c.iid, c.current, c.max) for c in al.active_list(hero(items=(it,))).item_charges)
                  for it in (WAND, Item("wand", "wand", usage=WAND.usage))))


def _old_item_charges():
    from wp.core import rest as rs
    c = hero(charges=(rs.Charge("rage", rs.ABILITY, Pool(1, 3)),))
    d = json.loads(cio.dumps(c))
    item_charge = dict(d["character"]["charges"][0])
    item_charge.update(name="wand", kind="item")
    d["character"]["charges"].append(item_charge)
    return tuple(x.name for x in cio.loads(json.dumps(d)).charges)


S.case("b-old-item-charges", "D1: old by-name item charges are dropped on load; ability charges stay", ("rage",))(_old_item_charges)

# ================================================================ C. formulas
S.case("c-rage-pool", "buffs.md [OWNER pkg 14 C]: rage max = con_mod + 2*(level+1): Con mod 3, level 4 -> 13", 13)(
    lambda: pv.max_of(hero(level=4, abilities=abil(con=16)), pool("rage", "con_mod + 2*(level+1)")))
S.case("c-ops", "buffs.md: 2*lvl (level 3) = 6; min(level, 2) = 2; max(str_mod, 1) = 1; bab + 1 = 4", (6, 2, 1, 4))(
    lambda: tuple(cf.evaluate(f, {"level": 3, "str_mod": 0, "bab": 3}) for f in ("2*lvl", "min(level, 2)", "max(str_mod, 1)",
                                                                                  "bab + 1")))
S.case("c-rounding", "buffs.md: / rounds DOWN (7/2 = 3, -7/2 = -4); the result is rounded down (level*0.5 at 3 -> 1; "
       "-level*0.5 -> -2); floor(2.5) = 2", (3, -4, 1, -2, 2))(
    lambda: tuple(cf.evaluate(f, {"level": 3}) for f in ("7/2", "-7/2", "level*0.5", "-level*0.5", "floor(2.5)")))


def _con_change():
    c = run(hero(level=4, abilities=abil(con=16)), ("add_pool", {"name": "Rage", "max": "con_mod + 2*(level+1)"}))
    low = Character(**{**c.__dict__, "abilities": abil(con=12)})       # Con mod 3 -> 1
    return (pv.max_of(c, c.pools[0]), pv.current(c, c.pools[0]), pv.max_of(low, low.pools[0]), pv.current(low, low.pools[0]),
            low.pools[0].current)


S.case("c-clamp", "buffs.md: Con 16 -> 12 lowers the max 13 -> 11 on read; the current 13 stays and is shown over max "
       "(package 16 A6, owner: no clamp)", (13, 13, 11, 13, 13))(_con_change)
S.case("c-bad-pool-formula", "buffs.md: a bad formula is refused when added",
       "refused: bad pool max formula 'con_mod +': unexpected end")(
    lambda: refused(hero(), "add_pool", name="X", max="con_mod +"))
def _err(text):
    try:
        cf.validate(text)
    except cf.FormulaError as e:
        return e
    return "valid"


S.case("c-unsafe", "buffs.md: no eval: an unknown name and quotes are refused",
       ("unknown variable '__import__'", "character \"'\" is not allowed"))(
    lambda: (str(_err("__import__"))[:29], str(_err("__import__('os')"))))
S.case("c-broken-never-crashes", "buffs.md: a broken formula stored by hand gives 0 in the derived view (no crash)", 0)(
    lambda: pv.max_of(hero(), pool("x", "level +* 2")))
S.case("c-effect-formula", "buffs.md: an effect value \"2*lvl\" at level 3 -> attack +6", 6)(
    lambda: dv.total(hero(level=3, statuses=(Status("s", sid="s", effects=(Effect(bo.ATTACK, "2*lvl"),)),)), bo.ATTACK))
S.case("c-effect-bad-refused", "buffs.md: a status with a broken formula is refused when added",
       "refused: bad effect formula in s: unknown variable 'foo' (allowed: level, lvl, str_mod, dex_mod, con_mod, int_mod, wis_mod, cha_mod, bab, hp_max, mana_max, base_slots, pain, morale, balance_max, spirit_max, bp_max, comfort_max, tagged_base_slots:<tag>)")(
    lambda: refused(hero(), "add_status", status=Status("s", sid="s", effects=(Effect(bo.ATTACK, "foo"),))))

# ================================================================ D. injury effects
CUT = Injury("cut", "light", 2, jid="cut_1", effects=(Effect(bo.ATTACK, -2),))
TIRED = Injury("tired", "light", 2, jid="tired_1", effects=(Effect(bo.BLOCK_REGEN),))
S.case("d-penalty", "injuries.md [OWNER pkg 14 D]: an injury -2 to attack; removing it removes the effect", (-2, 0))(
    lambda: (dv.total(hero(injuries=(CUT,)), bo.ATTACK),
             dv.total(run(hero(injuries=(CUT,)), ("remove_injury", {"injury_id": "cut_1"})), bo.ATTACK)))
S.case("d-regen-block", "injuries.md: an injury can block the balance regen (0 -> 0, reason tired_1)", (0, ("tired_1",)))(
    lambda: (lambda c: (run(c, ("tick", {})).balance_current, blk.regen_block_reasons(c)))(hero(balance_current=0, injuries=(TIRED,))))
S.case("d-container", "buffs.md: the container view shows the injury's effects", 1)(
    lambda: len(next(e for e in cv.container_view(hero(injuries=(CUT,))).entries if e.kind == cv.INJURY).effects))

# ================================================================ E. per-round examples
def _monk():
    aura = per_round("aura", "ki", 1, per_tick_hp=1)
    return run(hero(hp_current=10, pools=(pool("ki", 5, restore="short_rest"),), statuses=(aura,)), ("activate_status", {"sid": "aura"}))


S.case("e-monk", "buffs.md [OWNER pkg 14 E]: ki 5, aura 1 per round + 1 HP per tick: ki 4 after activation; ticks: "
       "(ki 3, HP 11), (2, 12); removed by hand: no payment, no regen (2, 12)",
       (4, [(3, 11), (2, 12)], (2, 12)))(
    lambda: (lambda c: (c.pools[0].current,
                        [(x.pools[0].current, x.hp_current) for x in (run(c, ("tick", {})), run(c, ("tick", {}), ("tick", {})))],
                        (lambda y: (y.pools[0].current, y.hp_current))(
                            run(c, ("tick", {}), ("tick", {}), ("remove_status", {"sid": "aura"}), ("tick", {})))))(_monk()))
S.case("e-monk-rest", "resources.md: the short rest restores ki to 5", 5)(
    lambda: run(_monk(), ("tick", {}), ("short_rest", {})).pools[0].current)
S.case("e-cursed", "buffs.md: darkness 7, 3 per round: activation 4; tick 1 pays (1); tick 2 cannot pay -> ends by itself",
       (4, [(True, 1), (False, 1)]))(
    lambda: (lambda c: (c.pools[0].current, ticks(c, 2)))(
        run(hero(pools=(pool("darkness", 7),), statuses=(per_round("curse", "darkness", 3),)), ("activate_status", {"sid": "curse"}))))
S.case("e-rage", "buffs.md: rage pool max con_mod + 2*(level+1) = 13, 1 per round: 12 after activation, 11 after a tick; "
       "the long rest restores 13", (12, 11, 13))(
    lambda: (lambda c: (c.pools[0].current, run(c, ("tick", {})).pools[0].current,
                        run(c, ("tick", {}), ("remove_status", {"sid": "rage"}), ("long_rest", {})).pools[0].current))(
        run(hero(level=4, abilities=abil(con=16), pools=(pool("rage", "con_mod + 2*(level+1)", 13, "long_rest"),),
                 statuses=(per_round("rage", "rage", 1),)), ("activate_status", {"sid": "rage"}))))

# ================================================================ F. action / restore blocks, restore by effect
def blocker(**kw):
    return Status("x", sid="x", effects=(Effect(**kw),))


CASTER = dict(caster=mg.MAGE, mana=Pool(10, 10), balance_current=6, balance_bonus=6, level=5)
S.case("f-spell-blocked", "buffs.md [OWNER pkg 14 F]: block_action spell_cast -> cast_spell refused; the view lists it",
       ("refused: casting is blocked by x", {"spell_cast": ("x",)}))(
    lambda: (lambda c: (refused(c, "cast_spell", circle=1), blk.blocked_actions(c)))(
        hero(statuses=(blocker(target=bo.BLOCK_ACTION, block_actions=("spell_cast",)),), **CASTER)))
S.case("f-heal-blocked", "buffs.md: block_action heal -> restore hp refused; mana still restores",
       ("refused: healing is blocked by x", 10))(
    lambda: (lambda c: (refused(c, "restore", resource="hp", amount=2),
                        run(c, ("restore", {"resource": "mana", "amount": 2})).mana.current))(
        hero(hp_current=10, mana=Pool(8, 10), statuses=(blocker(target=bo.BLOCK_ACTION, block_actions=("heal",)),))))
S.case("f-any-actions", "buffs.md: block_action any -> attack, move, spell_cast, heal flags (attack / move only exposed)",
       ("attack", "heal", "move", "spell_cast"))(
    lambda: tuple(sorted(blk.blocked_actions(hero(statuses=(blocker(target=bo.BLOCK_ACTION, block_actions=("any",)),))))))
S.case("f-restore-block-rest", "buffs.md: block_restore hp + mana: a long rest does not raise HP 10 or mana 2 (spirit 5 -> 5 max)",
       (10, 2))(
    lambda: (lambda c: (c.hp_current, c.mana.current))(run(
        hero(hp_current=10, mana=Pool(2, 10), statuses=(blocker(target=bo.BLOCK_RESTORE, block_resources=("hp", "mana")),)),
        ("long_rest", {}))))
S.case("f-restore-block-tick", "buffs.md: block_restore hp stops the per-tick heal (10 stays); without it 12", (10, 12))(
    lambda: tuple(run(hero(hp_current=10, statuses=s + (Status("r", sid="r", per_tick_hp=2),)), ("tick", {})).hp_current
                  for s in ((blocker(target=bo.BLOCK_RESTORE, block_resources=("hp",)),), ())))
S.case("f-alias", "buffs.md: block_restore balance = block_balance_regen (both block the regen: 0 -> 0)", (0, 0))(
    lambda: tuple(run(hero(balance_current=0, statuses=(blocker(**kw),)), ("tick", {})).balance_current
                  for kw in (dict(target=bo.BLOCK_RESTORE, block_resources=("balance",)), dict(target=bo.BLOCK_REGEN))))
S.case("f-pool-block", "buffs.md: block_restore pool:ki -> the short rest does not restore ki; restore_pool refused",
       (1, "refused: restoring ki is blocked by x"))(
    lambda: (lambda c: (run(c, ("short_rest", {})).pools[0].current, refused(c, "restore_pool", pid="ki")))(
        hero(pools=(pool("ki", 5, 1, "short_rest"),), statuses=(blocker(target=bo.BLOCK_RESTORE, block_resources=("pool:ki",)),))))


def _per_tick(*extra):
    st = Status("well", sid="well", per_tick_restore={"mana": 2, "spirit": 1, "balance": 1, "pool:ki": 1})
    c = hero(mana=Pool(2, 10), spirit_current=1, balance_current=0, pools=(pool("ki", 5, 1),), statuses=(st,) + extra)
    c = run(c, ("tick", {}))
    return (c.mana.current, c.spirit_current, c.balance_current, c.pools[0].current)


S.case("f-restore-by-effect", "buffs.md: per_tick_restore mana 2, spirit 1, balance 1, ki 1 (balance also regenerates +1)",
       (4, 2, 2, 2))(lambda: _per_tick())
S.case("f-restore-by-effect-blocked", "buffs.md: block_restore any -> nothing is restored", (2, 1, 0, 1))(
    lambda: _per_tick(blocker(target=bo.BLOCK_RESTORE, block_resources=("any",))))
S.case("f-one-shot", "buffs.md: a one-shot mana +3 at activation (2 -> 5); blocked -> 2", (5, 2))(
    lambda: tuple(run(hero(mana=Pool(2, 10), statuses=(Status("p", sid="p", one_shot=(OneShot("mana", 3),),
                                                             duration=ef.INSTANT, active=False),) + s),
                      ("activate_status", {"sid": "p"})).mana.current
                  for s in ((), (blocker(target=bo.BLOCK_RESTORE, block_resources=("mana",)),))))
S.case("f-bad-restore-key", "buffs.md: an unknown per-tick restore key is refused",
       "refused: unknown per-tick restore resources: gold (use mana, spirit, balance, pool:<id>)")(
    lambda: refused(hero(), "add_status", status=Status("s", sid="s", per_tick_restore={"gold": 1})))

# ================================================================ G. rule switches
def rules(**kw):
    return RulesSettings(**kw)


S.case("g-ignore-pain", "resources.md [OWNER pkg 14 G]: ignore_pain: pain 2 gives no attack penalty; the pain count stays 2",
       ((-2, 2), (0, 2)))(
    lambda: tuple((dv.total(c, bo.ATTACK), dv.pain_total(c)) for c in (
        hero(pain=(PainEntry(2),)), hero(pain=(PainEntry(2),), rules_settings=rules(ignore_pain=True)))))
S.case("g-ignore-negative-morale", "defense.md: ignore_negative_morale: scale -4 -> 0 (not -2); +4 still +2", (0, 2))(
    lambda: tuple(dv.morale_bonus(hero(in_combat=True, morale_scale=m, rules_settings=rules(ignore_negative_morale=True)))
                  for m in (-4, 4)))
S.case("g-speed-multiplier", "combat.md: speed_multiplier 1.5 -> 30; 0.5 with base 25 -> 12 (rounded down)", (30, 12))(
    lambda: (dv.speed(hero(rules_settings=rules(speed_multiplier=1.5))),
             dv.speed(hero(base_speed=25, rules_settings=rules(speed_multiplier=0.5)))))
S.case("g-rest-regen", "rest.md: short rest free HP 2 + level = 3; multiplier 2 and bonus 1 -> 7 (HP 5 -> 12)", (8, 12))(
    lambda: tuple(run(hero(hp_current=5, rules_settings=r), ("short_rest", {})).hp_current
                  for r in (rules(), rules(rest_regen_multiplier=2, rest_regen_bonus=1))))
S.case("g-hp-regen-tick", "resources.md: hp_regen_per_tick 2 -> HP 10 -> 12; blocked by block_restore hp -> 10", (12, 10))(
    lambda: tuple(run(hero(hp_current=10, rules_settings=rules(hp_regen_per_tick=2), statuses=s), ("tick", {})).hp_current
                  for s in ((), (blocker(target=bo.BLOCK_RESTORE, block_resources=("hp",)),))))
S.case("g-overload-off", "classes_magic.md: overload_enabled false: a cast adds no overload (0) and overload 3 does not block "
       "the regen (0 -> 1)", (0, 1))(
    lambda: (run(hero(rules_settings=rules(overload_enabled=False), **CASTER), ("cast_spell", {"circle": 1})).overload,
             run(hero(balance_current=0, overload=3, rules_settings=rules(overload_enabled=False)), ("tick", {})).balance_current))
S.case("g-overload-on", "classes_magic.md: by default the cast adds overload 2 and overload blocks the regen", (2, 0))(
    lambda: (run(hero(**CASTER), ("cast_spell", {"circle": 1})).overload,
             run(hero(balance_current=0, overload=3), ("tick", {})).balance_current))

# ================================================================ H. journal
def _sequence():
    c = hero(items=(Item("sw", "sword", kind="weapon", hands=1, groups=("blades",)),), **CASTER)
    return run(c, ("start_combat", {}), ("equip_hands", {"iid": "sw"}), ("cast_spell", {"circle": 1}),
               ("take_damage", {"amount": 3}), ("tick", {}), ("end_combat", {}))


S.case("h-order", "resources.md [OWNER pkg 14 H]: commands logged in order with kind and combat round",
       ((1, "start_combat", "combat", 1), (2, "equip_hands", "item", 1), (3, "cast_spell", "spell", 1),
        (4, "take_damage", "damage", 1), (5, "tick", "combat", 2), (6, "end_combat", "combat", 0)))(
    lambda: tuple((e.seq, e.command, e.kind, e.round) for e in _sequence().log))
S.case("h-ids-numbers", "resources.md: params and results are ids and numbers (equip_hands iid sw; take_damage amount 3)",
       ({"iid": "sw"}, 3))(lambda: (_sequence().log[1].params, _sequence().log[3].params["amount"]))
S.case("h-save-load", "D11: the journal survives save/load", True)(
    lambda: (lambda c: cio.loads(cio.dumps(c)).log == c.log)(_sequence()))
S.case("h-read-only", "resources.md: a soft refusal (activation price not set) changes nothing and is not logged", 0)(
    lambda: len(run(hero(items=(Item("r", "ring", equipped=True),)), ("activate_item", {"iid": "r"})).log))
S.case("h-limit", "resources.md: log_limit 2 keeps the last two entries (seq 5, 6)", (5, 6))(
    lambda: tuple(e.seq for e in run(_sequence_limit(), ("tick", {}), ("tick", {}), ("tick", {}), ("tick", {}),
                                     ("tick", {}), ("tick", {})).log))


def _sequence_limit():
    return hero(rules_settings=rules(log_limit=2), in_combat=True, combat_round=1)   # a tick changes the round


S.case("h-rest-status-injury", "resources.md: rests, statuses, injuries, stance, pools are logged with their kinds",
       ("status", "injury", "charges", "stance", "rest"))(
    lambda: tuple(e.kind for e in run(hero(feats=(Feat("st", is_stance=True),), pools=(pool("ki", 3),), trauma=10, temp_hp=2),
                                      ("add_status", {"status": Status("s", sid="s")}), ("add_injury", {"name": "cut"}),
                                      ("spend_pool", {"pid": "ki"}), ("set_active_stance", {"fid": "st"}),
                                      ("short_rest", {})).log))

if __name__ == "__main__":
    sys.exit(S.run())
