"""Package 24: hands with sides (A), AC cell variants and defence settings as data (B), doll layout data (C).
Expected numbers by hand from RULES/ac_zones.md, defense.md, defense_layers.md, doll.md.
Run: python Wp_claude/tests/model/test_pkg24.py"""
import os
import sys
import tempfile
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import session as sm  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.core import ac as acm  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.model import ac_zones_view as zv  # noqa: E402
from wp.model import attack_view as av  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model import doll_layout as dl  # noqa: E402
from wp.model import hands as hd  # noqa: E402
from wp.model.character import ABILITIES, Ability, AttackRecord, Character, Item  # noqa: E402
from wp.rules_data import rules as rd  # noqa: E402

S = Suite("test_pkg24")
TMP = tempfile.mkdtemp(prefix="wp_p24_")
SHIELD = Item("sh", "heavy shield", kind="shield", hands=1, shield=2, shield_type="heavy")
BUCKLER = Item("bk", "buckler", kind="shield", hands=1, shield=1, shield_type="buckler")
SWORD = Item("sw", "sword", kind="weapon", hands=1, groups=("blades",))
DAGGER = Item("dg", "dagger", kind="weapon", hands=1, groups=("blades",))
GREAT = Item("gs", "greatsword", kind="weapon", hands=2, groups=("blades",))
RING = Item("rg", "ring", slot="fingers")
HAT = Item("ht", "hat", slot="head")
HAT2 = Item("ht2", "hood", slot="head")
DODGE = Status("dodge", sid="dodge", effects=(Effect("ac", 1, "dodge"),))


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


def hero(items=(SHIELD,), statuses=(DODGE,), **kw):
    """Dex 14 (+2), dodge +1, no armor, light armor proficiency: parry 2 at level 1 (defense.md)."""
    return Character(abilities={a: Ability(base=14 if a == "dex" else 10) for a in ABILITIES}, items=tuple(items),
                     statuses=tuple(statuses), armor_grade="light", shield_grade="heavy", **kw)


def held(*items):
    return hero(items=tuple(i.__class__(**dict(i.__dict__, in_hands=True)) for i in items))


def var(ch, cell):
    with rd.using(ch):
        return {v["id"]: v["ac"] for v in zv.cells(ch)[str(cell)]["variants"]}


def grid(ch, vid="melee"):
    with rd.using(ch):
        c = zv.cells(ch)
    return tuple(next((v["ac"] for v in c[k]["variants"] if v["id"] == vid), None) for k in sorted(c, key=int))


# ---------------------------------------------------------------- A. hands with sides
def _defaults():
    ch = run(hero(items=(SHIELD, SWORD, DAGGER)), ("equip_hands", {"iid": "sw"}), ("equip_hands", {"iid": "sh"}))
    a = hd.view(ch)
    b = refusal(lambda: dispatch(ch, "equip_hands", iid="dg"))
    c = hd.view(run(hero(items=(SWORD, DAGGER)), ("equip_hands", {"iid": "sw"}), ("equip_hands", {"iid": "dg"})))
    return (a["left"], a["right"]), b, (c["left"], c["right"])


S.case("h-defaults", "pkg 24 A1: sword -> right (first free), shield -> left (default shield side); a third item: "
       "no hands; two weapons: right then left", (("sh", "sw"), "not_enough_free_hands", ("dg", "sw")))(_defaults)
S.case("h-side", "pkg 24 A1: equip_hands side=right puts the shield in the right hand; the right hand taken -> refused",
       ("right", "hand_occupied"))(
    lambda: (lambda ch: (hd.side_of(ch, "sh"), refusal(lambda: dispatch(ch, "equip_hands", iid="sw", side="right"))))(
        run(hero(items=(SHIELD, SWORD)), ("equip_hands", {"iid": "sh", "side": "right"}))))


