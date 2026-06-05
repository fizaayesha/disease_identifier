import os
import json
import uuid
from datetime import datetime

HISTORY_DIR = "history"
METADATA_FILE = os.path.join(HISTORY_DIR, "metadata.json")
IMAGES_DIR = os.path.join(HISTORY_DIR, "images")
MAX_HISTORY_SIZE = 50

def ensure_history_dirs():
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR, exist_ok=True)

def save_to_history(image, confidence, clean_text, filename):
    ensure_history_dirs()
    history = []
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r") as f:
                history = json.load(f)
        except:
            history = []

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    image_id = str(uuid.uuid4())
    image_path = os.path.join(IMAGES_DIR, f"{image_id}.png")
    image.save(image_path)

    entry = {
        "id": image_id,
        "timestamp": timestamp,
        "image_name": filename,
        "image_path": image_path,
        "confidence": confidence,
        "text": clean_text
    }

    history.insert(0, entry)

    if len(history) > MAX_HISTORY_SIZE:
        evicted_entries = history[MAX_HISTORY_SIZE:]
        history = history[:MAX_HISTORY_SIZE]
        for evicted in evicted_entries:
            image_file = evicted.get("image_path")
            if image_file and os.path.exists(image_file):
                try:
                    os.remove(image_file)
                except:
                    pass

    with open(METADATA_FILE, "w") as f:
        json.dump(history, f, indent=4)
    return entry

def load_history():
    if not os.path.exists(METADATA_FILE):
        return []
    try:
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def clear_all_history():
    if os.path.exists(METADATA_FILE):
        os.remove(METADATA_FILE)
    if os.path.exists(IMAGES_DIR):
        for f in os.listdir(IMAGES_DIR):
            try:
                os.remove(os.path.join(IMAGES_DIR, f))
            except:
                pass
