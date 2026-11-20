"""Package 16 (part A-C): review 4 fixes, effect targets of sheet numbers, edit commands, refusal reasons, long rest in
combat, pools over max, read-only dicts, circles 0-9, iterative attacks.
Expected numbers are computed by hand from RULES and the owner's package 16 decisions.
Run: python Wp_claude/tests/model/test_pkg16a.py"""
import ast
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import ROOT, Suite  # noqa: E402

from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import magic as mg  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.weapons import Weapon  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import maneuver_view as mv  # noqa: E402
from wp.model import pool_view as pv  # noqa: E402
from wp.model import stats_view as stv  # noqa: E402
from wp.model.character import (ABILITIES, Ability, AttackRecord, Character, Item, ResourcePool,  # noqa: E402
                                RulesSettings, Usage, WeaponEntry)
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_pkg16a")


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def reason(ch, name, /, **kw):
    """The refusal reason id, and whether the state stayed the same (a refusal never changes anything)."""
    try:
        dispatch(ch, name, **kw)
    except CommandError as e:
        return e.reason
    return "allowed"


def abil(**scores):
    return {a: Ability(base=scores.get(a, 10)) for a in ABILITIES}


def hero(**kw):
    base = dict(hp_rolls=(8,), hp_current=8, spirit_current=5, balance_current=5, bp_current=2, training=1000)
    base.update(kw)
    return Character(**base)


def buff(*effects, name="buff"):
    return Status(name, sid=name, effects=tuple(effects))


def with_buff(*effects, **kw):
    return hero(statuses=(buff(*effects),), **kw)


# ================================================================ A1 bugs
S.case("a1-circle-10", "pkg 16 A1: cast_spell circle 10 -> CommandError circle_out_of_range (no IndexError)",
       "circle_out_of_range")(lambda: reason(hero(caster=mg.MAGE, mana=Pool(10, 10), level=5), "cast_spell", circle=10))
S.case("a1-circle-minus", "pkg 16 B: circle -1 refused too", "circle_out_of_range")(
    lambda: reason(hero(caster=mg.MAGE, mana=Pool(10, 10), level=5), "cast_spell", circle=-1))


def _twf():
    items = (Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("blades",)),
             Item("dg", "dagger", kind="weapon", hands=1, in_hands=True, groups=("blades",)))
    attacks = (AttackRecord("r1", "sw", "blades", twf=True, twf_off="r2"), AttackRecord("r2", "dg", "blades", grip="off"))
    ch = run(hero(items=items, attacks=attacks), ("remove_item", {"iid": "dg"}))
    return tuple((r.rid, r.twf, r.twf_off) for r in ch.attacks)


S.case("a1-twf-cleanup", "pkg 16 A1 (F6): removing the off-hand item clears the two-weapon link of the main record",
       (("r1", False, ""),))(_twf)
S.case("a1-noop-not-logged", "resources.md: commands that change nothing are not logged (take_damage 0, restore hp at max, "
       "a quiet tick)", 0)(
    lambda: len(run(hero(), ("take_damage", {"amount": 0}), ("restore", {"resource": "hp", "amount": 3}), ("tick", {})).log))
S.case("a1-change-logged", "resources.md: a real change is logged once", 1)(
    lambda: len(run(hero(), ("take_damage", {"amount": 2})).log))


def ring(cur=1):
    return Item("ring", "ring", equipped=True, usage=Usage(charges_max=3, charges_current=cur))


S.case("a1-set-charges-above-max", "gear.md set_charges: 0..max; 4 of max 3 refused, 3 allowed",
       ("charges_must_0", 3))(
    lambda: (reason(hero(items=(ring(),)), "set_charges", owner_kind="item", owner_id="ring", value=4),
             run(hero(items=(ring(),)), ("set_charges", {"owner_kind": "item", "owner_id": "ring", "value": 3})).items[0]
             .usage.charges_current))


def _no_tags():
    ch = run(hero(items=(Item("ax", "axe", kind="weapon", hands=1, in_hands=True, groups=("axes",)),),
                  attacks=(AttackRecord("r_ax", "ax", "axes"),)), ("add_maneuver", {"name": "Trip"}))
    v = mv.maneuver_view(ch)[0]
    return v.available, tuple(e.item for e in v.weapons)


