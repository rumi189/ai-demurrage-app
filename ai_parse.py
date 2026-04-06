import json

def run_ai_pipeline(raw_text):
    """
    Simple AI pipeline placeholder
    Returns structured events + detected NOR
    """

    events = []

    lines = raw_text.split("\n")

    for line in lines:
        if ":" in line:
            events.append({
                "event": line.strip(),
                "type": "unknown"
            })

    # Dummy NOR detection (upgrade later)
    nor_time = None

    return events, nor_time