"""Package 21: texts by key (wp/i18n), refusal texts, translation coverage, catalog name_i18n, Item.ilvl.
Expected strings by hand (Russian names copied from the beta GUI / the skill catalog).
Run: python Wp_claude/tests/storage/test_i18n.py"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import ROOT, Suite  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "Wp_claude", "tools"))
import i18n_report  # noqa: E402

from wp.catalog import catalog_view as cvw  # noqa: E402
from wp.catalog import convert  # noqa: E402
from wp.catalog import schema as cat  # noqa: E402
from wp.catalog import store as cs  # noqa: E402
from wp.commands import CommandError, dispatch  # noqa: E402
from wp.i18n import i18n, keys  # noqa: E402
from wp.model.character import Character, Item, ResourcePool  # noqa: E402
from wp.settings import store as st  # noqa: E402
from wp.settings.settings_cmds import settings_dispatch  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_i18n")
SILA = "\u0421\u0438\u043b\u0430"                       # "Sila" (Strength)
POISK = "\u041f\u043e\u0438\u0441\u043a"                # "Poisk" (Search)


def refusal(ch, name, **kw):
    try:
        dispatch(ch, name, **kw)
    except CommandError as e:
        return e
    return None


S.case("t-ru", "pkg 21: stat.str in Russian = the beta name", SILA)(lambda: i18n.t("stat.str"))
S.case("t-en", "pkg 21: stat.str in English", "Strength")(lambda: i18n.t("stat.str", "en"))
S.case("t-fallback-ru", "pkg 21: a key missing in en falls back to ru (skill.search)", POISK)(lambda: i18n.t("skill.search", "en"))
S.case("t-fallback-key", "pkg 21: a key missing everywhere shows the key id, never raises", "ui.no_such_key")(
    lambda: i18n.t("ui.no_such_key", "en"))
S.case("t-params", "pkg 21: {values[i]} from the refusal params: Ki need 5, have 3", "not enough Ki: need 5, have 3")(
    lambda: i18n.text_for(refusal(Character(pools=(ResourcePool("ki", "Ki", 3, 3),)), "spend_pool", pid="ki", n=5), "en"))
S.case("t-reason-ru-missing", "owner (package 27 F12): no Russian refusal text yet -> the English one (lang -> en -> "
       "ru -> key)", "not enough Ki: need 5, have 3")(
    lambda: i18n.text_for(refusal(Character(pools=(ResourcePool("ki", "Ki", 3, 3),)), "spend_pool", pid="ki", n=5), "ru"))
S.case("t-reason-no-text", "package 27 F12: a refusal with no text in any language -> its key id",
       "reason.zz_none")(lambda: i18n.t("reason.zz_none", "ru"))
S.case("t-other-ru-first", "package 27 F12: only reason.* keys try English first; skill.search in ru stays Russian",
       POISK)(lambda: i18n.t("skill.search", "ru"))
S.case("t-unknown-param", "pkg 21: an unknown {name} stays as it is", "a {x} b")(lambda: i18n._format("a {x} b", {"y": 1}))
S.case("t-plural-ru", "pkg 21: RU plural forms of 1, 2, 5, 11, 21, 22, 112",
       ("one", "few", "many", "many", "one", "few", "many"))(
    lambda: tuple(i18n.plural_form(n, "ru") for n in (1, 2, 5, 11, 21, 22, 112)))
S.case("t-plural-en", "pkg 21: EN plural forms of 1, 2, 0", ("one", "other", "other"))(
    lambda: tuple(i18n.plural_form(n, "en") for n in (1, 2, 0)))
S.case("t-language-switch", "pkg 21: language switched by the app setting", ("ru", "en"))(
    lambda: (i18n.language(st.AppSettings()),
             i18n.language(settings_dispatch(st.AppSettings(), "settings_set", key="language", value="en").state)))
S.case("t-strings-view", "pkg 21: all strings of a prefix for the UI: 6 stats", 6)(lambda: len(i18n.strings("stat.", "en")))


# ---------------------------------------------------------------- coverage
def _not_covered():
    todo = io.open(i18n_report.TODO, encoding="utf-8").read()
    ru = i18n.load("ru")
    groups = ("reason", "settings", "rules", "catalog", "skill")
    return sorted(k for k, g in keys.required().items() if g in groups and k not in ru and "`%s`" % k not in todo)


S.case("c-covered", "pkg 21: every reason id, setting, constant label, catalog kind and skill id has a Russian text or "
       "is listed in TRANSLATION_TODO.md", [])(_not_covered)
S.case("c-todo-current", "pkg 21: TRANSLATION_TODO.md is up to date (run tools/i18n_report.py)", True)(
    lambda: io.open(i18n_report.TODO, encoding="utf-8").read() == i18n_report.report_text())
S.case("c-skills-ru", "pkg 21: all 45 skill names are in ru.json", 45)(
    lambda: sum(1 for k in i18n.load("ru") if k.startswith("skill.")))
S.case("c-reasons-found", "pkg 21: refusal ids are collected from the code (circle_out_of_range, slot_occupied, field_type)",
       True)(lambda: {"circle_out_of_range", "slot_occupied", "field_type"} <= keys.reason_ids())


# ---------------------------------------------------------------- catalog names, ilvl
S.case("n-name-i18n", "pkg 21: name_i18n {en: Rope} -> Rope in en; the typed name otherwise", ("Rope", "Verevka"))(
    lambda: (cvw.display_name({"id": "r", "name": "Verevka", "name_i18n": {"en": "Rope"}}, "en"),
             cvw.display_name({"id": "r", "name": "Verevka", "name_i18n": {"en": "Rope"}}, "ru")))
S.case("n-name-i18n-schema", "pkg 21: name_i18n must be a map", ("field_type", None))(
    lambda: ((cat.check("items", {"id": "x", "name": "x", "name_i18n": ["Rope"]}) or ("",))[0],
             cat.check("items", {"id": "x", "name": "x", "name_i18n": {"en": "Rope"}})))
S.case("q133-ilvl", "Q133: Item.ilvl empty by default; the catalog ring (ilvl 1) maps to it; survives save / load", (None, 1, 1))(
    lambda: (Item("x", "x").ilvl, convert.item_from_entry(cs.load_shipped("items").find("ring_of_guard"), "r").ilvl,
             cio.loads(cio.dumps(Character(items=(Item("x", "x", ilvl=1),)))).items[0].ilvl))

if __name__ == "__main__":
    sys.exit(S.run())