def _move():
    ch = run(hero(items=(SHIELD, SWORD)), ("equip_hands", {"iid": "sh"}), ("equip_hands", {"iid": "sw"}))
    taken = refusal(lambda: dispatch(ch, "move_hand_item", iid="sh", side="right"))
    sw = run(ch, ("move_hand_item", {"iid": "sh", "side": "right", "swap": True}))
    alone = run(hero(items=(SHIELD,)), ("equip_hands", {"iid": "sh"}), ("move_hand_item", {"iid": "sh", "side": "right"}))
    return taken, (hd.side_of(sw, "sh"), hd.side_of(sw, "sw"), sw.item("sw").hand), hd.side_of(alone, "sh")


S.case("h-move-swap", "pkg 24 A1: move to a taken hand refused; swap=True swaps (the sword stores left); a free "
       "hand: moved", ("hand_occupied", ("right", "left", "left"), "right"))(_move)


def _two_handed():
    ch = run(hero(items=(GREAT, SHIELD)), ("equip_hands", {"iid": "gs"}))
    v = hd.view(ch)
    return (v["left"], v["right"], v["both"]), refusal(lambda: dispatch(ch, "move_hand_item", iid="gs", side="left")), \
        refusal(lambda: dispatch(ch, "equip_hands", iid="sh"))


S.case("h-two-handed", "gear.md: a two-handed weapon takes both hands; it cannot move; a shield then has no hand",
       (("gs", "gs", True), "two_handed_both_hands", "not_enough_free_hands"))(_two_handed)
S.case("h-old-file", "pkg 24 A1: held items without a stored side get sides by the held order: shield left, sword "
       "right; two swords: right, left", ({"sh": "left", "sw": "right"}, {"sw": "right", "dg": "left"}))(
    lambda: (hd.sides(held(SHIELD, SWORD)), hd.sides(held(SWORD, DAGGER))))
S.case("h-stored-wins", "pkg 24 A1: a stored side is kept (dagger left); the other item takes the free hand",
       {"sw": "right", "dg": "left"})(
    lambda: hd.sides(hero(items=(Item("sw", "sword", hands=1, groups=("blades",), in_hands=True),
                                 Item("dg", "dagger", hands=1, groups=("blades",), in_hands=True, hand="left")))))


def _twf():
    ch = run(hero(items=(SWORD, DAGGER)), ("equip_hands", {"iid": "sw"}), ("equip_hands", {"iid": "dg"}))
    ch = run(ch, ("add_attack", {"iid": "sw", "group": "blades", "rid": "a1"}),
             ("add_attack", {"iid": "dg", "group": "blades", "rid": "a2"}))
    with rd.using(ch):
        before = (av.attack(ch, ch.attacks[0]).off_hand, av.attack(ch, ch.attacks[1]).off_hand)
    auto = run(ch, ("set_twf", {"rid": "a1"}))
    flip = run(ch, ("set_main_hand", {"rid": "a2", "side": "left"}))
    with rd.using(flip):
        after = av.attack(flip, flip.attacks[1]).off_hand
    return before, auto.attacks[0].twf_off, after


S.case("h-twf", "pkg 24 A3: main hand = right by default: the dagger (left) is off hand; set_twf without an off record "
       "takes the other-hand record; set_main_hand left: the dagger record is on its main hand",
       ((False, True), "a2", False))(_twf)

# ---------------------------------------------------------------- A2 / B1. cells and variants
S.case("v-melee", "ac_zones.md: Dex +2, dodge +1, heavy shield 2 (left): cells 1-4 and 7 = 10 + 3 + 2 = 15; "
       "6 and 9 = 13; 8 (back: no Dex, no dodge, no shield) = 10", (15, 15, 15, 15, 13, 15, 10, 13))(
    lambda: grid(held(SHIELD)))
S.case("v-parry", "ac_zones.md: parry 2 (light armor proficiency) > armor 0: melee_parry 17 in cells 1-3, none elsewhere",
       (17, 17, 17, None, None, None, None, None))(lambda: grid(held(SHIELD), "melee_parry"))
S.case("v-ranged", "pkg 24 B1: ranged: no parry, the shield counts where it covers: same as melee",
       (15, 15, 15, 15, 13, 15, 10, 13))(lambda: grid(held(SHIELD), "ranged"))
