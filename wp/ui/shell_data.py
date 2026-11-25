"""The numbers of the window shell (package 32): wp/ui/data/shell.json (UI numbers, not game rules). No Qt here."""
import io
import json
import os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "shell.json")


def load(path=PATH):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


SHELL = load()
