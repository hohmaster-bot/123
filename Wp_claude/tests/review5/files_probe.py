"""Review 5 / area 2: character files, backups, names, path traversal. Every case runs in its own temp folder.
Run: python Wp_claude/tests/review5/files_probe.py"""
import json
import os
import shutil
import tempfile

from common import Character, rich, temp_session, drop
from wp.app import files
from wp.commands import CommandError
from wp.settings import store as st


def case(title, fn):
    try:
        out = fn()
        print("%-58s -> %s" % (title, out))
    except CommandError as e:
        print("%-58s -> CommandError %s" % (title, e.reason))
    except Exception as e:  # noqa: BLE001
        print("%-58s -> RAISED %s: %s" % (title, type(e).__name__, str(e)[:90]))


def names():
    d = tempfile.mkdtemp(prefix="wp_r5f_")
    for n in ("..", "../x", "..\\x", "C:\\x", "/abs", "CON", "nul", "COM1", "aux.txt", "a" * 300, "tab\there",
              "nl\nx", "nul\x00byte", "\u0413\u0435\u0440\u043e\u0439", "name.", " lead", "ok name", "x.json"):
        case("create %r" % (n[:20],), lambda n=n: (files.create(d, n, Character()),
                                                     sorted(os.listdir(d))[-3:])[1])
    shutil.rmtree(d, ignore_errors=True)


def prefix_collision():
    """backups of 'a' are found by the prefix 'a.' -> the backups of 'a.b' count as backups of 'a'."""
    d = tempfile.mkdtemp(prefix="wp_r5f_")
    files.create(d, "a", Character(level=1))
    files.create(d, "a.b", Character(level=7))
    for t in range(3):
        files.save(d, "a.b", Character(level=7), "backups", 5, 1000 + t)
    files.save(d, "a", Character(level=1), "backups", 1, 2000)      # keep 1 newest for "a"
    left = sorted(os.listdir(os.path.join(d, "backups")))
    print("prefix: after saving 'a' with keep=1, backups left: %s (the 3 of 'a.b' expected to stay)" % (left,))
    # corrupt 'a' and look at what recovery offers
    with open(os.path.join(d, "a.json"), "w") as f:
        f.write("{broken")
    for t in range(2):
        files.save(d, "a.b", Character(level=7), "backups", 5, 3000 + t)
    try:
        files.load(d, "a", "backups")
    except CommandError as e:
        b = e.params.get("backup")
        print("prefix: 'a' damaged, offered backup = %s" % (os.path.basename(b) if b else b,))
        ch = files.restore_backup(d, "a", "backups")
        print("prefix: restore_backup('a') gives level %d (a has level 1; a.b has level 7)" % ch.level)
    shutil.rmtree(d, ignore_errors=True)


def backups_folder_dot():
    d = tempfile.mkdtemp(prefix="wp_r5f_")
    files.create(d, "hero", Character(level=3))
    out = []
    for t in range(3):
        try:
            files.save(d, "hero", Character(level=3), ".", 1, 1000 + t)
        except Exception as e:  # noqa: BLE001
            out.append(type(e).__name__)
    print("backups_folder '.', keep 1: files now %s, hero.json exists: %s %s" % (
        sorted(os.listdir(d)), os.path.exists(os.path.join(d, "hero.json")), out))
    shutil.rmtree(d, ignore_errors=True)


def backups_folder_outside():
    d = tempfile.mkdtemp(prefix="wp_r5f_")
    outside = tempfile.mkdtemp(prefix="wp_r5_out_")
    files.create(d, "hero", Character())
    files.save(d, "hero", Character(), outside, 5, 1000)          # absolute path accepted by the schema?
    files.save(d, "hero", Character(), "..", 5, 1001)
    s_ok = st.get(st.AppSettings(), "backups_folder")
    from wp.settings import settings_cmds as sc
    res = []
    for v in ("..", outside, "../../evil", ""):
        try:
            sc.dispatch(st.AppSettings(), "settings_set", key="backups_folder", value=v) if hasattr(sc, "dispatch") \
                else None
            res.append((v[-12:], "accepted"))
        except CommandError as e:
            res.append((v[-12:], e.reason))
        except Exception as e:  # noqa: BLE001
            res.append((v[-12:], type(e).__name__))
    print("backups_folder outside the characters folder: backups written to %s: %s; parent: %s; schema says %r; "
          "settings_set: %s" % (outside[-14:], os.listdir(outside), [f for f in os.listdir(os.path.dirname(d))
                                                                       if f.startswith("hero.")][:2], s_ok, res))
    shutil.rmtree(d, ignore_errors=True)
    shutil.rmtree(outside, ignore_errors=True)