S.case("v-right-hand", "ac_zones.md: the shield in the right hand mirrors: 4 -> 13, 6 -> 15, 7 -> 13, 9 -> 15",
       (15, 15, 15, 13, 15, 13, 10, 15))(
    lambda: grid(run(hero(items=(SHIELD,)), ("equip_hands", {"iid": "sh", "side": "right"}))))
S.case("v-swap-moves-cover", "pkg 24 A2: moving the shield from left to right moves its cells (cell 4: 15 -> 13, "
       "cell 6: 13 -> 15)", ((15, 13), (13, 15)))(
    lambda: (lambda c: ((var(c, 4)["melee"], var(c, 6)["melee"]),
                        (lambda d: (var(d, 4)["melee"], var(d, 6)["melee"]))(
                            run(c, ("move_hand_item", {"iid": "sh", "side": "right"})))))(
        run(hero(items=(SHIELD,)), ("equip_hands", {"iid": "sh"}))))
S.case("v-two-shields", "pkg 24 A2: heavy 2 (left) + buckler 1 (right covers 3, 2, 6): cell 6 = 13 + 1 = 14; cell 2 "
       "the larger 2 = 15; cell 9 none = 13", (14, 15, 13))(
    lambda: (lambda c: (var(c, 6)["melee"], var(c, 2)["melee"], var(c, 9)["melee"]))(
        run(hero(items=(SHIELD, BUCKLER)), ("equip_hands", {"iid": "sh"}), ("equip_hands", {"iid": "bk"}))))
S.case("v-shield-weapon", "gear.md: shield + weapon: the shield keeps its cells (cell 1 = 15, cell 6 = 13)", (15, 13))(
    lambda: (lambda c: (var(c, 1)["melee"], var(c, 6)["melee"]))(
        run(hero(items=(SHIELD, SWORD)), ("equip_hands", {"iid": "sw"}), ("equip_hands", {"iid": "sh"}))))


def _chance():
    ch = held(SHIELD)
    ch = Character(**dict(ch.__dict__, statuses=ch.statuses + (Status("eyes", sid="ey", effects=(
        Effect("dex_loss_chance_pct", 50),)),)))
    with rd.using(ch):
        c = zv.cells(ch)["8"]["variants"]
    return tuple((v["id"], v["ac"], v["chance_pct"]) for v in c)


S.case("v-chance", "pkg 24 B1: a 50% cancel of the Dex loss: back cell 8 shows 10 (no Dex) and 13 (Dex +2, dodge +1, "
       "chance 50); the same for ranged", (("melee", 10, None), ("melee_dex", 13, 50), ("ranged", 10, None),
                                          ("ranged_dex", 13, 50)))(_chance)


def with_effects(*effects, items=(SHIELD,)):
    ch = held(*items)
    return Character(**dict(ch.__dict__, statuses=ch.statuses + (Status("x", sid="x", effects=tuple(effects)),)))


S.case("b-parry-cells", "pkg 24 B2: parry_cells +4 gives cell 4 a parry value (17); -1 removes cell 1",
       (17, None))(lambda: (var(with_effects(Effect("parry_cells", 1, cells=("4",))), 4).get("melee_parry"),
                            var(with_effects(Effect("parry_cells", -1, cells=("1",))), 1).get("melee_parry")))
S.case("b-shield-cells", "pkg 24 B2: shield_cells +6: cell 6 gets the shield (15); -2: cell 2 loses it (13)", (15, 13))(
    lambda: (var(with_effects(Effect("shield_cells", 1, cells=("6",))), 6)["melee"],
             var(with_effects(Effect("shield_cells", -1, cells=("2",))), 2)["melee"]))
S.case("b-dex-cells", "pkg 24 B2: dex_loss_cells +6: cell 6 loses Dex and dodge (10); -8: the back keeps them (13)",
       (10, 13))(lambda: (var(with_effects(Effect("dex_loss_cells", 1, cells=("6",))), 6)["melee"],
                          var(with_effects(Effect("dex_loss_cells", -1, cells=("8",))), 8)["melee"]))


def _scoped_ac():
    ch = with_effects(Effect("ac", 2, "deflection", cells=("8",)))
    with rd.using(ch):
        modes = acm.all_modes(dv.ac_input(ch))
    return var(ch, 8)["melee"], var(ch, 2)["melee"], modes["front"], modes["flat_footed"]


