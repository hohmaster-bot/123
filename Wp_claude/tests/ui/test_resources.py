"""Package 33: the RESOURCES block and the level-up button of the Classic window, without a screen
(QT_QPA_PLATFORM=offscreen; without PySide6 the suite is SKIPPED, exit 0).
Numbers by hand from wp/ui/data/demo.json and RULES/resources.md:
demo HP max (8 + 1) + (6 + 1) = 16 (rolls 8 and 6, Con 12 +1 per die), set to 16; balance 4 (BP 4); a hit of 5
-> HP 11, balance 0, overflow 1 -> OT 1, pain 1;
temp HP 4; spirit 7 of 10 (5 + 5 x Cha 12 mod 1); mana 5 / 8 (a manual source row +8, package 34); overload 1; pool Ki 3 / 3; xp 1450, level 2,
training 1000 + 200 = 1200.
Run: python Wp_claude/tests/ui/test_resources.py"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
FONTS = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
if os.path.isdir(FONTS):
    os.environ.setdefault("QT_QPA_FONTDIR", FONTS)
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("test_resources: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app.session import Session  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui import app as ua  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_resources")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_res_")
SHOTS = os.path.join(HERE, "..", "ui_shots")


def started(tag):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    ua.start_character(w)
    QAPP.processEvents()
    return s, w, w.blocks["resources"]


def res(s):
    return s.view("resources")


def cur(s, rid):
    return res(s)[rid]["current"]


# ---------------------------------------------------------------- the tubes of the demo
def _tubes():
    s, w, b = started("tubes")
    hp = b.rows["hp"]
    return (sorted(b.rows), (hp.tube.current, hp.tube.maximum, hp.tube.temp), hp.value.text(),
            b.rows["spirit"].value.text(), b.rows["mana"].chip.text(), b.rows["pool:ki"].value.text())


S.case("r-tubes", "UI_WISHES 3: HP, balance, spirit, mana, the pool Ki; HP 11 / 16 with temp 4; spirit 7 / 10; "
       "the overload chip 1; Ki 3 / 3", (["balance", "hp", "mana", "pool:ki", "spirit"], (11, 16, 4), "11 / 16",
                                         "7 / 10", "overload 1", "3 / 3"))(_tubes)


# ---------------------------------------------------------------- the value editor
def _edit():
    s, w, b = started("edit")
    out = []
    for text in ("+5", "-3", "30"):
        b.apply_edit("hp", text)
        out.append(cur(s, "hp"))
    return out, b.rows["hp"].value.objectName(), [e.command for e in s.character.log[-3:]]


S.case("r-edit", "UI_WISHES 4: +5 -> 11 + 5 = 16, -3 -> 13, 30 replaces (30 over the max 16: the over-max colour, "
       "not clamped); adjust / adjust / set", ([16, 13, 30], "over_max", ["adjust_value", "adjust_value", "set_value"]))(
    _edit)


def _popup():
    s, w, b = started("popup")
    dlg = b.open_editor("hp")
    dlg.value.setText("")
    dlg.temp.setText("7")
    dlg.accept()
    return res(s)["temp_hp"], cur(s, "hp"), dlg.temp is not None, b.open_editor("mana").temp is None


S.case("r-temp", "UI_WISHES 4: the HP popup has the temp HP field: 7 -> temp HP 7 (set_temp_hp), HP stays 11; "
       "the mana popup has no temp field", (7, 11, True, True))(_popup)


def _negative():
    s, w, b = started("negative")
    r = b.apply_edit("mana", "-9")
    bad = b.apply_edit("mana", "abc")
    return r.ok, r.reason, b.message.text() if bad is None else "?", cur(s, "mana")


S.case("r-negative", "rules (pkg 27 F19): mana 5 - 9 = -4 refused with its text; bad text -> the editor text",
       (False, "out_of_range", 'Cannot read "abc": type +N, -N or a number', 5))(_negative)


def _negative_text():
    s, w, b = started("negtext")
    b.apply_edit("mana", "-9")
    return b.message.text()


S.case("r-refusal-text", "pkg 33: a refusal shows its i18n text in the message line (no traceback)",
       "-4 is out of range")(_negative_text)


# ---------------------------------------------------------------- mechanics buttons
def _damage():
    s, w, b = started("damage")
    dlg = b.press("hp", "take_damage")
    dlg.amount.setValue(6)
    dlg.kind.setCurrentIndex(dlg.kind.findData("fire"))
    dlg.accept()
    v = res(s)
    e = s.character.log[-1]
    return (dlg.kind.count(), cur(s, "hp"), v["temp_hp"], cur(s, "balance"), v["ot"], v["pain"], e.command,
            e.params.get("dtype"))


S.case("r-damage", "resources.md: Take damage 6 fire (12 types): temp 4 absorbs 4, HP 11 - 2 = 9, balance 0 floors, "
       "overflow 2 -> OT 1 + 2 = 3, pain 1 + 1 = 2; the journal keeps the type fire",
       (12, 9, 0, 0, 3, 2, "take_damage", "fire"))(_damage)


def _balance():
    s, w, b = started("balance")
    b.apply_edit("balance", "4")
    dlg = b.press("balance", "damage_to_balance")
    dlg.amount.setValue(3)
    dlg.accept()
    v = res(s)
    return cur(s, "balance"), cur(s, "hp"), v["ot"], v["pain"], s.character.log[-1].command


S.case("r-balance", "resources.md: balance set to 4, Damage to balance 3 -> 1; HP 11, OT 1 and pain 1 unchanged",
       (1, 11, 1, 1, "damage_to_balance"))(_balance)


def _heal():
    s, w, b = started("heal")
    dlg = b.press("hp", "heal")
    dlg.amount.setValue(3)
    dlg.accept()
    return cur(s, "hp"), s.character.log[-1].command


S.case("r-heal", "resources.md: Heal 3 -> 11 + 3 = 14 (restore, never above the max 16)", (14, "restore"))(_heal)


def _plus_minus():
    s, w, b = started("plusminus")
    b.press("mana", "plus")
    up = cur(s, "mana")
    b.press("mana", "minus")
    b.press("spirit", "minus")
    b.press("mana", "overload_plus")
    b.press("pool:ki", "minus")
    return up, cur(s, "mana"), cur(s, "spirit"), res(s)["overload"], res(s)["pools"][0][2]["current"]


S.case("r-plus-minus", "UI_WISHES 4: mana 5 + 1 -> 6, -1 -> 5; spirit 7 - 1 = 6; overload 1 + 1 = 2; "
       "Ki 3 - 1 = 2", (6, 5, 6, 2, 2))(_plus_minus)


# ---------------------------------------------------------------- look: style, auto-switch, pools
def _style():
    s, w, b = started("style")
    t = b.rows["hp"].tube
    before = (t.height(), t.maximumWidth(), t.current, t.style_name)
    w.set_setting("resource_style", "flat")
    t = b.rows["hp"].tube
    return before, (t.height(), t.maximumWidth(), t.current, t.style_name)


S.case("r-style", "UI_WISHES 3: glass -> flat keeps the size and the value (HP tube 21 px high: the block fits "
       "(380 - 52) / 5 - 44 = 21.6 < 26; width 240)", ((21, 240, 11, "glass"), (21, 240, 11, "flat")))(_style)


def _autoswitch():
    s, w, b = started("auto")
    size = dict(s.setting("resource_size"))
    size["mana"] = [240, 6]
    w.set_setting("resource_size", size)
    thin = (b.rows["mana"].tube.mode, b.rows["mana"].tube.height(), b.rows["mana"].value.isHidden())
    w.set_setting("resource_autoswitch", False)
    return thin, b.rows["mana"].tube.mode, b.rows["hp"].tube.height()


S.case("r-autoswitch", "UI_WISHES 3: mana height 6 < medium 10 -> the thin bar (12 px minimum, the number inside, "
       "the value text hidden); auto-switch off -> big, HP back to its 26", (("thin", 12, True), "big", 26))(_autoswitch)


def _pools():
    s, w, b = started("pools")
    for name in ("Rage", "Luck", "Grit"):
        s.dispatch("add_pool", name=name, max=2)
    QAPP.processEvents()
    rows = [r for r in b.rows if r.startswith("pool:")]
    return sorted(rows), [r for r in rows if not b.rows[r].compact], [r for r in rows if b.rows[r].compact], \
        b.compact_scroll.isHidden()


S.case("r-pools", "UI_WISHES 6: four pools: the first three large (Ki, Rage, Luck), the 4th (Grit) compact in its "
       "scroll area", (["pool:grit", "pool:ki", "pool:luck", "pool:rage"], ["pool:ki", "pool:rage", "pool:luck"],
                       ["pool:grit"], False))(_pools)


def _custom():
    s, w, b = started("custom")
    w.session_settings("quick_add", button={"label": "Drink", "group": "resource:mana",
                                            "action": {"command": "adjust_value",
                                                       "params": {"resource": "mana", "delta": 2}}})
    row = b.rows["mana"]
    bid = next(iter(row.custom))
    row.custom[bid].click()
    return row.custom[bid].text(), cur(s, "mana"), s.can_undo()


S.case("r-custom", "UI_WISHES 4: a quick button of group resource:mana shows under mana; its click runs "
       "Session.run_quick (adjust_value +2 -> 5 + 2 = 7, one undo step); it appears live after quick_add", ("Drink", 7, True))(_custom)


# ---------------------------------------------------------------- level-up (section A in the UI)
def _level_button():
    s, w, b = started("levelbutton")
    x = w.blocks["experience_strip"]
    s.dispatch("add_experience", amount=-451)
    at999 = x.level_button.isEnabled()
    s.dispatch("add_experience", amount=1)
    return at999, x.level_button.isEnabled()


S.case("r-level-button", "owner: the Level up button is disabled at 1450 - 451 = 999 and enabled at 1000",
       (False, True))(_level_button)


def _level_up():
    s, w, b = started("levelup")
    x = w.blocks["experience_strip"]
    w.answer = True
    dlg = x.level_up()
    low = dlg.roll.minimum()
    dlg.roll.setValue(6)
    dlg.accept()
    t = s.view("training")
    return (low, t["level"], t["experience"]["total"], t["training"], s.character.hp_rolls,
            w.messages[-1].split("\n"), w.blocks["identity"].level.text())


S.case("r-level-up", "owner: ask -> roll (minimum 1) 6 -> level 3; xp 1450 - 1000 = 450; training 1200 + 300 = "
       "1500; rolls (8, 6, 6); the two reminders in the message box",
       (1, 3, 450, 1500, (8, 6, 6), ["Distribute the new drive points", "You got 300 training"], "Level 3"))(_level_up)


def _level_no():
    s, w, b = started("levelno")
    w.answer = False
    return w.blocks["experience_strip"].level_up(), s.view("training")["level"]


S.case("r-level-no", "owner: answering No to 'Raise the level?' changes nothing", (None, 2))(_level_no)


# ---------------------------------------------------------------- screenshots of the block in the three themes
def _shots():
    s, w, b = started("shots")
    w.resize(1280, 800)
    w.show()
    os.makedirs(SHOTS, exist_ok=True)
    out = []
    for tid in themes.shipped_ids():
        w.choose_theme(tid)
        QAPP.processEvents()
        path = os.path.join(SHOTS, "resources_%s.png" % tid)
        out.append(bool(b.grab().save(path, "PNG")) and os.path.getsize(path) > 0)
    w.close()
    return out


S.case("r-shots", "pkg 33: a screenshot of the resources block in each shipped theme (tests/ui_shots/resources_*.png)",
       [True, True, True])(_shots)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
