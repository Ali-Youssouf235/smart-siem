import json
from pathlib import Path
from config import STATE_FILE


def load_last_record():

    if not Path(STATE_FILE).exists():
        return 0

    try:

        with open(STATE_FILE, "r") as f:
            return json.load(f).get("last_record_id", 0)

    except Exception:
        return 0


def save_last_record(record_id):

    with open(STATE_FILE, "w") as f:

        json.dump(
            {
                "last_record_id": record_id
            },
            f,
            indent=4
        )