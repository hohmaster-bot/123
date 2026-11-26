"""Package 36 P3 in the window (offscreen; without PySide6 the suite is SKIPPED, exit 0): the Race tab (replaces the
placeholder; Class stays one): the empty state, Take race from the catalog (a user catalog file with one test race),
Take of a priced ability, Change race with the confirmation list. Shots race_*.
Run: python Wp_claude/tests/ui/test_race36.py"""
import io
import json
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
    print("test_race36: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app.session import Session  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_race36")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_race36_")
SHOTS = os.path.join(HERE, "..", "ui_shots")
RACES = [{"id": "zz_testling", "name": "Testling", "module": "test", "type_tags": ["humanoid"], "speed": 25,
          "effects": [{"target": "stat:str", "value": 2}, {"target": "hp_max", "value": 6}],
          "abilities": [{"id": "keen", "name": "Keen", "text": "+1 to saves.",
                         "effects": [{"target": "save", "value": 1}]},
                        {"id": "wings", "name": "Wings", "price": 600, "text": "Fly 20 ft (average).",
                         "effects": [{"target": "move:fly", "value": 20, "note": "average"}]}],
          "quirks": [{"id": "oath", "name": "Oath", "text": "Keeps the oath."}], "languages": ["Old tongue"]},
         {"id": "zz_other", "name": "Other", "module": "test", "speed": 20,
          "effects": [{"target": "stat:dex", "value": 2}], "abilities": [], "languages": ["City"]}]


def started(tag):
    user = os.path.join(TMP, tag, "settings")
    os.makedirs(os.path.join(user, "catalogs"), exist_ok=True)
    with io.open(os.path.join(user, "catalogs", "races.json"), "w", encoding="utf-8") as f:
        json.dump({"kind": "races", "format": 1, "title": "test", "counter": 0, "retired": [], "meta": {},
                   "entries": RACES}, f)
    s = Session(os.path.join(TMP, tag, "characters"), user)
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    s.new("Hero", Character(training=1000))
    w.character_changed()
    w.blocks["tabs"].select("race")
    QAPP.processEvents()
    return s, w, w.blocks["combat"].pages["race"]


def pick(p, rid):
    p.choice.setCurrentIndex(p.choice.findData(rid))


def _flow():
    s, w, p = started("flow")
    empty = p.summary.text(), p.buttons["change"].isEnabled()
    pick(p, "zz_testling")
    p.act("take")
    taken = p.summary.text(), [p.table.item(r, 0).text() for r in range(p.table.rowCount())], \
        p.table.item(1, 0).toolTip()
    p.select(1)
    p.act("buy")
    bought = s.character.training, p.table.item(1, 3).text()
    pick(p, "zz_other")
    w.answer = False
    p.act("change")
    asked = w.messages[-1]
    stayed = s.character.race_id
    w.answer = True
    p.act("change")
    return empty, taken, bought, ("Oath" in asked and "Wings" in asked, stayed), s.character.race_id, \
        s.character.training


S.case("r-flow", "decision 15: no race -> the empty state; Take race Testling: the summary (speed 25, Old tongue "
       "native), the abilities with the text on hover; Take Wings: 1000 - 600 = 400; Change race asks with the list "
       "(Oath, Wings ...): No keeps it, Yes changes to Other; training stays 400",
       (("No race yet: choose one and press Take race", False),
        ("Testling (test); humanoid; speed 25 ft; languages: Old tongue *", ["Keen", "Wings"], "Fly 20 ft (average)."),
        (400, "yes"), (True, "zz_testling"), "zz_other", 400))(_flow)


def _class_placeholder():
    s, w, p = started("class")
    w.blocks["tabs"].select("class")
    c = w.blocks["combat"]
    return c.stack.currentWidget() is c.placeholder, c.placeholder.text()


S.case("r-class", "pkg 36: the Class tab stays a placeholder", (True, "Class: this tab comes in a later step"))(
    _class_placeholder)


def _shots():
    s, w, p = started("shots")
    pick(p, "zz_testling")
    p.act("take")
    w.resize(1280, 800)
    w.show()
    out = []
    for tid in themes.shipped_ids():
        w.choose_theme(tid)
        w.blocks["tabs"].select("race")
        QAPP.processEvents()
        path = os.path.join(SHOTS, "race_%s.png" % tid)
        out.append(bool(w.blocks["combat"].grab().save(path, "PNG")))
    w.close()
    return out


S.case("r-shots", "pkg 36 P3: screenshots race_* in the three shipped themes", [True] * 3)(_shots)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