def image_file_traversal():
    """A record loaded from app_settings.json with file '../victim.txt': does image_remove delete it?"""
    d = tempfile.mkdtemp(prefix="wp_r5f_")
    user = os.path.join(d, "user")
    os.makedirs(user)
    victim = os.path.join(d, "victim.txt")
    open(victim, "w").write("keep me")
    data = {"kind": st.KIND, "format": st.FORMAT, "values": {"undo_depth": "abc", "backups_count": -7}, "images": [{"id": "pic", "name": "pic", "kind": "icon", "tags": [],
                                                            "file": "../victim.txt"}]}
    with open(os.path.join(user, st.FILE), "w", encoding="utf-8") as f:
        json.dump(data, f)
    try:
        app = st.load(user)
        print("image: loaded records %s" % ([dict(i) for i in app.images],))
        from wp.settings import images
        print("image: resolve -> %s" % (images.resolve(app, "pic", user)[0][-20:],))
        from wp.settings import settings_cmds as sc
        try:
            sc.REGISTRY["image_remove"](app, image_id="pic", user_folder=user)
        except Exception as e:  # noqa: BLE001
            print("image_remove raised", type(e).__name__, e)
        print("image: victim outside the user folder still exists after image_remove: %s" % os.path.exists(victim))
        print("app values loaded unchecked: undo_depth=%r backups_count=%r" % (st.get(app, "undo_depth"),
                                                                              st.get(app, "backups_count")))
        from wp.app import session as sess
        s = sess.Session(os.path.join(d, "chars"), user)
        try:
            s.new("h")
            r = s.dispatch("take_damage", amount=1)
            print("session with undo_depth 'abc': dispatch ok=%s" % r.ok)
        except Exception as e:  # noqa: BLE001
            print("session with undo_depth 'abc': RAISED %s %s" % (type(e).__name__, str(e)[:60]))
    except Exception as e:  # noqa: BLE001
        print("image: load refused %s %s" % (type(e).__name__, str(e)[:80]))
    shutil.rmtree(d, ignore_errors=True)


def corrupt_and_partial():
    s = temp_session()
    s.save()
    p = files.path_of(s.characters_dir, s.name)
    s.dispatch("take_damage", amount=1)
    s.save()
    s.dispatch("take_damage", amount=1)
    s.save()
    with open(p, "w") as f:
        f.write('{"format": 1, "level": ')
    s.close() if False else None
    try:
        s.open(s.name)
        print("corrupt: opened a damaged file without refusal")
    except CommandError as e:
        print("corrupt: refusal %s, backup offered: %s" % (e.reason, bool(e.params.get("backup"))))
        s.restore_backup(s.name)
        print("corrupt: restored, hp %d" % s.character.hp_current)
    # duplicate keys / NaN in the file
    for text in ('{"level": 1, "level": 99}', '{"hp_current": NaN}', '{"hp_current": Infinity}',
                 '{"hp_current": 1e400}', '{"level": "5"}', '{"level": 10000000000000000000000}',
                 "[" * 5000 + "]" * 5000, '{"abilities": {"str": {"base": -5}}}', '{"items": [{"iid": "a"}, '
                 '{"iid": "a"}]}', '{"level": 1, "extra_field": 1}', '{"level": true}', '{"level": -3}'):
        with open(p, "w") as f:
            f.write(text)
        try:
            ch = s.open(s.name)
            print("hostile file %-40r -> opened: level=%r hp=%r items=%d" % (
                text[:40], ch.level, ch.hp_current, len(ch.items)))
        except CommandError as e:
            print("hostile file %-40r -> refused %s" % (text[:40], e.reason))
        except Exception as e:  # noqa: BLE001
            print("hostile file %-40r -> RAISED %s %s" % (text[:40], type(e).__name__, str(e)[:60]))
    drop(s)


def import_names():
    s = temp_session()
    src = files.path_of(s.characters_dir, s.name)
    for n in ("..\\..\\x", "", "imported", "imported"):
        case("import as %r" % n, lambda n=n: (s.import_file(src, n), "ok")[1])
    case("rename open character to '..'", lambda: s.rename(s.name, ".."))
    case("duplicate to an existing name", lambda: s.duplicate(s.name, "imported"))
    case("delete the open character", lambda: s.delete(s.name))
    case("export to a missing folder", lambda: s.export(s.name, os.path.join(s._tmp, "no", "such", "x.json")))
    drop(s)


if __name__ == "__main__":
    names()
    prefix_collision()
    backups_folder_dot()
    backups_folder_outside()
    image_file_traversal()
    corrupt_and_partial()
    import_names()
