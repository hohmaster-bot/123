"""Package 25: undo / redo (A), class system v0 (B), drives with level notes and principles (C), hidden item
properties (D), stored-only picks as flags (E), spell damage as data (F). Numbers by hand.
Run: python Wp_claude/tests/model/test_pkg25.py"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import session as sm  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.commands import notebook_cmds as nbc  # noqa: E402
from wp.core import ac as acm  # noqa: E402
from wp.core.effects import Effect  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.core.skills import Skill  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import classes as klass  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import pick_flags as pf  # noqa: E402
from wp.model import spell_damage as sd  # noqa: E402
from wp.model import spell_view as spv  # noqa: E402
from wp.model import stats_view as stv  # noqa: E402
from wp.model.experience import XpEntry  # noqa: E402
from wp.model.character import AttackRecord, Character, Item, WeaponEntry  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_pkg25")
TMP = tempfile.mkdtemp(prefix="wp_p25_")


def refusal(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


def run(ch, *steps):
    for name, params in steps:
        ch = dispatch(ch, name, **params).state
    return ch


def classed(cid, level=5, **kw):
    kw.setdefault("xp_log", (XpEntry("xp0", 1000),))      # enough for one level_up (package 33)
    return run(Character(level=level, **kw), ("set_class", {"class_id": cid}))


def saves(ch):
    with rd.using(ch):
        return tuple(klass.save_base(ch, k) for k in ("fort", "ref", "will"))


# ---------------------------------------------------------------- A. undo / redo
def new_session(**settings):
    from wp.settings.settings_cmds import settings_dispatch
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    for k, v in settings.items():
        s.app = settings_dispatch(s.app, "settings_set", key=k, value=v).state
    s.new("Hero", Character(hp_rolls=(8,), hp_current=8, training=1000))
    return s


def _undo_purchase():
    s = new_session()
    s.dispatch("learn_spell", name="Spark", circle=1)            # 20 + 10 * 1 = 30
    after = s.character.training
    u = s.undo()
    back = (s.character.training, len(s.character.spells), s.character.log[-1].command, u.topics)
    s.redo()
    return after, back, (s.character.training, s.character.log[-1].command)


S.case("u-purchase", "pkg 25 A: learn a spell (1000 -> 970), undo -> 1000 and no spell, journal line undo, the "
       "command's topics; redo -> 970", (970, (1000, 0, "undo", ("spells", "training", "log")), (970, "redo")))(
    _undo_purchase)


def _undo_tick():
    s = new_session()
    s.dispatch("start_combat")
    s.dispatch("tick")
    r = s.character.combat_round
    s.undo()
    return r, s.character.combat_round


S.case("u-tick", "pkg 25 A: a combat tick (round 1 -> 2) is undone (round 1)", (2, 1))(_undo_tick)


def _limit():
    s = new_session(undo_depth=2)
    for _ in range(3):
        s.dispatch("take_damage", amount=1)                     # HP 8 -> 7 -> 6 -> 5
    out = [s.undo().ok, s.undo().ok, s.undo().ok]
    return out, s.character.hp_current


S.case("u-limit", "pkg 25 A: undo_depth 2: two undos (HP 5 -> 6 -> 7), the third has nothing", ([True, True, False], 7))(
    _limit)


def _failed():
    s = new_session()
    s.dispatch("take_damage", amount=2)
    bad = s.dispatch("spend_bp", n=9)
    s.undo()
    return bad.ok, s.character.hp_current, s.can_undo()


S.case("u-failed", "pkg 25 A: a refused command is not on the stack: undo takes back the damage (HP 8)", (False, 8, False))(
    _failed)


def _new_clears_redo():
    s = new_session()
    s.dispatch("take_damage", amount=1)
    s.undo()
    s.dispatch("take_damage", amount=2)
    return s.can_redo(), s.redo().reason


S.case("u-new-clears", "pkg 25 A: a new command clears redo", (False, "nothing_to_redo"))(_new_clears_redo)


def _non_undoable():
    s = new_session()
    ok = s.dispatch("set_char_setting", key="char_portrait", value="hero").ok
    return ok, s.can_undo(), s.dispatch("take_damage", amount=1).ok and s.can_undo()


S.case("u-non-undoable", "pkg 25 A: a command listed in wp/app/data/undo.json (character settings) is not on the stack",
       (True, False, True))(_non_undoable)


def _shared():
    s = new_session()
    before = s.character
    s.dispatch("take_damage", amount=1)
    return s._undo[-1][0] is before, s.character.abilities is before.abilities


S.case("u-shared", "pkg 25 A: the stack keeps the old Character object itself (no copy); unchanged parts are shared",
       (True, True))(_shared)
S.case("u-autosave", "pkg 25 A: undo is a change for autosave (dirty)", True)(
    lambda: (lambda s: (s.dispatch("take_damage", amount=1), s.save(), s.undo(), s.dirty_since is not None)[-1])(
        new_session()))

# ---------------------------------------------------------------- B. class system v0
S.case("c-saves", "ROADMAP assumption: level 5 good save = 2 + 5 // 2 = 4, poor = 5 // 3 = 1 (sample fighter: fort good)",
       (4, 1, 1))(lambda: saves(classed("sample_fighter")))
S.case("c-bab", "Q167 assumption: BAB level 5: good 5, medium 5 * 0.75 = 3, poor 5 * 0.5 = 2", (5, 3, 2))(
    lambda: tuple(klass.bab(classed(c)) for c in ("sample_fighter", "sample_cleric", "sample_mage")))
S.case("c-override", "pkg 25 B: a hand BAB 7 and fort 9 win over the class", (7, (9, 1, 1)))(
    lambda: (lambda c: (klass.bab(c), saves(c)))(run(classed("sample_fighter"), ("set_bab_override", {"value": 7}),
                                                     ("set_save_override", {"save": "fort", "value": 9}))))
S.case("c-empty", "pkg 25 B: no class = the typed values as before (BAB 3, fort 2)", (3, (2, 0, 0)))(
    lambda: (lambda c: (klass.bab(c), saves(c)))(Character(level=5, bab=3, save_base={"fort": 2, "ref": 0, "will": 0})))
S.case("c-removed", "pkg 25 B: set_class '' goes back to the typed values", 3)(
    lambda: klass.bab(run(classed("sample_fighter", bab=3), ("set_class", {"class_id": ""}))))


def _views_use_class():
    c = run(classed("sample_fighter"), ("add_attack", {"iid": "unarmed", "group": "unarmed_combat", "rid": "u"}))
    with rd.using(c):
        line = next(x.value for x in av.attack(c, c.attacks[0]).to_hit_lines if x.label == "bab")
        fort = stv.view(c)["fort"].lines[0]
    return line, fort


S.case("c-views", "pkg 25 B: the attack line bab and the fort save base read the class (5, 4)", (5, ("base", 4)))(
    _views_use_class)
S.case("c-hit-die", "pkg 25 B: the class hit die (sample cleric d8) caps level_up: 8 ok, 9 refused", (2, "hit_die_roll_must"))(
    lambda: (lambda c: (run(c, ("level_up", {"hp_roll": 8})).level,
                        refusal(lambda: dispatch(c, "level_up", hp_roll=9))))(classed("sample_cleric", level=1, hit_die=6)))


def _prof():
    sk = (Skill("athletics", "str"), Skill("stealth", "dex"))
    own = refusal(lambda: dispatch(classed("sample_cleric", skills=sk), "buy_professionalism", skills=("athletics",),
                                   class_skill_points=2))
    wrong = refusal(lambda: dispatch(classed("sample_fighter", skills=sk), "buy_professionalism", skills=("stealth",),
                                     class_skill_points=2))
    ok = run(classed("sample_fighter", skills=sk), ("buy_professionalism", {"skills": ("athletics",),
                                                                            "class_skill_points": 2}))
    return own, wrong, ok.training


S.case("c-professionalism", "Q104 closed: a class with its own professionalism refuses; a skill outside the class list "
       "refuses; a class skill: 1000 - 300 = 700", ("class_own_professionalism", "not_class_skill", 700))(_prof)
S.case("c-spellbook", "pkg 25 B: learn_spell circle 1 = 30; the sample mage (spellbook) pays half by default (15); an "
       "explicit discount=False pays 30", (15, 30, 30))(
    lambda: (run(classed("sample_mage"), ("learn_spell", {"name": "a", "circle": 1})).spells[0].cost,
             run(classed("sample_fighter"), ("learn_spell", {"name": "a", "circle": 1})).spells[0].cost,
             run(classed("sample_mage"), ("learn_spell", {"name": "a", "circle": 1, "discount": False})).spells[0].cost))
S.case("c-divine", "pkg 25 B: divine class -> failure mode zero_balance; others cancel", ("zero_balance", "cancel"))(
    lambda: (spv.failure_mode(classed("sample_cleric")), spv.failure_mode(classed("sample_mage"))))
S.case("c-unknown", "pkg 25 B: an unknown class id is refused", "not_found")(
    lambda: refusal(lambda: dispatch(Character(), "set_class", class_id="nope")))


def _user_catalog():
    entry = {"id": "my", "name": "Mine", "hit_die": 12, "bab_growth": "good", "saves": {"will": "good"}}
    c = run(Character(level=4), ("set_class", {"class_id": "my", "catalog": {"my": entry}}))
    return klass.bab(c), saves(c), klass.hit_die(c)


S.case("c-catalog", "pkg 25 B: a class from a given catalog: level 4 good BAB 4, will 2 + 2 = 4, fort / ref 4 // 3 = 1, "
       "die 12", (4, (1, 1, 4), 12))(_user_catalog)

# ---------------------------------------------------------------- C. drives
def _drive():
    c = run(Character(), ("add_drive", {"name": "Revenge", "level": 2}))
    a = nbc.drive_view(c, c.drives[0])["principle_missing"]
    c = run(c, ("set_drive_principle", {"did": c.drives[0].did, "text": "Never forgive"}))
    b = nbc.drive_view(c, c.drives[0])["principle_missing"]
    low = run(Character(), ("add_drive", {"name": "Calm", "level": 1}))
    return a, b, nbc.drive_view(low, low.drives[0])["principle_missing"]


S.case("n-principle", "narrative.md (pkg 25 C): level 2 without a principle -> reminder; with one -> none; level 1 -> none",
       (True, False, False))(_drive)


def _notes():
    c = run(Character(), ("add_drive", {"name": "Fear", "level": 4, "principle": "p"}))
    did = c.drives[0].did
    c = run(c, ("set_drive_level_note", {"did": did, "level": 4, "text": "+2 Will / -2 Cha"}),
            ("set_drive_level_note", {"did": did, "level": 1, "text": "none"}))
    v = nbc.drive_view(c, c.drives[0])
    c2 = run(c, ("edit_drive", {"did": did, "name": "Terror"}), ("set_drive_level", {"did": did, "level": 1}))
    return v["note"], sorted(v["level_notes"]), nbc.drive_view(c2, c2.drives[0])["note"], c2.drives[0].name, \
        refusal(lambda: dispatch(c, "set_drive_level_note", did=did, level=6, text="x")), \
        len(run(c, ("remove_drive", {"did": did})).drives)


S.case("n-notes", "pkg 25 C: the note of the current level shown next to the number; notes kept per level; level 6 "
       "refused; edit and remove", ("+2 Will / -2 Cha", ["1", "4"], "none", "Terror", "drive_level_range", 0))(_notes)
S.case("n-attention", "narrative.md: attention income unchanged: level 7, drives 4, 5, 3 -> 1 + 2 + 2 = 5", 5)(
    lambda: run(Character(level=7), ("add_drive", {"name": "a", "level": 4}), ("add_drive", {"name": "b", "level": 5}),
                ("add_drive", {"name": "c", "level": 3}), ("end_cycle", {})).attention)

# ---------------------------------------------------------------- D. hidden properties
RING = Item("rg", "ring", equipped=True, qualification_n=2)


def _hidden(qualified):
    c = run(Character(training=1000, items=(RING,)),
            ("add_hidden_property", {"iid": "rg", "text": "glow", "min_qualification": 1}),
            ("add_hidden_property", {"iid": "rg", "text": "ward", "min_qualification": 2,
                                     "effects": (Effect("ac", 1, "deflection"),)}),
            ("add_hidden_property", {"iid": "rg", "text": "aegis", "min_qualification": 3,
                                     "effects": (Effect("ac", 5, "insight"),)}))
    if qualified:
        c = run(c, ("buy_item_qualification", {"iid": "rg"}))     # 50 * 2 = 100
    with rd.using(c):
        v = dv.item_view(c, "rg")
        front = acm.ac(dv.ac_input(c))
    return tuple((h[1], h[2]) for h in v.hidden), front, c.training


S.case("q-locked", "Q109: before the qualification every property is ??? and gives nothing (AC 10)",
       ((("???", True), ("???", True), ("???", True)), 10, 1000))(lambda: _hidden(False))
S.case("q-unlocked", "Q109: qualification 2 bought (100): levels 1 and 2 open (ward: deflection +1 -> AC 11), level 3 "
       "stays ???", ((("glow", False), ("ward", False), ("???", True)), 11, 900))(lambda: _hidden(True))


def _activated_tab():
    it = Item("st", "staff", equipped=True, qualification_n=1, qualified=True, activation_day=1)
    c = run(Character(items=(it,), spirit_current=1), ("add_hidden_property", {"iid": "st", "text": "x", "tab": "activated",
                                                              "effects": (Effect("ac", 2, "luck"),)}))
    with rd.using(c):
        off = acm.ac(dv.ac_input(c))
    c = run(c, ("activate_item", {"iid": "st"}))
    with rd.using(c):
        on = acm.ac(dv.ac_input(c))
    return off, on


S.case("q-tab", "pkg 25 D: a property of the activated tab acts only while the item is activated (10 -> 12)", (10, 12))(
    _activated_tab)

# ---------------------------------------------------------------- E. picks as flags
def node(*bonuses):
    return WeaponEntry(Weapon("blades", scale=3), picks=tuple(Pick(8 + i, b) for i, b in enumerate(bonuses)))


def _flags():
    c = Character(weapons=(node("ignore_vulnerability", "ignore_cover_20", "damage_3"),))
    f = pf.abilities(c)
    return tuple((x["bonus"], x["charges"]) for x in f)


S.case("p-flags", "weapons.md (pkg 25 E): ignore the first vulnerability (once per fight: charge 1 of 1) and ignore 20% "
       "cover (no charge) show; damage +3 is a number, not a flag",
       (("ignore_vulnerability", (1, 1)), ("ignore_cover_20", None)))(_flags)
S.case("p-gone", "pkg 25 E: without the pick the flag is gone", ())(lambda: pf.abilities(Character(weapons=(node("damage_3"),))))


def _flag_spend():
    c = Character(weapons=(node("ignore_vulnerability"),))
    c = run(c, ("spend_charge", {"owner_kind": "pick", "owner_id": "blades:8"}))
    spent = pf.abilities(c)[0]["charges"]
    c = run(c, ("start_combat", {}), ("end_combat", {}))
    return spent, pf.abilities(c)[0]["charges"]


S.case("p-charge", "weapons.md: once per fight: spent (0 of 1), back at the end of combat (1 of 1)", ((0, 1), (1, 1)))(
    _flag_spend)


def _attack_flags():
    c = Character(weapons=(node("no_attack_tag"),), items=(Item("sw", "sword", kind="weapon", hands=1, groups=("blades",),
                                                                in_hands=True),),
                  attacks=(AttackRecord("r", "sw", "blades"),))
    with rd.using(c):
        return tuple(x["bonus"] for x in av.attack(c, c.attacks[0]).abilities)


S.case("p-attack-view", "pkg 25 E: the attack view of a blades record lists its group's flags", ("no_attack_tag",))(
    _attack_flags)

# ---------------------------------------------------------------- F. spell damage
def spell(level, *damage, **kw):
    c = run(Character(level=level, training=1000, **kw), ("learn_spell", {"name": "Fire", "circle": 1}))
    return run(c, ("set_spell_damage", {"spid": c.spells[0].spid, "damage": damage}))


S.case("s-fireball", "pkg 25 F: a fireball-like sample at level 5: 5d6 fire, burst, 100 ft, Ref half",
       ((5, 6, 0, "fire", "burst", "100", "ref"),))(
    lambda: tuple((x["dice_count"], x["die_size"], x["flat"], x["damage_type"], x["area"], x["range"], x["save"])
                  for x in sd.spell_damage(*(lambda c: (c, c.spells[0]))(spell(5, {
                      "dice_count": "level", "die_size": 6, "damage_type": "fire", "area": "burst", "range": "100",
                      "save": "ref", "save_effect": "half"})))["components"]))
S.case("s-scaling", "pkg 25 F: dice level / 2 at level 5 = 2 (rounded down), flat level = 5", (2, 5))(
    lambda: (lambda x: (x["dice_count"], x["flat"]))(sd.view(spell(5, {"dice_count": "level / 2", "flat": "level",
                                                                       "damage_type": "cold"}))[0]["components"][0]))
S.case("s-pain", "combat.md: pain and morale apply to the damage roll: pain 2 -> -2, morale 0, roll modifier -2",
       (-2, 0, -2))(lambda: (lambda v: (v["pain"], v["morale"], v["roll_modifier"]))(
           sd.view(spell(5, {"dice_count": "1", "damage_type": "acid"}, pain=(PainEntry(2),)))[0]))
S.case("s-refusals", "pkg 25 F: unknown damage type / area / save, a bad formula are refused",
       ("unknown_damage_type", "unknown_area", "unknown_save", "bad_effect_formula"))(
    lambda: tuple(refusal(lambda d=d: spell(5, d)) for d in (
        {"damage_type": "water"}, {"damage_type": "fire", "area": "cube"}, {"damage_type": "fire", "save": "luck"},
        {"damage_type": "fire", "dice_count": "level +"})))


def _roundtrip():
    from wp.storage import character_io as cio
    c = spell(5, {"dice_count": "level", "damage_type": "fire"})
    c = run(c, ("set_class", {"class_id": "sample_mage"}), ("add_drive", {"name": "d", "level": 3,
                                                                          "level_notes": {"3": "x"}}))
    c = run(Character(**dict(c.__dict__, items=(RING,))), ("add_hidden_property", {"iid": "rg", "text": "t"}))
    return cio.loads(cio.dumps(c)) == c


S.case("s-roundtrip", "pkg 25: class snapshot, drive notes, hidden properties and spell damage survive save / load",
       True)(_roundtrip)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
