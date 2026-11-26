"""Package 35 P1 (owner review of package 34) without a screen (offscreen; without PySide6 the suite is SKIPPED, exit
0): Zero initiative, action / reaction squares one by one, the Sources dialog (zero rows hidden, show all), dialog
sizes, the wrapping tab bar, the AC consistency audit, the no-sources hint. Demo numbers: actions 3, reactions 1,
AC 13 (back 10), mana 5 / 8. Run: python Wp_claude/tests/ui/test_p35a.py"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import ROOT, Suite  # noqa: E402

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
FONTS = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
if os.path.isdir(FONTS):
    os.environ.setdefault("QT_QPA_FONTDIR", FONTS)
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("test_p35a: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app.session import Session  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.model.character import Item  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui import app as ua  # noqa: E402
from wp.ui import params_logic as pl  # noqa: E402
from wp.ui.screen_blocks import SB  # noqa: E402
from wp.ui.sources_dialog import open_sources  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_p35a")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_p35a_")
SHOTS = os.path.join(HERE, "..", "ui_shots")


def started(tag, demo=True):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    if demo:
        ua.start_character(w)
    else:
        s.new("Empty")
        w.character_changed()
    QAPP.processEvents()
    return s, w


def editor(s, rec=None, status=None):
    s.set_editor_mode(True)
    if rec is not None:
        s.dispatch("add_entry", collection="items", record=rec)
    s.set_editor_mode(False)


# ---------------------------------------------------------------- 1 Zero initiative
def _zero():
    s, w = started("zero")
    c = w.blocks["combat"]
    texts = [b.text() for b in c.buttons.values()]
    c.buttons["combat"].click()
    s.dispatch("spend_actions", n=2)
    c.buttons["zero"].click()
    words = []
    for lang in ("en", "ru"):
        with open(os.path.join(ROOT, "wp", "i18n", lang + ".json"), encoding="utf-8") as f:
            words += [v.lower() for v in json.load(f).values() if isinstance(v, str)]
    bad = [v for v in words if "end of turn" in v or "new round" in v or "\u043a\u043e\u043d\u0435\u0446 \u0445\u043e\u0434\u0430" in v]
    return texts, bool(c.buttons["zero"].toolTip()), s.view("combat")["actions"]["current"], c.round.text(), bad


S.case("z-zero", "owner review 1: the buttons Start combat / Zero initiative / End of cycle (with a hint); Zero "
       "initiative = the tick: actions 1 -> 3, round 1 -> 2; no 'end of turn' / 'new round' text left",
       (["Start combat", "Zero initiative", "End of cycle"], True, 3, "Round 2", []))(_zero)


# ---------------------------------------------------------------- 2 squares one by one
def _squares():
    s, w = started("squares")
    c = w.blocks["combat"]
    c.squares[2].click()                       # spend 1 (square 1 goes)
    c.squares[2].click()                       # spend 1 (square 2 goes)
    two = [bool(b.property("spent")) for b in c.squares]
    c.squares[0].click()                       # a SPENT square: return one
    back = [bool(b.property("spent")) for b in c.squares], s.view("combat")["actions"]["current"]
    c.reaction_squares[0].click()
    r1 = s.view("combat")["reactions"]["current"]
    c.reaction_squares[0].click()
    lines = [e.command for e in s.character.log][-4:]
    return two, back, r1, s.view("combat")["reactions"]["current"], lines


S.case("z-squares", "owner review 2: spend 1 then 2 (smallest first); a click on spent 1 returns one -> only 1 spent, "
       "2 actions; the reaction spent 0 and returned 1; journal lines",
       ([True, True, False], ([True, False, False], 2), 0, 1,
        ["spend_actions", "return_action", "spend_reaction", "return_reaction"]))(_squares)


# ---------------------------------------------------------------- 3 Sources dialog: zero rows hidden, show all
def _zero_rows():
    s, w = started("rows")
    d = open_sources(w, "ac:2")
    hidden = d.table.rowCount(), len(d.view["rows"]), d.hidden
    d.show_all.setChecked(True)
    shown = d.table.rowCount(), s.setting("sources_show_all")
    s.set_editor_mode(True)
    e = open_sources(w, "ac:2")
    editor_start = e.show_all.isChecked()
    e.show_all.setChecked(False)
    saved = s.setting("sources_show_all")
    s.set_editor_mode(False)
    return hidden, shown, editor_start, saved


# demo cell 2: base 10 + Dex (dodge layer) 3 = 13: 2 rows with a value, 11 zero layers hidden (13 rows; the flat layer
# is listed only with a value)
S.case("s-zero-rows", "owner review 3: AC cell 2 shows 2 of 13 rows (11 zero rows hidden); show all -> 13, the setting "
       "remembered; the editor mode starts ON and its toggle is not saved",
       ((2, 13, 11), (13, True), True, True))(_zero_rows)


# ---------------------------------------------------------------- 4 dialog sizes
def _sizes():
    s, w = started("sizes")
    d = open_sources(w, "hp_max")
    fitted = d.size().width() >= d.table.minimumWidth(), d.size().height() >= d.table.minimumHeight()
    d.resize(520, 410)
    d.done(0)
    saved = list(s.setting("dialog_sizes").get("sources"))
    again = open_sources(w, "fort").size()
    w.set_setting("dialog_sizes", {"sources": [99999, 99999]})
    big = open_sources(w, "fort")
    screen = big.screen().availableGeometry()
    return fitted, saved, (again.width(), again.height()), (big.width() <= screen.width(),
                                                            big.height() <= screen.height())


S.case("s-sizes", "owner review 4: the dialog takes its content's size; dragged to 520 x 410 -> remembered per id and "
       "used next time; never larger than the screen", ((True, True), [520, 410], (520, 410), (True, True)))(_sizes)


# ---------------------------------------------------------------- 5 the tab bar wraps
def rows_at(t, width):
    t.bar.resize(width, t.bar.height())
    t.bar.relayout()                           # a hidden widget gets its resize event only when shown
    return t.rows()


def _wrap():
    s, w = started("wrap")
    t = w.blocks["tabs"]
    before = json.dumps(s.profile("classic"), sort_keys=True)
    wide = rows_at(t, 2000)
    narrow = rows_at(t, 150)
    xs = max(b.geometry().right() for b in t.bar.buttons) <= 150 or narrow == len(t.tabs)
    s.set_editor_mode(True)
    QAPP.processEvents()
    t.pin("pin")
    pinned = s.profile("classic").get("tab_rows")
    t.pin("fewer")
    fewer = s.profile("classic").get("tab_rows"), t.rows()
    t.pin("pin")
    s.set_editor_mode(False)
    last = rows_at(t, 2000)
    return wide, narrow > wide, xs, pinned == narrow, fewer[0] == narrow - 1 and fewer[1] == narrow - 1, \
        s.profile("classic").get("tab_rows"), before == json.dumps(s.profile("classic"), sort_keys=True), last


S.case("s-wrap", "owner review 5: 13 tabs in one row when wide, more rows when narrow (no clipping); editor pin keeps "
       "the rows, one fewer works, pin again = automatic (0); resizing never rewrites the profile",
       (1, True, True, True, True, 0, True, 1))(_wrap)


# ---------------------------------------------------------------- 6 the AC consistency audit
def _places(s, w):
    """Every place an AC number is shown must agree: the cell, its tooltip, the Sources total, the variants line."""
    a = w.blocks["ac_block"]
    d = s.view("defense")
    info = pl.ac_cells(d, SB["ac_grid"], SB["ac_you"])
    bad = []
    for cid, (primary, secondary, _, _) in info.items():
        cell = a.cells[cid]
        dlg = open_sources(w, "ac:" + cid)
        tip = cell.toolTip()
        if cell.value.text() != str(primary) or dlg.total.text() != "Total %d" % primary:
            bad.append((cid, "primary", cell.value.text(), dlg.total.text()))
        if ("melee %d" % primary) not in tip or ("melee %d" % primary) not in dlg.extra.text():
            bad.append((cid, "tooltip", tip, dlg.extra.text()))
        if secondary != primary:
            want = "with parry %d" % secondary
            if cell.note.text() != want or want not in tip or want not in dlg.extra.text():
                bad.append((cid, "secondary", cell.note.text()))
        elif cell.note.text():
            bad.append((cid, "note", cell.note.text()))
    m = dict(d["modes"])
    if a.modes.text() != "flat-footed %d, touch %d" % (m["flat_footed"], m["touch"]):
        bad.append(("modes", a.modes.text()))
    if str(m["flat_footed"]) != a.cells["8"].value.text():
        bad.append(("flat_footed", m["flat_footed"], a.cells["8"].value.text()))
    return bad


def _audit():
    out = {}
    s, w = started("audit_empty", demo=False)
    out["empty"] = _places(s, w), w.blocks["ac_block"].cells["2"].value.text()
    s, w = started("audit")
    out["demo"] = _places(s, w), w.blocks["ac_block"].cells["2"].value.text()
    s.dispatch("add_status", status=Status("Ward", sid="ward", effects=(Effect("ac", 1, "deflection"),)), active=True)
    out["buff"] = _places(s, w), w.blocks["ac_block"].cells["2"].value.text()
    editor(s, Item("sh", "heavy shield", kind="shield", hands=1, shield=2, shield_type="heavy"))
    s.dispatch("equip_hands", iid="sh", side="left")
    out["shield"] = _places(s, w), w.blocks["ac_block"].cells["2"].value.text()
    s.dispatch("start_combat")
    s.dispatch("add_status", status=Status("Cheer", sid="cheer", effects=(Effect("morale_scale", 5),)), active=True)
    out["morale_on"] = _places(s, w), w.blocks["ac_block"].cells["2"].value.text()
    s.dispatch("end_combat")
    out["morale_off"] = _places(s, w), w.blocks["ac_block"].cells["2"].value.text()
    s2, w2 = started("audit_level")
    s2.dispatch("level_up", hp_roll=5)                      # level 3: the parry layer becomes 14 (the owner's 13 / 14)
    out["level3"] = _places(s2, w2), w2.blocks["ac_block"].cells["2"].value.text(), \
        w2.blocks["ac_block"].cells["2"].note.text()
    return out


# empty: 10; demo: 10 + Dex 3 = 13; + deflection 1 = 14; + heavy shield 2 = 16 (front); morale does not touch AC;
# level 3 (the owner's case): 13 big and "with parry 14" small, named in the cell, the tooltip and the Sources dialog
S.case("s-ac-audit", "owner review 6: every place shows the same AC (cell, tooltip, Sources total and variants, "
       "flat-footed / touch line) for an empty hero, the demo, a buff, a shield, morale on / off, level 3 with parry",
       {"empty": ([], "10"), "demo": ([], "13"), "buff": ([], "14"), "shield": ([], "16"), "morale_on": ([], "16"),
        "morale_off": ([], "16"), "level3": ([], "13", "with parry 14")})(_audit)


# ---------------------------------------------------------------- 7 the no-sources hint
def _hint():
    s, w = started("hint", demo=False)
    row = w.blocks["resources"].rows["mana"]
    empty = row.hint.isVisibleTo(w), row.hint_text.text()
    hp_hint = w.blocks["resources"].rows["hp"].hint.isVisibleTo(w)
    row.hint_text.clicked.emit()
    opened = w.sources.number
    row.hint_button.click()
    gone = row.hint.isVisibleTo(w), "no_sources" in s.setting("hints_seen")
    s2, w2 = started("hint_demo")
    return empty, hp_hint, opened, gone, w2.blocks["resources"].rows["mana"].hint.isVisibleTo(w2)


S.case("s-hint", "owner review 7: an empty hero (mana max 0, no sources) shows the hint under mana (not under HP 8); a "
       "click opens the mana sources; Understood! hides it for good; the demo (mana 8) shows none",
       ((True, "No sources - editor mode: click to add"), False, "mana_max", (False, True), False))(_hint)


# ---------------------------------------------------------------- 9 screenshots of items 3, 4, 5, 7
def _shots():
    out = []
    s, w = started("shots")
    s2, w2 = started("shots_empty", demo=False)
    os.makedirs(SHOTS, exist_ok=True)
    w.resize(1280, 800)
    w.show()
    w2.resize(1280, 800)
    w2.show()
    for tid in themes.shipped_ids():
        for win in (w, w2):
            win.choose_theme(tid)
        QAPP.processEvents()
        d = open_sources(w, "hp_max")
        d.show()
        QAPP.processEvents()
        shots = (("sources_rows", d), ("tabs_wrap", w.blocks["tabs"]), ("no_sources", w2.blocks["resources"]))
        for name, widget in shots:
            path = os.path.join(SHOTS, "%s_%s.png" % (name, tid))
            out.append(bool(widget.grab().save(path, "PNG")) and os.path.getsize(path) > 0)
        d.close()
    w.close()
    w2.close()
    return out


S.case("s-shots", "pkg 35 P1: screenshots sources_rows_* (items 3, 4), tabs_wrap_* (5), no_sources_* (7) in the three "
       "shipped themes", [True] * 9)(_shots)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
