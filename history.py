"""
SecureSteg — history.py
JSON-file based history storage (equivalent of the web version's localStorage).
"""

import json
import os
from datetime import datetime

HISTORY_PATH = os.path.join(os.path.expanduser("~"), ".securesteg_history.json")
MAX_ENTRIES = 50


def get_history():
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_history(entry_type: str, message: str, seed, tech: str):
    history = get_history()

    trimmed_msg = message if len(message) <= 100 else message[:100] + "…"

    history.insert(0, {
        "type": entry_type,
        "message": trimmed_msg,
        "seed": str(seed),
        "tech": tech,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })

    history = history[:MAX_ENTRIES]

    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except OSError:
        pass


def delete_entry(index: int):
    history = get_history()
    if 0 <= index < len(history):
        history.pop(index)
        try:
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except OSError:
            pass


def clear_history():
    try:
        if os.path.exists(HISTORY_PATH):
            os.remove(HISTORY_PATH)
    except OSError:
        pass
