import json
import re
import streamlit as st
from openai import OpenAI

client = OpenAI()


# =========================
# SAFE JSON PARSER (BULLETPROOF)
# =========================
def safe_json_loads(raw_text):
    try:
        if not raw_text:
            st.error("Empty AI response")
            return None

        text = raw_text.strip()

        # Remove markdown ```json blocks
        if text.startswith("```"):
            text = re.sub(r"```json|```", "", text).strip()

        # Remove leading/trailing junk before JSON
        first_brace = text.find("{")
        last_brace = text.rfind("}")

        if first_brace != -1 and last_brace != -1:
            text = text[first_brace:last_brace + 1]

        # Fix common AI issues
        text = text.replace("\n", " ")
        text = text.replace("\t", " ")

        return json.loads(text)

    except Exception as e:
        st.error("❌ JSON Parsing Failed")
        st.text(str(e))
        st.text("---- RAW AI OUTPUT ----")
        st.text(raw_text)
        return None


# =========================
# AI EXTRACTION ENGINE (STABLE)
# =========================
def extract_events_ai(text):

    prompt = f"""
You are a maritime laytime expert.

STRICT RULES:
- Output ONLY valid JSON
- NO markdown
- NO explanations
- NO comments

Return EXACT format:

{{
  "events": [
    {{
      "datetime_start": "YYYY-MM-DD HH:MM",
      "datetime_end": "YYYY-MM-DD HH:MM",
      "event": "description",
      "type": "nor | cargo | waiting | weather | shifting | other",
      "port": "port name"
    }}
  ],
  "nor": "YYYY-MM-DD HH:MM or null"
}}

TEXT:
{text[:6000]}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        raw_output = response.choices[0].message.content

        st.subheader("🔍 AI RAW OUTPUT (DEBUG)")
        st.text(raw_output)

        parsed = safe_json_loads(raw_output)

        if parsed is None:
            st.error("AI returned invalid JSON")
            return None

        return parsed

    except Exception as e:
        st.error("❌ AI Extraction Failed")
        st.text(str(e))
        return None


# =========================
# PROCESS EVENTS SAFELY
# =========================
def process_ai_events(ai_data):

    if not ai_data:
        return [], None

    events = ai_data.get("events", [])
    nor = ai_data.get("nor", None)

    clean_events = []

    for e in events:
        try:
            start = e.get("datetime_start")
            end = e.get("datetime_end")

            if not start or not end:
                continue

            clean_events.append({
                "start": start,
                "end": end,
                "event": e.get("event", "").lower(),
                "type": e.get("type", "other"),
                "port": e.get("port", "unknown")
            })

        except:
            continue

    return clean_events, nor


# =========================
# MAIN EXECUTION BLOCK
# =========================
def run_ai_pipeline(text):

    st.info("🤖 Running AI Extraction...")

    ai_data = extract_events_ai(text)

    if not ai_data:
        st.error("AI failed to extract structured data")
        return [], None

    events, nor = process_ai_events(ai_data)

    st.success(f"✅ Extracted {len(events)} events")

    return events, nor