import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATA_FILE = os.getenv("DATA_FILE", "data/knowledge_base.json")

DEFAULT_DATA = {
    "user_profile": {
        "name": "",
        "current_role": "",
        "profile_summary": "",
        "attachments": [],
        "urls": []
    },
    "technical_skills": {
        # initial categories can be empty; user can add categories dynamically
    },
    "projects": [],
    "other_activities": []
}


def load_data():
    """Load knowledge base JSON data; return default structure if missing/corrupt."""
    if not os.path.exists(DATA_FILE):
        # create file with default structure
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))  # return fresh copy

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # overwrite with default if corrupted
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))

    # Ensure all top-level keys exist for backward compatibility
    for k, v in DEFAULT_DATA.items():
        if k not in data:
            data[k] = v

    # Make sure technical_skills is a dict
    if not isinstance(data.get("technical_skills", {}), dict):
        data["technical_skills"] = {}

    return data


def save_data(data):
    """Save the knowledge base JSON data to disk. Returns True on success."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        # For debugging; in production consider logging
        print(f"[data_store] Error saving data: {e}")
        return False
