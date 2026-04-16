import json
import os
from datetime import datetime

METADATA_FILE = "metadata.json"


def load_metadata():
    if not os.path.exists(METADATA_FILE):
        return []

    with open(METADATA_FILE, "r") as f:
        return json.load(f)


def save_metadata(data):
    with open(METADATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_backup_record(file_name, file_ids, size):
    data = load_metadata()

    record = {
        "backup_id": len(data) + 1,
        "file_name": file_name,
        "file_ids": file_ids,
        "backup_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "size": size
    }

    data.append(record)
    save_metadata(data)