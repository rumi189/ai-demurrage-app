import streamlit as st
import pdfplumber
import sqlite3
from datetime import datetime, timedelta
from openai import OpenAI
import json

# ==============================
# CONFIG
# ==============================
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

# ==============================
# DB SETUP
# ==============================
c.execute("""
CREATE TABLE IF NOT EXISTS voyages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    laytime_used REAL,
    excess REAL,
    demurrage REAL,
    created_at TEXT
)
""")
conn.commit()

st.set_page_config(layout="wide")
st.title("🚢 Laytime AI SaaS (V49)")

# ==============================
# LOGIN (SIMPLE)
# ==============================
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    user = st.text_input("Enter Username")
    if st.button("Login"):
        st.session_state.user = user
    st.stop()

st.success(f"Logged in as {st.session_state.user}")

# ==============================
# PDF EXTRACT
# ==============================
def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""
    return text

# ==============================
# AI EVENT EXTRACTION
# ==============================
def extract_events(text):

    prompt = f"""
Extract SOF events into JSON:

{{
 "nor": "",
 "events":[
  {{"start":"","end":"","event":""}}
 ]
}}

{text[:5000]}
"""

    res = client.chat.completions.create(
        model="gpt-5.2",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return json.loads(res.choices[0].message.content)

# ==============================
# CALCULATION
# ==============================
def calculate(events, nor, allowed, rate, notice):

    for e in events:
        e["start"] = datetime.strptime(e["start"], "%Y-%m-%d %H:%M")
        e["end"] = datetime.strptime(e["end"], "%Y-%m-%d %H:%M")

    if nor:
        start = datetime.strptime(nor, "%Y-%m-%d %H:%M") + timedelta(hours=notice)
    else:
        start = events[0]["start"]

    end = events[-1]["end"]

    total = (end - start).total_seconds() / 3600
    excess = max(0, total - allowed)
    dem = (excess / 24) * rate

    return total, excess, dem

# ==============================
# INPUTS
# ==============================
st.sidebar.header("⚙️ Inputs")

allowed = st.sidebar.number_input("Allowed Laytime", 72.0)
rate = st.sidebar.number_input("Rate", 15000.0)
notice = st.sidebar.number_input("NOR Notice", 6.0)

uploaded_file = st.file_uploader("Upload SOF")

voyage_name = st.text_input("Voyage Name")

# ==============================
# PROCESS
# ==============================
if uploaded_file and voyage_name:

    text = extract_text(uploaded_file)

    st.subheader("📄 SOF Preview")
    st.text(text[:1000])

    data = extract_events(text)

    events = data["events"]
    nor = data.get("nor")

    total, excess, dem = calculate(events, nor, allowed, rate, notice)

    st.subheader("📊 Results")
    st.write("Laytime Used:", round(total,2))
    st.write("Excess:", round(excess,2))
    st.write("Demurrage:", round(dem,2))

    # SAVE BUTTON
    if st.button("💾 Save Voyage"):

        c.execute("""
        INSERT INTO voyages (name, laytime_used, excess, demurrage, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (voyage_name, total, excess, dem, str(datetime.now())))

        conn.commit()
        st.success("Saved!")

# ==============================
# DASHBOARD
# ==============================
st.subheader("📊 Voyage Dashboard")

rows = c.execute("SELECT * FROM voyages ORDER BY id DESC").fetchall()

for r in rows:
    st.write(f"🚢 {r[1]} | Demurrage: ${round(r[4],2)} | Date: {r[5]}")