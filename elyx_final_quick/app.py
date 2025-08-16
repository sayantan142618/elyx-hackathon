import json
import pandas as pd
import streamlit as st
from pathlib import Path
import datetime as dt
import re

st.set_page_config(page_title="Elyx Journey — Member 360", layout="wide")

# --- CSS ---
st.markdown("""
<style>
summary {
    cursor: pointer;
    padding: 10px 14px;
    border-radius: 8px;
    background: #1E1E1E;
    color: #E0E0E0;
    margin-bottom: 8px;
    font-weight: bold;
    list-style: none;
}
summary::-webkit-details-marker { display: none; }
details[open] summary {
    background: #333;
}
.details-box {
    padding: 12px;
    margin: 6px 0 15px 0;
    border: 1px solid #444;
    border-radius: 8px;
    background: #1A1A1A;
}
.tag {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 12px;
    margin-top: 5px;
}
.chat-bubble {
    border-radius: 10px;
    padding: 10px;
    margin: 5px 0;
    background: #2A2A2A;
    color: #E0E0E0;
}
mark {
    background: yellow;
    color: black;
    padding: 0 2px;
    border-radius: 2px;
}
</style>
""", unsafe_allow_html=True)

# --- Highlight search matches ---
def highlight_text(text, keyword):
    if keyword:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text)
    return text

# --- Dummy Data (replace with your JSON files) ---
msgs = [
    {"id": 1, "speaker": "Dr. Smith", "timestamp": "2025-01-21", "text": "Adjust workout routine."},
    {"id": 2, "speaker": "Member", "timestamp": "2025-01-22", "text": "Feeling better after update."},
]
decs = [
    {"date": "2025-01-21", "title": "Swap intervals", "type": "Plan Update", "rationale": "Better endurance.", "source_message_ids": [1]},
    {"date": "2025-01-22", "title": "Exercise update EX", "type": "Lifestyle Change", "rationale": "Improved recovery.", "source_message_ids": [2]},
]

# --- Decision Types ---
type_emojis = {
    "Medication": "💊",
    "Therapy": "🧠",
    "Diagnostic Test": "🔬",
    "Plan Update": "📝",
    "Lifestyle Change": "🏋️",
    "Logistics": "✈️"
}
type_colors = {
    "Medication": "#d9534f",
    "Therapy": "#5bc0de",
    "Diagnostic Test": "#5cb85c",
    "Plan Update": "#f0ad4e",
    "Lifestyle Change": "#0275d8",
    "Logistics": "#6f42c1"
}

# --- Timeline ---
st.subheader("🗺️ The Journey: Key Decisions Over Time")
decision_search = st.text_input("🔍 Search decisions (title, type, or rationale)...", key="decision_search").lower()

for dec in sorted(decs, key=lambda d: dt.datetime.fromisoformat(d['date'])):
    searchable_text = f"{dec['title']} {dec['type']} {dec['rationale']}".lower()
    if decision_search in searchable_text or decision_search == "":
        
        # summary line (clickable)
        summary_line = f"{type_emojis.get(dec['type'], '📌')} {dec['title']} ({dec['date'][:10]})"
        
        # expanded details
        details_html = f"""
        <details>
          <summary>{summary_line}</summary>
          <div class="details-box">
            <span class="tag" style="background:{type_colors.get(dec['type'], '#1a4f78')}; color:white;">{dec['type']}</span><br><br>
            <b>Rationale:</b> {highlight_text(dec['rationale'], decision_search)}<br><br>
            <b>💬 Communication Trail:</b>
          </div>
        </details>
        """
        st.markdown(details_html, unsafe_allow_html=True)

        # messages
        for m in [m for m in msgs if m['id'] in dec['source_message_ids']]:
            st.markdown(
                f"<div class='chat-bubble'><b>{m['speaker']}</b> - {m['timestamp']}<br>{highlight_text(m['text'], decision_search)}</div>",
                unsafe_allow_html=True
            )











  




