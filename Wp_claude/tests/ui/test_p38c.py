"""Package 38 P5 in the window (offscreen; without PySide6 the suite is SKIPPED, exit 0): the effect editor dialog. Opened
from the Feats tab (Effects): add +2 attack to the feat (the attack bonus 0 -> 2), change it, remove it; a bad formula
shows its refusal and saves nothing; the search narrows the targets; opened from the catalog window for a catalog
entry. Shots effect_editor_<theme>.png in the three themes.
Run: python Wp_claude/tests/ui/test_p38c.py"""
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
    print("test_p38c: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app import effect_editor as ee  # noqa: E402
from wp.app.session import Session  # noqa: E402
from wp.core import bonuses as bo  # noqa: E402
from wp.model import derived_view as dv  # noqa: E402
from wp.model.character import Character, Feat  # noqa: E402
from wp.ui.page_window import open_page  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_p38c")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_p38c_")
SHOTS = os.path.join(HERE, "..", "ui_shots")


def started(tag):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    s.new("Hero", Character(feats=(Feat("brave", "Brave"),)))
    w.character_changed()
    QAPP.processEvents()
    return s, w


def dialog(w):
    w.blocks["tabs"].select("feats")
    p = w.blocks["combat"].pages["feats"]
    p.select(0)
    return p.act("effects")


def _flow():
    s, w = started("flow")
    d = dialog(w)
    first = d.carrier.currentData()
    d.set_form(target="attack", value="2")
    d.act("add")
    added = d.list.item(0).text(), dv.total(s.character, bo.ATTACK)
    d.list.setCurrentRow(0)
    d.set_form(value="level + 3")
    d.act("change")
    changed = dv.total(s.character, bo.ATTACK)
    d.set_form(value="2 +")
    bad = d.act("change")
    after_bad = dv.total(s.character, bo.ATTACK), bool(d.message.text())
    d.list.setCurrentRow(0)
    d.act("remove")
    return first, added, changed, bad.ok, after_bad, d.list.count(), dv.total(s.character, bo.ATTACK)


S.case("flow", "decision 9: Effects on the feat Brave: add +2 attack (0 -> 2), change to level + 3 (4), a bad formula "
       "refused with a message (still 4), remove (0)",
       (("feats", "brave"), ("attack 2", 2), 4, False, (4, True), 0, 0))(_flow)


def _search():
    s, w = started("search")
    d = dialog(w)
    d.search.setText("fight_")
    return [d.target.itemText(i) for i in range(d.target.count())]


S.case("search", "decision 9: the target search narrows the list (the comfort-per-fight constants)",
       ["const:comfort.fight_cap", "const:comfort.fight_max", "const:comfort.fight_minus"])(_search)


def _catalog():
    s, w = started("catalog")
    pw = open_page(w, "catalogs")
    page = pw.page
    page.kind.setCurrentIndex(page.kind.findData("feats"))
    ids = [r[0] for r in page.rows]
    page.select(ids.index("toughness"))
    d = page.act("effects")
    d.set_form(target="save:fort", value="1")
    d.act("add")
    return d.carrier.currentData(), [(e.target, e.value) for e in ee.catalog_effects(s, "feats", "toughness")]


S.case("catalog", "decision 9: from the catalog window: +1 Fort added to the Toughness entry (saved to the user file)",
       (("catalog", "feats", "toughness"), [("hp_max", "max(3, level)"), ("save:fort", 1)]))(_catalog)


def _shots():
    out = []
    for theme in ("dark", "light", "grey_blue"):
        s, w = started("shot_" + theme)
        w.set_setting("theme", theme)
        d = dialog(w)
        d.set_form(target="attack", value="2", situational="vs giants")
        d.act("add")
        d.resize(640, 520)
        QAPP.processEvents()
        path = os.path.join(SHOTS, "effect_editor_%s.png" % theme)
        d.grab().save(path)
        out.append(os.path.getsize(path) > 0)
    return out


S.case("shots", "the effect editor in the three themes (the owner looks at them)", [True, True, True])(_shots)

if __name__ == "__main__":
    sys.exit(S.run())
