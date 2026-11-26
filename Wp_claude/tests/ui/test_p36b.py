"""Package 36 P2 in the window (offscreen; without PySide6 the suite is SKIPPED, exit 0): the situational star and
hover on a Parameters / AC cell, the Sources dialog rows (situational, condition, cycle), the speed hover with the
movement modes, the trigger reminder with its action button and Handled, the manual condition checkbox of a status,
the manual trigger button of a feat. Demo character plus statuses / feats added by commands.
Run: python Wp_claude/tests/ui/test_p36b.py"""
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
    print("test_p36b: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app.session import Session  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.triggers import Trigger  # noqa: E402
from wp.model.character import Feat  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui import app as ua  # noqa: E402
from wp.ui.sources_dialog import open_sources  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_p36b")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_p36b_")
SHOTS = os.path.join(HERE, "..", "ui_shots")
POWER = Feat("power_of_rationality", "Power of rationality",
             effects=(Effect("save", 2, "racial", situational="vs magic"), Effect("ac", 1, situational="vs traps")))
WINGS = Feat("wings", "Dragon wings", effects=(Effect("move:fly", 20, note="average"),))
REAR = Trigger("rear", "cycle_end", "Reliable rear: +2 comfort", "change_resource", "comfort", 2)
SESSION = Trigger("session", "manual", "End of session: injury points - 4", "reduce_injury_points", "", 4)
CROWN = Feat("shadow", "Shadow of the crown", triggers=(REAR, SESSION))
MOUNT = Status("Mounted fighting", sid="mounted", active=True,
               effects=(Effect("attack_melee", 2, condition="manual:on a horse"),))


def started(tag):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    ua.start_character(w)
    s.set_editor_mode(True)
    for f in (POWER, WINGS, CROWN):
        s.dispatch("add_entry", collection="feats", record=f)
    s.set_editor_mode(False)
    s.dispatch("add_status", status=MOUNT, active=True)
    QAPP.processEvents()
    return s, w


def _cells():
    s, w = started("cells")
    fort = w.blocks["parameters"].cells["fort"]
    ac = w.blocks["ac_block"].cells["2"]
    d = open_sources(w, "fort")
    return fort.value.text(), fort.caption.text(), fort.toolTip(), ac.caption.text().endswith(" *"), \
        "vs traps" in ac.toolTip(), any("situational" in x and "vs magic" in x for x in d.extra.text().split("; "))


S.case("c-situational", "decision 8: Fort stays +3 (the demo), a star on the caption, '+2 vs magic' on hover; the AC "
       "cell gets its star and the traps line; the Sources dialog has the situational row",
       ("+3", "Fort *", "+2 vs magic (situational: not in the total)", True, True, True))(_cells)


def _speed_and_condition():
    s, w = started("speed")
    speed = w.blocks["bottom_strip"].cells[(0, "speed")].toolTip()
    melee = w.blocks["parameters"].cells["attack_melee"]
    before = melee.value.text()
    box = w.blocks["statuses"].rows["mounted"]["conditions"]["on a horse"]
    box.setChecked(True)
    after = w.blocks["parameters"].cells["attack_melee"].value.text()
    d = open_sources(w, "attack_melee")
    return speed, before, after, "while manual:on a horse: holds now" in d.extra.text()


S.case("c-speed-cond", "decisions 10, 7: the speed hover lists fly 20 ft average; the status box 'on a horse' turns "
       "the +2 on: melee +3 -> +5; the Sources dialog says the condition holds",
       ("fly 20 ft average", "+3", "+5", True))(_speed_and_condition)


def _triggers():
    s, w = started("triggers")
    s.dispatch("end_cycle")
    r = w.blocks["reminders"]
    nid = list(r.trigger_rows)[0]
    texts = r.trigger_rows[nid]["text"].text(), r.trigger_rows[nid]["action"].text()
    comfort = s.character.comfort_current
    r.trigger_rows[nid]["action"].click()
    gone = nid not in r.trigger_rows, s.character.comfort_current - comfort
    w.blocks["tabs"].select("feats")
    page = w.blocks["combat"].pages["feats"]
    page.select([f.fid for f in s.character.feats].index("shadow"))
    page.act("fire")
    manual = [x["text"].text() for x in r.trigger_rows.values()]
    return texts, gone, manual


S.case("t-reminders", "decision 6: end of cycle -> the reminder with its button 'comfort +2'; pressed: comfort + 2 and "
       "the reminder leaves; the Feats tab Trigger button fires the manual one",
       (("Reliable rear: +2 comfort", "comfort +2"), (True, 2), ["End of session: injury points - 4"]))(_triggers)


def _shots():
    s, w = started("shots")
    s.dispatch("end_cycle")
    w.resize(1280, 800)
    w.show()
    out = []
    for tid in themes.shipped_ids():
        w.choose_theme(tid)
        QAPP.processEvents()
        for name, block in (("engine_params", "parameters"), ("engine_reminders", "reminders")):
            path = os.path.join(SHOTS, "%s_%s.png" % (name, tid))
            out.append(bool(w.blocks[block].grab().save(path, "PNG")))
    w.close()
    return out


S.case("s-shots", "pkg 36 P2: screenshots engine_params_* (the stars), engine_reminders_* in the three themes",
       [True] * 6)(_shots)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
