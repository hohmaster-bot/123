"""Package 33: the resources block logic and the font settings WITHOUT Qt (wp/ui/tube_logic.py, wp/theme/qss.fonts).
Numbers by hand from the package text. Run: python Wp_claude/tests/storage/test_ui_logic33.py"""
import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.theme import qss  # noqa: E402
from wp.theme import themes  # noqa: E402
from wp.ui import tube_logic as tl  # noqa: E402

S = Suite("test_ui_logic33")
DARK = next(e for e in themes.shipped().entries if e["id"] == "dark")


def _imports(path):
    tree = ast.parse(open(path, encoding="ascii").read())
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            out.append(n.module or "")
    return out


def bad(text):
    try:
        tl.parse_edit(text)
    except tl.EditError as e:
        return e.key
    return "accepted"


# ================================================================ the value editor
S.case("e-parse", "pkg 33: +5 -> add 5, -3 -> add -3, 30 -> set 30, ' + 7 ' -> add 7",
       (("add", 5), ("add", -3), ("set", 30), ("add", 7)))(
    lambda: (tl.parse_edit("+5"), tl.parse_edit("-3"), tl.parse_edit("30"), tl.parse_edit(" + 7 ")))
S.case("e-bad", "pkg 33: bad text refused with the i18n key: 'abc', '', '5+', '1.5'",
       ("resources.bad_edit",) * 4)(lambda: tuple(bad(t) for t in ("abc", "", "5+", "1.5")))
S.case("e-command", "ARCH/ui_gaps 'Editor mapping': add -> adjust_value; set -> set_value; a pool set 5 with 3 shown "
       "-> adjust_value +2", (("adjust_value", {"resource": "hp", "delta": -3}),
                               ("set_value", {"resource": "mana", "value": 30}),
                               ("adjust_value", {"resource": "pool:ki", "delta": 2})))(
    lambda: (tl.edit_command("hp", "add", -3, 11), tl.edit_command("mana", "set", 30, 0),
             tl.edit_command("pool:ki", "set", 5, 3)))

# ================================================================ the tube mapping
S.case("t-fill", "pkg 33: 11 / 16 = 0.6875; 0 max -> 0; 20 / 16 -> 1.0 (over max flagged, not clamped in the text)",
       (0.6875, 0.0, 1.0, True, False))(
    lambda: (tl.fill(11, 16), tl.fill(3, 0), tl.fill(20, 16), tl.over_max(20, 16), tl.over_max(16, 16)))
S.case("t-ticks", "pkg 33: ticks every 10 of 16 -> 10/16 = 0.625; every 5 of 20 -> 0.25, 0.5, 0.75; step 0 -> none",
       ((0.625,), (0.25, 0.5, 0.75), ()))(lambda: (tl.ticks(16, 10), tl.ticks(20, 5), tl.ticks(20, 0)))
S.case("t-temp", "UI_WISHES 5: temp HP 4 of max 16 -> 0.25 of the tube; 20 of 16 -> the whole tube", (0.25, 1.0))(
    lambda: (tl.temp_fill(4, 16), tl.temp_fill(20, 16)))
MODES = {"big": 18, "medium": 10}
S.case("t-mode", "UI_WISHES 3: auto-switch 20 -> big, 12 -> medium, 6 -> thin; auto-switch off -> big",
       ("big", "medium", "thin", "big"))(
    lambda: (tl.pick_mode(20, True, MODES), tl.pick_mode(12, True, MODES), tl.pick_mode(6, True, MODES),
             tl.pick_mode(6, False, MODES)))
POOLS = (("ki", "Ki", {}), ("rage", "Rage", {}), ("luck", "Luck", {}), ("grit", "Grit", {}))
S.case("t-pools", "UI_WISHES 6: first three large, the 4th compact; pool_order grit first; pools_large (luck)",
       ((("ki", "rage", "luck"), ("grit",)), (("grit", "ki", "rage"), ("luck",)), (("luck",), ("ki", "rage", "grit"))))(
    lambda: tuple((tuple(p[0] for p in a), tuple(p[0] for p in b)) for a, b in (
        tl.split_pools(POOLS), tl.split_pools(POOLS, order=("grit",)), tl.split_pools(POOLS, large=("luck",)))))

# ================================================================ C. fonts
S.case("f-family", "owner: the app font family in the qss (installed); numbers default = the family",
       (True, "Georgia", "Georgia"))(
    lambda: (lambda f: ('font-family: "Georgia"' in qss.build_qss(DARK, 1.0, fonts=f), f["font_family"],
                        f["font_numbers"]))(qss.fonts(DARK, "Georgia", "", 12, ("Georgia", "Segoe UI"))))
S.case("f-numbers", "owner: font_family_numbers Consolas for the numbers only", ("Segoe UI", "Consolas", True))(
    lambda: (lambda f: (f["font_family"], f["font_numbers"],
                        'font-family: "Consolas"' in qss.build_qss(DARK, 1.0, fonts=f)))(
        qss.fonts(DARK, "", "Consolas", 12, ("Consolas", "Segoe UI"))))
S.case("f-size", "owner: font_size 14 is the base: 14 x 1.5 = 21 px; small 10 x 14 / 12 = 11.67 x 1.5 = 17.5 -> 18",
       ("21", "18"))(
    lambda: (lambda t: (t["font_base"], t["font_small"]))(
        qss.scaled(DARK, 1.5, fonts=qss.fonts(DARK, "", "", 14, None))))
S.case("f-large", "owner: large 16 x 14 / 12 = 18.67 x 1.5 = 28 px; font_size 12 x 1.0 -> base 12", ("28", "12"))(
    lambda: (qss.scaled(DARK, 1.5, fonts=qss.fonts(DARK, "", "", 14, None))["font_large"],
             qss.scaled(DARK, 1.0, fonts=qss.fonts(DARK, "", "", 12, None))["font_base"]))
S.case("f-fallback", "owner: a font that is not installed falls back to the theme family (Segoe UI), then the system "
       "font", ("Segoe UI", "Arial"))(
    lambda: (qss.fonts(DARK, "No Such Font", "", 12, ("Segoe UI",))["font_family"],
             qss.fonts(DARK, "No Such Font", "", 12, ("Arial",), system="Arial")["font_family"]))
S.case("f-theme-numbers", "pkg 33: a theme may carry fonts.numbers (optional token); the app setting wins",
       ("Courier New", "Consolas"))(
    lambda: (qss.fonts(dict(DARK, fonts=dict(DARK["fonts"], numbers="Courier New")), "", "", 12, None)["font_numbers"],
             qss.fonts(dict(DARK, fonts=dict(DARK["fonts"], numbers="Courier New")), "", "Consolas", 12,
                       None)["font_numbers"]))
S.case("f-theme-check", "pkg 33: fonts.numbers is optional in a theme (check passes); a number there is refused",
       (None, "bad_size"))(
    lambda: (themes.check(dict(DARK, fonts=dict(DARK["fonts"], numbers="Consolas"))),
             (themes.check(dict(DARK, fonts=dict(DARK["fonts"], numbers=5))) or ("",))[0]))
S.case("f-no-qt", "pkg 33: tube_logic and qss import no Qt", (False, False))(
    lambda: tuple(any(n.startswith("PySide6") for n in _imports(m.__file__)) for m in (tl, qss)))

if __name__ == "__main__":
    sys.exit(S.run())
