import time

from collector import collect_events

print("SMART SIEM AGENT")

while True:

    events = collect_events()

    for e in events:

        print("=" * 70)

        print("Record :", e["RecordId"])

        print("Time   :", e["TimeCreated"])

        print("Level  :", e["LevelDisplayName"])

        print("EventID:", e["Id"])

        print("Source :", e["ProviderName"])

        print("Message:")

        print(e["Message"])

    time.sleep(2)