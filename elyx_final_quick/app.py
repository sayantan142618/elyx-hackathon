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

# --- Utils ---
def highlight_text(text, keyword):
    if not keyword:
        return text
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text)

# --- CSS (kept from Code 1) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

html, body, [class*="st-"] {
  font-family: 'Roboto', sans-serif;
  line-height: 1.6;
}

/* Light */
[data-testid="stAppViewContainer"] {
  background-color: #F8F9FA;
  color: #212529;
}
.card {
  background: #FFFFFF;
  color: #212529;
}
.kpi {
  background: #FFFFFF;
  color: #212529;
  border-left: 5px solid #1a4f78;
}
.chat-bubble {
  background: #f5f5f5;
  color: #212529;
}

/* Dark */
@media (prefers-color-scheme: dark) {
  [data-testid="stAppViewContainer"] {
    background-color: #121212 !important;
    color: #E0E0E0 !important;
  }
  .card {
    background: #1E1E1E !important;
    color: #E0E0E0 !important;
    border-color: #333 !important;
  }
  .kpi {
    background: #1E1E1E !important;
    color: #E0E0E0 !important;
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

/* KPI grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
}
.kpi {
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.06);
}
.kpi .label {
  font-size: 13px;
  opacity: 0.8;
}
.kpi .value {
  font-size: 26px;
  font-weight: 700;
}

/* Cards */
.card {
  border: 1px solid #ced4da;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  transition: transform .15s ease, box-shadow .15s ease;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.08);
}
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
.card-emoji {
  font-size: 26px;
  line-height: 1;
}
.card-title {
  font-weight: 700;
  font-size: 18px;
  flex: 1;
}
.card-meta {
  font-size: 13px;
  opacity: .7;
}
.pill {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  color: #fff;
  font-size: 12px;
  margin-left: 6px;
}

/* Chat bubble */
.chat-bubble {
  border-radius: 10px;
  padding: 10px;
  margin: 6px 0;
  max-width: 100%;
  word-wrap: break-word;
}

/* Highlight */
mark {
  background-color: #FFE066;
  color: #111;
  padding: 0 2px;
  border-radius: 2px;
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
except FileNotFoundError:
    st.error("❌ Missing data files in 'data' directory.")
    st.stop()

# --- KPI summary ---
metrics_summary = {
    "Doctor Hours": round(metrics['doctor_hours'].sum(), 1),
    "Performance Hours": round(metrics['performance_hours'].sum(), 1),
    "Nutrition Hours": round(metrics['nutrition_hours'].sum(), 1),
    "PT Hours": round(metrics['pt_hours'].sum(), 1),
    "Concierge Hours": round(metrics['ruby_hours'].sum(), 1)
}

# --- Header ---
st.image("logo.png", use_container_width=False, width=120)
st.markdown("<div class='big-title'>Elyx Journey — Member 360</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Decisions with Data to Maximize Health</div>", unsafe_allow_html=True)
st.markdown("---")

# --- Member Profile ---
st.subheader('🚀 Member Profile')
st.markdown(f"**Member:** {p.get('member', 'N/A')} | **Age:** {p.get('age', 'N/A')} | **Occupation:** {p.get('occupation', 'N/A')}")
st.markdown(f"**Core Goals:** {', '.join(p.get('goals', ['N/A']))}")

# --- KPI Cards ---
st.markdown("### 📊 Key Metrics")
st.markdown(
    "<div class='kpi-grid'>" +
    "".join(f"<div class='kpi'><div class='label'>{k}</div><div class='value'>{v}</div></div>"
            for k, v in metrics_summary.items()) +
    "</div>", unsafe_allow_html=True
)
st.markdown("---")

# --- Timeline ---
st.subheader('🗺️ The Journey: Key Decisions')
decision_search = st.text_input("🔍 Search decisions...").lower()

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

for dec in sorted(decs, key=lambda d: dt.datetime.fromisoformat(d['date'])):
    searchable = f"{dec.get('title','')} {dec.get('type','')} {dec.get('rationale','')}".lower()
    if decision_search in searchable or not decision_search:
        emoji = type_emojis.get(dec.get('type',''), '📌')
        color = type_colors.get(dec.get('type',''), '#1a4f78')
        st.markdown(
            f"""
            <div class="card">
              <div class="card-header">
                <div class="card-emoji">{emoji}</div>
                <div class="card-title">{dec.get('title','')}</div>
                <div class="card-meta">{dec.get('date','')[:10]}</div>
                <span class="pill" style="background:{color}">{dec.get('type','')}</span>
              </div>
              <div><b>Rationale:</b> {highlight_text(dec.get('rationale',''), decision_search)}</div>
            </div>
            """, unsafe_allow_html=True
        )

st.markdown("---")

# --- Progress Metrics ---
st.subheader("📈 Progress Metrics")
if not metrics.empty:
    min_date, max_date = metrics['date'].min().date(), metrics['date'].max().date()

    # Date inputs
    col1, col2, col3 = st.columns([1,1,0.5])
    with col1:
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    with col3:
        if st.button("🔄 Reset Range"):
            start_date, end_date = min_date, max_date
            st.rerun()

    # Slider
    start_date, end_date = st.slider(
        "Or adjust with slider:",
        min_value=min_date,
        max_value=max_date,
        value=(start_date, end_date),
        format="YYYY-MM-DD"
    )

    filtered = metrics[(metrics['date'].dt.date >= start_date) & (metrics['date'].dt.date <= end_date)]
    if not filtered.empty:
        hours_df = filtered.melt(
            id_vars='date',
            value_vars=['doctor_hours','pt_hours','ruby_hours','performance_hours','nutrition_hours'],
            var_name='Type', value_name='Hours'
        )
        chart = alt.Chart(hours_df).mark_area(opacity=0.7).encode(
            x='date:T', y='Hours:Q', color='Type:N',
            tooltip=['date:T','Type:N','Hours:Q']
        )
        st.altair_chart(chart, use_container_width=True)

        if 'hrv' in filtered.columns:
            st.altair_chart(
                alt.Chart(filtered).mark_line(point=True).encode(
                    x='date:T', y='hrv:Q', tooltip=['date:T','hrv:Q']
                ), use_container_width=True
            )
    else:
        st.info("No data for this range.")

















  




