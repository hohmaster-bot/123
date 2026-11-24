"""Review 5 / area 4: settings schema, profiles, themes and images with hostile values (all in memory / temp).
Run: python Wp_claude/tests/review5/settings_probe.py"""
import json
import os
import shutil
import tempfile

from common import CONSTS, drop, temp_session
from wp.commands import CommandError
from wp.settings import settings_cmds as sc
from wp.settings import store as st


def try_(title, fn):
    try:
        r = fn()
        print("%-60s -> accepted %s" % (title, str(getattr(r, "info", ""))[:50]))
    except CommandError as e:
        print("%-60s -> refused %s" % (title, e.reason))
    except Exception as e:  # noqa: BLE001
        print("%-60s -> RAISED %s %s" % (title, type(e).__name__, str(e)[:60]))


def app_values():
    a = st.AppSettings()
    for k, v in (("undo_depth", -1), ("undo_depth", 10 ** 9), ("undo_depth", "5"), ("undo_depth", True),
                 ("undo_depth", 2.5), ("autosave_interval_s", float("nan")), ("backups_count", 101),
                 ("language", "de"), ("language", "../../x"), ("backups_folder", "C:\\Windows"),
                 ("hotkeys", {"toggle_mode": "Ctrl+Ctrl"}), ("resource_display", {"hp": "huge"}),
                 ("window_classic", [0, 0, -5, 10 ** 9]), ("unknown_key", 1)):
        try_("settings_set %s=%r" % (k, v), lambda k=k, v=v: sc.settings_dispatch(a, "settings_set", key=k, value=v))


def rule_values():
    s = temp_session()
    by_type = {}
    for c in CONSTS:
        by_type.setdefault(c["type"], c["id"])
    for t, cid in sorted(by_type.items()):
        for v in ("x", None, [1], {"a": 1}, float("nan"), 10 ** 30, -10 ** 9, True):
            r = s.dispatch("set_rule_setting", key=cid, value=v)
            print("set_rule_setting %-34s (%s) = %-12r -> %s" % (cid, t, v if not isinstance(v, int) or abs(v) < 1e6
                                                                 else "big", "ok" if r.ok else r.reason))
    drop(s)


def profiles():
    a = st.AppSettings()
    for text in ('{"id": "x"}', "[]", "not json", '{"panels": [{"panel": "nope"}]}',
                 json.dumps({"name": "p", "panels": [{"id": "a", "panel": "resources", "size": [-1, 10 ** 9]}]}),
                 "[" * 3000 + "]" * 3000):
        try_("profile_import classic %r" % text[:40], lambda t=text: sc.settings_dispatch(a, "profile_import",
                                                                                       mode="classic", text=t))
    try_("profile_set classic default dock=space", lambda: sc.settings_dispatch(a, "profile_set", mode="classic",
                                                                               pid="default", dock="space"))
    try_("profile_delete the last profile", lambda: sc.settings_dispatch(a, "profile_delete", mode="classic",
                                                                        pid="default"))
    try_("settings_import deep nesting", lambda: sc.settings_dispatch(a, "settings_import", text="[" * 3000 + "]" * 3000))


def images():
    d = tempfile.mkdtemp(prefix="wp_r5i_")
    a = st.AppSettings()
    big = os.path.join(d, "big.png")
    open(big, "wb").write(b"\x89PNG" + b"0" * (3 * 1024 * 1024))
    txt = os.path.join(d, "x.exe")
    open(txt, "wb").write(b"MZ")
    fake = os.path.join(d, "fake.png")
    open(fake, "wb").write(b"not an image at all")
    try_("image_add 3 MB png", lambda: sc.settings_dispatch(a, "image_add", source=big, user_folder=d))
    try_("image_add .exe", lambda: sc.settings_dispatch(a, "image_add", source=txt, user_folder=d))
    try_("image_add a text file named .png (content not checked?)",
         lambda: sc.settings_dispatch(a, "image_add", source=fake, user_folder=d))
    try_("image_add missing file", lambda: sc.settings_dispatch(a, "image_add", source=os.path.join(d, "no.png"),
                                                                user_folder=d))
    r = sc.settings_dispatch(a, "image_add", source=fake, name="pic", user_folder=d)
    a2 = r.state if hasattr(r, "state") else r.app
    rid = r.info["id"]
    a3 = sc.settings_dispatch(a2, "image_remove", image_id=rid, user_folder=d)
    a3 = a3.state if hasattr(a3, "state") else a3.app
    r2 = sc.settings_dispatch(a3, "image_add", source=fake, name="pic", user_folder=d)
    print("image ids: first %s, removed, re-added -> %s (retired, must differ)" % (rid, r2.info["id"]))
    shutil.rmtree(d, ignore_errors=True)


def themes():
    from wp.theme import themes as th
    names = [x for x in dir(th) if not x.startswith("_")]
    print("theme module: %s" % ", ".join(n for n in names if n[0].islower())[:200])


if __name__ == "__main__":
    app_values()
    rule_values()
    profiles()
    images()
    themes()
