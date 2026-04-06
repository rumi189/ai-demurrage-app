from datetime import datetime

def build_time_segments(events):
    """
    Converts event list into timeline segments
    """

    segments = []

    for i in range(len(events) - 1):
        start = events[i].get("time")
        end = events[i + 1].get("time")

        if start and end:
            segments.append({
                "start": start,
                "end": end,
                "event": events[i].get("event", "")
            })

    return segments


def calculate_laytime(segments, allowed_hours):
    """
    Basic laytime calculation
    """

    total_hours = 0

    for seg in segments:
        try:
            start = datetime.fromisoformat(seg["start"])
            end = datetime.fromisoformat(seg["end"])

            diff = (end - start).total_seconds() / 3600
            total_hours += diff
        except:
            continue

    excess = max(0, total_hours - allowed_hours)

    return {
        "total_hours": round(total_hours, 2),
        "laytime_used": round(total_hours, 2),
        "excess": round(excess, 2)
    }