"""Package 35 P4 without a screen (offscreen; without PySide6 the suite is SKIPPED, exit 0): one test per content tab
(Injuries, Drives, Inventory, Training, Rest, Skills, Feats, Catalogs): real numbers of a hand-built character and one
action through a Session command; the expand button never rewrites the profile. Shots tab_<name>_dark.png.
Hero: Str 14 (+2), Dex 12, Con 12 (+1), others 10; OT 7, comfort 5 of 5, training 300.
Run: python Wp_claude/tests/ui/test_tabs35.py"""
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
    print("test_tabs35: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app.session import Session  # noqa: E402
from wp.model.character import ABILITIES, Ability, Character, Item  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_tabs35")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_tabs35_")
SHOTS = os.path.join(HERE, "..", "ui_shots")


def hero():
    base = {"str": 14, "dex": 12, "con": 12}
    return Character(abilities={a: Ability(base=base.get(a, 10)) for a in ABILITIES}, trauma=7, training=300,
                     comfort_current=5)


def started(tag, tab, ch=None):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    s.new("Hero", ch or hero())
    w.character_changed()
    w.blocks["tabs"].select(tab)
    QAPP.processEvents()
    return s, w, w.blocks["combat"].pages[tab]


def cells(page):
    t = page.table
    return [[t.item(r, c).text() for c in range(t.columnCount())] for r in range(t.rowCount())]


def shot(w, name):
    w.resize(1280, 800)
    w.show()
    w.choose_theme("dark")
    QAPP.processEvents()
    os.makedirs(SHOTS, exist_ok=True)
    path = os.path.join(SHOTS, "tab_%s_dark.png" % name)
    ok = bool(w.blocks["combat"].grab().save(path, "PNG")) and os.path.getsize(path) > 0
    w.close()
    return ok


def _injuries():
    s, w, p = started("injuries", "injuries")
    empty = p.empty.isVisible() or p.empty.text() != "", p.summary.text()
    p.severity.setCurrentIndex(0)
    p.act("take")                                   # a light injury: OT 7 - 2 = 5 (injuries.md 2 / 5 / 12)
    return empty, p.summary.text(), cells(p)[0][:2], shot(w, "injuries")


S.case("t-injuries", "injuries.md: no injury (empty state), OT 7; take a light injury -> OT 7 - 2 = 5, one row",
       ((True, "OT 7, injuries 0"), "OT 5, injuries 1", ["light", "light"], True))(_injuries)


def _drives():
    s, w, p = started("drives", "drives")
    s.set_editor_mode(True)
    s.dispatch("add_drive", name="Growth", level=2)
    s.set_editor_mode(False)
    before = cells(p)[0][:3]
    p.select(0)
    p.act("up")                                     # drive_buy_up: level 3 for 3 comfort
    return before, cells(p)[0][2], s.character.comfort_current, shot(w, "drives")


S.case("t-drives", "narrative.md: drive Growth level 2 without a principle (marked !: the taboo is needed from level 2); "
       "buy +1 -> 3 for 3 comfort (5 - 3 = 2; drives.buy_up_cost)", (["Growth !", "", "2"], "3", 2, True))(_drives)


def _inventory():
    ch = hero()
    s, w, p = started("inventory", "inventory")
    s.set_editor_mode(True)
    s.dispatch("add_entry", collection="items", record=Item("cloak", "cloak", weight_l=20))
    s.set_editor_mode(False)
    rows = cells(p)
    p.select(0)
    p.act("equip")
    before = json.dumps(s.profile("classic"), sort_keys=True)
    p.toggle_expand()
    hidden = not w.blocks["resources"].isVisibleTo(w), w.expanded
    p.toggle_expand()
    _ = ch
    return rows[0][:3], p.summary.text(), s.character.items[0].equipped, hidden, w.expanded, \
        before == json.dumps(s.profile("classic"), sort_keys=True), w.blocks["resources"].isVisibleTo(w), \
        shot(w, "inventory")


# load: Str 14 -> light up to 86, max 129 (gear.md table as in package 34); the cloak 20 L -> "20 of 129 light"
S.case("t-inventory", "gear.md: the cloak 20 L, 1; load 20 of 129 (light); Equip -> worn; Expand hides the other "
       "blocks and Collapse brings them back; the profile is never rewritten",
       (["cloak", "20", "1"], "Load 20 of 129 (light)", True, (True, "combat"), None, True, True, True))(_inventory)


def _training():
    s, w, p = started("training", "training")
    s.set_editor_mode(True)
    s.dispatch("add_entry", collection="items", record=Item("ring", "ring", qualification_n=2))
    s.set_editor_mode(False)
    rows, before = cells(p), p.summary.text().split(";")[0]
    p.select(0)
    r = p.act("qualify")                            # gear.md: qualification 50 x 2 = 100 training
    return before, rows, r.ok, s.character.training, cells(p), shot(w, "training")


S.case("t-training", "gear.md: training 300; the ring needs qualification 2; buy -> 300 - 50 x 2 = 200, bought",
       ("Training 300", [["ring", "2", ""]], True, 200, [["ring", "2", "yes"]], True))(_training)


def _rest():
    ch = hero()
    s, w, p = started("rest", "rest", ch)
    s.dispatch("set_value", resource="hp", value=3)
    rows = [r[0] for r in cells(p)]
    p.act("short")
    return rows, [e.command for e in s.character.log][-1], shot(w, "rest")


S.case("t-rest", "rest.md: HP below max -> the short rest offers healing; Short rest runs short_rest",
       (["heal"], "short_rest", True))(lambda: (lambda r: ([x for x in r[0] if x == "heal"],) + r[1:])(_rest()))


def _skills():
    s, w, p = started("skills", "skills")
    empty = p.empty.text()
    return empty, shot(w, "skills")


S.case("t-skills", "skills.md: a hero without skills shows the empty state (no fake rows)",
       ("No skills yet", True))(_skills)


def _feats():
    s, w, p = started("feats", "feats")
    return p.empty.text(), p.summary.text(), shot(w, "feats")


S.case("t-feats", "pkg 35: no feats -> the empty state; the feat catalog count comes from the catalog data (3 samples)",
       ("No feats yet", "Feats 0; in the catalog 3", True))(_feats)


def _catalogs():
    from wp.ui.page_window import open_page          # pkg 36 P1.3: Catalog is a top menu with its own window
    s, w, _ = started("catalogs", "journal")
    p = open_page(w, "catalogs").page
    p.kind.setCurrentIndex(p.kind.findData("feats"))
    rows = [r[0] for r in cells(p)]
    return rows, p.expand_button.isHidden(), shot(w, "catalogs")


S.case("t-catalogs", "pkg 35 / 36: the catalog browser (own window of the Catalog menu) lists the feat catalog "
       "entries (read-only); no Expand in an own window", (["finesse_training"], True, True))(
    lambda: (lambda r: ([x for x in r[0] if x == "finesse_training"],) + r[1:])(_catalogs()))

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
