import win32evtlog

server = "localhost"
logtype = "OpenSSH/Operational"

hand = win32evtlog.OpenEventLog(server, logtype)

flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

events = win32evtlog.ReadEventLog(hand, flags, 0)

for event in events[:5]:
    print("RecordNumber :", event.RecordNumber)
    print("TimeGenerated:", event.TimeGenerated)
    print("SourceName   :", event.SourceName)
    print("EventID      :", event.EventID)
    print("Message data :", event.StringInserts)
    print("-" * 50)