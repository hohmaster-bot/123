"""Package 37 P1 in the window (offscreen; without PySide6 the suite is SKIPPED, exit 0): the catalog trainings of the
Training tab (show locked, Buy units), the links both ways in the Feats tab (hover held by / holds, a lost holder red,
the Link action, dependents under their parent). Shots tab_training_*, links_* in the three themes.
Run: python Wp_claude/tests/ui/test_p37a.py"""
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
    print("test_p37a: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app import ui_data  # noqa: E402
from wp.app.session import Session  # noqa: E402
from wp.model.character import Character, Feat, Item  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_p37a")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_p37a_")
SHOTS = os.path.join(HERE, "..", "ui_shots")


def started(tag, race=None, ch=None):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    s.new("Hero", ch or Character(training=2000))
    if race:
        s.dispatch("take_race", race=ui_data.catalog_entry(s, "races", race))
    w.character_changed()
    QAPP.processEvents()
    return s, w


def _training():
    s, w = started("training", "ragmal")
    w.blocks["tabs"].select("training")
    p = w.blocks["combat"].pages["training"]
    rows = [p.catalog.item(r, 0).text() for r in range(p.catalog.rowCount())]
    p.select_training("ragmal_mana")
    p.buy(3)
    after = s.character.training, p.catalog.item(0, 3).text()
    s2, w2 = started("locked")
    w2.blocks["tabs"].select("training")
    q = w2.blocks["combat"].pages["training"]
    hidden = q.catalog.rowCount()
    q.show_locked.setChecked(True)
    return rows, after, hidden, q.catalog.item(0, 5).text()


S.case("t-tab", "decision 2: the Ragmal sees Mana training; Buy 3 units: 2000 - 600 = 1400, units 3; a hero without the "
       "ability sees nothing until 'show locked', then the reason",
       (["\u0422\u0440\u0435\u043d\u0438\u0440\u043e\u0432\u043a\u0430 \u043c\u0430\u043d\u044b"], (1400, "3"), 0, "needs the ability magic_body"))(_training)


def _links():
    ch = Character(items=(Item("ring", "golden ring"),),
                   feats=(Feat("parent", "Parent"), Feat("child", "Child", held_by="feat:parent"),
                          Feat("lost", "Lost", held_by="item:gone")))
    s, w = started("links", ch=ch)
    w.blocks["tabs"].select("feats")
    p = w.blocks["combat"].pages["feats"]
    names = [p.table.item(r, 0).text() for r in range(p.table.rowCount())]
    tips = {p.table.item(r, 0).text().strip(): p.table.item(r, 0).toolTip() for r in range(p.table.rowCount())}
    p.select(names.index("Lost"))
    p.holder.setCurrentIndex(p.holder.findData("item:ring"))
    p.act("link")
    return names, "holds: Child" in tips["Parent"], "held by: Parent" in tips["Child"], \
        ("not backed" in tips["Lost"] and "color:" in tips["Lost"]), dict((f.fid, f.held_by) for f in s.character.feats)["lost"]


S.case("l-tab", "decision 5: Child listed under Parent (indented); hover: Parent 'holds: Child', Child 'held by: Parent', "
       "Lost red 'not backed'; Link to the ring through the command",
       (["Parent", "    Child", "Lost"], True, True, True, "item:ring"))(_links)


def _shots():
    out = []
    ch = Character(items=(Item("ring", "golden ring"),),
                   feats=(Feat("parent", "Parent"), Feat("child", "Child", held_by="feat:parent"),
                          Feat("lost", "Lost", held_by="item:gone")))
    s, w = started("shots", "ragmal")
    s2, w2 = started("shots_links", ch=ch)
    for win in (w, w2):
        win.resize(1280, 800)
        win.show()
    for tid in themes.shipped_ids():
        for win, tab, name in ((w, "training", "tab_training"), (w2, "feats", "links")):
            win.choose_theme(tid)
            win.blocks["tabs"].select(tab)
            QAPP.processEvents()
            path = os.path.join(SHOTS, "%s_%s.png" % (name, tid))
            out.append(bool(win.blocks["combat"].grab().save(path, "PNG")))
    w.close()
    w2.close()
    return out


S.case("s-shots", "pkg 37 P1: screenshots tab_training_*, links_* in the three themes", [True] * 6)(_shots)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
