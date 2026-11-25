"""Package 27 A (review 5 F1, F7, F8, F10, F11, F25): backups by exact name, the backups folder, image paths,
character names, catalog entry codes. Run: python Wp_claude/tests/app/test_pkg27_files.py"""
import base64
import json
import os
import shutil
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.app import files  # noqa: E402
from wp.catalog import store as cs  # noqa: E402
from wp.commands import CommandError  # noqa: E402
from wp.model.character import Character  # noqa: E402
from wp.settings import images  # noqa: E402
from wp.settings import store as st  # noqa: E402
from wp.settings.settings_cmds import settings_dispatch  # noqa: E402

S = Suite("test_pkg27_files")
TMP = tempfile.mkdtemp(prefix="wp_p27a_")
SUB = "backups"


def folder():
    return tempfile.mkdtemp(dir=TMP)


def reason(fn):
    try:
        fn()
    except CommandError as e:
        return e.reason
    return "allowed"


def names(paths):
    return sorted(os.path.basename(p) for p in paths)


def three_chars():
    """a (level 1), a.b (level 7), a.b.c (level 3); each saved 3 more times -> 3 backups each (times 10.., 20.., 30..)."""
    d = folder()
    for i, (n, lv) in enumerate((("a", 1), ("a.b", 7), ("a.b.c", 3))):
        files.create(d, n, Character(level=lv))
        for k in range(3):
            files.save(d, n, Character(level=lv), SUB, 5, 10 * (i + 1) + k)
    return d


def _prefix():
    d = three_chars()
    before = [len(files.backups_of(d, n, SUB)) for n in ("a", "a.b", "a.b.c")]
    files.save(d, "a", Character(level=1), SUB, 1, 100)
    after = [len(files.backups_of(d, n, SUB)) for n in ("a", "a.b", "a.b.c")]
    return before, after


S.case("f1-own-backups", "F1: a, a.b, a.b.c have 3 backups each; saving a with keep 1 leaves a 1 and the others 3",
       ([3, 3, 3], [1, 3, 3]))(_prefix)


def _restore():
    d = three_chars()
    with open(files.path_of(d, "a"), "w") as f:
        f.write("{broken")
    offered = reason(lambda: files.load(d, "a", SUB))
    return offered, files.restore_backup(d, "a", SUB).level, files.load(d, "a.b", SUB).level


S.case("f1-restore", "F1: a damaged -> file_corrupt; the restore gives a's own backup (level 1), a.b keeps level 7",
       ("file_corrupt", 1, 7))(_restore)


def _rename():
    d = three_chars()
    files.rename(d, "a", "z", SUB)
    return (len(files.backups_of(d, "z", SUB)), len(files.backups_of(d, "a", SUB)), len(files.backups_of(d, "a.b", SUB)),
            files.load(d, "a.b", SUB).level)


S.case("f1-rename", "F1: rename a -> z moves only a's 3 backups; a.b keeps its 3 and its level 7", (3, 0, 3, 7))(_rename)
S.case("f1-stamp-only", "F1: a.b.<stamp>.json is not a backup of a; a.<stamp>.json is",
       (None, True))(lambda: (files.STAMP_TAIL.match("b.19700101-000010-000.json"),
                              bool(files.STAMP_TAIL.match("19700101-000010-000.json"))))

# ---------------------------------------------------------------- F7 backups folder
S.case("f7-folder", "F7: backups_folder accepts one name; '', '.', '..', a/b, a\\b, C:\\x, ' x' refused",
       ("allowed",) + ("bad_folder_name",) * 7)(
    lambda: tuple(reason(lambda v=v: settings_dispatch(st.AppSettings(), "settings_set", key="backups_folder", value=v))
                  for v in ("old_backups", "", ".", "..", "a/b", "a\\b", "C:\\x", " x")))

# ---------------------------------------------------------------- F10 names
BAD = ("CON", "nul", "COM1", "aux.txt", "Lpt9.json", "x.json", "a" * 101, "t\tb", "n\nl", "z\x00", "dot.", "sp ", "..")


def _names():
    d = folder()
    return tuple(reason(lambda n=n: files.create(d, n, Character())) for n in BAD)


S.case("f10-bad-names", "F10: reserved, .json, 101 chars, tab, newline, NUL, trailing dot / space, '..' -> bad_name",
       ("bad_name",) * len(BAD))(_names)
S.case("f10-good-names", "F10: 'COM10', 'a.b', 100 chars, Cyrillic are names", (None, None, None, None))(
    lambda: tuple(files.name_problem(n) for n in ("COM10", "a.b", "a" * 100, "\u0413\u0435\u0440\u043e\u0439")))
