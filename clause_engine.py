# clause_engine.py

def process_charter_party(text):
    """
    Dummy BIMCO clause processor (V13 baseline)
    Returns structured clause insights
    """

    if not text:
        return {
            "laytime_terms": "Not detected",
            "exceptions": "Not detected",
            "risk": "Unknown"
        }

    text = text.lower()

    result = {}

    # Detect laytime type
    if "weather working day" in text or "wwd" in text:
        result["laytime_terms"] = "Weather Working Day (WWD)"
    elif "running hours" in text:
        result["laytime_terms"] = "Running Hours"
    else:
        result["laytime_terms"] = "Unknown"

    # Detect exceptions
    exceptions = []
    if "rain" in text:
        exceptions.append("Rain")
    if "strike" in text:
        exceptions.append("Strike")
    if "breakdown" in text:
        exceptions.append("Breakdown")

    result["exceptions"] = ", ".join(exceptions) if exceptions else "None detected"

    # Simple risk logic
    if "without prejudice" in text:
        result["risk"] = "⚠️ Legal ambiguity detected"
    else:
        result["risk"] = "Normal"

    return result