S.case("a1-maneuver-no-tags", "combat.md (Q79): a maneuver without tags fits every held weapon (the axe)",
       (True, ("ax",)))(_no_tags)

# ================================================================ A2 effect targets
S.case("a2-stat-str", "buffs.md:6-7 +4 Str (enhancement): Str 10 -> 14, mod +2; CMB = BAB 0 + 2 = 2", (14, 2, 2))(
    lambda: (lambda c: (dv.ability_current(c, "str"), dv.ability_mod(c, "str"), stv.cmb(c).total))(
        with_buff(Effect("stat:str", 4, "enhancement"))))
S.case("a2-stat-stacking", "defense.md stacking: enhancement +4 and +2 -> +4; untyped +1 adds -> Str 15, mod +2", (15, 2))(
    lambda: (lambda c: (dv.ability_current(c, "str"), dv.ability_mod(c, "str")))(
        with_buff(Effect("stat:str", 4, "enhancement"), Effect("stat:str", 2, "enhancement"), Effect("stat:str", 1))))
S.case("a2-stat-con-hp", "progression.md: Con +4 -> mod +2; HP = max(1, 8 + 2) = 10", 10)(
    lambda: dv.hp_max(with_buff(Effect("stat:con", 4, "enhancement"))))
S.case("a2-stat-blocked", "buffs.md block_bonus enhancement on scope stat:str: the +4 is dropped -> Str 10", 10)(
    lambda: dv.ability_current(with_buff(Effect("stat:str", 4, "enhancement"),
                                         Effect("block_bonus", block_type="enhancement", block_scope=("stat:str",))), "str"))
S.case("a2-stat-penalty", "buffs.md: -4 Str (stat damage effect) -> Str 6, mod -2", (6, -2))(
    lambda: (lambda c: (dv.ability_current(c, "str"), dv.ability_mod(c, "str")))(with_buff(Effect("stat:str", -4))))
S.case("a2-hp-max", "pkg 16 A2: hp_max +5 -> 8 + 5 = 13; BP max = ceil(13 / 4) = 4", (13, 4))(
    lambda: (lambda c: (dv.hp_max(c), dv.bp_max(c)))(with_buff(Effect("hp_max", 5))))
S.case("a2-bp-max", "pkg 16 A2: bp_max +2 -> ceil(8 / 4) + 2 = 4", 4)(lambda: dv.bp_max(with_buff(Effect("bp_max", 2))))
S.case("a2-balance", "rest.md: balance max = armor 0 + BP 2 + effect 3 = 5; regen = level 1 + Con 0 + 2 = 3", (5, 3))(
    lambda: (lambda c: (dv.balance_max(c), dv.balance_regen(c)))(
        with_buff(Effect("balance_max", 3), Effect("balance_regen", 2))))
S.case("a2-spirit", "resources.md: spirit 5 + 5 * Cha 0 = 5, + effect 3 = 8", 8)(lambda: dv.spirit_max(with_buff(Effect("spirit_max", 3))))
S.case("a2-mana", "pkg 16 A2: mana 2/4 + mana_max 2 -> max 6; restore 10 -> 6; the stored max stays 4", (6, 6, 4))(
    lambda: (lambda c: (dv.mana_max(c), c.mana.current, c.mana.max))(
        run(with_buff(Effect("mana_max", 2), mana=Pool(2, 4), mana_enabled=True),
            ("restore", {"resource": "mana", "amount": 10}))))
S.case("a2-mana-rest", "classes_magic.md: the long rest restores mana to the max with the effect: 0/4 + 2 -> 6; stored max 4",
       (6, 4))(
    lambda: (lambda c: (c.mana.current, c.mana.max))(
        run(with_buff(Effect("mana_max", 2), mana=Pool(0, 4), mana_enabled=True, caster=mg.MAGE), ("long_rest", {}))))
S.case("a2-slots", "pkg 16 A2: circle-1 slots 0/2 + slots:1 +1 -> max 3", 3)(
    lambda: dv.slot_pool(with_buff(Effect("slots:1", 1), slots={1: Pool(0, 2)}), 1).max)
