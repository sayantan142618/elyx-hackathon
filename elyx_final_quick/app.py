import json
import pandas as pd
import streamlit as st
from pathlib import Path
import datetime as dt
import re
import altair as alt

# --- App Config ---
st.set_page_config(
    page_title="Elyx Journey — Member 360",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Paths ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'

# --- Highlight search matches ---
def highlight_text(text, keyword):
    if keyword:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text)
    return text

# --- Adaptive CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

html, body, [class*="st-"] {
    font-family: 'Roboto', sans-serif;
    line-height: 1.6;
}

/* Light Mode */
[data-testid="stAppViewContainer"] {
    background-color: #F8F9FA;
    color: #212529;
}
.timeline-card {
    background-color: #FFFFFF;
    color: #212529;
}
.kpi-container {
    background-color: #FFFFFF;
    border-left-color: #1a4f78;
}
.chat-bubble {
    background: #f5f5f5;
    color: #212529;
}

/* Dark Mode */
@media (prefers-color-scheme: dark) {
    [data-testid="stAppViewContainer"] {
        background-color: #121212 !important;
        color: #E0E0E0 !important;
    }
    .timeline-card {
        background-color: #1E1E1E !important;
        color: #E0E0E0 !important;
        border-color: #333333 !important;
    }
    .kpi-container {
        background-color: #1E1E1E !important;
        border-left-color: #4DA3FF !important;
    }
    .chat-bubble {
        background: #2A2A2A !important;
        color: #E0E0E0 !important;
    }
}

/* Titles */
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
    font-weight: 300;
    margin-bottom: 25px;
}
.logo {
    display: block;
    margin-left: auto;
    margin-right: auto;
    max-width: 150px;
}

/* KPI cards */
.kpi-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: flex-start;
}
.kpi-container {
    flex: 1 1 calc(33.33% - 20px);
    min-width: 220px;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    text-align: center;
    border-left: 5px solid #1a4f78;
}
.kpi-label {
    font-size: 14px;
    opacity: 0.8;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
}

/* Chat bubbles */
.chat-bubble {
    border-radius: 10px;
    padding: 10px;
    margin: 5px 0;
    max-width: 100%;
    word-wrap: break-word;
}

/* Highlighted search */
mark {
    background-color: yellow;
    color: black;
    padding: 0 2px;
    border-radius: 2px;
}

/* Custom timeline cards */
.timeline-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px;
    cursor: pointer;
    border-radius: 10px;
    border: 1px solid #ced4da;
    margin-bottom: 10px;
    transition: all 0.2s ease-in-out;
}
.timeline-card-header:hover {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.timeline-card-title {
    font-weight: 600;
    flex-grow: 1;
}
.timeline-card-date {
    font-size: 0.9em;
    opacity: 0.7;
    margin-right: 10px;
}
.timeline-card-icon {
    font-size: 1.5em;
    transition: transform 0.2s;
}
.timeline-card-icon.rotated {
    transform: rotate(90deg);
}
</style>
""", unsafe_allow_html=True)

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
type_colors = {
    "Medication": "#d9534f",
    "Therapy": "#5bc0de",
    "Diagnostic Test": "#5cb85c",
    "Plan Update": "#f0ad4e",
    "Lifestyle Change": "#0275d8",
    "Logistics": "#6f42c1"
}

# Use a session state to manage the visibility of content for each decision
if 'timeline_state' not in st.session_state:
    st.session_state.timeline_state = {}

for dec in sorted(decs, key=lambda d: dt.datetime.fromisoformat(d['date'])):
    searchable_text = f"{dec['title']} {dec['type']} {dec['rationale']}".lower()
    
    if decision_search in searchable_text or decision_search == "":
        card_placeholder = st.empty()
        if card_placeholder.button(
            f"{type_emojis.get(dec['type'], '📌')} **{dec['title']}** — {dec['date'][:10]} ({dec['type']})",
            key=f"card_{dec['date']}_{dec['title']}"
        ):
            st.session_state.timeline_state[dec['title']] = not st.session_state.timeline_state.get(dec['title'], False)
            st.rerun()

        if st.session_state.timeline_state.get(dec['title'], False):
            with st.container(border=True):
                st.markdown(f"**Rationale:** {highlight_text(dec['rationale'], decision_search)}", unsafe_allow_html=True)
                st.markdown("### 💬 Communication Trail")
                for m in sorted([m for m in msgs if m['id'] in dec['source_message_ids']], key=lambda x: x['timestamp']):
                    st.markdown(
                        f"<div class='chat-bubble'><b>{m['speaker']}</b> - {m['timestamp'][:10]}<br>{highlight_text(m['text'], decision_search)}</div>",
                        unsafe_allow_html=True
                    )

st.markdown("---")

# --- Metrics Visuals ---
st.subheader('📈 Progress Metrics')
if not metrics.empty:
    min_date, max_date = metrics['date'].min().date(), metrics['date'].max().date()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

    # Sync with slider
    start_date, end_date = st.slider(
        "Or adjust with slider:",
        min_value=min_date,
        max_value=max_date,
        value=(start_date, end_date),
        format="YYYY-MM-DD"
    )

    filtered = metrics[(metrics['date'].dt.date >= start_date) & (metrics['date'].dt.date <= end_date)]

    if not filtered.empty:
        hours_df = filtered.melt(id_vars=['date'], 
                                 value_vars=['doctor_hours','pt_hours','ruby_hours','performance_hours','nutrition_hours'],
                                 var_name='Type', value_name='Hours')

        chart = alt.Chart(hours_df).mark_area(opacity=0.7).encode(
            x='date:T',
            y='Hours:Q',
            color='Type:N',
            tooltip=['date:T','Type:N','Hours:Q']
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

        if 'hrv' in filtered.columns:
            line = alt.Chart(filtered).mark_line(point=True).encode(
                x='date:T', y='hrv:Q', tooltip=['date:T','hrv:Q']
            )
            st.altair_chart(line, use_container_width=True)
    else:
        st.info("No data for this date range.")
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
            f"<div class='chat-bubble'><b>{m['speaker']}</b> - {m['timestamp'][:10]}<br>{highlight_text(m['text'], chat_search)}</div>",
            unsafe_allow_html=True
        )
else:
    st.info("No messages found.")














  




