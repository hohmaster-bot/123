"""Input limits of the app layer (data: wp/app/data/limits.json; package 27 A). Not game rules."""
import io
import json
import os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "limits.json")


def _load():
    with io.open(PATH, encoding="utf-8") as f:
        return json.load(f)


LIMITS = _load()


def get(key):
    return LIMITS[key]
