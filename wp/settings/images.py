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


def find(app, image_id):
    return next((i for i in app.images if i["id"] == image_id), None)


def resolve(app, image_id, user_folder):
    """(absolute path, None) or (PLACEHOLDER, warning id)."""
    rec = find(app, image_id)
    if rec is None:
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
    if user_folder and os.path.isfile(path):
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
