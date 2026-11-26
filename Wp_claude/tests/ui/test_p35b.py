"""Package 35 P2 without a screen (offscreen; without PySide6 the suite is SKIPPED, exit 0): the bottom strip, the
Journal tab and the Settings tab. Demo numbers: OT 1, pain 1 (the demo hit of 5 with balance 4), speed 20, load
0 of 129. Run: python Wp_claude/tests/ui/test_p35b.py"""
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
    print("test_p35b: SKIPPED (PySide6 is not installed: pip install PySide6); TOTAL 0")
    sys.exit(0)

from wp.app.session import Session  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui import app as ua  # noqa: E402
from wp.ui.window import MainWindow  # noqa: E402

S = Suite("test_p35b")
QAPP = QApplication.instance() or QApplication([])
TMP = tempfile.mkdtemp(prefix="wp_p35b_")
SHOTS = os.path.join(HERE, "..", "ui_shots")


def started(tag):
    s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
    w = MainWindow(s, quiet=True, system_dark=True)
    w.set_setting("language", "en")
    ua.start_character(w)
    QAPP.processEvents()
    return s, w


def cells(w, row=0):
    b = w.blocks["bottom_strip"]
    return {nid: (c.value.text() if not c.isHidden() else None) for (r, nid), c in b.cells.items() if r == row}


# ---------------------------------------------------------------- the bottom strip
def _strip():
    s, w = started("strip")
    out = cells(w)
    s.dispatch("start_combat")
    s.set_editor_mode(True)
    s.dispatch("source_add", number="morale", name="Banner", value=3)
    s.set_editor_mode(False)
    in_combat = cells(w)["morale"]
    s.dispatch("end_combat")
    note = w.blocks["bottom_strip"].cells[(0, "load")].note.text()
    return out, in_combat, cells(w)["morale"], note


S.case("b-strip", "UI_WISHES 10: OT 1, pain 1, morale hidden out of combat, speed 20 (speed.base_ft, no race), load 0 "
       "of 129 (gear.md: Str 14 -> light 79, max 129); in combat with a "
       "manual morale row +3 -> +3; hidden again after combat; the load note names the category and the limits",
       ({"ot": "1", "pain": "1", "morale": None, "speed": "20", "load": "0 of 129"}, "+3", None,
        "light; light up to 79, heavy up to 129"))(_strip)


def _clicks():
    s, w = started("clicks")
    b = w.blocks["bottom_strip"]
    out = []
    for nid in ("ot", "pain", "speed", "load"):
        b.cells[(0, nid)].on_click(nid)
        out.append((w.sources.number, w.sources.total.text()))
    return out


S.case("b-click", "pkg 35: a strip cell opens the Sources dialog of its number (OT 1, pain 1, speed 20, load = the Str "
       "mod +2 of the limits)", [("ot", "Total 1"), ("pain", "Total 1"), ("speed", "Total 20"),
                                   ("load", "Total 2")])(_clicks)


def _second():
    s, w = started("second")
    b = w.blocks["bottom_strip"]
    h1 = b.height()
    b.toggle_strip()
    two = len(b.layout_rows), b.height() == 2 * h1, cells(w, 1)
    b.toggle_strip()
    return two, len(b.layout_rows), tuple(s.profile("classic")["strips"])


S.case("b-second", "UI_WISHES 10: + strip adds the second strip (temp HP 4, attention 1, initiative +2; twice the "
       "height); - strip removes it (profile strips empty again)",
       ((2, True, {"temp_hp": "4", "attention": "1", "initiative": "2"}), 1, ()))(_second)


def _journal_button():
    s, w = started("jbutton")
    w.blocks["bottom_strip"].journal_button.click()
    c = w.blocks["combat"]
    return w.blocks["tabs"].tabs[w.blocks["tabs"].bar.currentIndex()], c.stack.currentWidget() is c.pages["journal"]


S.case("b-journal", "UI_WISHES 10: the Journal button opens the Journal tab of the right column", ("journal", True))(
    _journal_button)


# ---------------------------------------------------------------- the journal tab
def _journal():
    s, w = started("journal")
    j = w.blocks["combat"].tab_page("journal")
    s.dispatch("adjust_value", resource="mana", delta=1)
    s.dispatch("adjust_value", resource="spirit", delta=-1)
    first = [(e.command, e.params.get("resource")) for e in j.lines[:2]]
    j.text.setText("spirit")
    spirit = [(e.command, e.params.get("resource")) for e in j.lines]
    j.text.setText("")
    j.add_note("Met the Duke")
    note = j.lines[0].command, j.lines[0].params.get("text"), s.character.journal_notes
    j.undo()
    after_undo = s.character.journal_notes, s.can_redo(), j.redo_button.isEnabled()
    j.redo()
    j.kind.setCurrentIndex(j.kinds.index("note"))
    only = [e.command for e in j.lines]
    return first, spirit, note, after_undo, s.character.journal_notes, only