S.case("a2-pool-max", "pkg 16 A2: Ki max 3 + pool_max:ki 2 -> 5", 5)(
    lambda: pv.max_of(with_buff(Effect("pool_max:ki", 2)), ResourcePool("ki", "Ki", 3, 3)))
S.case("a2-comfort", "training.md: comfort max 5 + 5 * 1 = 10, + 2 = 12", 12)(lambda: dv.comfort_max(with_buff(Effect("comfort_max", 2))))
S.case("a2-parry-maxdex", "pkg 16 A2: parry 0 + 1 = 1; armor max Dex 2 + 1 = 3", (1, 3))(
    lambda: (lambda i: (i.parry, i.max_dex))(dv.ac_input(with_buff(
        Effect("parry", 1), Effect("max_dex", 1), items=(Item("mail", "mail", equipped=True, armor=4, max_dex=2),)))))
S.case("a2-counts", "pkg 16 A2: reactions 1 + 1 = 2; base slots 5 + 2 = 7; attention per cycle 1 + 0 + 1 = 2", (2, 7, 2))(
    lambda: (lambda c: (dv.reactions(c), dv.base_slots(c), dv.attention_per_cycle(c)))(
        with_buff(Effect("reactions", 1), Effect("base_slots", 2), Effect("attention_per_cycle", 1))))
S.case("a2-armor-penalty", "pkg 16 A2: armor skill penalty -3 + 2 = -1; + 5 -> 0 (never above 0)", (-1, 0))(
    lambda: tuple(dv.armor_skill_penalty(with_buff(Effect("armor_skill_penalty", n),
                                                   items=(Item("mail", "mail", equipped=True, armor=4, skill_penalty=-3),)))
                  for n in (2, 5)))
S.case("a2-load", "gear.md: 65 L with Str mod 0 -> heavy (light up to 59); load_mod +1 -> light (up to 69)", ("heavy", "light"))(
    lambda: tuple(dv.load_status(hero(items=(Item("bag", "sack", weight_l=65),), statuses=st)) for st in
                  ((), (buff(Effect("load_mod", 1)),))))


def _sword(*statuses, **kw):
    return hero(items=(Item("sw", "sword", kind="weapon", hands=1, in_hands=True, groups=("blades",), crit_mult=2),),
                attacks=(AttackRecord("r1", "sw", "blades", **kw),), weapons=(WeaponEntry(Weapon("blades")),),
                statuses=statuses)


S.case("a2-crit-mult", "pkg 16 A2: crit x2 + crit_mult 1 -> x3", 3)(
    lambda: av.attack(_sword(buff(Effect("crit_mult", 1))), _sword().attacks[0]).crit_mult)
S.case("a2-removed-source", "pkg 16 A2: removing the status takes the +4 Str away again -> Str 10", 10)(
    lambda: dv.ability_current(run(with_buff(Effect("stat:str", 4)), ("delete_status", {"sid": "buff"})), "str"))

# ================================================================ A3 edit commands
S.case("a3-edit-sheet", "pkg 16 A3: edit mode sets any value without limits (training -50, level 25)", (-50, 25))(
    lambda: (lambda c: (c.training, c.level))(run(hero(), ("edit_sheet", {"training": -50, "level": 25}))))
S.case("a3-edit-ability", "pkg 16 A3: Str base 30 in edit mode -> mod +10", 10)(
    lambda: dv.ability_mod(run(hero(), ("edit_ability", {"name": "str", "base": 30})), "str"))
S.case("a3-rename", "pkg 16 A3: rename an item keeps its id", ("sw", "Blade"))(
    lambda: (lambda it: (it.iid, it.name))(run(_sword(), ("edit_entry", {"collection": "items", "oid": "sw", "name": "Blade"}))
                                          .items[0]))
S.case("a3-add-remove", "pkg 16 A3: add a feat by record (id from the title), then delete it", ("power", 0))(
    lambda: (lambda c: (c.feats[0].fid, len(run(c, ("remove_entry", {"collection": "feats", "oid": "power"})).feats)))(
        run(hero(), ("add_entry", {"collection": "feats", "record": __import__("wp.model.character", fromlist=["Feat"]).Feat(
            "", title="Power")}))))
