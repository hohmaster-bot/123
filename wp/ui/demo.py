"""The demo character of the window shell (package 32): built by plain Session commands only (data: data/demo.json).
No Qt here. build(session, name=None) creates the file, runs the steps and saves; a refused step raises DemoError."""
import io
import json
import os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "demo.json")


class DemoError(RuntimeError):
    pass


def load(path=DATA):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def free_name(session, base=None):
    """"Demo", then "Demo 2", "Demo 3" ... (the first name no character file has)."""
    base = base or load()["name"]
    taken = set(session.list_characters())
    n, name = 1, base
    while name in taken:
        n += 1
        name = "%s %d" % (base, n)
    return name


def build(session, name=None):
    data = load()
    name = name or free_name(session, data["name"])
    session.new(name)
    editor = session.editor_mode
    session.editor_mode = True         # the demo source rows are editor commands (package 34)
    try:
        for command, params in data["steps"]:
            r = session.dispatch(command, **params)
            if not r.ok:
                raise DemoError("demo step %s refused: %s %r" % (command, r.reason, r.params))
    finally:
        session.editor_mode = editor
    session.save()
    session.open(name)                 # a fresh start: the demo steps are not undo steps of the player
    return name
