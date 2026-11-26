"""Package 35 P5 (ROADMAP step 8): the Classic layout editor. Qt-free numbers (snap, move, resize, column) and an
offscreen UI round trip (move / hide / restore, warnings that never forbid, the profile written only by the editor;
without PySide6 the UI part is SKIPPED). Run: python Wp_claude/tests/ui/test_layout35.py"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.ui import layout_logic as ll  # noqa: E402

S = Suite("test_layout35")
TMP = tempfile.mkdtemp(prefix="wp_lay35_")
SHOTS = os.path.join(HERE, "..", "ui_shots")

S.case("l-snap", "UI_WISHES 13: grid snap 10: 123 -> 120, 125 -> 130 (half up), 0 -> 0; step 0 leaves the value",
       (120, 130, 0, 123))(lambda: (ll.snap(123, 10), ll.snap(125, 10), ll.snap(0, 10), ll.snap(123, 0)))
PANELS = [{"id": "a", "dock": "left", "position": [0, 0], "size": [260, 170]},
          {"id": "b", "dock": "left", "position": [0, 180], "size": [260, 380]},
          {"id": "c", "dock": "right", "position": [0, 0], "size": [220, 90]}]
S.case("l-move", "pkg 35: b up swaps the places of a and b; a up at the edge: nothing",
       ({"b": {"position": [0, 0]}, "a": {"position": [0, 180]}}, {}))(
    lambda: (ll.move_fields(PANELS, "b", -1), ll.move_fields(PANELS, "a", -1)))
S.case("l-column", "pkg 35: c to the left column goes under b: 180 + 380 + 10 = 570 (snapped); to an empty column y 0",
       ({"dock": "left", "position": [0, 570]}, {"dock": "center", "position": [0, 0]}))(
    lambda: (ll.to_column(PANELS, "c", "left", 10), ll.to_column(PANELS, "c", "center", 10)))
S.case("l-resize", "pkg 35: 260 x 170 wider by 10 -> 270; 263 snaps to 260; never below one step",
       ({"size": [270, 170]}, {"size": [260, 170]}, {"size": [10, 10]}))(
    lambda: (ll.resize_fields((260, 170), 10, 0, 10), ll.resize_fields((263, 170), 0, 0, 10),
             ll.resize_fields((5, 5), -10, -10, 10)))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
FONTS = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
if os.path.isdir(FONTS):
    os.environ.setdefault("QT_QPA_FONTDIR", FONTS)
try:
    from PySide6.QtWidgets import QApplication
    HAVE_QT = True
except ImportError:
    HAVE_QT = False

if HAVE_QT:
    from wp.app.session import Session  # noqa: E402
    from wp.theme import themes  # noqa: E402
    from wp.ui import app as ua  # noqa: E402
    from wp.ui.layout_editor import open_layout_editor  # noqa: E402
    from wp.ui.window import MainWindow  # noqa: E402
    QAPP = QApplication.instance() or QApplication([])

    WINDOWS = []

    def started(tag):
        s = Session(os.path.join(TMP, tag, "characters"), os.path.join(TMP, tag, "settings"))
        w = MainWindow(s, quiet=True, system_dark=True)
        WINDOWS.append(w)
        w.set_setting("language", "en")
        ua.start_character(w)
        s.set_editor_mode(True)
        QAPP.processEvents()
        return s, w

    def panel(s, pid):
        return next(dict(i) for i in s.profile("classic")["panels"] if i["id"] == pid)

    def _roundtrip():
        s, w = started("roundtrip")
        before = json.dumps(s.profile("classic"), sort_keys=True)
        w.resize(700, 500)
        w.adapt()
        unchanged = before == json.dumps(s.profile("classic"), sort_keys=True)
        e = open_layout_editor(w)
        e.select("resources")
        e.act("up")                                   # resources above identity
        moved = [i["id"] for i in sorted((dict(i) for i in s.profile("classic")["panels"] if i["dock"] == "left"),
                                         key=lambda i: tuple(i["position"])[::-1])]
        e.select("favorites")
        e.set_visible(False)
        hidden = "favorites" not in w.blocks, panel(s, "favorites")["visible"]
        e.select("tabs")
        e.act("wider")
        wide = panel(s, "tabs")["size"][0]
        e.set_tab_rows(2)                             # the tab bar pin from P1 is part of the editor
        pinned = s.profile("classic")["tab_rows"], w.blocks["tabs"].bar.pinned
        e.reset()
        back = json.dumps(s.profile("classic"), sort_keys=True) == before, "favorites" in w.blocks
        return unchanged, moved, hidden, wide, pinned, back

    S.case("l-roundtrip", "UI_WISHES 13: a resize never writes the profile; resources up (above identity); favourites "
           "hidden (the block leaves the window); tabs 300 + 10 = 310 (snap 10); the tab rows pinned to 2; restore the default profile = as before",
           (True, ["resources", "identity"], (True, False), 310, (2, 2), (True, True)))(_roundtrip)

    def _warnings():
        s, w = started("warnings")
        e = open_layout_editor(w)
        e.select("resources")
        e.set_visible(False)                          # all HP controls hidden: a warning, not a refusal
        hp = "hp_controls_hidden" in e.warning_ids, panel(s, "resources")["visible"]
        e.set_visible(True)
        e.select("identity")
        for _ in range(30):
            e.act("narrower")                         # 260 -> 10 (one step): under the minimum, still saved
        return hp, "block_under_minimum" in e.warning_ids, panel(s, "identity")["size"][0]

    S.case("l-warnings", "UI_WISHES 13: hiding the resources warns 'all HP controls hidden' (saved anyway); a block "
           "under its minimum warns, never forbidden (10 px saved)", ((True, False), True, 10))(_warnings)

    def _shots():
        out = []
        s, w = started("shots")
        w.resize(1280, 800)
        w.show()
        os.makedirs(SHOTS, exist_ok=True)
        for tid in themes.shipped_ids():
            w.choose_theme(tid)
            e = open_layout_editor(w)
            e.show()
            QAPP.processEvents()
            path = os.path.join(SHOTS, "layout_editor_%s.png" % tid)
            out.append(bool(e.grab().save(path, "PNG")) and os.path.getsize(path) > 0)
            e.close()
        w.close()
        return out

    S.case("l-shots", "pkg 35 P5: screenshots layout_editor_* in the three shipped themes", [True] * 3)(_shots)



def _cleanup():
    """Close and delete every window before the interpreter ends (rebuilt regions leave no Qt object behind)."""
    if HAVE_QT:
        for w in WINDOWS:
            for name in ("layout_editor", "sources"):
                d = getattr(w, name, None)
                if d is not None:
                    d.close()
                    d.deleteLater()
            w.close()
            w.deleteLater()
        QAPP.processEvents()


if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        _cleanup()
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
