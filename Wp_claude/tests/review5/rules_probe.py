"""Review 5 / area 1: RULES examples of packages 16-25 recomputed by hand and checked through the Session.
Every expected number below is from the RULES text (file / section in the label), not from the code.
Also: every int constant set to 0 and to -1 (hostile but schema-valid?) must not make a view raise.
Run: python Wp_claude/tests/review5/rules_probe.py"""
from dataclasses import replace

from common import CONSTS, all_views, drop, temp_session
from wp.catalog import store as cs
from wp.core import effects as ef
from wp.core.damage import Pool
from wp.model import attack_view as av
from wp.model import classes as klass
from wp.model import derived_view as dv
from wp.model.character import Ability, Character
from wp.rules_data import rules as rd

RESULTS = []


def check(label, expected, actual):
    ok = expected == actual
    RESULTS.append(ok)
    print("%s %-70s expected %r got %r" % ("OK  " if ok else "FAIL", label, expected, actual))


def plain(hp=8, **kw):
    ab = {a: Ability(base=10) for a in ("str", "dex", "con", "int", "wis", "cha")}
    base = dict(level=1, hp_rolls=(hp,), hit_die=10, hp_current=hp, abilities=ab, bp_current=0, balance_current=0)
    base.update(kw)
    return Character(**base)


def with_fx(*effects, **kw):
    return replace(plain(**kw), statuses=(ef.Status("buff", sid="buff", effects=tuple(effects), active=True),))


def hp_after(ch, **hit):
    s = temp_session(ch)
    s.dispatch("take_damage", **hit)
    v = s.character.hp_current
    drop(s)
    return v


def damage():
    check("resources.md DR 3, 10 physical: HP 8 -> 1", 1, hp_after(with_fx(ef.Effect("dr", 3)), amount=10))
    check("resources.md DR 3, 10 fire: HP 8 -> -2", -2, hp_after(with_fx(ef.Effect("dr", 3)), amount=10, dtype="fire"))
    check("resources.md resist fire 5, 10 fire: HP 8 -> 3", 3,
          hp_after(with_fx(ef.Effect("resist:fire", 5)), amount=10, dtype="fire"))
    check("resources.md 8 slashing + 3 fire, DR 3, resist fire 2 -> 6 damage", 8 - 6,
          hp_after(with_fx(ef.Effect("dr", 3), ef.Effect("resist:fire", 2)), amount=0,
                   parts=((8, "slashing"), (3, "fire"))))
    check("resources.md DR 1/- stacking + DR 10/piercing = 11 (12 piercing -> 1 dmg)", 7,
          hp_after(with_fx(ef.Effect("dr", 1, stacks=True), ef.Effect("dr", 10)), amount=12, dtype="piercing"))
    check("defense.md cold -100: 10 -> 0", 8, hp_after(with_fx(ef.Effect("percent:cold", -100)), amount=10, dtype="cold"))
    check("defense.md fire +50: 10 -> 15 (HP 20 -> 5)", 5,
          hp_after(with_fx(ef.Effect("percent:fire", 50), hp=20, hit_die=20), amount=10, dtype="fire"))
    check("defense.md +50 and -25 -> +50 (HP 20 -> 5)", 5,
          hp_after(with_fx(ef.Effect("percent:fire", 50), ef.Effect("percent:fire", -25), hp=20, hit_die=20),
                   amount=10, dtype="fire"))
    check("defense.md +25 and -50 -> -50 (HP 20 -> 15)", 15,
          hp_after(with_fx(ef.Effect("percent:fire", 25), ef.Effect("percent:fire", -50), hp=20, hit_die=20),
                   amount=10, dtype="fire"))
    check("defense.md resist fire 2 then +50: (10-2)*1.5 = 12 (HP 20 -> 8)", 8,
          hp_after(with_fx(ef.Effect("resist:fire", 2), ef.Effect("percent:fire", 50), hp=20, hit_die=20),
                   amount=10, dtype="fire"))
    check("defense.md 5 fire with +50 -> 7.5 -> 8 (HP 8 -> 0)", 0,
          hp_after(with_fx(ef.Effect("percent:fire", 50)), amount=5, dtype="fire"))
    # a damage part of an unknown type: refused or counted as physical?
    s = temp_session(with_fx(ef.Effect("dr", 3)))
    r = s.dispatch("take_damage", amount=10, dtype="nope")
    print("INFO unknown damage type 'nope': ok=%s reason=%s HP %d (DR 3 physical)" % (r.ok, r.reason,
                                                                                     s.character.hp_current))
    r = s.dispatch("take_damage", amount=1, skip="../../etc")
    print("INFO skip given as a plain string: ok=%s reason=%s" % (r.ok, r.reason))
    drop(s)


