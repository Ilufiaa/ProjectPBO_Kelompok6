import json, os

SAVE_FILE = "savegame.json"
MAX_LEVEL = 5

def load_save():
    """Return dict: {'unlocked': int}  — level tertinggi yang sudah di-unlock (1-based)."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
                return {"unlocked": int(data.get("unlocked", 1))}
        except Exception:
            pass
    return {"unlocked": 1}

def save_progress(unlocked_level: int):
    """Simpan level yang sudah di-unlock."""
    data = load_save()
    if unlocked_level > data["unlocked"]:
        data["unlocked"] = min(unlocked_level, MAX_LEVEL)
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)