S.case("b-scoped-ac", "Q157 / pkg 24 B2: deflection +2 only in cell 8: back 12, front cell 15; the old modes follow "
       "their preset cells: front 15, flat-footed 12", (12, 15, 15, 12))(_scoped_ac)
S.case("b-scoped-parry", "pkg 24 B2: parry +2 only in cell 2: parry 4 there (19), 2 in cell 1 (17)", (19, 17))(
    lambda: (lambda c: (var(c, 2)["melee_parry"], var(c, 1)["melee_parry"]))(
        with_effects(Effect("parry", 2, cells=("2",)))))
S.case("b-scoped-shield", "pkg 24 B2: a shield bonus +3 only in cell 6 (shield type: larger wins, 3 > 0 there): 16",
       16)(lambda: var(with_effects(Effect("ac", 3, "shield", cells=("6",))), 6)["melee"])
S.case("b-ranged-parry-setting", "pkg 24 B3: ac_zones.ranged_ignores_parry 0: ranged uses parry in cells 1-3 (17)", 17)(
    lambda: var(run(held(SHIELD), ("set_rule_setting", {"key": "ac_zones.ranged_ignores_parry", "value": 0})), 1)["ranged"])
S.case("b-parry-cells-setting", "pkg 24 B3: the parry cells as a per-character constant [1, 2, 3, 4]: cell 4 parry 17",
       17)(lambda: var(run(held(SHIELD), ("set_rule_setting", {"key": "ac_zones.parry_cells", "value": [1, 2, 3, 4]})),
                       4).get("melee_parry"))
S.case("b-buckler-setting", "pkg 24 B3: shield cells per type as a constant: a buckler that covers only 2 -> cell 1 = 13",
       13)(lambda: var(run(held(BUCKLER), ("set_rule_setting", {"key": "ac_zones.shield_cells", "value": {
           "buckler": [2], "light": [1, 2, 3, 4, 7], "heavy": [1, 2, 3, 4, 7], "tower": [1, 2, 3, 4, 7], "": [1, 2, 3, 4, 7]}})),
                       1)["melee"])


def _presets():
    ch = held(SHIELD)
    with rd.using(ch):
        inp = dv.ac_input(ch)
        m = acm.all_modes(inp)
    return var(ch, 2)["melee"] == m["front"], var(ch, 2)["melee_parry"] == m["parry"], var(ch, 6)["melee"] == m["flank"], \
        var(ch, 8)["melee"] == m["flat_footed"]


S.case("b-presets", "pkg 24 B4: cells 2 / 6 / 8 still give front, parry, flank, flat-footed", (True, True, True, True))(_presets)


def _settings_view():
    s = new_session()
    v = s.view("defense")
    keys = sorted(x.key for x in v["settings"])
    s.dispatch("set_rule_setting", key="ac_zones.parry_cells", value=[1, 2])
    changed = [x.key for x in s.view("defense")["settings"] if x.changed]
    return "ac_zones.parry_cells" in keys and "hands.default_shield_side" in keys, changed, v["display"]["primary"]


def new_session():
    d = tempfile.mkdtemp(dir=TMP)
    s = sm.Session(os.path.join(d, "ch"), os.path.join(d, "user"))
    s.new("Hero", held(SHIELD))
    return s


S.case("b-settings-view", "pkg 24 B3: the defense view lists the cell rules with defaults and the changed flag; the "
       "display hints (primary melee)", (True, ["ac_zones.parry_cells"], "melee"))(_settings_view)

# ---------------------------------------------------------------- C. doll layout
S.case("d-entries", "pkg 24 C: both layouts hold the 21 single slots + left and right hand (the hands slot = its two "
       "hands); basic shows only the hands", (23, True, True, ("left_hand", "right_hand")))(
    lambda: (lambda lay: (len(dl.ENTRY_IDS), sorted(e["id"] for e in lay["basic"]) == sorted(dl.ENTRY_IDS),
                          sorted(e["id"] for e in lay["body"]) == sorted(dl.ENTRY_IDS),
                          tuple(sorted(e["id"] for e in lay["basic"] if e["visible"]))))(dl.shipped()))
