import json
import pandas as pd
import streamlit as st
from pathlib import Path
import datetime as dt

# --- App Config ---
st.set_page_config(
    page_title="Elyx Journey — Member 360",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Paths ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'

# --- Custom CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
    }
    .main {
        background-color: #F8F9FA;
        color: #212529;
    }
    .sidebar .sidebar-content {
        background-color: #E9ECEF;
        color: #495057;
    }
    .big-title {
        font-size: 50px !important;
        text-align: center;
        font-weight: 700;
        color: #1a4f78;
        margin-top: -30px;
    }
    .sub-title {
        text-align: center;
        font-size: 20px;
        color: #495057;
        font-weight: 300;
        margin-bottom: 30px;
    }
    .kpi-container {
        padding: 20px;
        border-radius: 10px;
        background-color: #FFFFFF;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-left: 5px solid #1a4f78;
    }
    .kpi-label {
        font-size: 16px;
        color: #6c757d;
        font-weight: 400;
    }
    .kpi-value {
        font-size: 36px;
        font-weight: 700;
        color: #1a4f78;
    }
    h2, h3 {
        color: #1a4f78;
        font-weight: 700;
        border-bottom: 2px solid #ced4da;
        padding-bottom: 5px;
    }
    .chat-bubble {
        background-color: #E9ECEF;
        border-radius: 15px;
        padding: 10px 15px;
        margin: 5px 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .stExpander > button {
        padding: 10px 20px;
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
st.image("logo.png", width=120)
st.markdown("<div class='big-title'>Elyx Journey — Member 360</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Decisions with Data to Maximize Health</div>", unsafe_allow_html=True)
st.markdown("---")

# --- Member Profile ---
st.subheader('🚀 Member Profile & Key Metrics')
st.markdown(f"**Member:** {p.get('member', 'N/A')} | **Age:** {p.get('age', 'N/A')} | **Occupation:** {p.get('occupation', 'N/A')}")
st.markdown(f"**Core Goals:** {', '.join(p.get('goals', ['N/A']))}")
st.markdown("---")

# --- KPI Cards ---
col1, col2, col3 = st.columns(3)
for i, (label, value) in enumerate(metrics_summary.items()):
    with [col1, col2, col3][i % 3]:
        st.markdown(
            f"<div class='kpi-container'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div></div>",
            unsafe_allow_html=True
        )

st.markdown("---")

# --- Decisions Timeline with Enhanced Search ---
st.subheader('🗺️ The Journey: Key Decisions Over Time')
decision_search = st.text_input("🔍 Search decisions (title, type, or rationale)...").lower()

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
        
        # Corrected Expander Title Format
        st_expander_title = f"{emoji} **{dec['date'][:10]}** — {dec['title']} ({dec['type']})"
        with st.expander(st_expander_title):
            st.markdown(f"**Rationale:** {dec['rationale']}")
            st.markdown("---")
            st.markdown("### 💬 Communication Trail")
            
            # Corrected Chat Bubble Formatting with a clear layout
            for m in sorted([m for m in msgs if m['id'] in dec['source_message_ids']], key=lambda x: x['timestamp']):
                st.markdown(
                    f"<div class='chat-bubble'><b>{m['speaker']}</b> - {m['timestamp'][:10]}<br>{m['text']}</div>",
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

# --- Conversation Log with Search ---
st.subheader('💬 Full Conversation Log')
chat_search = st.text_input("🔍 Search conversations...", help="Filter messages by keyword.").lower()
filtered_chat = [m for m in msgs if chat_search in m['text'].lower() or chat_search == ""]

if filtered_chat:
    for m in reversed(filtered_chat[-50:]):
        st.markdown(f"**{m['speaker']}** <span style='color:#6c757d; font-size:12px;'>— {m['timestamp']}</span>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-bottom: 10px;'>{m['text']}</div>", unsafe_allow_html=True)
else:
    st.info("No messages found.")

