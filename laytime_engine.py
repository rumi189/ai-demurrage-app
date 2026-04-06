from datetime import timedelta

def apply_laytime_rules(df, laytime_type="SHINC", nor_time=None, nor_hours=6):
    
    df = df.copy()
    df["count"] = 0
    df["reason"] = ""

    # STEP 1: Apply NOR + Notice Time
    if nor_time:
        laytime_start = nor_time + timedelta(hours=nor_hours)
    else:
        laytime_start = df.iloc[0]["start"]

    for i, row in df.iterrows():

        start = row["start"]
        end = row["end"]
        event = row["event"].lower()
        duration = (end - start).total_seconds() / 3600

        # Before laytime → ignore
        if end <= laytime_start:
            df.loc[i, "count"] = 0
            df.loc[i, "reason"] = "Pre-laytime"
            continue

        # Adjust start if overlaps laytime start
        if start < laytime_start:
            start = laytime_start
            duration = (end - start).total_seconds() / 3600

        # --- CORE LOGIC ---

        # Weather always excluded
        if "weather" in event:
            df.loc[i, "count"] = 0
            df.loc[i, "reason"] = "Weather excluded"

        # Waiting / anchorage → Charterer delay
        elif "waiting" in event or "anchorage" in event:
            df.loc[i, "count"] = duration
            df.loc[i, "reason"] = "Waiting = Charterer"

        # Cargo operations → count
        elif "loading" in event or "discharging" in event:
            df.loc[i, "count"] = duration
            df.loc[i, "reason"] = "Cargo ops"

        # SHINC logic (Sundays included)
        elif laytime_type == "SHINC":
            df.loc[i, "count"] = duration
            df.loc[i, "reason"] = "SHINC included"

        # SHEX logic (exclude Sundays)
        elif laytime_type == "SHEX":
            if start.weekday() == 6:
                df.loc[i, "count"] = 0
                df.loc[i, "reason"] = "Sunday excluded"
            else:
                df.loc[i, "count"] = duration
                df.loc[i, "reason"] = "Working day"

        else:
            df.loc[i, "count"] = duration
            df.loc[i, "reason"] = "Default"

    return df