"""Texts by key (package 21, D4, D24). Files: wp/i18n/ru.json, wp/i18n/en.json (flat key -> string, UTF-8 data).

t(key, lang, **params): the string of `lang`, else the Russian one, else the key id itself (never raises); a refusal
text (reason.*) tries lang, then English, then Russian (package 27 F12).
{name} is replaced by params[name] ({values[0]} works for the "values" of a refusal); an unknown {name} stays as is.
plural(key, n, lang): picks key.one / key.few / key.many (ru) or key.one / key.other (en) by n.
text_for(error, lang): the text of a refusal (CommandError) from "reason.<reason id>" and its params.
language(app): the current language from the app settings (setting "language"; switched by settings_set).
strings(prefix, lang): every key with this prefix and its text (with the fallbacks), for the UI.
"""
import io
import json
import os
import string

FOLDER = os.path.dirname(os.path.abspath(__file__))
LANGS = ("ru", "en")
BASE = "ru"
_CACHE = {}


def path_of(lang):
    return os.path.join(FOLDER, "%s.json" % lang)


def load(lang):
    """{key: text} of a language file (cached; {} for a missing file)."""
    if lang not in _CACHE:
        p = path_of(lang)
        if os.path.exists(p):
            with io.open(p, encoding="utf-8") as f:
                data = json.load(f)
            _CACHE[lang] = {k: v for k, v in data.items() if isinstance(v, str) and not k.startswith("_")}
        else:
            _CACHE[lang] = {}
    return _CACHE[lang]


def reload():
    _CACHE.clear()


class _Keep(dict):
    def __missing__(self, key):
        return "{" + key + "}"


class _Fmt(string.Formatter):
    def get_value(self, key, args, kwargs):
        if isinstance(key, str) and key not in kwargs:
            raise KeyError(key)
        return super().get_value(key, args, kwargs)


def _format(text, params):
    if not params:
        return text
    try:
        return _Fmt().vformat(text, (), _Keep(params))
    except (KeyError, IndexError, ValueError, AttributeError):
        return text


REASON = "reason."
EN = "en"


def chain(key, lang=BASE):
    """The languages tried for a key: lang, then Russian. A refusal text (reason.*) tries English before Russian
    (owner, package 27, review 5 F12: the English text shows until ru.json has one)."""
    return (lang, EN, BASE) if key.startswith(REASON) else (lang, BASE)


def raw(key, lang=BASE):
    """The text without params, with the fallback chain, or None."""
    for lg in chain(key, lang):
        v = load(lg).get(key)
        if v:
            return v
    return None


def t(key, lang=BASE, **params):
    text = raw(key, lang)
    return key if text is None else _format(text, params)


def plural_form(n, lang=BASE):
    n = abs(int(n))
    if lang == "ru":
        if n % 10 == 1 and n % 100 != 11:
            return "one"
        if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
            return "few"
        return "many"
    return "one" if n == 1 else "other"


def plural(key, n, lang=BASE, **params):
    form = plural_form(n, lang)
    text = raw("%s.%s" % (key, form), lang)
    if text is None:
        text = raw(key, lang)
    return key if text is None else _format(text, dict(params, n=n))


def text_for(error, lang=BASE):
    params = dict(getattr(error, "params", {}) or {})
    if "values" in params:
        params["values"] = tuple(params["values"]) if isinstance(params["values"], (list, tuple)) else (params["values"],)
    return t("reason." + getattr(error, "reason", "invalid_value"), lang, **params)


def language(app):
    from wp.settings import store as st
    lang = st.get(app, "language")
    return lang if lang in LANGS else BASE


def strings(prefix, lang=BASE):
    keys = set(load(BASE)) | set(load(lang))
    return {k: t(k, lang) for k in sorted(keys) if k.startswith(prefix)}
