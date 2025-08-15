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

# --- Paths ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'

# --- Highlight function ---
def highlight_text(text, keyword):
    if keyword:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text)
    return text

# --- Custom CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
    }
    .big-title {
        font-size: 42px !important;
        text-align: center;
        font-weight: 700;
        color: #1a4f78;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        font-size: 18px;
        color: #495057;
        font-weight: 300;
        margin-bottom: 25px;
    }
    .logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        max-width: 150px;
    }
    .kpi-container {
        padding: 15px;
        border-radius: 10px;
        background-color: #FFFFFF;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-left: 5px solid #1a4f78;
        margin-bottom: 15px;
    }
    .kpi-label {
        font-size: 14px;
        color: #6c757d;
        font-weight: 400;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #1a4f78;
    }
    .chat-bubble {
        background-color: #E9ECEF;
        border-radius: 15px;
        padding: 10px 15px;
        margin: 8px 0;
    }
    mark {
        background-color: yellow;
        color: black;
        padding: 0 2px;
        border-radius: 2px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Load data ---
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
except KeyError as e:
    st.error(f"❌ A key is missing from your 'persona.json' file: {e}")
    st.info("Please ensure 'persona.json' contains keys like 'member', 'age', 'occupation', and 'goals'.")
    st.stop()

# --- Header ---
st.image("logo.png", use_column_width=False, output_format="PNG", caption="", width=120)
st.markdown("<div class='big-title'>Elyx Journey — Member 360</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Decisions with Data to Maximize Health</div>", unsafe_allow_html=True)
st.markdown("---")

# --- Member Profile ---
st.subheader('🚀 Member Profile')
st.markdown(f"**Member:** {p.get('member', 'N/A')} | **Age:** {p.get('age', 'N/A')} | **Occupation:** {p.get('occupation', 'N/A')}")
st.markdown(f"**Core Goals:** {', '.join(p.get('goals', ['N/A']))}")

# --- KPI Cards ---
st.markdown("### 📊 Key Metrics")
kpi_cols = st.columns(3)
for i, (label, value) in enumerate(metrics_summary.items()):
    with kpi_cols[i % 3]:
        st.markdown(
            f"<div class='kpi-container'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div></div>",
            unsafe_allow_html=True
        )

st.markdown("---")

# --- Decisions Timeline with Enhanced Search + Highlight ---
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
        emoji = type_emojis.get(dec['type'], "📌")
        with st.expander(f"{emoji} {dec['date'][:10]} — {dec['title']} ({dec['type']})"):
            st.markdown(f"**Rationale:** {highlight_text(dec['rationale'], decision_search)}", unsafe_allow_html=True)
            st.markdown("### 💬 Communication Trail")
            for m in sorted([m for m in msgs if m['id'] in dec['source_message_ids']], key=lambda x: x['timestamp']):
                st.markdown(
                    f"<div class='chat-bubble'><b>{m['speaker']}</b> - {m['timestamp'][:10]}<br>{highlight_text(m['text'], decision_search)}</div>",
                    unsafe_allow_html=True
                )

st.markdown("---")

# --- Metrics Chart ---
st.subheader('📈 Progress Metrics')
if not metrics.empty:
    min_date, max_date = metrics['date'].min().date(), metrics['date'].max().date()
    start_date, end_date = st.slider("Select Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="YYYY-MM-DD")
    filtered_metrics = metrics[(metrics['date'].dt.date >= start_date) & (metrics['date'].dt.date <= end_date)]
    chart_data = filtered_metrics.set_index('date')[['doctor_hours', 'pt_hours', 'ruby_hours', 'performance_hours', 'nutrition_hours']]
    st.line_chart(chart_data)
else:
    st.info("No metrics available.")

st.markdown("---")

# --- Conversation Log with Search + Highlight ---
st.subheader('💬 Full Conversation Log')
chat_search = st.text_input("🔍 Search conversations...", key="chat_search").lower()
filtered_chat = [m for m in msgs if chat_search in m['text'].lower() or chat_search == ""]

if filtered_chat:
    for m in reversed(filtered_chat[-50:]):
        st.markdown(
            f"<div class='chat-bubble'><b>{m['speaker']}</b> - {m['timestamp'][:10]}<br>{highlight_text(m['text'], chat_search)}</div>",
            unsafe_allow_html=True
        )
else:
    st.info("No messages found.")

