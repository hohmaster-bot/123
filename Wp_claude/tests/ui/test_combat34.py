"""Package 34 part 2: the statuses / favourites / reminders blocks, the tab bar and the combat tab, without a screen
(offscreen; without PySide6 the suite is SKIPPED, exit 0). Demo numbers: 3 actions, 1 reaction, the unarmed attack.
Run: python Wp_claude/tests/ui/test_combat34.py"""
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
    print("test_combat34: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app.session import Session  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui import app as ua  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_combat34")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_cmb34_")
SHOTS = os.path.join(HERE, "..", "ui_shots")
RAGE = Status("Rage", sid="rage", duration="ticks", full_ticks=5, effects=(Effect("attack", 2, "morale"),))
BLESS = Status("Bless", sid="bless", effects=(Effect("save", 1, "morale"),))


def started(tag, statuses=True):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    ua.start_character(w)
    if statuses:
        s.dispatch("add_status", status=RAGE, active=True)
        s.dispatch("add_status", status=BLESS)
    QAPP.processEvents()
    return s, w


def _filters():
    s, w = started("filters")
    b = w.blocks["statuses"]
    out = [b.shown()]
    b.set_mode("active")
    out.append(b.shown())
    b.set_mode("all")
    b.rows["bless"]["star"].click()                 # a favourite through set_status_favorite
    b.set_mode("favorites")
    out.append(b.shown())
    return out, b.rows["bless"]["info"].text(), w.blocks["favorites"].chips


S.case("c-filters", "UI_WISHES 8: All = rage, bless; Active = rage; the star makes bless a favourite -> Favorites = "
       "bless and the favourites row shows it", ([["rage", "bless"], ["rage"], ["bless"]], "off", ["Bless"]))(_filters)


def _toggle():
    s, w = started("toggle")
    b = w.blocks["statuses"]
    b.rows["bless"]["on"].click()                   # activate_status
    on = [st.active for st in s.character.statuses]
    b.rows["rage"]["on"].click()                    # remove_status (ends it, the entry stays)
    return on, [st.active for st in s.character.statuses], b.rows["rage"]["info"].text()


S.case("c-toggle", "buffs.md: On activates bless (rage stays active); End ends rage, the entry stays",
       ([True, True], [False, True], "off"))(_toggle)


def _effects():
    s, w = started("effects")
    w.blocks["statuses"].rows["rage"]["name"].click()
    d = w.sources
    return d.number, d.total.text(), [(r["name"], r["value"]) for r in d.view["rows"]], d.add_button.isVisible()


S.case("c-effects", "UI_WISHES 8: a click on a buff opens its effects in the Sources dialog (read-only)",
       ("status:rage", "Effects", [("attack", 2)], False))(_effects)


def _reminders():
    s, w = started("reminders", statuses=False)
    s.dispatch("add_experience", amount=1000)           # 1450 + 1000 -> 1999: the excess reminder (pkg 33)
    r = w.blocks["reminders"]
    before = r.texts()
    s.dismiss_note(0)
    return before, r.texts()


S.case("c-reminders", "owner: a one-shot reminder (xp excess: of 1000 only 549 counted) stays until dismissed",
       (["Experience is at most 1999: of 1000 only 549 counted, the excess is not counted"], []))(_reminders)


def _actions():
    s, w = started("actions", statuses=False)
    c = w.blocks["combat"]
    c.squares[2].click()                            # any free square spends ONE: the smallest number goes
    first = [not b.property("spent") for b in c.squares]          # pkg 35: spent squares stay clickable (return)
    c.squares[2].click()
    second = [not b.property("spent") for b in c.squares]
    c.reaction_squares[0].click()
    return first, second, [not b.property("spent") for b in c.reaction_squares],         s.view("combat")["actions"]["current"]


S.case("c-actions", "combat.md (owner): spending takes the smallest number first: 1 grey, then 1 and 2; the reaction "
       "spent; 3 - 2 = 1 action left", ([False, True, True], [False, False, True], [False], 1))(_actions)


def _combat():
    s, w = started("combat", statuses=False)
    c = w.blocks["combat"]
    c.buttons["combat"].click()
    on = s.view("combat")["in_combat"], c.buttons["combat"].text(), c.round.text()
    c.buttons["zero"].click()                       # pkg 35: Zero initiative (the tick)
    rnd = c.round.text()
    c.buttons["combat"].click()
    return on, rnd, s.view("combat")["in_combat"]


S.case("c-combat", "combat.md: Start combat -> round 1 (button End combat); Zero initiative -> round 2; End combat",
       ((True, "End combat", "Round 1"), "Round 2", False))(_combat)


def _quick():
    s, w = started("quick", statuses=False)
    w.session_settings("quick_add", button={"label": "Drink", "action": {"command": "adjust_value",
                                                                          "params": {"resource": "mana", "delta": 1}}})
    c = w.blocks["combat"]
    n8 = len(c.quick_cells)
    c.quick_cells[0].click()
    mana = s.view("resources")["mana"]["current"]
    w.session_settings("profile_set", mode="classic", pid="default", quick_cells=12)
    return n8, c.quick_cells[0].text(), mana, len(c.quick_cells), c.grid.columnCount()


S.case("c-quick", "UI_WISHES 9: 8 cells by default (4 columns); Drink runs (mana 5 + 1 = 6); quick_cells 12 -> 12",
       (8, "Drink", 6, 12, 4))(_quick)


def _tabs():
    s, w = started("tabs", statuses=False)
    t, c = w.blocks["tabs"], w.blocks["combat"]
    names = [t.bar.tabText(i) for i in range(t.bar.count())]
    t.bar.setCurrentIndex(t.tabs.index("race"))          # pkg 35: Skills has content now; Race stays a placeholder
    other = c.stack.currentWidget() is c.placeholder, c.placeholder.text()
    t.bar.setCurrentIndex(0)
    return len(names), names[0], other, c.stack.currentWidget() is c.page


S.case("c-tabs", "UI_WISHES 9: 13 tabs; Race shows only its placeholder (no fake content); back to Combat",
       (13, "Combat", (True, "Race: this tab comes in a later step"), True))(_tabs)


def _shots():
    s, w = started("shots")
    s.dispatch("set_status_favorite", sid="bless", value=True)
    s.dispatch("spend_actions", n=1)
    w.resize(1280, 800)
    w.show()
    os.makedirs(SHOTS, exist_ok=True)
    out = []
    for tid in themes.shipped_ids():
        w.choose_theme(tid)
        QAPP.processEvents()
        for name, widget in (("statuses", w.blocks["statuses"]), ("combat", w.blocks["combat"])):
            path = os.path.join(SHOTS, "%s_%s.png" % (name, tid))
            out.append(bool(widget.grab().save(path, "PNG")) and os.path.getsize(path) > 0)
    w.close()
    return out


S.case("c-shots", "pkg 34: statuses_* and combat_* screenshots in the three shipped themes", [True] * 6)(_shots)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