def balance_cap():
    # resources.md: balance 6/6, hit 5 -> 1/6, then cap 5 -> 1/5. Balance max = armor + current BP + bonuses.
    ch = plain(hp=30, hit_die=30, bp_current=6, balance_current=6)
    s = temp_session(ch)
    m0 = dv.balance_max(s.character)
    s.dispatch("start_combat")
    s.dispatch("take_damage", amount=5)
    with rd.using(s.character):
        check("resources.md balance 6/6 (max seen %d), hit 5 -> balance 1, cap 5" % m0, (1, 5),
              (s.character.balance_current, dv.balance_max(s.character)))
    # fully blocked by temp HP: cap does not drop
    s.dispatch("set_temp_hp", value=10)
    s.dispatch("take_damage", amount=4)
    with rd.using(s.character):
        check("resources.md hit fully blocked by temp HP: cap stays 5", 5, dv.balance_max(s.character))
    drop(s)
    # pay_hp_cost: balance 7, cost 9 -> balance 0, HP unchanged, OT +2, pain +1, cap 7
    s = temp_session(plain(hp=30, hit_die=30, bp_current=7, balance_current=7))
    s.dispatch("start_combat")
    hp0, ot0 = s.character.hp_current, s.character.trauma
    with rd.using(s.character):
        pain0 = dv.pain_total(s.character)
    s.dispatch("pay_hp_cost", amount=9)
    c = s.character
    with rd.using(c):
        check("resources.md pay_hp_cost 9 at balance 7: (bal, HP same, OT+, pain+, cap)", (0, True, 2, 1, 7),
              (c.balance_current, c.hp_current == hp0, c.trauma - ot0, dv.pain_total(c) - pain0, dv.balance_max(c)))
    drop(s)


def mana():
    s = temp_session(replace(plain(), mana=Pool(2, 10), mana_enabled=True))
    s.dispatch("restore_mana", amount=5)
    a = s.character.mana.current
    s.dispatch("restore_mana", amount=20)
    b = s.character.mana.current
    s.dispatch("set_value", resource="mana", value=12)
    s.dispatch("restore_mana", amount=3)
    c = s.character.mana.current
    check("classes_magic.md restore_mana 2/10 +5 -> 7; +20 -> 10; 12/10 stays 12", (7, 10, 12), (a, b, c))
    r = s.dispatch("restore_mana", amount=2.7)
    print("INFO restore_mana amount 2.7: ok=%s, mana %r (int() truncation, no refusal)" % (r.ok, s.character.mana.current))
    drop(s)


def iterative():
    from wp.model.character import AttackRecord, Item
    sw = Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("blades",))
    ch = replace(plain(), items=(sw,), attacks=(AttackRecord("r", "sw", "blades", primary=True),), in_combat=True,
                 combat_round=1)
    s = temp_session(ch)
    pens = []
    for _ in range(3):
        pens.append(s.view("attacks")[0].iterative)
        s.dispatch("use_attack", rid="r")
    check("combat.md 3 attacks 0 / -5 / -10", [0, -5, -10], pens)
    s.dispatch("set_iterative_count", n=2)
    check("combat.md manual set 2 -> -10", -10, s.view("attacks")[0].iterative)
    s.dispatch("add_status", status=ef.Status("calm", sid="it", effects=(ef.Effect("iterative_penalty", 2),)),
               active=True)
    check("combat.md reduction 2 at count 2 -> -6", -6, s.view("attacks")[0].iterative)
    s.dispatch("set_rule_setting", key="tick.max_order_items", value=1) if False else None
    drop(s)