S.case("d-check-shipped", "pkg 24 C: the shipped layouts have no warning", ((), ()))(
    lambda: (dl.check(dl.shipped()["basic"]), dl.check(dl.shipped()["body"])))


def _check_bad():
    body = [dict(e) for e in dl.shipped()["body"] if e["id"] != "pet"]
    body[0]["x"] = 0.95                                     # 0.95 + 0.12 > 1
    body[1].update(x=body[2]["x"], y=body[2]["y"])           # on top of the next entry
    w = dl.check(body)
    return ("doll_entry_missing", "pet") in w, ("doll_out_of_range", body[0]["id"]) in w, \
        ("doll_overlap", body[1]["id"], body[2]["id"]) in w


S.case("d-check-bad", "pkg 24 C: a missing entry, a rectangle out of 0..1 and an overlap are warnings",
       (True, True, True))(_check_bad)


def _placeholder():
    s = new_session()
    lay = s.view("items", doll_view="basic")["layout"]
    return lay["background"]["path"], lay["background"]["warning"], lay["view"]


S.case("d-placeholder", "pkg 19 / 24 C: the doll picture is not in the image registry -> placeholder", (
    "placeholder", "no_image", "basic"))(_placeholder)


def _doll_items():
    ch = run(hero(items=(SHIELD, SWORD, RING, HAT, HAT2)), ("equip_to_slot", {"iid": "sh", "slot": "left_hand"}),
             ("equip_to_slot", {"iid": "sw", "slot": "right_hand"}), ("equip_to_slot", {"iid": "rg", "slot": "fingers"}),
             ("equip_to_slot", {"iid": "ht", "slot": "head"}))
    items, _ = dl.contents(ch)
    sw = run(ch, ("swap_slots", {"a": "left_hand", "b": "right_hand"}))
    after, _ = dl.contents(sw)
    gone = run(ch, ("unequip_slot", {"slot": "fingers"}))
    return ((items["left_hand"], items["right_hand"], items["fingers"], items["head"]),
            (after["left_hand"], after["right_hand"]), dl.contents(gone)[0]["fingers"],
            refusal(lambda: dispatch(ch, "equip_to_slot", iid="ht2", slot="head")),
            refusal(lambda: dispatch(ch, "equip_to_slot", iid="ht2", slot="fingers")),
            refusal(lambda: dispatch(ch, "swap_slots", a="head", b="fingers")),
            refusal(lambda: dispatch(gone, "unequip_slot", slot="fingers")))


S.case("d-commands", "pkg 24 C: equip into chosen entries; swap the two hands; unequip; refusals: slot taken, item "
       "does not fit, a head item cannot go to the fingers, an empty slot",
       (("sh", "sw", "rg", "ht"), ("sw", "sh"), "", "slot_occupied", "item_not_fit_slot", "item_not_fit_slot",
        "slot_empty"))(_doll_items)
S.case("d-hands-full", "doll.md: a third one-handed item into a hand entry: refused (hands full)",
       "not_enough_free_hands")(
    lambda: refusal(lambda: dispatch(run(hero(items=(SHIELD, SWORD, DAGGER)),
                                         ("equip_to_slot", {"iid": "sh", "slot": "left_hand"}),
                                         ("equip_to_slot", {"iid": "sw", "slot": "right_hand"})),
                                     "equip_to_slot", iid="dg", slot="left_hand")))

def _roundtrip():
    from wp.storage import character_io as cio
    c = Character(items=(Item("a", "axe", hands=1, in_hands=True, hand="left"),),
                  attacks=(AttackRecord("r", "a", "blades", main_hand="left"),),
                  statuses=(Status("s", sid="s", effects=(Effect("ac", 2, "deflection", cells=("8",)),)),))
    d = cio.loads(cio.dumps(c))
    return d == c, d.items[0].hand, d.attacks[0].main_hand, d.statuses[0].effects[0].cells


S.case("s-roundtrip", "pkg 24: Item.hand, AttackRecord.main_hand and Effect.cells survive save / load",
       (True, "left", "left", ("8",)))(_roundtrip)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