S.case("f10-taken-is-taken", "F10: an existing name stays name_taken (not bad_name)", "name_taken")(
    lambda: (lambda d: (files.create(d, "hero", Character()), reason(lambda: files.create(d, "hero", Character())))[1])(
        folder()))


# ---------------------------------------------------------------- F8 / F25 images
def png(d, name="icon.png", body=b"\x89PNG\r\n\x1a\n0000"):
    p = os.path.join(d, name)
    with open(p, "wb") as f:
        f.write(body)
    return p


def _outside():
    top = folder()
    user = os.path.join(top, "user")
    os.makedirs(user)
    victim = os.path.join(top, "victim.txt")
    png(top, "victim.txt", b"keep me")
    data = json.loads(st.dumps(st.AppSettings()))
    data["images"] = [{"id": "x", "name": "x", "file": "../victim.txt", "kind": "icon"},
                      {"id": "ok", "name": "ok", "file": "images/ok.png", "kind": "icon"}]
    loaded = st.loads(json.dumps(data))
    imported = reason(lambda: settings_dispatch(st.AppSettings(), "settings_import", text=json.dumps(data)))
    forged = st.AppSettings(images=(st.freeze({"id": "x", "name": "x", "file": "../victim.txt"}),))
    settings_dispatch(forged, "image_remove", image_id="x", user_folder=user)
    return [i["id"] for i in loaded.images], imported, os.path.exists(victim), images.resolve(forged, "x", user)[0]


S.case("f8-paths", "F8: load drops the record ../victim.txt (keeps images/ok.png); import refused; image_remove of a "
       "forged record leaves the victim file; resolve gives the placeholder",
       (["ok"], "bad_image_record", True, "placeholder"))(_outside)


def _content():
    d = folder()
    fake = png(d, "fake.png", b"just text")
    real = png(d)
    gif = png(d, "a.gif", b"GIF89a....")
    svg = png(d, "a.svg", b"<?xml version='1.0'?><svg></svg>")
    webp = png(d, "a.webp", b"RIFF\x00\x00\x00\x00WEBPVP8 ")
    jpg_as_png = png(d, "j.png", b"\xff\xd8\xff\xe0")
    return tuple(reason(lambda p=p: settings_dispatch(st.AppSettings(), "image_add", source=p, name="i", user_folder=d))
                 for p in (fake, real, gif, svg, webp, jpg_as_png))


S.case("f25-content", "F25: a text named .png and a jpg named .png refused; png, gif, svg, webp by their content pass",
       ("bad_image_content", "allowed", "allowed", "allowed", "allowed", "bad_image_content"))(_content)


S.case("f25-profile-dock", "F25: profile_set dock 'space' (a panel field, not a profile one) -> unknown_fields; a panel "
       "dock 'space' -> not_allowed", ("unknown_fields", "not_allowed"))(
    lambda: (reason(lambda: settings_dispatch(st.AppSettings(), "profile_set", mode="classic", pid="default", dock="space")),
             __import__("wp.settings.schema", fromlist=["x"]).check_fields("panel", {"dock": "space"})[0]))


# ---------------------------------------------------------------- F11 entry codes
def code_of(obj, raw=None):
    raw = raw if raw is not None else json.dumps(obj).encode("utf-8")
    return cs.CODE_PREFIX + base64.urlsafe_b64encode(zlib.compress(raw)).decode("ascii")


def _codes():
    from wp.catalog.catalog_cmds import catalog_dispatch
    layers = cs.Layers(None, cs.Catalog("feats"))
    out = []
    for code in (code_of([1]), code_of({"entry": {}}), code_of({"kind": "feats", "entry": []}),
                 code_of(None, b"[" * 5000 + b"]" * 5000), code_of({"kind": "feats", "entry": {"name": "big", "notes": "a" * 2000000}}),
                 cs.CODE_PREFIX + "A" * 200001):
        out.append(reason(lambda c=code: catalog_dispatch(layers, "catalog_import_entry", code=c)))
    out.append(reason(lambda: catalog_dispatch(layers, "catalog_add_entry", fields={"name": "n" * 101})))
    return tuple(out)


S.case("f11-codes", "F11: a list, no kind, entry a list, 5000 nested brackets, 2 MB unpacked (limit 1 MB), a code over "
       "200000 chars -> catalog_error; a 101-char name -> name_too_long", ("catalog_error",) * 6 + ("name_too_long",))(
    _codes)

if __name__ == "__main__":
    try:
        code = S.run()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(code)
