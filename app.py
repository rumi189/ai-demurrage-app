import streamlit as st

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Laytime AI SaaS", layout="wide")

# -----------------------------
# LOGIN SYSTEM (Simple)
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🚢 Laytime AI SaaS (V50)")

    username = st.text_input("Enter Username")

    if st.button("Login"):
        if username:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()

    st.stop()

# -----------------------------
# MAIN APP
# -----------------------------
st.title("🚢 Laytime AI SaaS (V50)")
st.success(f"Logged in as {st.session_state.username}")

# -----------------------------
# SIDEBAR INPUTS
# -----------------------------
st.sidebar.header("⚙️ Inputs")

allowed_laytime = st.sidebar.number_input(
    "Allowed Laytime (hrs)", value=72.0
)

rate = st.sidebar.number_input(
    "Demurrage Rate (USD/day)", value=15000.0
)

nor_notice = st.sidebar.number_input(
    "NOR Notice (hrs)", value=6.0
)

# -----------------------------
# FILE UPLOAD
# -----------------------------
st.subheader("📄 Upload Statement of Facts")

uploaded_file = st.file_uploader("Upload SOF PDF", type=["pdf"])

# -----------------------------
# PROCESSING PIPELINE
# -----------------------------
if uploaded_file:

    st.info("Processing SOF...")

    try:
        # IMPORT MODULES (your existing files)
        from sof_parser import extract_text
        from ai_parse import run_ai_pipeline
        from time_engine import build_time_segments
        from laytime_engine import calculate_laytime

        # -------------------------
        # STEP 1: EXTRACT TEXT
        # -------------------------
        raw_text = extract_text(uploaded_file)

        st.success("PDF Read Successfully")

        with st.expander("📜 Raw Text"):
            st.text(raw_text[:3000])  # preview

        # -------------------------
        # STEP 2: AI PARSE
        # -------------------------
        events, nor_time = run_ai_pipeline(raw_text)

        st.success("AI Parsing Complete")

        with st.expander("🧠 Extracted Events"):
            st.json(events)

        st.write("### 🕒 NOR Detected")
        st.write(nor_time)

        # -------------------------
        # STEP 3: BUILD TIMELINE
        # -------------------------
        segments = build_time_segments(events)

        with st.expander("⏱ Time Segments"):
            st.json(segments)

        # -------------------------
        # STEP 4: CALCULATE LAYTIME
        # -------------------------
        results = calculate_laytime(
            segments,
            allowed_hours=allowed_laytime,
            demurrage_rate=rate,
            nor_notice_hours=nor_notice,
            nor_time=nor_time
        )

        # -------------------------
        # STEP 5: DISPLAY RESULTS
        # -------------------------
        st.header("📊 Laytime Results")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Hours", round(results.get("total_hours", 0), 2))
        col2.metric("Laytime Used", round(results.get("laytime_used", 0), 2))
        col3.metric("Excess Hours", round(results.get("excess", 0), 2))

        st.metric(
            "💰 Demurrage (USD)",
            f"${round(results.get('demurrage', 0), 2)}"
        )

        # -------------------------
        # DEBUG (Optional)
        # -------------------------
        with st.expander("🔍 Full Result JSON"):
            st.json(results)

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")