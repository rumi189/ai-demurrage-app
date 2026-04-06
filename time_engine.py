import re


# =========================================================
# 1. CLEAN RAW TIME STRING (OCR SAFE)
# =========================================================
def clean_time_string(t):
    """
    Cleans raw OCR / text input
    Converts:
    0820 → 08:20
    830 → 08:30
    Removes garbage characters
    """
    if not t:
        return None

    t = str(t).strip()

    # Remove non-time characters
    t = re.sub(r'[^0-9:]', '', t)

    # Convert 4-digit format → HH:MM
    if re.match(r'^\d{4}$', t):
        return t[:2] + ":" + t[2:]

    # Convert 3-digit → HH:MM (e.g. 830 → 08:30)
    if re.match(r'^\d{3}$', t):
        return "0" + t[0] + ":" + t[1:]

    return t


# =========================================================
# 2. CONVERT TIME → DECIMAL HOURS
# =========================================================
def time_to_hours(t):
    """
    Converts time string → decimal hours

    Handles:
    - 0000 / 0001 → 0.0 (shipping standard)
    - 2400 → 24.0
    - Normal HH:MM
    """

    t = clean_time_string(t)

    if not t or ":" not in t:
        return None

    try:
        hh, mm = t.split(":")
        hh = int(hh)
        mm = int(mm)

        # 🔥 SHIPPING LOGIC FIX
        if hh == 0 and mm <= 1:
            return 0.0

        if hh == 24:
            return 24.0

        return hh + (mm / 60)

    except:
        return None


# =========================================================
# 3. FIX MIDNIGHT CROSSING
# =========================================================
def fix_midnight_crossing(start_h, end_h):
    """
    Example:
    22:30 → 03:00 → becomes 22.5 → 27.0
    """

    if start_h is None or end_h is None:
        return start_h, end_h

    if end_h < start_h:
        end_h += 24

    return start_h, end_h


# =========================================================
# 4. VALIDATION (OPTIONAL BUT STRONG)
# =========================================================
def validate_time(h):
    """
    Ensures time is within reasonable maritime range
    """
    if h is None:
        return False

    return 0 <= h <= 48


# =========================================================
# 5. FULL PIPELINE FOR ONE ROW
# =========================================================
def process_time_row(start, end):
    """
    Complete processing pipeline
    Returns:
    start_h, end_h, duration
    """

    start_h = time_to_hours(start)
    end_h = time_to_hours(end)

    start_h, end_h = fix_midnight_crossing(start_h, end_h)

    # Validate
    if not validate_time(start_h) or not validate_time(end_h):
        return None, None, 0

    # Calculate duration
    duration = round(end_h - start_h, 4)

    # Prevent negative or absurd values
    if duration < 0 or duration > 48:
        duration = 0

    return start_h, end_h, duration


# =========================================================
# 6. APPLY TO DATAFRAME
# =========================================================
def apply_time_engine(df):
    """
    Applies full time engine to dataframe
    Requires columns: start, end
    """

    df[['start_h', 'end_h', 'duration']] = df.apply(
        lambda row: process_time_row(row['start'], row['end']),
        axis=1,
        result_type='expand'
    )

    return df