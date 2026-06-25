import os
import json

DEFAULT_MODEL = "arcee-ai/trinity-mini"
DEFAULT_HISTORY_LENGTH = 20
DEFAULT_AUTO_COMPACT = False


def load_config():
    """Load settings from config.json. Return a dict with the settings."""
    config_path = "config.json"
    if not os.path.isfile(config_path):
        return {
            "model": DEFAULT_MODEL,
            "history_length": DEFAULT_HISTORY_LENGTH,
            "auto_compact": DEFAULT_AUTO_COMPACT,
        }
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        config.setdefault("model", DEFAULT_MODEL)
        config.setdefault("history_length", DEFAULT_HISTORY_LENGTH)
        config.setdefault("auto_compact", DEFAULT_AUTO_COMPACT)
        return config
    except (json.JSONDecodeError, OSError) as e:
        print(f"\n[WARNING] Could not load config.json: {e}. Using defaults.")
        return {
            "model": DEFAULT_MODEL,
            "history_length": DEFAULT_HISTORY_LENGTH,
            "auto_compact": DEFAULT_AUTO_COMPACT,
        }
    

def save_config(config):
    """Save the settings dict to config.json."""
    config_path = "config.json"
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"\n[ERROR] Failed to save config: {e}")