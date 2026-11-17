# -*- coding: utf-8 -*-
"""Baseline: numeric examples from Wp_claude/RULES/*.md run against the
legacy code at repo root (character.py, purchases.py, modifiers.py).

One test = one example. Each test FAILS on a wrong result.

Run as a script (no pytest needed):
    python Wp_claude/tests/test_rules_baseline.py
    -> prints a markdown table, exit code 1 if any case failed.
Run with pytest (if installed):
    python -m pytest Wp_claude/tests/test_rules_baseline.py

Code files are ASCII only (CLAUDE.md), so all text here is English.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import character as ch  # noqa: E402
import purchases as pu  # noqa: E402
import modifiers as mo  # noqa: E402


class NotImplementedInCode(Exception):
    """The function the rule needs does not exist in the legacy code."""


CASES = []


def case(cid, src, rule, expected, func):
    def deco(fn):
        CASES.append({"id": cid, "src": src, "rule": rule,
                      "expected": expected, "func": func, "fn": fn})
        return fn
    return deco


def new_char(level=1, hp_rolls=None, **abil):
    c = ch.Character("test")
    c.char_class["level"] = level
    c.char_class["hp_rolls"] = list(hp_rolls or [8] * level)
    for k, v in abil.items():
        c.abilities[k] = v
    c.recompute_derived()
    return c


# ---------------------------------------------------------------- defense.md

for _scale, _exp, _tag in [(3, 1, "Example"), (-4, -2, "Example"),
                           (1, 0, "Example"), (-10, -5, "formula text"),
                           (10, 5, "formula text"),
                           (-3, -1, "formula trunc(scale/2)")]:
    def _mk(scale=_scale):
        def fn():
            c = new_char()
            c.morale = scale
            return c.morale_bonus()
        return fn
    case("DEF-morale%+d" % _scale, "defense.md Morale (%s)" % _tag,
         "morale scale %d -> bonus trunc(%d/2)" % (_scale, _scale),
         _exp, "Character.morale_bonus")(_mk())


@case("DEF-enchant", "defense.md Typed bonus pools, Example",
      "+1 enchanted sword + 'magic weapon' +1 enchant -> +1, not +2",
      1, "modifiers.apply_bonus_type")
def _def_enchant():
    return mo.apply_bonus_type([{"value": 1, "type": "enhancement"},
                                {"value": 1, "type": "enhancement"}])


# -------------------------------------------------------------- resources.md

@case("RES-temphp", "resources.md HP and temp HP, Example",
      "3 temp HP, 7 damage -> temp 0, HP -4, balance -4",
      (0, -4, -4), "Character.take_damage")
def _res_temphp():
    c = new_char(hp_rolls=[30])
    c.combat["hp_current"] = 30
    c.combat["hp_temp"] = 3
    c.balance["current"] = 10
    c.take_damage(7)
    return (c.combat["hp_temp"], c.combat["hp_current"] - 30,
            c.balance["current"] - 10)


def _overflow_char():
    c = new_char(hp_rolls=[30])
    c.combat["hp_current"] = 30
    c.balance["current"] = 1
    return c


@case("RES-overflow-1", "resources.md Balance, Example [OWNER]",
      "balance 1, hit 10 -> HP -10, balance 0, trauma +9",
      (-10, 0, 9), "Character.take_damage")
def _res_overflow1():
    c = _overflow_char()
    c.take_damage(10)
    return (c.combat["hp_current"] - 30, c.balance["current"],
            c.injury_points)


@case("RES-overflow-1-pain", "resources.md Balance, Example [OWNER]",
      "balance 1, hit 10 -> pain +1 (overflow > 0)",
      1, "Character.take_damage + pain_level")
def _res_overflow1_pain():
    c = _overflow_char()
    p0 = c.pain_level()
    c.take_damage(10)
    return c.pain_level() - p0


@case("RES-overflow-3", "resources.md Balance, Example [OWNER]",
      "then hits 1 and 1 (balance 0) -> totals HP -12, trauma 11",
      (-12, 11), "Character.take_damage")
def _res_overflow3():
    c = _overflow_char()
    for d in (10, 1, 1):
        c.take_damage(d)
    return (c.combat["hp_current"] - 30, c.injury_points)


@case("RES-overflow-3-pain", "resources.md Balance, Example [OWNER]",
      "then hits 1 and 1 (balance 0) -> total pain 3",
      3, "Character.take_damage + pain_level")
def _res_overflow3_pain():
    c = _overflow_char()
    p0 = c.pain_level()
    for d in (10, 1, 1):
        c.take_damage(d)
    return c.pain_level() - p0


for _hp, _exp in [(0, 0), (-2, 0), (-5, 1), (-7, 2), (-12, 4)]:
    def _mk(hp=_hp):
        def fn():
            c = new_char(hp_rolls=[20])
            c.combat["hp_current"] = hp
            return c.pain_from_hp()
        return fn
    case("RES-hppain%d" % _hp, "resources.md Pain, Examples [OWNER]",
         "temp pain from HP at hp %d" % _hp, _exp,
         "Character.pain_from_hp")(_mk())


@case("RES-hppain-heal", "resources.md Pain, Examples [OWNER]",
      "hp -7 healed by 2 -> -5 -> temp pain 1",
      1, "Character.restore_hp + pain_from_hp")
def _res_hppain_heal():
    c = new_char(hp_rolls=[20])
    c.combat["hp_current"] = -7
    c.restore_hp(2)
    return c.pain_from_hp()


def _spell_from_editor(circle, mana_cost):
    """Spell dict as the legacy editor fills it: circle auto-fill from
    SPELL_CIRCLE_TABLE (gui_spells._auto_fill_circle), mana as the rule says.
    Legacy spells have no duration -> overload link."""
    t = ch.SPELL_CIRCLE_TABLE[circle]
    return {"name": "s", "circle": circle, "slot_circle": circle,
            "mana_cost": mana_cost, "balance_cost": t["balance"],
            "overload": t["overload"]}


def _mage():
    c = new_char(hp_rolls=[30])
    c.mana["enabled"] = True
    c.mana["max"] = 10
    c.mana["current"] = 10
    c.balance["current"] = 10
    c.overload = 0
    return c


@case("MAG-mage-4r", "classes_magic.md / resources.md Spell cost, Example",
      "mage, circle 2 (3 mana), 4 rounds -> mana -3, balance -3, overload +4",
      (-3, -3, 4), "Character.cast_spell")
def _mag_mage4():
    c = _mage()
    c.spells = [_spell_from_editor(2, 3)]
    c.cast_spell(0)
    return (c.mana["current"] - 10, c.balance["current"] - 10, c.overload)


@case("MAG-mage-inst", "classes_magic.md Spell cost, Example",
      "instant 3-mana spell -> mana -3, balance -3, overload 0",
      (-3, -3, 0), "Character.cast_spell")
def _mag_mage_inst():
    c = _mage()
    c.spells = [_spell_from_editor(2, 3)]
    c.cast_spell(0)
    return (c.mana["current"] - 10, c.balance["current"] - 10, c.overload)


def _nonmage_cast(circle):
    c = new_char(hp_rolls=[30])
    c.spell_slots_enabled = True
    c.spell_slots = {str(circle): {"current": 2, "max": 2}}
    c.balance["current"] = 10
    c.overload = 0
    c.spells = [_spell_from_editor(circle, 0)]
    c.cast_spell(0)
    return (c.spell_slots[str(circle)]["current"] - 2,
            c.balance["current"] - 10, c.overload)


@case("MAG-nonmage-3r", "classes_magic.md Spell cost, Example",
      "non-mage circle 1, 3 rounds -> slot -1, balance 0, overload +6",
      (-1, 0, 6), "Character.cast_spell")
def _mag_nonmage3():
    return _nonmage_cast(1)


@case("MAG-nonmage-4r", "resources.md Spirit/mana/overload, Example",
      "non-mage, spell lasting 4 rounds -> slot spent, balance 0, overload +8",
      (-1, 0, 8), "Character.cast_spell")
def _mag_nonmage4():
    return _nonmage_cast(2)


# ------------------------------------------------------------------- gear.md

for _str, _mod, _exp in [(10, 0, (59, 109)), (14, 2, (79, 129)),
                         (6, -2, (39, 89)), (16, 3, (89, 139)),
                         (8, -1, (49, 99))]:
    def _mk(s=_str):
        def fn():
            c = new_char(str=s)
            return (c.max_weight_light(), c.max_weight_loaded())
        return fn
    case("GEAR-load%+d" % _mod, "gear.md Weight, Examples [OWNER confirmed]",
         "Str mod %+d -> light/heavy %.1f / %.1f B (in L)"
         % (_mod, _exp[0] / 10.0, _exp[1] / 10.0),
         _exp, "Character.max_weight_light / max_weight_loaded")(_mk())


@case("GEAR-base-start", "gear.md Base [OWNER]",
      "base starts with 5 slots", 5, "Character.__init__ base.slots_max")
def _gear_base_start():
    return new_char().base["slots_max"]


@case("GEAR-base-cap", "gear.md Base [OWNER]",
      "base max = 10*level (level 2 -> 20)", 20, "purchases.buy_base_slot")
def _gear_base_cap():
    c = new_char(level=2)
    c.training["available"] = 100000
    while True:
        try:
            pu.buy_base_slot(c)
        except pu.PurchaseError:
            break
        if c.base["slots_max"] > 1000:
            break
    return c.base["slots_max"]


# ------------------------------------------------------------------- rest.md

for _hp, _exp in [(11, 3), (15, 4), (19, 5), (20, 5), (21, 6), (4, 1)]:
    def _mk(hp=_hp):
        def fn():
            c = new_char(hp_rolls=[hp])
            return c.pain_threshold["max"]
        return fn
    case("REST-bp%d" % _hp, "rest.md BP cap, Tests [OWNER]",
         "BP cap = ceil(max HP %d / 4)" % _hp, _exp,
         "Character.recompute_derived pain_threshold.max")(_mk())


def _balance_char():
    c = new_char(hp_rolls=[4])
    c.add_item(name="leather", category="armor", location="equipped",
               slot="armor", ac_type="armor", ac_bonus=2)
    c.balance_bonus = 3
    c.recompute_derived()
    return c


@case("REST-balmax", "rest.md BP and balance, Example [OWNER]",
      "4 max HP -> BP 1; leather armor 2; race +3 -> balance max 6",
      6, "Character.recompute_derived balance.max")
def _rest_balmax():
    c = _balance_char()
    c.pain_threshold["current"] = c.pain_threshold["max"]
    c.recompute_derived()
    return c.balance["max"]


@case("REST-balmax-curbp", "rest.md BP and balance, Note [confirmed]",
      "same, but current BP spent to 0 -> balance max 5 (uses CURRENT BP)",
      5, "Character.recompute_derived balance.max")
def _rest_balmax_cur():
    c = _balance_char()
    c.pain_threshold["current"] = 0
    c.recompute_derived()
    return c.balance["max"]


@case("REST-shortheal", "rest.md Short rest, Example",
      "level 3: free short-rest heal = 2+3 = +5 HP",
      5, "Character.short_rest")
def _rest_shortheal():
    c = new_char(level=3, hp_rolls=[8, 8, 8])
    c.combat["hp_current"] = 1
    r = c.short_rest()
    return r["hp"]


@case("REST-short-2nd", "rest.md Short rest, Example",
      "second HP restore in the same short rest costs 1 BP",
      1, "(BP spend menu)")
def _rest_short_2nd():
    raise NotImplementedInCode("no BP spend menu / second-restore logic")


@case("REST-tempbp", "rest.md BP and balance [OWNER]",
      "2 pain, BP 2/1, spend 2 BP to remove 2 pain -> BP 0/1, pain 0",
      (0, 1, 0), "(BP -> pain spend)")
def _rest_tempbp():
    raise NotImplementedInCode("no function spends BP to remove pain")


@case("REST-long-pain", "rest.md Long rest [OWNER]",
      "long rest removes temporary pain (pain 2 -> 0)",
      0, "Character.long_rest")
def _rest_long_pain():
    c = new_char(hp_rolls=[20])
    c.pain_extra_temp = 2
    c.long_rest()
    return c.pain_extra_temp


# -------------------------------------------------------------- injuries.md

for _sev, _exp in [("light", 2), ("medium", 5), ("heavy", 12)]:
    def _mk(sev=_sev):
        def fn():
            c = new_char()
            c.injury_points = 20
            pu.add_injury(c, sev)
            return 20 - c.injury_points
        return fn
    case("INJ-ot-%s" % _sev, "injuries.md Trauma points [OWNER]",
         "%s injury removes %d OT" % (_sev, _exp), _exp,
         "purchases.add_injury")(_mk())


@case("INJ-comfort", "injuries.md Trauma points [OWNER]",
      "1 comfort removes 3 OT", 3, "purchases.spend_comfort_for_ot")
def _inj_comfort():
    c = new_char()
    c.injury_points = 10
    c.comfort["current"] = 1
    return pu.spend_comfort_for_ot(c)


for _str, _exp in [(10, 2), (18, 4)]:
    def _mk(s=_str):
        def fn():
            c = new_char(str=s)
            c.injury_points = 10
            c.attention["current"] = 1
            return pu.spend_attention_for_ot(c)
        return fn
    case("INJ-att-str%d" % _str, "injuries.md Trauma points [OWNER]",
         "1 attention removes max(2, Str mod) OT, Str %d" % _str, _exp,
         "purchases.spend_attention_for_ot")(_mk())


for _sev, _exp in [("light", 3), ("medium", 2), ("heavy", 1)]:
    def _mk(sev=_sev):
        def fn():
            c = new_char()
            c.injury_points = 20
            return pu.add_injury(c, sev)["heal_rating"]
        return fn
    case("INJ-rl-%s" % _sev, "injuries.md Healing rating [OWNER]",
         "base RL %s = %d" % (_sev, _exp), _exp, "purchases.add_injury")(_mk())


@case("INJ-rl-att", "injuries.md Healing rating [OWNER]",
      "1 attention raises light RL 3 -> 5 (Str 10)",
      5, "purchases.upgrade_heal_rating")
def _inj_rl_att():
    c = new_char()
    c.injury_points = 20
    pu.add_injury(c, "light")
    c.attention["current"] = 1
    pu.upgrade_heal_rating(c, 0)
    return c.injuries[0]["heal_rating"]


@case("INJ-noot-back", "buffs.md Stacking flags, Test",
      "removing an injury must NOT bring OT back",
      8, "purchases.remove_injury")
def _inj_noot():
    c = new_char()
    c.injury_points = 10
    pu.add_injury(c, "light")
    pu.remove_injury(c, 0)
    return c.injury_points


# ----------------------------------------------------------- progression.md

@case("PROG-start-training", "progression.md / skills.md [OWNER]",
      "new character (level 1) has 1000 training", 1000,
      "Character.__init__ training.available")
def _prog_start():
    return new_char().training["available"]


@case("PROG-levelup", "progression.md Level up [OWNER]",
      "level up to 3 gives 100*3 = 300 training", 300, "(core level_up)")
def _prog_levelup():
    raise NotImplementedInCode(
        "no core function; formula only inside gui.py _do_level_up")


@case("PROG-spell-mastery", "progression.md Spell mastery, Example",
      "circle 2 upgrade = 25*(1+4) = 125", 125,
      "purchases.spell_mastery_cost")
def _prog_spell_mastery():
    return pu.spell_mastery_cost(2)


@case("RES-comfort-max", "resources.md Comfort [OWNER]",
      "comfort max = 5 + 5*level (level 3 -> 20)", 20, "(comfort max formula)")
def _res_comfort_max():
    c = new_char(level=3, hp_rolls=[8, 8, 8])
    if c.comfort["max"] == 10:
        raise NotImplementedInCode(
            "comfort.max is a stored number (default 10), no formula; "
            "level 3 char still has max %d" % c.comfort["max"])
    return c.comfort["max"]


# ---------------------------------------------------------------- skills.md

for _tier, _old, _new, _exp in [("normal", 0, 1, 20), ("normal", 2, 3, 60),
                                ("normal", 19, 20, 400),
                                ("advanced", 0, 1, 15),
                                ("specialized", 0, 1, 10),
                                ("specialized", 19, 20, 200)]:
    def _mk(tier=_tier, new=_new):
        def fn():
            # level 1 character; cost of the single step to the NEW rank
            return pu.skill_rank_step_cost(tier, new, 1)
        return fn
    case("SK-%s-%d-%d" % (_tier[:4], _old, _new), "skills.md Training cost, Tests [OWNER]",
         "%s rank %d->%d costs %d" % (_tier, _old, _new, _exp), _exp,
         "purchases.skill_rank_step_cost")(_mk())


def _skill(name, tier):
    return {"name": name, "stat": "int", "tier": tier, "rank": 0,
            "source": "training", "invested": 0, "mods": []}


@case("SK-2nd-adv", "skills.md Training cost, Example",
      "2nd advanced skill costs 40+20*1 = 60", 60,
      "purchases.skill_promote_cost")
def _sk_2nd_adv():
    c = new_char()
    c.skills = [_skill("a", "advanced"), _skill("b", "normal")]
    return pu.skill_promote_cost(c, "b")


@case("SK-3rd-spec", "skills.md Training cost, Example",
      "3rd specialization costs 200+50*2 = 300", 300,
      "purchases.skill_spec_cost")
def _sk_3rd_spec():
    c = new_char()
    c.skills = [_skill("a", "specialized"), _skill("b", "specialized"),
                _skill("c", "advanced")]
    return pu.skill_spec_cost(c, "c")


@case("SK-free-spec", "skills.md Creation and free grants, Example [OWNER]",
      "free specialization + buying 1 more -> second costs 250", 250,
      "purchases.apply_skill_changes(free=True) + skill_spec_cost")
def _sk_free_spec():
    c = new_char()
    c.skills = [_skill("a", "advanced"), _skill("b", "advanced")]
    pu.apply_skill_changes(c, "a", "specialized", 1, free=True)
    return pu.skill_spec_cost(c, "b")


# --------------------------------------------------------------- weapons.md

def _wpn(name, level, difficulty=1, scale=1):
    return {"name": name, "level": level, "difficulty": difficulty,
            "scale": scale, "desc": "", "bonuses": [],
            "source": "training", "invested": 0}


@case("WPN-cost-60", "weapons.md Cost of +1 grade, Example",
      "X=0, difficulty 1, scale 2 -> 60", 60, "purchases.weapon_grade_up_cost")
def _wpn_cost60():
    c = new_char()
    c.proficiencies["weapons"] = [_wpn("w", 0, 1, 2)]
    return pu.weapon_grade_up_cost(c, "w")


@case("WPN-cost-240", "weapons.md Cost of +1 grade, Example",
      "X=2, difficulty 2, scale 3 -> 240", 240, "purchases.weapon_grade_up_cost")
def _wpn_cost240():
    c = new_char()
    c.proficiencies["weapons"] = [_wpn("w", 3, 2, 3), _wpn("e1", 8),
                                  _wpn("e2", 9)]
    return pu.weapon_grade_up_cost(c, "w")


@case("WPN-basics-cost", "weapons.md Combat basics [OWNER confirmed]",
      "basics cost 50 / 100 / 150 for scale 1 / 2 / 3", (50, 100, 150),
      "purchases.weapon_basics_cost")
def _wpn_basics_cost():
    return tuple(pu.weapon_basics_cost(s) for s in (1, 2, 3))


@case("WPN-basics-bump", "weapons.md Combat basics [OWNER confirmed]",
      "basics on difficulty 1 -> +4 grades", 4, "purchases.buy_weapon_basics")
def _wpn_basics_bump():
    c = new_char()
    pu.buy_weapon_basics(c, "sword", difficulty=1, scale=1)
    return c.weapon_by_name("sword")["level"]


@case("WPN-basics-nostack", "weapons.md Combat basics, Example [OWNER]",
      "grandpa's sword + long swords + heavy blades basics -> sword level 4, not 12",
      4, "(weapon parent hierarchy / effective level)")
def _wpn_basics_nostack():
    raise NotImplementedInCode(
        "weapons have no parent links (variety/group); each name is "
        "independent, so 'max over ancestors' cannot be computed")


def _set_bonuses(level, picks):
    c = new_char()
    c.proficiencies["weapons"] = [_wpn("w", level)]
    pu.set_weapon_bonuses(c, "w", [{"slot": s, "id": b} for s, b in picks])
    return "allowed"


def _try(fn):
    try:
        return fn()
    except pu.PurchaseError:
        return "rejected"


@case("WPN-pick-expert-open", "weapons.md Bonuses by tier, Test",
      "after 3 different specialist picks, an expert pick at level 8 is allowed",
      "allowed", "purchases.set_weapon_bonuses")
def _wpn_pick1():
    return _try(lambda: _set_bonuses(8, [
        (5, "spec_attack_1"), (6, "spec_crit_range"), (7, "spec_parry_1"),
        (8, "expert_damage_3")]))


@case("WPN-pick-expert-closed", "weapons.md Bonuses by tier (rule text)",
      "expert pick with specialist slots empty is not allowed (need 3 specialist picks first)",
      "rejected", "purchases.set_weapon_bonuses")
def _wpn_pick1b():
    return _try(lambda: _set_bonuses(8, [(8, "expert_damage_3")]))


@case("WPN-pick-2nd-at9", "weapons.md Bonuses by tier, Test",
      "at level 9, picking 'crit range +1' a 2nd time is allowed",
      "allowed", "purchases.set_weapon_bonuses")
def _wpn_pick2():
    return _try(lambda: _set_bonuses(9, [
        (5, "spec_crit_range"), (6, "spec_attack_1"), (7, "spec_parry_1"),
        (8, "expert_damage_3"), (9, "spec_crit_range")]))


@case("WPN-pick-3rd-at11", "weapons.md Bonuses by tier, Test",
      "3rd 'crit range +1' is not allowed before level 12 (try at 11)",
      "rejected", "purchases.set_weapon_bonuses")
def _wpn_pick3():
    return _try(lambda: _set_bonuses(11, [
        (5, "spec_crit_range"), (6, "spec_attack_1"), (7, "spec_parry_1"),
        (8, "expert_damage_3"), (9, "spec_crit_range"),
        (10, "spec_crit_range")]))


@case("WPN-pick-3rd-at12", "weapons.md Bonuses by tier, Test",
      "3rd 'crit range +1' is allowed at level 12 (master slot)",
      "allowed", "purchases.set_weapon_bonuses")
def _wpn_pick3b():
    return _try(lambda: _set_bonuses(12, [
        (5, "spec_crit_range"), (6, "spec_attack_1"), (7, "spec_parry_1"),
        (8, "expert_damage_3"), (9, "spec_crit_range"),
        (12, "spec_crit_range")]))


# ------------------------------------------------------------- narrative.md

def _lens_step(cur, mx, delta):
    import gui_chips

    class _App(object):
        pass
    app = _App()
    app.c = new_char()
    app.c.lenses = [{"name": "New World", "current": cur, "max": mx}]
    app._refresh = lambda: None
    gui_chips._lens_step(app, 0, delta)
    ln = app.c.lenses[0]
    return ln["current"], app.c.lens_status(ln)


@case("NAR-lens-green", "narrative.md Lens, Examples",
      "lens 11/15 + 4 -> 15/15 (green)", (15, "closed"),
      "gui_chips._lens_step + Character.lens_status")
def _nar_lens_green():
    return _lens_step(11, 15, 4)


@case("NAR-lens-red", "narrative.md Lens, Examples",
      "lens 1/15 - 1 -> 0/15 (red)", (0, "failed"),
      "gui_chips._lens_step + Character.lens_status")
def _nar_lens_red():
    return _lens_step(1, 15, -1)


@case("NAR-lens-cap16", "narrative.md Lens, Examples",
      "lens 15/15 + 1 stays 15 (cannot go to 16)", (15, "closed"),
      "gui_chips._lens_step")
def _nar_lens_16():
    return _lens_step(15, 15, 1)


@case("NAR-lens-floor", "narrative.md Lens, Examples",
      "lens 0/15 - 1 stays 0 (cannot go to -1)", (0, "failed"),
      "gui_chips._lens_step")
def _nar_lens_m1():
    return _lens_step(0, 15, -1)


@case("NAR-lens-new", "narrative.md Lens, Examples",
      "new lens starts at 1/15", 1, "(core lens constructor)")
def _nar_lens_new():
    raise NotImplementedInCode(
        "no core constructor; lens is created inside the tkinter dialog "
        "gui_stub._lens_dialog with current=0")


# ------------------------------------------------------------- combat.md

@case("CMB-iterative", "combat.md Attack tag and iteration [OWNER]",
      "2nd attack-tagged option -5, 3rd -10", (-5, -10),
      "(iterative attack penalty)")
def _cmb_iter():
    raise NotImplementedInCode("no 'attack' tag counter / iterative penalty")


@case("CMB-dying-pain", "resources.md Pain, Example [OWNER]",
      "dying: move (1, clean) + special attack (2 actions) -> 2 pain",
      2, "(dying action slots)")
def _cmb_dying():
    raise NotImplementedInCode("no dying state / painful action slots")


# ================================================================ runner

def run_case(cs):
    """Return (status, actual_text). status: PASS / FAIL / NOT_IMPL / ERROR."""
    try:
        actual = cs["fn"]()
    except NotImplementedInCode as e:
        return "NOT_IMPL", str(e)
    except Exception as e:  # real crash in legacy code
        return "ERROR", "%s: %s" % (type(e).__name__, e)
    if actual == cs["expected"]:
        return "PASS", repr(actual)
    return "FAIL", repr(actual)


def _make_pytest(cs):
    def test():
        status, actual = run_case(cs)
        assert status == "PASS", "%s: expected %r, got %s (%s)" % (
            cs["id"], cs["expected"], actual, status)
    test.__name__ = "test_" + cs["id"].replace("-", "_").replace("+", "p")
    return test


for _cs in CASES:
    _t = _make_pytest(_cs)
    globals()[_t.__name__] = _t


def main():
    rows = []
    counts = {}
    for cs in CASES:
        status, actual = run_case(cs)
        counts[status] = counts.get(status, 0) + 1
        rows.append((cs, status, actual))
    print("| id | rule (source) | expected | code gave | status | code function |")
    print("|---|---|---|---|---|---|")
    for cs, status, actual in rows:
        print("| %s | %s (%s) | %r | %s | %s | %s |" % (
            cs["id"], cs["rule"], cs["src"], cs["expected"],
            actual.replace("|", "/"), status, cs["func"]))
    print()
    print("TOTAL %d: %s" % (len(rows), ", ".join(
        "%s %d" % (k, v) for k, v in sorted(counts.items()))))
    return 0 if counts.get("PASS", 0) == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
