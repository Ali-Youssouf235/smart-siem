import subprocess
import json
from state import load_last_record, save_last_record


LOG_NAME = "OpenSSH/Operational"


def collect_events():

    last_record = load_last_record()

    powershell = f"""
    Get-WinEvent -FilterHashtable @{{LogName='{LOG_NAME}'}} |
    Select-Object RecordId,TimeCreated,ProviderName,Id,LevelDisplayName,Message |
    ConvertTo-Json -Depth 3
    """

    result = subprocess.run(
        ["powershell", "-Command", powershell],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    if result.returncode != 0:
        return []

    if not result.stdout.strip():
        return []

    try:
        events = json.loads(result.stdout)

    except Exception:
        return []

    if isinstance(events, dict):
        events = [events]

    new_events = []

    highest = last_record

    for event in events:

        record = event["RecordId"]

        if record > last_record:

            new_events.append(event)

            if record > highest:
                highest = record

    save_last_record(highest)

    return sorted(
        new_events,
        key=lambda x: x["RecordId"]
    )