"""Package 32: the style sheet of the window shell, wp/theme/qss.py build_qss (pure Python, no Qt). Numbers by hand
from wp/theme/data/themes.json (dark base font 12, small 10) and the shell part of qss_template.json (min font 11).
Run: python Wp_claude/tests/storage/test_qss_shell.py"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import ROOT, Suite  # noqa: E402

from wp.theme import qss, themes  # noqa: E402

S = Suite("test_qss_shell")
SHIPPED = {e["id"]: e for e in themes.shipped().entries}


def rule(text, selector):
    """The body of the first rule with exactly this selector."""
    m = re.search(r"(?m)^%s \{\n(.*?)\}" % re.escape(selector), text, re.S)
    return m.group(1) if m else None


def _colours():
    out = []
    for tid in ("dark", "light", "grey_blue"):
        body = rule(qss.build_qss(SHIPPED[tid]), "QWidget")
        c = SHIPPED[tid]["colors"]
        out.append(("background-color: %s;" % c["background"] in body, "color: %s;" % c["text"] in body))
    return out


S.case("q-colours", "pkg 32: the background and the text colour of each shipped theme are in the QWidget rule",
       [(True, True)] * 3)(_colours)
S.case("q-scale", "pkg 32: dark base font 12 px: 100% -> 12 px, 150% -> 18 px (12 x 1.5), 80% -> 10 px (9.6 rounded)",
       ("font-size: 12px;", "font-size: 18px;", "font-size: 10px;"))(
    lambda: tuple(re.search(r"font-size: \d+px;", rule(qss.build_qss(SHIPPED["dark"], s), "QWidget")).group(0)
                  for s in (1.0, 1.5, 0.8)))
S.case("q-min-font", "pkg 32 (UI_WISHES Classic v2 point 11): dark small font 10 -> the minimum 11 px at 100%, "
       "11 x 1.5 = 16.5 -> 16 px (round half to even) at 150%", ("font-size: 11px;", "font-size: 16px;"))(
    lambda: tuple(re.search(r"font-size: \d+px;", rule(qss.build_qss(SHIPPED["dark"], s), "QLabel#muted")).group(0)
                  for s in (1.0, 1.5)))
S.case("q-light-no-white", "owner: the light theme never has a pure white background", [])(
    lambda: re.findall(r"background-color: #ffffff;", qss.build_qss(SHIPPED["light"]).lower()))


def _fallback():
    own = {"id": "mine", "name": "Mine", "colors": {"background": "#101010"}}
    text = qss.build_qss(own)
    return (rule(text, "QWidget").splitlines()[0].strip(), "background-color: %s;" % SHIPPED["dark"]["colors"]["surface"]
            in rule(text, "QFrame#block"))


S.case("q-fallback", "pkg 32: a theme without a token takes the dark one (surface of dark in the block rule); its own "
       "background stays", ("background-color: #101010;", True))(_fallback)
S.case("q-rgba", "pkg 32: #rrggbbaa -> rgba (0x26 = 38, 0x80 = 128); #rrggbb unchanged",
       ("rgba(255, 255, 255, 38)", "rgba(0, 0, 0, 128)", "#1b1d21"))(
    lambda: (qss.qt_color("#ffffff26"), qss.qt_color("#00000080"), qss.qt_color("#1b1d21")))
S.case("q-spacing", "pkg 32: the gap (spacing 6 of dark) is scaled too: 150% -> 9", ("6", "9"))(
    lambda: (qss.scaled(SHIPPED["dark"], 1.0)["spacing"], qss.scaled(SHIPPED["dark"], 1.5)["spacing"]))
S.case("q-switch", "pkg 32: another theme gives another sheet (dark != light)", True)(
    lambda: qss.build_qss(SHIPPED["dark"]) != qss.build_qss(SHIPPED["light"]))
S.case("q-pure", "pkg 32: wp/theme/qss.py imports no Qt", False)(
    lambda: any(ln.lstrip().startswith(("import PySide", "from PySide"))
                for ln in open(os.path.join(ROOT, "wp", "theme", "qss.py"), encoding="ascii")))

if __name__ == "__main__":
    sys.exit(S.run())
