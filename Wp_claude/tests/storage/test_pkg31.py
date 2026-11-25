"""Package 31: one-time hints, layout warnings, profile_reset, tube settings, themes and background (owner).
Numbers by hand (WCAG 2 contrast: black on white 21, white on white 1). Run: python Wp_claude/tests/storage/test_pkg31.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.catalog import store as cs  # noqa: E402
from wp.commands import CommandError  # noqa: E402
from wp.settings import screen_settings as ss  # noqa: E402
from wp.settings import store as st  # noqa: E402
from wp.settings.settings_cmds import settings_dispatch  # noqa: E402
from wp.theme import themes  # noqa: E402

S = Suite("test_pkg31")


def run(app, *steps):
    for name, params in steps:
        app = settings_dispatch(app, name, **params).state
    return app


def ref(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


# ---------------------------------------------------------------- hints
def _hints():
    a = st.AppSettings()
    first = ss.hint_visible(a, "tube_editor")
    a = run(a, ("hint_dismiss", {"hint_id": "tube_editor"}), ("hint_dismiss", {"hint_id": "tube_editor"}))
    gone, other = ss.hint_visible(a, "tube_editor"), ss.hint_visible(a, "ac_block")
    seen = tuple(st.get(a, "hints_seen"))
    back = ss.hint_visible(run(a, ("hints_reset", {})), "tube_editor")
    off = run(st.AppSettings(), ("settings_set", {"key": "hints_off", "value": True}))
    return first, gone, other, seen, back, any(v for _, _, v in ss.hints_view(off))


S.case("h-once", "owner: a hint shows until Understood; dismissed stays dismissed (twice = once); others still show; "
       "reset shows it again; hints_off hides every hint",
       (True, False, True, ("tube_editor",), True, False))(_hints)
S.case("h-unknown", "pkg 31: an unknown hint id is refused; every hint has a text key", ("not_found", True))(
    lambda: (ref(lambda: settings_dispatch(st.AppSettings(), "hint_dismiss", hint_id="zz")),
             all(k == "hint." + h for h, k, _ in ss.hints_view(st.AppSettings()))))


# ---------------------------------------------------------------- layout warnings and profile_reset
def classic(app):
    return st.profile(app, "classic")


def _with_panels(panels):
    a = st.AppSettings()
    p = dict(st._plain(classic(a)), panels=panels, cells=[])
    from wp.settings import settings_cmds as sc
    return sc._with_profile(a, "classic", st.freeze(p))


RES = {"id": "r", "panel": "resources", "position": [0, 0], "size": [280, 220]}


def _warnings():
    small = ss.layout_warnings(_with_panels([dict(RES, size=[10, 10])]))
    hidden = ss.layout_warnings(_with_panels([dict(RES, visible=False), {"id": "c", "panel": "combat",
                                                                           "position": [0, 0], "size": [320, 240]}]))
    out = ss.layout_warnings(_with_panels([dict(RES, position=[700, 0])]), window=(800, 600))
    fine = ss.layout_warnings(_with_panels([RES]), window=(800, 600))
    return [w[0] for w in small], [w[0] for w in hidden], [w[0] for w in out], fine


S.case("w-three", "owner: resources 10x10 (min 120x60) -> under minimum; the resources panel hidden and no HP cell -> "
       "HP hidden; at x 700 width 280 in an 800 window -> outside; a normal layout -> no warning",
       (["block_under_minimum"], ["hp_controls_hidden"], ["block_outside_window"], ()))(_warnings)


def _reset():
    a = run(st.AppSettings(), ("profile_set", {"mode": "classic", "pid": "default", "name": "Mine", "quick_cells": 12}))
    b = run(a, ("profile_reset", {"mode": "classic", "pid": "default"}))
    return classic(a)["quick_cells"], classic(b)["quick_cells"], classic(b)["name"], classic(b)["id"]


S.case("w-reset", "owner: profile_reset puts the shipped default back (quick cells 12 -> 8), the profile keeps its id "
       "and name", (12, 8, "Mine", "default"))(_reset)


# ---------------------------------------------------------------- tube settings
def setv(key, value):
    return ref(lambda: settings_dispatch(st.AppSettings(), "settings_set", key=key, value=value))


S.case("t-settings", "owner: style glass / flat (neon refused); size w and h separately ([200] refused); auto-switch a "
       "flag; three large pools at most (4 refused); background dim 0-100",
       ("allowed", "not_allowed", "allowed", "wrong_type", "wrong_type", "allowed", "out_of_range", "out_of_range"))(
    lambda: (setv("resource_style", "flat"), setv("resource_style", "neon"),
             setv("resource_size", {"hp": [200, 300]}), setv("resource_size", {"hp": [200]}),
             setv("resource_autoswitch", "no"), setv("pools_large", ["a", "b", "c"]),
             setv("pools_large", ["a", "b", "c", "d"]), setv("background_dim", 101)))
S.case("t-defaults", "owner: glass, auto-switch on, no background picture, the readable overlay on, theme dark",
       ("glass", True, "", True, "dark"))(
    lambda: tuple(st.get(st.AppSettings(), k) for k in ("resource_style", "resource_autoswitch", "background_image",
                                                         "background_readable", "theme")))


# ---------------------------------------------------------------- themes
def layers():
    return cs.Layers(themes.shipped(), cs.Catalog(themes.KIND))


def colors(lay, tid):
    return dict(next(e for e, _ in cs.merged(lay) if e["id"] == tid)["colors"])


S.case("c-wcag", "WCAG 2: black on white = 21; white on white = 1; the dark theme text #e6e6e6 on #1b1d21 = 13.5 "
       "(by hand: L 0.7913 and 0.0122 -> 0.8413 / 0.0622)", (21.0, 1.0, 13.5))(
    lambda: (themes.contrast_ratio("#000000", "#ffffff"), themes.contrast_ratio("#ffffff", "#ffffff"),
             round(themes.contrast_ratio("#e6e6e6", "#1b1d21"), 1)))


def _low():
    lay = themes.theme_edit(layers(), "dark", colors={"text": "#333333"})
    t = next(e for e, _ in cs.merged(lay) if e["id"] == "dark")
    return [w[0] for w in themes.warnings(t)][:1], colors(lay, "dark")["text"]


S.case("c-warn", "owner: text #333333 on the dark background is below 4.5 -> a warning, the theme still saves",
       (["low_contrast"], "#333333"))(_low)
S.case("c-shipped-ok", "owner: the three shipped themes have no contrast warning", ((), (), ()))(
    lambda: tuple(themes.warnings(e) for e in themes.shipped().entries))


def _reset_theme():
    lay = themes.theme_edit(layers(), "dark", colors={"accent": "#000000"})
    back = themes.theme_reset(lay, "dark")
    lay2, own = themes.theme_copy(layers(), "dark")
    return colors(lay, "dark")["accent"], colors(back, "dark")["accent"], own, ref(lambda: themes.theme_reset(lay2, own))


S.case("c-reset", "owner: theme_reset brings the shipped accent #5b9bd5 back; copy dark -> dark_1; an own theme has no "
       "shipped version (not_shipped)", ("#000000", "#5b9bd5", "dark_1", "not_shipped"))(_reset_theme)
BAD = ("red", "#12345", "#GGGGGG", "123456", "#1234567", "", None, 5, "#12345678x")
S.case("c-bad-colors", "owner: a colour that is not #RRGGBB (or #RRGGBBAA) is refused", ("bad_color",) * len(BAD))(
    lambda: tuple(ref(lambda b=b: themes.theme_edit(layers(), "dark", colors={"text": b})) for b in BAD))


def _system():
    a = run(st.AppSettings(), ("settings_set", {"key": "theme_follow_system", "value": True}))
    return (themes.active(a, layers(), system_dark=False)["id"], themes.active(a, layers(), system_dark=True)["id"],
            themes.active(st.AppSettings(), layers(), system_dark=False)["id"])


S.case("c-system", "owner: follow the system: light system -> light, dark -> dark; off -> the theme setting (dark)",
       ("light", "dark", "dark"))(_system)


def _soft_light():
    c = colors(layers(), "light")
    return c["background"].lower() != "#ffffff", c["surface"].lower() != "#ffffff", \
        sorted(e["id"] for e in themes.shipped().entries)


S.case("c-three", "owner: three shipped themes; the light one is never pure white", (True, True,
                                                                                     ["dark", "grey_blue", "light"]))(
    _soft_light)
S.case("c-tokens", "owner: the screen tokens exist in every shipped theme (tube, chips, thresholds, squares)", True)(
    lambda: all(all(k in e["colors"] for k in ("tube_glass", "tube_highlight", "chip_buff", "threshold_bad",
                                                "action_square", "action_spent", "overload_chip", "temp_hp"))
                for e in themes.shipped().entries))

if __name__ == "__main__":
    sys.exit(S.run())
