"""QSS from theme tokens (package 21): pure Python, no Qt import, testable without PySide6.

tokens(theme) -> {flat token: text}: colors by name, fonts as font_family / font_base / font_small / font_large, and the
scalars (radius, spacing, border_width, icon_style, overlay_opacity).
build(theme, template=None) -> the QSS text: for each rule of the template (data: qss_template.json)
    "<selector> {\n    <property>: <value>;\n}\n" with {token} replaced; rules are joined by an empty line.
A {token} the theme does not have -> ThemeError (reason missing_token).
build_qss(theme, scale=1.0, fallback=None) (package 32): the style sheet of the window shell. A token the theme lacks
is taken from the fallback theme (default: the shipped dark one); fonts are at least the template's min_font_px
(UI_WISHES "Classic v2" 11) and with spacing multiplied by the scale (round); #rrggbbaa colours become rgba(r, g, b,
a) (Qt reads an 8-digit #hex as #aarrggbb). scaled(theme, scale, fallback) gives the same token values to the UI
(gaps of the layouts).
"""
import io
import json
import os
import re

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "qss_template.json")
_TOKEN = re.compile(r"\{([a-z_]+)\}")
INDENT = "    "


class ThemeError(ValueError):
    def __init__(self, text, reason, **params):
        super().__init__(text)
        self.reason = reason
        self.params = params


def load_template(path=TEMPLATE):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)["rules"]


def tokens(theme):
    out = {k: str(v) for k, v in dict(theme.get("colors", {})).items()}
    for k, v in dict(theme.get("fonts", {})).items():
        out["font_" + k] = str(v)
    for k in ("radius", "spacing", "border_width", "icon_style", "overlay_opacity"):
        if k in theme:
            out[k] = str(theme[k])
    return out


def _fill(text, toks):
    def sub(m):
        if m.group(1) not in toks:
            raise ThemeError("the theme has no token %r" % m.group(1), "missing_token", values=(m.group(1),),
                             token=m.group(1))
        return toks[m.group(1)]
    return _TOKEN.sub(sub, text)


def _render(rules, toks):
    blocks = []
    for r in rules:
        body = "".join("%s%s: %s;\n" % (INDENT, prop, _fill(value, toks)) for prop, value in r["declarations"])
        blocks.append("%s {\n%s}\n" % (r["selector"], body))
    return "\n".join(blocks)


def build(theme, template=None):
    return _render(load_template() if template is None else template, tokens(theme))


def load_shell(path=TEMPLATE):
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d["shell"]


_HEX8 = re.compile(r"^#([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})$")


def qt_color(value):
    """#rrggbbaa -> rgba(r, g, b, a); anything else unchanged."""
    m = _HEX8.match(str(value))
    if not m:
        return str(value)
    return "rgba(%s)" % ", ".join(str(int(x, 16)) for x in m.groups())


def _dark():
    from wp.theme import themes
    return next(e for e in themes.shipped().entries if e["id"] == themes.DEFAULT)


def scaled(theme, scale=1.0, fallback=None, shell=None):
    """Flat tokens of the theme over the fallback theme, fonts (at least min_font_px) and spacing times the scale."""
    shell = load_shell() if shell is None else shell
    toks = tokens(_dark() if fallback is None else fallback)
    toks.update(tokens(theme))
    for k in shell["scaled"]:
        if k in toks:
            v = float(toks[k])
            if k.startswith("font_"):
                v = max(v, float(shell["min_font_px"]))
            toks[k] = str(int(round(v * float(scale))))
    return {k: qt_color(v) for k, v in toks.items()}

def build_qss(theme, scale=1.0, fallback=None, template=None):
    """The QSS text of the window shell (package 32): the template rules, then the shell rules."""
    shell = load_shell()
    rules = (load_template() + shell["rules"]) if template is None else template
    return _render(rules, scaled(theme, scale, fallback, shell))
