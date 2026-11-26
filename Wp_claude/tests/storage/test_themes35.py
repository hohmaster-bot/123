"""Package 35 P3 (ROADMAP step 1b): the theme editor and the background picture without Qt: the contrast numbers
(WCAG 2, by hand), copy / reset / edit through the Session theme commands (the shipped themes untouched), build_qss
with a changed token, the background dimming value. Run: python Wp_claude/tests/storage/test_themes35.py"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app.session import Session  # noqa: E402
from wp.theme import qss  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui import theme_logic as tl  # noqa: E402

S = Suite("test_themes35")
TMP = tempfile.mkdtemp(prefix="wp_th35_")


def session(tag):
    return Session(os.path.join(TMP, tag, "ch"), os.path.join(TMP, tag, "user"))


# black / white: (1 + 0.05) / (0 + 0.05) = 21; #777777: channel 119 / 255 = 0.4667 -> ((0.4667 + 0.055) / 1.055) ^ 2.4
# = 0.1845 -> (1.05) / (0.2345) = 4.48 (below 4.5: a warning); #767676 -> 0.1812 -> 4.54 (passes)
S.case("t-contrast", "WCAG 2 by hand: black on white 21.0; #777777 on white 4.48 (warn); #767676 on white 4.54 (ok)",
       (21.0, 4.48, 4.54))(lambda: (round(themes.contrast_ratio("#000000", "#ffffff"), 2),
                                    round(themes.contrast_ratio("#777777", "#ffffff"), 2),
                                    round(themes.contrast_ratio("#767676", "#ffffff"), 2)))


def _rows():
    t = {"colors": {"text": "#777777", "background": "#ffffff", "surface": "#ffffff", "chip_text": "#000000",
                    "chip_neutral": "#ffffff"}}
    return tl.contrast_rows(t)


S.case("t-rows", "owner 16: the contrast lines warn (never refuse): text on background / surface 4.48 not ok, chip "
       "text 21 ok", (("text", "background", 4.48, False), ("text", "surface", 4.48, False),
                      ("chip_text", "chip_neutral", 21.0, True)))(_rows)


def _copy():
    s = session("copy")
    r = s.theme_command("theme_copy", tid="dark", name="My dark")
    tid = r.info["id"]
    e = s.theme_command("theme_edit", tid=tid, colors={"text": "#777777"})
    mine = dict(next(t for t, _ in __import__("wp.catalog.store", fromlist=["merged"]).merged(s.themes)
                     if t["id"] == tid)["colors"])["text"]
    locked = s.theme_command("theme_edit", tid="dark", colors={"text": "#000000"})
    s2 = session("copy")                     # a new Session reads the user themes file
    again = [t for t, _ in __import__("wp.catalog.store", fromlist=["merged"]).merged(s2.themes) if t["id"] == tid]
    dark = dict(themes.shipped().find("dark")["colors"])["text"]
    return r.ok, e.ok, mine, locked.reason, len(again), dark != "#777777"


S.case("t-copy", "owner 16: copy dark -> an own theme; its text colour edited (saved in the user file, read back); a "
       "shipped theme is never edited (refused shipped_theme); the shipped dark stays untouched",
       (True, True, "#777777", "shipped_theme", 1, True))(_copy)


def _reset():
    s = session("reset")
    from wp.catalog import store as cs
    from dataclasses import replace
    layers = themes.theme_edit(s.themes, tid="light", colors={"text": "#123456"})   # an old override (by hand)
    s.themes = layers
    before = dict(themes.active(s.app, s.themes)["colors"]) if s.setting("theme") == "light" else None
    r = s.theme_command("theme_reset", tid="light")
    after = dict(next(t for t, _ in cs.merged(s.themes) if t["id"] == "light")["colors"])["text"]
    refused = s.theme_command("theme_reset", tid="nope")
    _ = (before, replace)
    return r.ok, after == dict(themes.shipped().find("light")["colors"])["text"], refused.reason


S.case("t-reset", "owner 16: reset to the shipped one drops an override (the shipped colour is back); an own / unknown "
       "theme has no shipped version (refused)", (True, True, "not_shipped"))(_reset)


def _qss():
    t = dict(themes.shipped().find("dark"))
    t["colors"] = dict(t["colors"], accent="#ff00aa")
    return "#ff00aa" in qss.build_qss(t), "#ff00aa" in qss.build_qss(themes.shipped().find("dark"))


S.case("t-qss", "pkg 35: build_qss uses a changed token (accent #ff00aa appears; the shipped dark has none)",
       (True, False))(_qss)
S.case("t-dim", "owner 16: background_dim 0 -> alpha 0; 50 -> 127.5 rounds half up to 128; 100 -> 255; out of range "
       "clamped", (0, 128, 255, 255, 0))(
    lambda: (tl.dim_alpha(0), tl.dim_alpha(50), tl.dim_alpha(100), tl.dim_alpha(150), tl.dim_alpha(-5)))
S.case("t-readable", "owner 16: 'keep numbers readable' puts the token background_overlay behind the blocks; off = none",
       (True, ""))(lambda: ("QFrame#block" in tl.background_qss(themes.shipped().find("dark"), True),
                            tl.background_qss(themes.shipped().find("dark"), False)))
S.case("t-tokens", "owner 16: every colour of the screen is a token: the editor lists all 56 schema colours; the "
       "shipped themes are not editable", (56, False, True))(
    lambda: (len(tl.color_tokens()), tl.editable("dark", themes.shipped_ids()), tl.editable("my", themes.shipped_ids())))

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
