"""The theme editor and the background picture without Qt (package 35 P3, ROADMAP step 1b; UI_WISHES "Classic screen
v2" point 16). Pure functions, tested without PySide6.

color_tokens() -> every colour token of the theme schema (the editor lists them all: every screen colour is a token).
editable(tid, shipped_ids) -> False for the three shipped themes (they stay untouched: copy one to edit it).
contrast_rows(theme) -> ((fg, bg, ratio rounded to 2, ok), ...) for the contrast pairs (WCAG 2; a warning only).
dim_alpha(dim) -> the alpha 0..255 of the black dimming over the background picture for the app setting
    background_dim 0..100 (round half up).
background_qss(theme, readable) -> extra QSS rules while a background picture is shown: the blocks and strips get
    the token background_overlay (with alpha) behind them when "keep numbers readable" is on; "" otherwise.
"""
from wp.theme import qss
from wp.theme import themes

ALPHA_MAX = 255                        # an 8-bit alpha channel (not a game rule)
PCT = 100                              # background_dim is a percent
ROUND_HALF = 0.5
PLACES = 2                             # the contrast ratio is shown with 2 decimals


def color_tokens():
    return tuple(themes.SCHEMA["colors"])


def editable(tid, shipped_ids):
    return tid not in tuple(shipped_ids)


def contrast_rows(theme):
    colors = theme.get("colors") or {}
    out = []
    for fg, bg in themes.CONTRAST_PAIRS:
        if fg in colors and bg in colors:
            r = themes.contrast_ratio(colors[fg], colors[bg])
            out.append((fg, bg, round(r, PLACES), r >= themes.SCHEMA["contrast_min"]))
    return tuple(out)


def dim_alpha(dim):
    d = max(0, min(PCT, int(dim)))
    return int(d * ALPHA_MAX / float(PCT) + ROUND_HALF)


def background_qss(theme, readable):
    if not readable:
        return ""
    color = qss.qt_color((theme.get("colors") or {}).get("background_overlay", ""))
    return "QFrame#block, QFrame#strip {\n    background-color: %s;\n}\n" % color