def classes():
    lay = cs.load_layers("classes", "_none_")
    s = temp_session(replace(plain(level=5, hp_rolls=(10, 5, 5, 5, 5)), bab=0))
    r = s.dispatch("set_class", class_id="sample_fighter", catalog=lay)
    with rd.using(s.character):
        c = s.character
        check("progression.md fighter lvl 5: BAB 5, fort good 4, ref poor 1 (ok=%s)" % r.ok, (5, 4, 1),
              (klass.bab(c), klass.save_base(c, "fort"), klass.save_base(c, "ref")))
    s.dispatch("set_class", class_id="sample_cleric", catalog=lay)
    with rd.using(s.character):
        check("progression.md cleric (medium) lvl 5: BAB floor(3.75)=3", 3, klass.bab(s.character))
    s.dispatch("set_class", class_id="sample_mage", catalog=lay)
    with rd.using(s.character):
        check("progression.md mage (poor) lvl 5: BAB floor(2.5)=2, will good 4", (2, 4),
              (klass.bab(s.character), klass.save_base(s.character, "will")))
    s.dispatch("set_bab_override", value=7)
    with rd.using(s.character):
        check("progression.md override wins: 7", 7, klass.bab(s.character))
    # snapshot: editing the catalog after set_class does not change the character
    from wp.catalog import catalog_cmds as cc
    lay2 = cc.catalog_dispatch(lay, "catalog_edit_entry", eid="sample_mage", bab_growth="good").state
    with rd.using(s.character):
        check("classes.md snapshot: catalog edit after set_class -> BAB still the override 7", 7, klass.bab(s.character))
    s.dispatch("set_bab_override", value=None)
    with rd.using(s.character):
        check("classes.md snapshot: catalog mage edited to good -> character keeps poor 2", 2, klass.bab(s.character))
    # level up beyond the hit die
    r = s.dispatch("level_up", hp_roll=7)
    print("INFO mage (d6) level_up hp_roll 7: ok=%s reason=%s" % (r.ok, r.reason))
    # BAB from a class feeds the attack
    r = s.dispatch("set_class", class_id="nope", catalog=lay2)
    print("INFO set_class unknown id: ok=%s reason=%s" % (r.ok, r.reason))
    r = s.dispatch("set_class", class_id="sample_mage", catalog=None)
    print("INFO set_class without a catalog: ok=%s reason=%s" % (r.ok, r.reason))
    drop(s)


def hit_dice():
    ab = {a: Ability(base=10) for a in ("str", "dex", "int", "wis", "cha")}
    ab["con"] = Ability(base=6)          # mod -2
    ch = replace(plain(level=3, hp_rolls=(10, 2, 1)), abilities=ab)
    s = temp_session(ch)
    with rd.using(s.character):
        check("progression.md hit dice 10,2,1 with Con -2: max(1,8)+max(1,0)+max(1,-1) = 10", 10,
              dv.hp_max(s.character))
    s.dispatch("add_status", status=ef.Status("tpl", sid="xd", effects=(ef.Effect("extra_hit_dice", 3),)), active=True)
    with rd.using(s.character):
        check("progression.md extra hit die 3 with Con -2 -> +1 -> 11", 11, dv.hp_max(s.character))
    drop(s)


def constants_zero():
    bad = []
    for c in CONSTS:
        if c["type"] != "int":
            continue
        for v in (0, -1):
            s = temp_session()
            s.dispatch("start_combat")
            r = s.dispatch("set_rule_setting", key=c["id"], value=v)
            if not r.ok:
                drop(s)
                continue
            views = all_views(s)
            raised = [k for k, x in views.items() if isinstance(x, tuple) and x and x[0] == "RAISED"]
            cmds = []
            for cmd, kw in (("tick", {}), ("take_damage", {"amount": 6}), ("short_rest", {}), ("long_rest", {}),
                            ("level_up", {"hp_roll": 5}), ("cast_spell", {"circle": 1})):
                try:
                    s.dispatch(cmd, **kw)
                except Exception as e:  # noqa: BLE001
                    cmds.append("%s:%s" % (cmd, type(e).__name__))
            if raised or cmds:
                bad.append((c["id"], v, raised[:3], cmds[:3], views[raised[0]][1] if raised else ""))
            drop(s)
    print("constants set to 0 / -1 accepted by set_rule_setting and then crashing a view or a command: %d" % len(bad))
    for b in bad:
        print("  %s = %d: views %s %s commands %s" % (b[0], b[1], b[2], b[4], b[3]))


