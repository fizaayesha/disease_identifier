import os
import json
import uuid
import logging
from datetime import datetime
from shutil import copy2

HISTORY_DIR = "history"
METADATA_FILE = os.path.join(HISTORY_DIR, "metadata.json")
IMAGES_DIR = os.path.join(HISTORY_DIR, "images")
MAX_HISTORY_SIZE = 50

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        except json.JSONDecodeError as e:
            logger.warning(f"Corrupted metadata file detected: {e}. Creating backup.")
            backup_file = f"{METADATA_FILE}.bak"
            try:
                copy2(METADATA_FILE, backup_file)
                logger.info(f"Backup created at {backup_file}")
            except Exception as backup_err:
                logger.error(f"Failed to create backup: {backup_err}")
            history = []
        except (IOError, OSError) as e:
            logger.error(f"Failed to read metadata file: {e}. Starting with empty history.")
            history = []
        except Exception as e:
            logger.error(f"Unexpected error loading history: {e}. Starting with empty history.")
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
                except (IOError, OSError) as e:
                    logger.warning(f"Failed to remove evicted image {image_file}: {e}")

    with open(METADATA_FILE, "w") as f:
        json.dump(history, f, indent=4)
    return entry

def load_history():
    if not os.path.exists(METADATA_FILE):
        return []
    try:
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse metadata file: {e}. Returning empty history.")
        return []
    except (IOError, OSError) as e:
        logger.error(f"Failed to read metadata file: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error loading history: {e}")
        return []

def clear_all_history():
    if os.path.exists(METADATA_FILE):
        try:
            os.remove(METADATA_FILE)
        except (IOError, OSError) as e:
            logger.error(f"Failed to remove metadata file: {e}")
    if os.path.exists(IMAGES_DIR):
        for f in os.listdir(IMAGES_DIR):
            try:
                os.remove(os.path.join(IMAGES_DIR, f))
            except (IOError, OSError) as e:
                logger.warning(f"Failed to remove image file {f}: {e}")
