"""Package 34 part 1: the Parameters block, the AC block and the Sources dialog of the Classic window, without a
screen (offscreen; without PySide6 the suite is SKIPPED, exit 0). Numbers by hand from the demo (wp/ui/data/demo.json):
Str 14 (+2), Dex 16 (+3), Con 12 (+1), Wis 13 (+1), Cha 12; sample fighter level 2 (BAB 2, Fort good 2 + 2 // 2 = 3,
Ref / Will poor 2 // 3 = 0); pain 1 (penalty -1) from the demo hit; no armor.
Parameters: melee 2 + 2 - 1 = +3, ranged 2 + 3 - 1 = +4, initiative 3 - 1 = +2, CMB 2 + 2 - 1 = +3,
CMD 10 + 2 + 2 + 3 = 17 (not a roll), Fort 3 + 1 - 1 = +3, Ref 0 + 3 - 1 = +2, Will 0 + 1 - 1 = 0, load 0 of 129
(Str 14: light 79 L, maximum 129 L). AC: 10 + Dex 3 = 13; the back cell 8 loses Dex: 10.
Run: python Wp_claude/tests/ui/test_screen34.py"""
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
    print("test_screen34: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app.session import Session  # noqa: E402
from wp.model.character import Item  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui import app as ua  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_screen34")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_scr34_")
SHOTS = os.path.join(HERE, "..", "ui_shots")


def started(tag):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    ua.start_character(w)
    QAPP.processEvents()
    return s, w


def item(s, rec):
    s.set_editor_mode(True)
    r = s.dispatch("add_entry", collection="items", record=rec)
    s.set_editor_mode(False)
    return r


def _numbers():
    s, w = started("numbers")
    p = w.blocks["parameters"].cells
    return {k: c.value.text() for k, c in p.items()}, p["load"].note.text()


S.case("u-params", "UI_WISHES 7: the Parameters cells show the demo numbers (by hand in the header)",
       ({"attack_melee": "+3", "attack_ranged": "+4", "initiative": "+2", "cmb": "+3", "cmd": "17", "fort": "+3",
         "ref": "+2", "will": "0", "load": "0 of 129"}, "light"))(_numbers)


def _ac():
    s, w = started("ac")
    a = w.blocks["ac_block"]
    return {c: cell.value.text() for c, cell in a.cells.items() if c != "5"}, a.cells["1"].caption.text(), \
        a.modes.text()


S.case("u-ac", "UI_WISHES 7: AC 13 everywhere, the back cell 8 = 10 (Dex lost); labels; flat-footed 10, touch 13",
       ({"1": "13", "2": "13", "3": "13", "4": "13", "6": "13", "7": "13", "8": "10", "9": "13"}, "front-left",
        "flat-footed 10, touch 13"))(_ac)


def _shield():
    s, w = started("shield")
    item(s, Item("sh", "heavy shield", kind="shield", hands=1, shield=2, shield_type="heavy"))
    s.dispatch("equip_hands", iid="sh", side="left")
    a = w.blocks["ac_block"]
    return "4" in a.shield_cells(), a.cells["4"].value.text(), "[shield]" in a.cells["4"].caption.text(), \
        a.cells["5"].value.text()


S.case("u-shield", "pkg 24 rules: heavy shield left: cell 4 gets the shield border and mark, 13 + 2 = 15; 'you' names "
       "the side", (True, "15", True, "shield left"))(_shield)


def _click():
    s, w = started("click")
    w.blocks["parameters"].cells["fort"].on_click("fort")
    d1 = w.sources
    w.blocks["ac_block"].cells["1"].on_click("ac:1")
    d2 = w.sources
    w.blocks["resources"].rows["hp"].value.clicked.emit()
    d3 = w.sources
    return (d1.number, d1.total.text(), d1.add_button.isVisible(), d2.number, d2.total.text(), d3.number,
            d3.total.text())


S.case("u-click", "owner 1A: a click opens the Sources dialog: Fort total 3 (read-only: no Add), AC cell 1 total 13, "
       "the HP max 16", ("fort", "Total 3", False, "ac:1", "Total 13", "hp_max", "Total 16"))(_click)


def _editor():
    s, w = started("editor")
    w.blocks["parameters"].open_sources("will")
    d = w.sources
    refused = d.add("Iron will", 2)
    w.actions["editor"].trigger()            # View > Editor mode
    d.reload()
    added = d.add("Iron will", 2)
    after = w.blocks["parameters"].cells["will"].value.text()
    d.set_value("iron_will", 3)
    edited = w.blocks["parameters"].cells["will"].value.text()
    d.toggle("iron_will", False)
    off = w.blocks["parameters"].cells["will"].value.text()
    lines = [e.command for e in s.character.log[-3:]]
    s.undo()
    return refused.reason, added.ok, after, edited, off, w.blocks["parameters"].cells["will"].value.text(), lines


S.case("u-editor", "owner 1A: outside the editor mode refused; in it Will 0 + 2 = +2, edited to 3 -> +3, off -> 0, undo "
       "-> +3; journal lines", ("editor_mode_needed", True, "+2", "+3", "0", "+3",
                                ["source_add", "source_edit", "source_toggle"]))(_editor)


def _overload():
    s, w = started("overload")
    item(s, Item("rock", "rock", weight_l=130))
    c = w.blocks["parameters"].cells["load"]
    return c.value.text(), c.note.text(), c.value.objectName()


S.case("u-overload", "gear.md: 130 L carried > 129 -> '130 of 129', the overload text, the red style",
       ("130 of 129", "you are overloaded and can only drag", "overload"))(_overload)


def _small():
    s, w = started("small")
    before = s.profile("classic")
    w.resize(1400, 1000)
    w.show()
    QAPP.processEvents()
    big = w.adapt_level
    w.resize(640, 480)
    QAPP.processEvents()
    small = w.adapt_level
    hidden = not w.blocks["parameters"].title.isVisible()
    w.close()
    return big, small, hidden, s.profile("classic") == before


S.case("u-small", "UI_WISHES 12: a large window keeps level 0; 640 x 480 goes through gaps, captions, details "
       "(level 3) and scrolls; the saved layout is never rewritten", (0, 3, True, True))(_small)


def _shots():
    s, w = started("shots")
    w.resize(1280, 800)
    w.show()
    os.makedirs(SHOTS, exist_ok=True)
    out = []
    w.blocks["parameters"].open_sources("fort")
    d = w.sources
    d.resize(520, 360)
    for tid in themes.shipped_ids():
        w.choose_theme(tid)
        QAPP.processEvents()
        d.setStyleSheet(w.qss)
        d.show()
        QAPP.processEvents()
        for name, widget in (("parameters", w.blocks["parameters"]), ("ac", w.blocks["ac_block"]), ("sources", d)):
            path = os.path.join(SHOTS, "%s_%s.png" % (name, tid))
            out.append(bool(widget.grab().save(path, "PNG")) and os.path.getsize(path) > 0)
    d.close()
    w.close()
    return out


S.case("u-shots", "pkg 34: parameters_*, ac_*, sources_* screenshots in the three shipped themes", [True] * 9)(_shots)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
