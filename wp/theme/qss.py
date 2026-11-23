"""QSS from theme tokens (package 21): pure Python, no Qt import, testable without PySide6.

tokens(theme) -> {flat token: text}: colors by name, fonts as font_family / font_base / font_small / font_large, and the
scalars (radius, spacing, border_width, icon_style, overlay_opacity).
build(theme, template=None) -> the QSS text: for each rule of the template (data: qss_template.json)
    "<selector> {\n    <property>: <value>;\n}\n" with {token} replaced; rules are joined by an empty line.
A {token} the theme does not have -> ThemeError (reason missing_token).
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


def build(theme, template=None):
    toks = tokens(theme)
    rules = load_template() if template is None else template
    blocks = []
    for r in rules:
        body = "".join("%s%s: %s;\n" % (INDENT, prop, _fill(value, toks)) for prop, value in r["declarations"])
        blocks.append("%s {\n%s}\n" % (r["selector"], body))
    return "\n".join(blocks)
