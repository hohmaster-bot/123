"""Package 38 P2 / P3 in the window (offscreen; without PySide6 the suite is SKIPPED, exit 0): the Rerolls block (default
in the right column under the combat tab: name, source, left / max, Use spends one) and the comfort-per-fight reminder
(its own button text "Take +N comfort", the button adds the comfort). Shots rerolls_* in the three themes.
Run: python Wp_claude/tests/ui/test_p38a.py"""
import os
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
    print("test_p38a: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app import ui_data  # noqa: E402
from wp.app.session import Session  # noqa: E402
from wp.catalog import store as cs  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_p38a")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_p38a_")
SHOTS = os.path.join(HERE, "..", "ui_shots")
REF = "feat:goddess_of_humanity:ally_reroll"
_A = next(a for e in cs.load_shipped("races").entries if e["id"] == "mordon" for a in e["abilities"]
          if a["id"] == "goddess_of_humanity")
SOURCE, RNAME = _A["name"], _A["rerolls"][0]["name"]


def started(tag, ch=None):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    s.new("Hero", ch or Character(training=2000, comfort_current=1))
    w.character_changed()
    QAPP.processEvents()
    return s, w


def mordon5(tag):
    s, w = started(tag)
    s.dispatch("take_race", race=ui_data.catalog_entry(s, "races", "mordon"))
    s.dispatch("buy_race_ability", aid="goddess_of_humanity")
    w.character_changed()
    QAPP.processEvents()
    return s, w


def _block():
    s, w = mordon5("block")
    b = w.blocks["rerolls"]
    row = b.widgets[REF]
    before = row["text"].text(), row["use"].isEnabled(), b.item.get("dock")
    row["use"].click()
    QAPP.processEvents()
    after = b.widgets[REF]
    return before, after["text"].text(), after["use"].isEnabled(), s.character.log[-1].command


S.case("block", "decision 7: the Rerolls block (right column) lists the Mordon reroll 1 of 1 (long rest) with its "
       "source (the history ability); Use spends it: 0 of 1, the button off, a journal line",
       (("%s (%s): 1 of 1, long rest" % (RNAME, SOURCE), True, "right"), "%s (%s): 0 of 1, long rest" % (RNAME, SOURCE),
        False, "spend_reroll"))(_block)
S.case("block-empty", "decision 7: a character without rerolls sees the empty text", "No rerolls")(
    lambda: started("empty")[1].blocks["rerolls"].list.itemAt(0).widget().text())


def _comfort():
    s, w = started("comfort")
    s.dispatch("start_combat")
    s.dispatch("edit_sheet", morale_scale=-5)
    s.dispatch("end_combat")
    w.character_changed()
    QAPP.processEvents()
    b = w.blocks["reminders"]
    nid = s.character.trigger_notes[-1].nid
    row = b.trigger_rows[nid]
    texts = row["text"].text(), row["action"].text()
    row["action"].click()
    QAPP.processEvents()
    return texts, s.character.comfort_current


# |morale| 5 -> 4 comfort; comfort 1 + 4 = 5
S.case("comfort-button", "decision 5: the combat end shows 'Comfort for the fight: +4' with the button 'Take +4 "
       "comfort'; the button adds it: 1 -> 5", (("Comfort for the fight: +4", "Take +4 comfort"), 5))(_comfort)


def _shots():
    out = []
    for theme in ("dark", "light", "grey_blue"):
        s, w = mordon5("shot_" + theme)
        w.set_setting("theme", theme)
        QAPP.processEvents()
        path = os.path.join(SHOTS, "rerolls_%s.png" % theme)
        w.grab().save(path)
        out.append(os.path.getsize(path) > 0)
    return out


S.case("shots", "the window with the Rerolls block in the three themes (the owner looks at them)",
       [True, True, True])(_shots)

if __name__ == "__main__":
    sys.exit(S.run())