S.case("a3-id-fixed", "D7: an id cannot be edited", "id_not_editable")(
    lambda: reason(_sword(), "edit_entry", collection="items", oid="sw", iid="x"))
S.case("a3-rules", "pkg 16 A3: rules_settings by command: iterative step -4", -4)(
    lambda: run(hero(), ("edit_rules", {"iterative_step": -4})).rules_settings.iterative_step)
S.case("a3-bad-formula", "buffs.md: a broken formula is refused in edit mode too", "bad_effect_formula")(
    lambda: reason(_sword(), "edit_entry", collection="items", oid="sw", effects_on=(Effect("attack", "level +"),)))
S.case("a3-no-log-edit", "D5: edit_sheet cannot touch the journal", "not_a_sheet_value")(
    lambda: reason(hero(), "edit_sheet", log=()))


# ================================================================ A4 reason ids
def _static():
    """Every CommandError(...) raised in wp/ gives a reason id (2nd argument or reason=...)."""
    missing = []
    for path in glob.glob(os.path.join(ROOT, "wp", "**", "*.py"), recursive=True):
        tree = ast.parse(open(path, encoding="ascii").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call) and \
                    getattr(node.exc.func, "id", None) == "CommandError":
                if len(node.exc.args) < 2 and not any(k.arg == "reason" for k in node.exc.keywords):
                    missing.append("%s:%d" % (os.path.basename(path), node.lineno))
    return missing


S.case("a4-every-raise-has-reason", "pkg 16 A4: every refusal in the code carries a reason id", [])(_static)
S.case("a4-converted", "pkg 16 A4: a core ValueError (unknown rest option) and an unknown command get reason ids too",
       ("invalid_value", "unknown_command"))(
    lambda: (reason(hero(), "short_rest", spends=[("zzz", {})]), reason(hero(), "no_such_command")))
S.case("a4-params", "pkg 16 A4: params carry the numbers of the refusal: Ki need 5, have 3",
       ("not_enough_need_have", {"values": ("Ki", 5, 3)}))(
    lambda: (lambda e: (e.reason, e.params))(_catch(hero(pools=(ResourcePool("ki", "Ki", 3, 3),)), "spend_pool", pid="ki", n=5)))
S.case("a4-unchanged", "D5: a refused command leaves the state as it was", True)(
    lambda: _catch(hero(), "spend_bp", n=9) is not None and hero() == hero())


def _catch(ch, name, **kw):
    try:
        dispatch(ch, name, **kw)
    except CommandError as e:
        return e
    return None


# ================================================================ A5 long rest in combat
S.case("a5-refused", "pkg 16 A5: long_rest during combat -> combat_active", "combat_active")(
    lambda: reason(hero(in_combat=True, combat_round=2), "long_rest"))
S.case("a5-end-then-rest", "pkg 16 A5: long_rest_end_combat: combat ends (round 0, overload 0) and HP 3 -> 8",
       (False, 0, 0, 8))(
    lambda: (lambda c: (c.in_combat, c.combat_round, c.overload, c.hp_current))(
        run(hero(in_combat=True, combat_round=3, overload=2, hp_current=3), ("long_rest_end_combat", {}))))

# ================================================================ A6 pools over max
S.case("a6-over-max", "resources.md Over max: Ki 5 of max 3 is shown as 5; restore_pool keeps 5; spend 1 -> 4", (5, 5, 4))(
    lambda: (lambda ch: (pv.current(ch, ch.pools[0]),
                         run(ch, ("restore_pool", {"pid": "ki"})).pools[0].current,
                         run(ch, ("spend_pool", {"pid": "ki", "n": 1})).pools[0].current))(
        hero(pools=(ResourcePool("ki", "Ki", 3, 5),))))


# ================================================================ A7 read-only dicts
def _frozen():
    ch = hero()
    try:
        ch.abilities["str"] = Ability(base=20)
        return "changed"
    except TypeError:
        pass
    st = Status("x", sid="x", per_tick_restore={"mana": 1})
    try:
        st.per_tick_restore["mana"] = 5
        return "changed"
    except TypeError:
        return (type(ch.abilities).__name__, cio.loads(cio.dumps(hero(slots={1: Pool(1, 2)}))) == hero(slots={1: Pool(1, 2)}))