def cells():
    s = temp_session()
    v = s.view("defense")["cells"]
    m = {int(k): [x["ac"] for x in c["variants"] if x["id"] == "melee"][0] for k, c in v.items()}
    check("ac_zones.md left heavy shield +2 covers 1,2,3,4,7 (not 6, 9); cell 8 loses Dex +1 and shield",
          (17, 17, 17, 17, 15, 17, 14, 15), tuple(m[k] for k in (1, 2, 3, 4, 6, 7, 8, 9)))
    par = {int(k): [x["id"] for x in c["variants"]] for k, c in v.items()}
    check("ac_zones.md melee_parry only in cells 1-3", [1, 2, 3], sorted(k for k, ids in par.items()
                                                                          if "melee_parry" in ids))
    ranged = {int(k): [x["ac"] for x in c["variants"] if x["id"] == "ranged"][0] for k, c in v.items()}
    check("ac_zones.md ranged keeps the shield where it covers (= melee without parry)", m, ranged)
    r = s.dispatch("move_hand_item", iid="sh", side="right", swap=True)
    v2 = s.view("defense")["cells"]
    m2 = {int(k): [x["ac"] for x in c["variants"] if x["id"] == "melee"][0] for k, c in v2.items()}
    cov = sorted(k for k in m2 if m2[k] == 17)
    print("INFO shield moved to the right hand (ok=%s): cells with the shield %s (left was [1, 2, 3, 4, 7])" % (r.ok, cov))
    s.dispatch("add_status", status=ef.Status("c6", sid="c6", effects=(ef.Effect("ac", 3, "luck", cells=(6,)),)),
               active=True)
    v3 = s.view("defense")["cells"]
    m3 = {int(k): [x["ac"] for x in c["variants"] if x["id"] == "melee"][0] for k, c in v3.items()}
    check("ac_zones.md cell-scoped luck +3 in cell 6 only", {k: m2[k] + (3 if k == 6 else 0) for k in m2}, m3)
    modes = s.view("defense")["modes"]
    print("INFO old modes after the cell-6 effect: %s (flank = cell 6 preset)" % (modes,))
    drop(s)


def tick_order():
    st = ef.Status("bleed", sid="bleed", per_tick_hp=-4, duration=ef.TICKS, full_ticks=3, active=True, remaining=3)
    ch = replace(plain(hp=30, hit_die=30, bp_current=5, balance_current=3), statuses=(st,), in_combat=True,
                 combat_round=1)
    s = temp_session(ch)
    with rd.using(s.character):
        regen = dv.balance_regen(s.character)
        cap = dv.balance_max(s.character)
    ot0 = s.character.trauma
    s.dispatch("tick")
    c = s.character
    exp_bal = max(0, min(cap, 3 + regen) - 4)
    exp_ot = max(0, 4 - min(cap, 3 + regen))
    check("resources.md tick: balance 3 (cap %d), regen %d, bleed -4 -> regen first: balance, OT" % (cap, regen),
          (exp_bal, exp_ot), (c.balance_current, c.trauma - ot0))
    drop(s)


def spellbook_price():
    lay = cs.load_layers("classes", "_none_")
    s = temp_session(replace(plain(level=3, hp_rolls=(6, 3, 3)), training=1000, caster="mage"))
    s.dispatch("set_class", class_id="sample_mage", catalog=lay)
    t0 = s.character.training
    r = s.dispatch("learn_spell", name="bolt", circle=2)
    check("training.md circle 2 -> 60, with a book (class spellbook) 30 (ok=%s %s)" % (r.ok, r.reason), 30,
          t0 - s.character.training)
    drop(s)


if __name__ == "__main__":
    damage()
    balance_cap()
    mana()
    iterative()
    classes()
    hit_dice()
    cells()
    tick_order()
    spellbook_price()
    constants_zero()
    print("rules probe: %d checks, %d failed" % (len(RESULTS), RESULTS.count(False)))
