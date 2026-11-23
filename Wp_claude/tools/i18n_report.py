"""Translation coverage (package 21): which text keys are missing in wp/i18n/ru.json / en.json, and which are unused.

python Wp_claude/tools/i18n_report.py          -> writes Wp_claude/TRANSLATION_TODO.md (owner doc, Russian headings)
python Wp_claude/tools/i18n_report.py --fill-en -> also adds missing EN refusal texts made from the English messages in
                                                    the code (%s -> {values[0]} ...); existing entries are never changed
Deterministic: the same files give the same TODO text.
"""
import ast
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from wp.i18n import i18n, keys  # noqa: E402

TODO = os.path.join(ROOT, "Wp_claude", "TRANSLATION_TODO.md")
# headings of the owner doc (Russian text kept as escapes: this file is ASCII code)
H_TITLE = "# \u0427\u0442\u043e \u043f\u0435\u0440\u0435\u0432\u0435\u0441\u0442\u0438 (TRANSLATION_TODO)"
H_NOTE = ("\u0421\u0434\u0435\u043b\u0430\u043d\u043e \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u043e\u043c "
          "Wp_claude/tools/i18n_report.py. \u0412\u043f\u0438\u0448\u0438\u0442\u0435 \u0442\u0435\u043a\u0441\u0442 "
          "\u0432 wp/i18n/ru.json (\u0438 en.json) \u043f\u043e \u043a\u043b\u044e\u0447\u0443 \u0438 \u0437\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u0435 "
          "\u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442 \u0441\u043d\u043e\u0432\u0430.")
H_RU = "## \u041d\u0435\u0442 \u0432 ru.json"
H_EN = "## \u041d\u0435\u0442 \u0432 en.json"
H_UNUSED = "## \u041b\u0438\u0448\u043d\u0438\u0435 \u043a\u043b\u044e\u0447\u0438 (\u043d\u0438\u0433\u0434\u0435 \u043d\u0435 \u043d\u0443\u0436\u043d\u044b)"


def _file(lang):
    p = i18n.path_of(lang)
    if not os.path.exists(p):
        return {}
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def missing(lang, need):
    have = _file(lang)
    return sorted(k for k in need if not have.get(k))


def unused(need):
    out = set()
    for lang in i18n.LANGS:
        out |= {k for k in _file(lang) if not k.startswith("_") and k not in need}
    return sorted(out)


def _grouped(ks, need):
    groups = {}
    for k in ks:
        groups.setdefault(need.get(k, k.split(".")[0]), []).append(k)
    out = []
    for g in sorted(groups):
        out += ["", "### %s (%d)" % (g, len(groups[g]))] + ["- `%s`" % k for k in groups[g]]
    return out


def report_text():
    need = keys.required()
    ru, en, extra = missing("ru", need), missing("en", need), unused(need)
    lines = [H_TITLE, "", H_NOTE, "", "%s (%d)" % (H_RU, len(ru))] + _grouped(ru, need)
    lines += ["", "%s (%d)" % (H_EN, len(en))] + _grouped(en, need)
    lines += ["", "%s (%d)" % (H_UNUSED, len(extra))] + ["- `%s`" % k for k in extra]
    return "\n".join(lines) + "\n"


_PCT = re.compile(r"%[-+ #0-9.]*[sdrif]")


def code_messages():
    """{reason id: English message with {values[i]}} from CommandError(text, reason, values=...) in the code."""
    out = {}
    for path in glob.glob(os.path.join(ROOT, "wp", "**", "*.py"), recursive=True):
        tree = ast.parse(open(path, encoding="ascii").read())
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "CommandError" and len(node.args) > 1):
                continue
            reason = node.args[1]
            if not (isinstance(reason, ast.Constant) and isinstance(reason.value, str)):
                continue
            msg = node.args[0]
            has_values = any(k.arg == "values" for k in node.keywords)
            if isinstance(msg, ast.Constant) and isinstance(msg.value, str):
                text = msg.value
            elif isinstance(msg, ast.BinOp) and isinstance(msg.op, ast.Mod) and isinstance(msg.left, ast.Constant) \
                    and has_values:
                count = [0]

                def sub(m):
                    i = count[0]
                    count[0] += 1
                    return "{values[%d]}" % i
                text = _PCT.sub(sub, msg.left.value)
            else:
                continue
            out.setdefault(reason.value, text.replace("%%", "%"))
    return out


def fill_en():
    data = _file("en")
    added = 0
    for rid, text in sorted(code_messages().items()):
        k = "reason." + rid
        if not data.get(k):
            data[k] = text
            added += 1
    text = json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=1) + "\n"
    with io.open(i18n.path_of("en"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    i18n.reload()
    return added


def main(argv):
    if "--fill-en" in argv:
        print("en.json: %d refusal texts added from the code" % fill_en())
    text = report_text()
    with io.open(TODO, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    need = keys.required()
    print("keys %d; missing ru %d, en %d; unused %d" % (len(need), len(missing("ru", need)), len(missing("en", need)),
                                                       len(unused(need))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