S.case("a7-frozen", "pkg 16 A7: dicts inside the frozen sheet cannot be changed in place; JSON save/load unchanged",
       ("FrozenDict", True))(_frozen)

# ================================================================ B circles
S.case("b-circles", "pkg 16 B: circles 0..9 only", tuple(range(10)))(lambda: mg.CIRCLES)
S.case("b-learn-10", "pkg 16 B: learn_spell circle 10 refused", "circle_must_0_9")(
    lambda: reason(hero(), "learn_spell", name="x", circle=10))


# ================================================================ C iterative attacks
def _series(ch, n=3, rid="r1"):
    out = []
    for _ in range(n):
        rec = next(r for r in ch.attacks if r.rid == rid)
        out.append(av.attack(ch, rec).iterative)
        ch = run(ch, ("use_attack", {"rid": rid}))
    return tuple(out)


S.case("c-default", "combat.md: 3 attacks -> 0 / -5 / -10", (0, -5, -10))(lambda: _series(_sword()))
S.case("c-reduction", "pkg 16 C: effect iterative_penalty 2 -> 0 / -3 / -6", (0, -3, -6))(
    lambda: _series(_sword(buff(Effect("iterative_penalty", 2)))))
S.case("c-tick-reset", "pkg 16 C: two attacks, then the zero-initiative tick -> the next attack has 0 again", 0)(
    lambda: av.attack(run(_sword(), ("use_attack", {"rid": "r1"}), ("use_attack", {"rid": "r1"}), ("tick", {})),
                      _sword().attacks[0]).iterative)
S.case("c-end-combat-reset", "pkg 16 C: end_combat resets the series", 0)(
    lambda: run(replace_ch(_sword(), in_combat=True, combat_round=1), ("use_attack", {"rid": "r1"}), ("end_combat", {}))
    .iterative_count)
S.case("c-manual", "pkg 16 C: set_iterative_count 2 -> the next attack -10", -10)(
    lambda: av.attack(run(_sword(), ("set_iterative_count", {"n": 2})), _sword().attacks[0]).iterative)
S.case("c-record-step", "pkg 16 C: a record with its own step -3 -> 0 / -3 / -6", (0, -3, -6))(
    lambda: _series(_sword(iterative_step=-3)))
S.case("c-settings-step", "pkg 16 C: rules_settings.iterative_step -4 -> 0 / -4 / -8", (0, -4, -8))(
    lambda: _series(replace_ch(_sword(), rules_settings=RulesSettings(iterative_step=-4))))
S.case("c-ignores", "buffs.md: a status that ignores the iterative penalty -> 0 / 0", (0, 0))(
    lambda: _series(_sword(Status("flow", sid="flow", ignores_iterative=True)), 2))
def _line():
    first = av.attack(_sword(), _sword().attacks[0])
    second = av.attack(run(_sword(), ("use_attack", {"rid": "r1"})), _sword().attacks[0])
    lines = [x.value for x in second.to_hit_lines if x.label == "iterative"]
    return lines, second.to_hit - first.to_hit, [x.label for x in first.to_hit_lines if x.label == "iterative"]


S.case("c-line", "pkg 16 C: the iterative part is its own to-hit line (-5) and lowers the total by 5; none on the first",
       ([-5], -5, []))(_line)
S.case("c-refusals", "pkg 16 C: negative count / unknown record refused", ("iterative_count_negative", "no_attack_record"))(
    lambda: (reason(_sword(), "set_iterative_count", n=-1), reason(_sword(), "use_attack", rid="nope")))
S.case("c-save", "D11: the iterative count and the record step survive save / load", (2, -3))(
    lambda: (lambda c: (c.iterative_count, c.attacks[0].iterative_step))(
        cio.loads(cio.dumps(run(_sword(iterative_step=-3), ("set_iterative_count", {"n": 2}))))))


def replace_ch(ch, **kw):
    from dataclasses import replace
    return replace(ch, **kw)


if __name__ == "__main__":
    sys.exit(S.run())
