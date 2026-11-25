"""Image registry (package 19, ROADMAP "Icon registry"): pictures the UI shows by id.

A record: {id, name, file (relative to the user data folder, images/<id>.<ext>), kind: icon | picture | background,
tags}. image_for maps "target kind:target id" (a feat, status, item, quick button, cell...) to an image id.
resolve() never raises: a missing file or record -> the placeholder id + a warning id.
Commands (settings dispatch): image_add (COPIES the file into <user folder>/images; extension and size checked by the
app settings image_extensions / image_max_kb), image_remove (also deletes the copied file; the id is retired and
never given again; references to it are dropped), image_rename, image_set_for.
"""
import os
import shutil
from dataclasses import replace

from wp.commands.base import CommandError
from wp.core.frozen import FrozenDict
from wp.settings import schema as sch
from wp.settings import settings_cmds as sc
from wp.settings import store as st

FOLDER = "images"
PLACEHOLDER = "placeholder"
MISSING_FILE = "image_missing"
NO_IMAGE = "no_image"


def file_path(user_folder, rec):
    """The absolute path of a record's file ("images/x.png" is stored with "/" on every system)."""
    return os.path.join(user_folder, *rec["file"].split("/"))


def inside_images(user_folder, path):
    """True when path is a file directly inside <user folder>/images (review 5 F8: checked before a delete)."""
    root = os.path.normcase(os.path.realpath(os.path.join(user_folder, FOLDER)))
    return os.path.dirname(os.path.normcase(os.path.realpath(path))) == root


SIGNATURES = {"png": (b"\x89PNG\r\n\x1a\n",), "jpg": (b"\xff\xd8\xff",), "jpeg": (b"\xff\xd8\xff",),
              "gif": (b"GIF87a", b"GIF89a")}
HEAD = 4096                            # bytes read to recognise a file


def content_matches(path, ext):
    """The file content is of its type (review 5 F25): png / jpg / gif by their magic bytes, webp = RIFF....WEBP,
    svg = an XML text with an <svg element. Other extensions (allowed by the user) are not checked."""
    with open(path, "rb") as f:
        head = f.read(HEAD)
    if ext in SIGNATURES:
        return any(head.startswith(sig) for sig in SIGNATURES[ext])
    if ext == "webp":
        return head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    if ext == "svg":
        text = head.lstrip(b"\xef\xbb\xbf \t\r\n").lower()
        return text.startswith((b"<?xml", b"<svg", b"<!--")) and b"<svg" in text
    return True


def find(app, image_id):
    return next((i for i in app.images if i["id"] == image_id), None)


def resolve(app, image_id, user_folder):
    """(absolute path, None) or (PLACEHOLDER, warning id)."""
    rec = find(app, image_id)
    if rec is None or not st.image_record_ok(rec):
        return PLACEHOLDER, NO_IMAGE
    path = file_path(user_folder, rec)
    if not os.path.isfile(path):
        return PLACEHOLDER, MISSING_FILE
    return path, None


def image_of(app, target_kind, target_id, user_folder):
    return resolve(app, app.image_for.get("%s:%s" % (target_kind, target_id), ""), user_folder)


@sc.settings_command
def image_add(app, source="", name="", kind="icon", tags=(), user_folder=""):
    if not os.path.isfile(source):
        raise CommandError("no such file: %s" % source, "file_not_found", values=(source,))
    ext = os.path.splitext(source)[1].lower().lstrip(".")
    if ext not in st.get(app, "image_extensions"):
        raise CommandError("file type .%s is not allowed" % ext, "bad_image_type", values=(ext,),
                           allowed=tuple(st.get(app, "image_extensions")))
    if not content_matches(source, ext):
        raise CommandError("the file is not a .%s image" % ext, "bad_image_content", values=(ext,))
    kb = (os.path.getsize(source) + 1023) // 1024
    if kb > st.get(app, "image_max_kb"):
        raise CommandError("the image is %d KB, the limit is %d KB" % (kb, st.get(app, "image_max_kb")), "image_too_big",
                           values=(kb, st.get(app, "image_max_kb")))
    rec = {"name": name or os.path.splitext(os.path.basename(source))[0], "kind": kind, "tags": list(tags)}
    bad = sch.check_fields("image", rec)
    if bad:
        sc.refuse(bad)
    iid, counter = sc._new_id(app, rec["name"], (i["id"] for i in app.images))
    rel = os.path.join(FOLDER, "%s.%s" % (iid, ext))
    dest = os.path.join(user_folder, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copyfile(source, dest)
    rec.update(id=iid, file=rel.replace(os.sep, "/"))
    return sc.SettingsResult(replace(app, images=app.images + (st.freeze(rec),), counter=counter), {"id": iid})


@sc.settings_command
def image_remove(app, image_id="", user_folder=""):
    rec = find(app, image_id)
    if rec is None:
        raise CommandError("no image %r" % (image_id,), "not_found", values=("images", image_id))
    path = file_path(user_folder, rec)
    if user_folder and st.image_record_ok(rec) and inside_images(user_folder, path) and os.path.isfile(path):
        os.remove(path)
    refs = FrozenDict({k: v for k, v in app.image_for.items() if v != image_id})
    return sc.SettingsResult(replace(app, images=tuple(i for i in app.images if i["id"] != image_id), image_for=refs,
                                     retired=app.retired + (image_id,)), {"id": image_id})


@sc.settings_command
def image_rename(app, image_id="", name=""):
    if not name:
        raise CommandError("an image needs a name", "name_needed")
    if find(app, image_id) is None:
        raise CommandError("no image %r" % (image_id,), "not_found", values=("images", image_id))
    return sc.SettingsResult(replace(app, images=tuple(st.freeze(dict(i, name=name)) if i["id"] == image_id else i
                                                       for i in app.images)), {"id": image_id})


@sc.settings_command
def image_set_for(app, target_kind="", target_id="", image_id=""):
    """Set (or with image_id "" clear) the picture of a target."""
    if target_kind not in sch.IMAGE_TARGETS:
        raise CommandError("unknown image target kind %r" % (target_kind,), "unknown_target", values=(target_kind,),
                           allowed=sch.IMAGE_TARGETS)
    if image_id and find(app, image_id) is None:
        raise CommandError("no image %r" % (image_id,), "not_found", values=("images", image_id))
    key = "%s:%s" % (target_kind, target_id)
    refs = {k: v for k, v in app.image_for.items() if k != key}
    if image_id:
        refs[key] = image_id
    return sc.SettingsResult(replace(app, image_for=FrozenDict(refs)), {"key": key})
