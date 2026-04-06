def ai_parse(text):

    prompt = f"""
You are a senior maritime laytime expert.

Carefully analyze the Statement of Facts.

CRITICAL RULES:

1. Cargo Start:
   - First actual loading/discharging activity
   - NOT shifting, waiting, or idle time

2. Cargo Complete:
   - Final completion of cargo operations

3. IGNORE:
   - Pre-arrival delays
   - Waiting before cargo starts
   - Events outside cargo window

4. Delays:
   - Only include delays DURING cargo operations
   - Must have valid start AND end

5. Ensure:
   - Cargo start < cargo complete
   - Timeline is logical

Return STRICT JSON ONLY:

{{
"cargo_start":"YYYY-MM-DD HH:MM",
"cargo_complete":"YYYY-MM-DD HH:MM",
"delays":[
    {{
    "type":"weather/port/charterer",
    "start":"YYYY-MM-DD HH:MM",
    "end":"YYYY-MM-DD HH:MM"
    }}
]
}}

TEXT:
{text[:4000]}
"""

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}]
    )

    return safe_json(response.choices[0].message.content)