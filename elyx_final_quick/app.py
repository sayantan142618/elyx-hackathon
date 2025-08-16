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

html, body, [class*="st-"] {
  font-family: 'Roboto', sans-serif;
  line-height: 1.6;
}

/* Light Mode */
[data-testid="stAppViewContainer"] {
  background-color: #F8F9FA;
  color: #212529;
}
.card, .kpi, .chat-bubble {
  background: #FFFFFF;
  color: #212529;
}
.kpi { border-left: 5px solid #1a4f78; }

/* Dark Mode */
@media (prefers-color-scheme: dark) {
  [data-testid="stAppViewContainer"] {
    background-color: #121212 !important;
    color: #E0E0E0 !important;
  }
  .card, .kpi, .chat-bubble {
    background: #1E1E1E !important;
    color: #E0E0E0 !important;
    border-color: #333 !important;
  }
  .kpi { border-left-color: #4DA3FF !important; }
  .chat-bubble { background: #2A2A2A !important; }
}

/* Headings */
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
.section-title {
  font-size: 22px;
  font-weight: 700;
  margin: 20px 0 10px;
  color: #1a4f78;
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
st.markdown("<div class='big-title'>Elyx Journey — Member 360</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Decisions with Data to Maximize Health</div>", unsafe_allow_html=True)
st.markdown("---")

# --- Member Profile ---
st.markdown("<div class='section-title'>🚀 Member Profile</div>", unsafe_allow_html=True)
st.markdown(f"**Member:** {p.get('member', 'N/A')} | **Age:** {p.get('age', 'N/A')} | **Occupation:** {p.get('occupation', 'N/A')}")
st.markdown(f"**Core Goals:** {', '.join(p.get('goals', ['N/A']))}")

# --- KPI Cards ---
st.markdown("<div class='section-title'>📊 Key Metrics</div>", unsafe_allow_html=True)
cols = st.columns(3)
for i, (label, value) in enumerate(metrics_summary.items()):
    with cols[i % 3]:
        st.metric(label, value)

st.markdown("---")

# --- Decisions Timeline ---
st.markdown("<div class='section-title'>🗺️ The Journey: Key Decisions Over Time</div>", unsafe_allow_html=True)
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
                st.markdown("**💬 Communication Trail**")
                for m in sorted([m for m in msgs if m['id'] in dec['source_message_ids']], key=lambda x: x['timestamp']):
                    st.markdown(
                        f"<div class='chat-bubble'><b>{m['speaker']}</b> - {m['timestamp'][:10]}<br>{highlight_text(m['text'], decision_search)}</div>",
                        unsafe_allow_html=True
                    )

st.markdown("---")

# --- Metrics Visuals ---
st.markdown("<div class='section-title'>📈 Progress Metrics</div>", unsafe_allow_html=True)
if not metrics.empty:
    min_date, max_date = metrics['date'].min().date(), metrics['date'].max().date()

    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date, key="start_date_input")
    with col2:
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date, key="end_date_input")
    with col3:
        if st.button("🔄 Reset"):
            start_date, end_date = min_date, max_date
            st.experimental_set_query_params()  # clears state

    start_date, end_date = st.slider(
        "Adjust Date Range:",
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
st.markdown("<div class='section-title'>💬 Full Conversation Log</div>", unsafe_allow_html=True)
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

















  




