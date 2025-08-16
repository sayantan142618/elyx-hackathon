import json
import pandas as pd
import streamlit as st
from pathlib import Path
import datetime as dt
import re

# --- App Config ---
st.set_page_config(
    page_title="Elyx Journey — Member 360",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Fix for Expander Icons ---
st.markdown("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<style>
/* Force Material Icons to render correctly */
.material-icons {
    font-family: 'Material Icons' !important;
    font-style: normal;
    font-weight: normal;
    font-size: 20px;  
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    display: inline-block;
    white-space: nowrap;
    direction: ltr;
    -webkit-font-feature-settings: 'liga';
    -webkit-font-smoothing: antialiased;
}

/* General font */
html, body, [class*="st-"] {
    font-family: 'Roboto', sans-serif;
    line-height: 1.6;
}

/* Expander titles fix (prevent overlap) */
.stExpander > button p {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
</style>
""", unsafe_allow_html=True)

# --- Highlight search matches ---
def highlight_text(text, keyword):
    if keyword:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text)
    return text

# --- Paths ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'

# --- Load Data ---
try:
    msgs = json.load((DATA_DIR / 'messages.json').open())
    decs = json.load((DATA_DIR / 'decisions.json').open())
    p = json.load((DATA_DIR / 'persona.json').open())
    metrics = pd.read_csv(DATA_DIR / 'internal_metrics.csv')
    metrics['date'] = pd.to_datetime(metrics['date'])

    metrics_summary = {
        "Doctor Hours": round(metrics['doctor_hours'].sum(), 1),
        "Performance Hours": round(metrics['performance_hours'].sum(), 1),
        "Nutrition Hours": round(metrics['nutrition_hours'].sum(), 1),
        "PT Hours": round(metrics['pt_hours'].sum(), 1),
        "Concierge Hours": round(metrics['ruby_hours'].sum(), 1)
    }
except FileNotFoundError:
    st.error("❌ Missing data files in 'data' directory.")
    st.stop()

# --- Header ---
st.image("logo.png", use_container_width=False, width=120)
st.markdown("<h1 style='text-align:center; color:#1a4f78;'>Elyx Journey — Member 360</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px;'>Empowering Decisions with Data to Maximize Health</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Member Profile ---
st.subheader('🚀 Member Profile')
st.markdown(f"**Member:** {p.get('member', 'N/A')} | **Age:** {p.get('age', 'N/A')} | **Occupation:** {p.get('occupation', 'N/A')}")
st.markdown(f"**Core Goals:** {', '.join(p.get('goals', ['N/A']))}")

# --- KPI Cards ---
st.markdown("### 📊 Key Metrics")
cols = st.columns(3)
for i, (label, value) in enumerate(metrics_summary.items()):
    with cols[i % 3]:
        st.metric(label, value)

st.markdown("---")

# --- Decisions Timeline ---
st.subheader('🗺️ The Journey: Key Decisions Over Time')
decision_search = st.text_input("🔍 Search decisions (title, type, or rationale)...", key="decision_search").lower()

type_emojis = {
    "Medication": "💊",
    "Therapy": "🧠",
    "Diagnostic Test": "🔬",
    "Plan Update": "📝",
    "Lifestyle Change": "🏋️",
    "Logistics": "✈️"
}

for dec in sorted(decs, key=lambda d: dt.datetime.fromisoformat(d['date'])):
    searchable_text = f"{dec['title']} {dec['type']} {dec['rationale']}".lower()
    if decision_search in searchable_text or decision_search == "":
        expander_title = f"{type_emojis.get(dec['type'], '📌')} {dec['title']} ({dec['date'][:10]})"
        with st.expander(expander_title, expanded=False):
            st.markdown(f"**Rationale:** {highlight_text(dec['rationale'], decision_search)}", unsafe_allow_html=True)
            st.markdown("### 💬 Communication Trail")
            for m in sorted([m for m in msgs if m['id'] in dec['source_message_ids']], key=lambda x: x['timestamp']):
                st.markdown(
                    f"<div style='background:#f5f5f5; border-radius:10px; padding:10px; margin:5px 0;'>"
                    f"<b>{m['speaker']}</b> - {m['timestamp'][:10]}<br>{highlight_text(m['text'], decision_search)}</div>",
                    unsafe_allow_html=True
                )

st.markdown("---")

# --- Metrics Chart ---
st.subheader('📈 Progress Metrics')
if not metrics.empty:
    min_date, max_date = metrics['date'].min().date(), metrics['date'].max().date()
    start_date, end_date = st.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )
    filtered_metrics = metrics[(metrics['date'].dt.date >= start_date) & (metrics['date'].dt.date <= end_date)]
    chart_data = filtered_metrics.set_index('date')[['doctor_hours', 'pt_hours', 'ruby_hours', 'performance_hours', 'nutrition_hours']]
    st.line_chart(chart_data)
else:
    st.info("No metrics available.")

st.markdown("---")

# --- Conversation Log ---
st.subheader('💬 Full Conversation Log')
chat_search = st.text_input("🔍 Search conversations...", key="chat_search").lower()
filtered_chat = [m for m in msgs if chat_search in m['text'].lower() or chat_search == ""]

if filtered_chat:
    for m in reversed(filtered_chat[-50:]):
        st.markdown(
            f"<div style='background:#f5f5f5; border-radius:10px; padding:10px; margin:5px 0;'>"
            f"<b>{m['speaker']}</b> - {m['timestamp'][:10]}<br>{highlight_text(m['text'], chat_search)}</div>",
            unsafe_allow_html=True
        )
else:
    st.info("No messages found.")






  




