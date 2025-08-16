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

# --- CSS ---
st.markdown("""
<style>
/* (keeping same CSS from Code 1 for clean look) */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

html, body, [class*="st-"] {
  font-family: 'Roboto', sans-serif;
  line-height: 1.6;
}
[data-testid="stAppViewContainer"] {
  background-color: #F8F9FA;
  color: #212529;
}
.card { background: #fff; border: 1px solid #ced4da; border-radius: 12px;
  padding: 16px; margin-bottom: 12px; transition: transform .15s, box-shadow .15s; }
.card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,.08);}
.card-header { display:flex; align-items:center; gap:12px; margin-bottom:8px;}
.card-emoji { font-size:26px;}
.card-title { flex:1; font-weight:700; font-size:18px;}
.card-meta { font-size:13px; opacity:.7;}
.pill { padding:4px 10px; border-radius:999px; color:#fff; font-size:12px; margin-left:6px;}
.kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:18px;}
.kpi { padding:16px; border-radius:12px; box-shadow:0 2px 4px rgba(0,0,0,.06);
  background:#fff; border-left:5px solid #1a4f78;}
.kpi .label{font-size:13px;opacity:.8;} .kpi .value{font-size:26px;font-weight:700;}
.chat-bubble { border-radius:10px; padding:10px; margin:6px 0; background:#f5f5f5; color:#212529; word-wrap:break-word;}
mark { background:#FFE066; color:#111; padding:0 2px; border-radius:2px;}
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
st.image("logo.png", width=120)
st.markdown("<div class='big-title'>Elyx Journey — Member 360</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Decisions with Data to Maximize Health</div>", unsafe_allow_html=True)
st.markdown("---")

# --- Profile ---
st.subheader('🚀 Member Profile')
st.markdown(f"**Member:** {p.get('member','N/A')} | **Age:** {p.get('age','N/A')} | **Occupation:** {p.get('occupation','N/A')}")
st.markdown(f"**Core Goals:** {', '.join(p.get('goals',['N/A']))}")

# --- KPI Grid ---
st.markdown("### 📊 Key Metrics")
st.markdown(
    "<div class='kpi-grid'>" +
    "".join(f"<div class='kpi'><div class='label'>{k}</div><div class='value'>{v}</div></div>"
            for k,v in metrics_summary.items()) +
    "</div>", unsafe_allow_html=True
)
st.markdown("---")

# --- Timeline ---
st.subheader('🗺️ The Journey: Key Decisions')
decision_search = st.text_input("🔍 Search decisions...").lower()

type_emojis = {"Medication":"💊","Therapy":"🧠","Diagnostic Test":"🔬",
               "Plan Update":"📝","Lifestyle Change":"🏋️","Logistics":"✈️"}
type_colors = {"Medication":"#d9534f","Therapy":"#5bc0de","Diagnostic Test":"#5cb85c",
               "Plan Update":"#f0ad4e","Lifestyle Change":"#0275d8","Logistics":"#6f42c1"}

for dec in sorted(decs, key=lambda d: dt.datetime.fromisoformat(d['date'])):
    searchable = f"{dec.get('title','')} {dec.get('type','')} {dec.get('rationale','')}".lower()
    if decision_search in searchable or not decision_search:
        emoji = type_emojis.get(dec.get('type',''),'📌')
        color = type_colors.get(dec.get('type',''),'#1a4f78')
        title, date_str, dtype = dec.get('title',''), dec.get('date','')[:10], dec.get('type','')
        
        st.markdown(
            f"<div class='card'><div class='card-header'>"
            f"<div class='card-emoji'>{emoji}</div>"
            f"<div class='card-title'>{title}</div>"
            f"<div class='card-meta'>{date_str}</div>"
            f"<span class='pill' style='background:{color}'>{dtype}</span></div>",
            unsafe_allow_html=True
        )
        st.markdown(f"<b>Rationale:</b> {highlight_text(dec.get('rationale',''), decision_search)}", unsafe_allow_html=True)

        if dec.get('before') or dec.get('after'):
            st.markdown(
                f"<div style='margin-top:10px; padding:10px; border-radius:10px; background:#f8f9fa;'>"
                f"<div><b>Before:</b> {dec.get('before','—')}</div>"
                f"<div><b>After:</b> {dec.get('after','—')}</div></div>", unsafe_allow_html=True)

        related = [m for m in msgs if m['id'] in dec.get('source_message_ids',[])]
        if related:
            st.markdown("**💬 Communication Trail**")
            for m in sorted(related, key=lambda x: x['timestamp']):
                st.markdown(
                    f"<div class='chat-bubble'><b>{m['speaker']}</b> — {m['timestamp'][:10]}<br>"
                    f"{highlight_text(m['text'], decision_search)}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --- Progress Metrics ---
st.subheader("📈 Progress Metrics")
if not metrics.empty:
    min_date, max_date = metrics['date'].min().date(), metrics['date'].max().date()
    col1,col2,col3 = st.columns([1,1,0.6])
    with col1: start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    with col2: end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    with col3:
        if st.button("🔄 Reset Range"): st.rerun()

    start_date, end_date = st.slider("Or adjust with slider:", min_date, max_date, (start_date,end_date), format="YYYY-MM-DD")
    filtered = metrics[(metrics['date'].dt.date >= start_date) & (metrics['date'].dt.date <= end_date)]

    if not filtered.empty:
        hours_df = filtered.melt(id_vars='date',
            value_vars=['doctor_hours','pt_hours','ruby_hours','performance_hours','nutrition_hours'],
            var_name='Type', value_name='Hours')
        st.altair_chart(alt.Chart(hours_df).mark_area(opacity=0.7).encode(
            x='date:T', y='Hours:Q', color='Type:N',
            tooltip=['date:T','Type:N','Hours:Q']
        ), use_container_width=True)

        if 'hrv' in filtered.columns:
            st.altair_chart(alt.Chart(filtered).mark_line(point=True).encode(
                x='date:T', y='hrv:Q', tooltip=['date:T','hrv:Q']
            ), use_container_width=True)
else:
    st.info("No metrics available.")

st.markdown("---")

# --- Full Conversation Log ---
st.subheader("💬 Full Conversation Log")
chat_search = st.text_input("🔎 Search conversations...").lower()
filtered_chat = [m for m in msgs if chat_search in m['text'].lower()] if chat_search else msgs
if filtered_chat:
    for m in reversed(filtered_chat[-50:]):
        st.markdown(
            f"<div class='chat-bubble'><b>{m['speaker']}</b> — {m['timestamp'][:10]}<br>"
            f"{highlight_text(m['text'], chat_search)}</div>", unsafe_allow_html=True)
else:
    st.info("No messages found.")


















  




