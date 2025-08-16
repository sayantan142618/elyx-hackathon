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
DATA_DIR = BASE_DIR / "data"

# --- Highlight search matches ---
def highlight_text(text, keyword):
    if keyword:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text)
    return text

# --- Adaptive CSS ---
st.markdown("""
<style>
html { scroll-behavior: smooth; }
section { scroll-margin-top: 80px; }

@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
html, body, [class*="st-"] { font-family: 'Roboto', sans-serif; line-height: 1.6; }

/* Light */
[data-testid="stAppViewContainer"] { background-color: #F8F9FA; color: #212529; }
.card, .kpi, .chat-bubble { background: #FFFFFF; color: #212529; }
.kpi { border-left: 5px solid #1a4f78; }

/* Dark */
@media (prefers-color-scheme: dark) {
  [data-testid="stAppViewContainer"] { background-color: #121212 !important; color: #E0E0E0 !important; }
  .card, .kpi, .chat-bubble { background: #1E1E1E !important; color: #E0E0E0 !important; border-color: #333 !important; }
  .kpi { border-left-color: #4DA3FF !important; }
  .chat-bubble { background: #2A2A2A !important; }
}

/* Header */
.hero {
  background: linear-gradient(90deg, #1a4f78, #2679b8);
  color: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  font-size: 20px;
  margin: 20px 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.hero b { color: #fffb; }

/* Titles */
.big-title { font-size: 42px !important; text-align: center; font-weight: 700; color: #1a4f78; margin-bottom: 5px; }
.sub-title { text-align: center; font-size: 18px; font-weight: 300; margin-bottom: 25px; }
.section-title {
  font-size: 24px; font-weight: 700; margin: 40px 0 20px;
  color: #1a4f78; display: flex; align-items: center; gap: 8px;
  border-bottom: 2px solid #e0e0e0; padding-bottom: 6px;
}

/* KPI grid */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
.kpi {
  padding: 16px; border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-align: center;
}
.kpi:hover { transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0,0,0,0.12); }
.kpi .label { font-size: 13px; opacity: 0.8; }
.kpi .value { font-size: 26px; font-weight: 700; }
.kpi .icon { font-size: 26px; margin-bottom: 6px; }

/* Timeline card */
.card {
  border: 1px solid #ced4da; border-radius: 12px; padding: 16px; margin-bottom: 12px;
  transition: transform .15s ease, box-shadow .15s ease;
}
.card:hover { transform: translateY(-3px); box-shadow: 0 6px 12px rgba(0,0,0,0.08); }

/* Chat bubble */
.chat-bubble { border-radius: 10px; padding: 10px; margin: 6px 0; word-wrap: break-word; }

/* Highlight search */
mark { background-color: #FFE066; color: #111; padding: 0 2px; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
try:
    msgs = json.load((DATA_DIR / "messages.json").open())
    decs = json.load((DATA_DIR / "decisions.json").open())
    p = json.load((DATA_DIR / "persona.json").open())
    metrics = pd.read_csv(DATA_DIR / "internal_metrics.csv")
    metrics["date"] = pd.to_datetime(metrics["date"])

    metrics_summary = {
        "Doctor Hours": round(metrics["doctor_hours"].sum(), 1),
        "Performance Hours": round(metrics["performance_hours"].sum(), 1),
        "Nutrition Hours": round(metrics["nutrition_hours"].sum(), 1),
        "PT Hours": round(metrics["pt_hours"].sum(), 1),
        "Concierge Hours": round(metrics["ruby_hours"].sum(), 1),
    }
except FileNotFoundError:
    st.error("❌ Missing data files in 'data' directory.")
    st.stop()

# --- Sidebar Navigation ---
st.sidebar.title("📌 Navigation")
st.sidebar.markdown("[🚀 Profile](#profile)")
st.sidebar.markdown("[📊 Key Metrics](#metrics)")
st.sidebar.markdown("[🗺️ Timeline](#timeline)")
st.sidebar.markdown("[📈 Progress](#progress)")
st.sidebar.markdown("[💬 Conversations](#chat)")

# --- Header ---
st.image("logo.png", width=120)
st.markdown("<div class='big-title'>Elyx Journey — Member 360</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Decisions with Data to Maximize Health</div>", unsafe_allow_html=True)

# --- Hero Summary ---
total_hours = sum(metrics_summary.values())
first_date, last_date = metrics["date"].min().date(), metrics["date"].max().date()
st.markdown(
    f"<div class='hero'>📈 Over this journey ({first_date} → {last_date}), "
    f"total engagement: <b>{int(total_hours)} hours</b>.</div>",
    unsafe_allow_html=True,
)

# --- Member Profile ---
st.markdown("<section id='profile'></section>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>🚀 Member Profile</div>", unsafe_allow_html=True)
st.markdown(f"**Member:** {p.get('member','N/A')} | **Age:** {p.get('age','N/A')} | **Occupation:** {p.get('occupation','N/A')}")
st.markdown(f"**Core Goals:** {', '.join(p.get('goals',['N/A']))}")

# --- KPI Cards ---
st.markdown("<section id='metrics'></section>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📊 Key Metrics</div>", unsafe_allow_html=True)
icons = ["🩺","⚡","🥗","🏋️","🤝"]
st.markdown(
    "<div class='kpi-grid'>" +
    "".join(f"<div class='kpi'><div class='icon'>{icons[i]}</div><div class='label'>{k}</div><div class='value'>{v}</div></div>"
            for i,(k,v) in enumerate(metrics_summary.items())) +
    "</div>", unsafe_allow_html=True
)

# --- Timeline ---
st.markdown("<section id='timeline'></section>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>🗺️ The Journey: Key Decisions</div>", unsafe_allow_html=True)
decision_search = st.text_input("🔍 Search decisions...", key="decision_search").lower()
type_emojis = {"Medication":"💊","Therapy":"🧠","Diagnostic Test":"🔬","Plan Update":"📝","Lifestyle":"🏋️","Logistics":"✈️"}
if "timeline_state" not in st.session_state: st.session_state.timeline_state = {}

for dec in sorted(decs, key=lambda d: dt.datetime.fromisoformat(d["date"])):
    searchable_text = f"{dec['title']} {dec['type']} {dec['rationale']}".lower()
    if decision_search in searchable_text or decision_search == "":
        card = st.container()
        if card.button(f"{type_emojis.get(dec['type'],'📌')} **{dec['title']}** — {dec['date'][:10]} ({dec['type']})",
                       key=f"card_{dec['date']}_{dec['title']}"):
            st.session_state.timeline_state[dec['title']] = not st.session_state.timeline_state.get(dec['title'], False)
            st.rerun()
        if st.session_state.timeline_state.get(dec['title'], False):
            st.markdown(f"<div class='card'><b>Rationale:</b> {highlight_text(dec['rationale'], decision_search)}</div>",
                        unsafe_allow_html=True)

# --- Progress Metrics ---
st.markdown("<section id='progress'></section>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📈 Progress Metrics</div>", unsafe_allow_html=True)
if not metrics.empty:
    min_date, max_date = metrics["date"].min().date(), metrics["date"].max().date()
    start_date, end_date = st.slider("Select Date Range:", min_value=min_date, max_value=max_date, value=(min_date, max_date))
    filtered = metrics[(metrics["date"].dt.date >= start_date) & (metrics["date"].dt.date <= end_date)]
    if not filtered.empty:
        hours_df = filtered.melt(id_vars=["date"], value_vars=["doctor_hours","pt_hours","ruby_hours","performance_hours","nutrition_hours"],
                                 var_name="Type", value_name="Hours")
        chart = alt.Chart(hours_df).mark_area(opacity=0.7).encode(
            x="date:T", y="Hours:Q", color="Type:N", tooltip=["date:T","Type:N","Hours:Q"]).interactive()
        st.altair_chart(chart, use_container_width=True)

# --- Conversations ---
st.markdown("<section id='chat'></section>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>💬 Full Conversation Log</div>", unsafe_allow_html=True)
chat_search = st.text_input("🔍 Search conversations...", key="chat_search").lower()
filtered_chat = [m for m in msgs if chat_search in m['text'].lower() or chat_search == ""]
for m in reversed(filtered_chat[-50:]):
    st.markdown(f"<div class='chat-bubble'><b>{m['speaker']}</b> - {m['timestamp'][:10]}<br>{highlight_text(m['text'], chat_search)}</div>",
                unsafe_allow_html=True)


















  