S.case("j-tab", "pkg 35: newest first (spirit, then mana); text filter 'spirit' (also the demo's set_value); a note "
       "is a journal line "
       "(journal_note, the text kept, notes 1); undo -> 0 and Redo enabled; redo -> 1; the kind filter Notes",
       ([("adjust_value", "spirit"), ("adjust_value", "mana")], [("adjust_value", "spirit"), ("set_value", "spirit")],
        ("journal_note", "Met the Duke", 1),
        (0, True, True), 1, ["journal_note"]))(_journal)


def _modes():
    s, w = started("modes")
    j = w.blocks["combat"].tab_page("journal")
    w.set_setting("journal_archive_at", 10)           # full mode: at 10 lines the old ones go to the archive
    w.set_setting("journal_archive_keep", 0)
    for _ in range(12):
        s.dispatch("adjust_value", resource="mana", delta=1)
    full = len(j.lines), len(s.full_log())
    w.set_setting("journal_short_max", 2)
    w.set_setting("journal_mode", "short")
    s.dispatch("adjust_value", resource="mana", delta=1)
    short = len(j.lines), j.mode.currentIndex()
    j.set_mode(1)
    return full[0] == full[1] and full[0] > 2, short, s.setting("journal_mode"), j.mode.currentIndex(),         len(j.lines) > 2


S.case("j-modes", "D29: the full mode shows the whole journal with the archive; the short mode only the last "
       "journal_short_max (2) lines in memory; the switch back to full is the app setting and shows the archive again",
       (True, (2, 0), "full", 1, True))(_modes)


# ---------------------------------------------------------------- the settings tab
def _settings():
    s, w = started("settings")
    p = w.blocks["combat"].tab_page("settings")
    p.set("language", "ru")
    p.choose_theme("light")
    p.set("font_size", 14)
    p.set("ui_scale", 1.25)
    p.set("hints_off", True)
    p.set("journal_mode", "short")
    p.profile(quick_cells=12, quick_columns=6)
    p.set("resource_style", "flat")
    p.editor(True)
    s2 = Session(s.characters_dir, s.user_dir)
    keys = ("language", "theme", "font_size", "ui_scale", "hints_off", "journal_mode", "resource_style")
    prof = s2.profile("classic")
    shown = p.w["language"].currentData(), p.w["theme"].currentData(), p.w["font_size"].value(), \
        p.w["editor_mode"].isChecked()
    return {k: s2.setting(k) for k in keys}, (prof["quick_cells"], prof["quick_columns"]), shown, s.editor_mode


S.case("s-roundtrip", "pkg 35: every Settings tab control is a settings command; a new Session reads them back (save "
       "and load); the editor mode is a Session state",
       ({"language": "ru", "theme": "light", "font_size": 14, "ui_scale": 1.25, "hints_off": True,
         "journal_mode": "short", "resource_style": "flat"}, (12, 6), ("ru", "light", 14, True), True))(_settings)


def _resets():
    s, w = started("resets")
    p = w.blocks["combat"].tab_page("settings")
    w.session_settings("hint_dismiss", hint_id="first_run")
    p.w["hints_reset"].click()
    hints = list(s.setting("hints_seen"))
    p.profile(quick_cells=12)
    p.w["profile_reset"].click()
    return hints, s.profile("classic")["quick_cells"]


S.case("s-resets", "UI_WISHES 13 / 14: show all hints again -> none seen; restore the default profile -> 8 cells",
       ([], 8))(_resets)


def _shots():
    s, w = started("shots")
    s.dispatch("start_combat")
    w.resize(1280, 800)
    w.show()
    os.makedirs(SHOTS, exist_ok=True)
    out = []
    c = w.blocks["combat"]
    for tid in themes.shipped_ids():
        w.choose_theme(tid)
        QAPP.processEvents()
        for name in ("journal", "settings"):
            w.blocks["tabs"].select(name)
            QAPP.processEvents()
            path = os.path.join(SHOTS, "%s_%s.png" % (name, tid))
            out.append(bool(c.grab().save(path, "PNG")) and os.path.getsize(path) > 0)
        path = os.path.join(SHOTS, "strip_%s.png" % tid)
        out.append(bool(w.blocks["bottom_strip"].grab().save(path, "PNG")) and os.path.getsize(path) > 0)
    w.close()
    return out


S.case("s-shots", "pkg 35 P2: screenshots strip_*, journal_*, settings_* in the three shipped themes", [True] * 9)(_shots)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
