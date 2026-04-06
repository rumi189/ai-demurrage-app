import re

def normalize_time(t):
    t = str(t).zfill(4)

    if t == "2400":
        return 24.0

    hh = int(t[:2])
    mm = int(t[2:])
    return hh + mm / 60


def extract_time_range(line):
    # Match 0820-0842
    match = re.search(r'(\d{3,4})\s*[-–]\s*(\d{3,4})', line)
    if match:
        return match.group(1), match.group(2)

    # Match single time
    match = re.search(r'\b(\d{3,4})\b', line)
    if match:
        return match.group(1), None

    return None, None


def parse_sof(text):
    events = []

    lines = text.split("\n")

    for line in lines:
        start_raw, end_raw = extract_time_range(line)

        if not start_raw:
            continue

        start = normalize_time(start_raw)
        end = normalize_time(end_raw) if end_raw else None

        events.append({
            "start": start,
            "end": end,
            "event": line
        })

    # Sort chronologically
    events = sorted(events, key=lambda x: x["start"])

    # Build timeline
    structured = []

    for i in range(len(events)):
        current = events[i]

        if current["end"] is not None:
            end = current["end"]
        elif i + 1 < len(events):
            end = events[i + 1]["start"]
        else:
            end = current["start"]

        duration = end - current["start"]

        if duration < 0:
            duration += 24  # midnight rollover

        structured.append({
            "start": current["start"],
            "end": end,
            "event": current["event"],
            "duration": round(duration, 4)
        })

    return structured