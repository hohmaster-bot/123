# gui_app_config.py — работа с config.json (последний персонаж, настройки вида)
import os
import json
from character import BASE_DIR

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")


def load_app_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_app_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[config] {e}")


def get_last_character():
    return load_app_config().get("last_character", "")


def set_last_character(name):
    cfg = load_app_config()
    cfg["last_character"] = name
    save_app_config(cfg)