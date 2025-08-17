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

# --- Sidebar Navigation ---
st.sidebar.markdown("## 📂 Navigation")
st.sidebar.markdown("- [🚀 Member Profile](#member-profile)")
st.sidebar.markdown("- [📊 Key Metrics](#key-metrics)")
st.sidebar.markdown("- [🗺️ Journey Timeline](#journey-timeline)")
st.sidebar.markdown("- [📈 Progress Metrics](#progress-metrics)")
st.sidebar.markdown("- [💬 Conversation Log](#conversation-log)")

theme_choice = st.sidebar.radio("🎨 Theme", ["Light", "Dark"], horizontal=True)

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

# --- KPI Summary ---
def sum_col(name):
    return round(pd.to_numeric(metrics.get(name, pd.Series(0)), errors="coerce").fillna(0).sum(), 1)

metrics_summary = {
    "Doctor Hours": sum_col('doctor_hours'),
    "Performance Hours": sum_col('performance_hours'),
    "Nutrition Hours": sum_col('nutrition_hours'),
    "PT Hours": sum_col('pt_hours'),
    "Concierge Hours": sum_col('ruby_hours')
}

# --- CSS ---
light_css = """
<style>
html, body, [class*="st-"] { font-family: 'Roboto', sans-serif; line-height: 1.6; }
[data-testid="stAppViewContainer"] { background-color: #F8F9FA; color: #212529; }
.big-title { font-size: 42px; text-align: center; font-weight: 700; color: #1a4f78; margin-bottom: 5px; }
.sub-title { text-align: center; font-size: 18px; font-weight: 300; margin-bottom: 25px; }
.kpi { background: #FFFFFF; border-left: 5px solid #1a4f78; border-radius: 10px; padding: 16px; margin:8px 0; }
.kpi .label { font-size: 14px; opacity: 0.7; }
.kpi .value { font-size: 28px; font-weight: 700; color: #1a4f78; }
.chat-bubble { background: #f5f5f5; border-radius: 8px; padding: 10px; margin: 6px 0; color: #212529; }
mark { background: #FFE066; color: #111; padding: 0 2px; border-radius: 2px; }
.section-title { font-size:28px; font-weight:700; margin:20px 0 10px 0; color:#1a4f78; }
</style>
"""

dark_css = """
<style>
html, body, [class*="st-"] { font-family: 'Roboto', sans-serif; line-height: 1.6; }
[data-testid="stAppViewContainer"] { background-color: #121212 !important; color: #E0E0E0 !important; }
.big-title { font-size: 42px; text-align: center; font-weight: 700; color: #4DA3FF; margin-bottom: 5px; }
.sub-title { text-align: center; font-size: 18px; font-weight: 300; margin-bottom: 25px; color: #bbb; }
.kpi { background: #1E1E1E; border-left: 5px solid #4DA3FF; border-radius: 10px; padding: 16px; margin:8px 0; }
.kpi .label { font-size: 14px; opacity: 0.7; }
.kpi .value { font-size: 28px; font-weight: 700; color: #4DA3FF; }
.chat-bubble { background: #2A2A2A; border-radius: 8px; padding: 10px; margin: 6px 0; color: #E0E0E0; }
mark { background: #FFB347; color: black; padding: 0 2px; border-radius: 2px; }
.section-title { font-size:28px; font-weight:700; margin:20px 0 10px 0; color:#4DA3FF; }
</style>
"""

# --- Extra Fix: Button Styling (Light + Dark + Type-specific) ---
button_css = """
<style>
[data-testid="stButton"] > button {
    border-radius: 8px !important;
    padding: 6px 14px !important;
    border: none !important;
    font-weight: 600 !important;
    margin: 4px 0;
    transition: 0.2s all ease-in-out;
}
/* Default Light */
[data-testid="stAppViewContainer"] .stButton>button {
    background-color: #1a4f78 !important;
    color: white !important;
}
[data-testid="stAppViewContainer"] .stButton>button:hover {
    opacity: 0.9; box-shadow: 0px 2px 6px rgba(0,0,0,0.2);
}
/* Default Dark */
[data-testid="stAppViewContainer"][data-baseweb="baseweb"] .stButton>button {
    background-color: #2A2A2A !important;
    color: #E0E0E0 !important;
}
[data-testid="stAppViewContainer"][data-baseweb="baseweb"] .stButton>button:hover {
    background-color: #333 !important; color: #fff !important;
}
/* Type-specific colors */
button.medication { background-color: #d9534f !important; color: white !important; }
button.therapy { background-color: #5bc0de !important; color: white !important; }
button.diagnostic { background-color: #f0ad4e !important; color: white !important; }
button.planupdate { background-color: #5cb85c !important; color: white !important; }
button.lifestyle { background-color: #337ab7 !important; color: white !important; }
button.logistics { background-color: #9b59b6 !important; color: white !important; }
</style>
"""

st.markdown(light_css if theme_choice == "Light" else dark_css, unsafe_allow_html=True)
st.markdown(button_css, unsafe_allow_html=True)

# --- Header ---
st.image("logo.png", use_container_width=False, width=120)
st.markdown("<div class='big-title'>Elyx Journey — Member 360</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Decisions with Data to Maximize Health</div>", unsafe_allow_html=True)
st.markdown("---")

# ================= Sections =================

# --- Member Profile ---
st.markdown("<div id='member-profile' class='section-title'>🚀 Member Profile</div>", unsafe_allow_html=True)
st.markdown(f"**Member:** {p.get('member','N/A')} | **Age:** {p.get('age','N/A')} | **Occupation:** {p.get('occupation','N/A')}")
st.markdown(f"**Core Goals:** {', '.join(p.get('goals',['N/A']))}")
st.markdown("---")

# --- Key Metrics ---
st.markdown("<div id='key-metrics' class='section-title'>📊 Key Metrics</div>", unsafe_allow_html=True)
cols = st.columns(3)
for i, (k, v) in enumerate(metrics_summary.items()):
    with cols[i % 3]:
        st.markdown(f"<div class='kpi'><div class='label'>{k}</div><div class='value'>{v}</div></div>", unsafe_allow_html=True)
st.markdown("---")

# --- Journey Timeline ---
st.markdown("<div id='journey-timeline' class='section-title'>🗺️ Journey Timeline</div>", unsafe_allow_html=True)
decision_search = st.text_input("🔍 Search decisions...", key="decision_search").lower().strip()
type_emojis = {"Medication": "💊","Therapy": "🧠","Diagnostic Test": "🔬","Plan Update": "📝","Lifestyle Change": "🏋️","Logistics": "✈️"}

# map type → css class
type_classes = {
    "Medication": "medication",
    "Therapy": "therapy",
    "Diagnostic Test": "diagnostic",
    "Plan Update": "planupdate",
    "Lifestyle Change": "lifestyle",
    "Logistics": "logistics"
}

if "timeline_state" not in st.session_state: st.session_state.timeline_state = {}

for dec in sorted(decs, key=lambda d: dt.datetime.fromisoformat(d["date"])):
    searchable_text = f"{dec.get('title','')} {dec.get('type','')} {dec.get('rationale','')} {dec.get('description','')}".lower()
    if decision_search in searchable_text or decision_search == "":
        btn_label = f"{type_emojis.get(dec['type'],'📌')} {dec.get('title','Untitled')} — {dec.get('date','')[:10]} ({dec.get('type','Unknown')})"
        css_class = type_classes.get(dec.get("type"), "")
        st.markdown(
            f"""
            <style>
            div[data-testid="stButton"] button[kind="secondary"] {{
                all: unset;
            }}
            </style>
            """, unsafe_allow_html=True
        )
        if st.button(btn_label, key=f"card_{dec['date']}_{dec['title']}", help=dec.get("type","")):
            st.session_state.timeline_state[dec['title']] = not st.session_state.timeline_state.get(dec['title'], False)
            st.rerun()

        # Inject CSS class dynamically
        st.markdown(
            f"<script>document.querySelector('button[kind=\"secondary\"][aria-label=\"{btn_label}\"]').classList.add('{css_class}');</script>",
            unsafe_allow_html=True
        )

        if st.session_state.timeline_state.get(dec['title'], False):
            st.markdown(f"**Rationale:** {highlight_text(dec.get('rationale','—'), decision_search)}", unsafe_allow_html=True)
            if dec.get("description"):
                st.markdown(highlight_text(dec["description"], decision_search), unsafe_allow_html=True)
            if dec.get("before") or dec.get("after"):
                st.markdown(f"<b>Before:</b> {dec.get('before','—')}<br><b>After:</b> {dec.get('after','—')}", unsafe_allow_html=True)
            related = [m for m in msgs if m['id'] in dec.get('source_message_ids',[])]
            if related:
                st.markdown("**💬 Communication Trail**")
                for m in sorted(related, key=lambda x: x['timestamp']):
                    st.markdown(f"<div class='chat-bubble'><b>{m['speaker']}</b> — {m['timestamp'][:10]}<br>{highlight_text(m['text'], decision_search)}</div>", unsafe_allow_html=True)
st.markdown("---")

# --- Progress Metrics ---
st.markdown("<div id='progress-metrics' class='section-title'>📈 Progress Metrics</div>", unsafe_allow_html=True)
if not metrics.empty:
    min_date, max_date = metrics['date'].min().date(), metrics['date'].max().date()
    if "start_date" not in st.session_state: st.session_state["start_date"] = min_date
    if "end_date" not in st.session_state: st.session_state["end_date"] = max_date

    col1, col2, col3 = st.columns([1,1,0.5])
    with col1: start_date = st.date_input("Start Date", st.session_state["start_date"], min_value=min_date, max_value=max_date)
    with col2: end_date = st.date_input("End Date", st.session_state["end_date"], min_value=min_date, max_value=max_date)
    with col3:
        if st.button("🔄 Reset"):
            st.session_state["start_date"], st.session_state["end_date"] = min_date, max_date
            st.rerun()

    st.session_state["start_date"], st.session_state["end_date"] = start_date, end_date
    filtered = metrics[(metrics['date'].dt.date >= start_date) & (metrics['date'].dt.date <= end_date)]
    if not filtered.empty:
        hours_cols = [c for c in ["doctor_hours","performance_hours","nutrition_hours","pt_hours","ruby_hours"] if c in filtered.columns]
        if hours_cols:
            hours_df = filtered.melt(id_vars="date", value_vars=hours_cols, var_name="Pillar", value_name="Hours")
            chart = alt.Chart(hours_df).mark_area(opacity=0.7).encode(
                x="date:T", y="Hours:Q", color="Pillar:N", tooltip=["date:T","Pillar:N","Hours:Q"]
            ).properties(height=280)
            st.altair_chart(chart, use_container_width=True)
        if "hrv" in filtered.columns:
            line = alt.Chart(filtered).mark_line(point=True).encode(x="date:T", y="hrv:Q", tooltip=["date:T","hrv:Q"]).properties(height=260, title="HRV Trend")
            st.altair_chart(line, use_container_width=True)
    else:
        st.info("No data for this date range.")
else:
    st.info("No metrics available.")
st.markdown("---")

# --- Conversation Log ---
st.markdown("<div id='conversation-log' class='section-title'>💬 Conversation Log</div>", unsafe_allow_html=True)
chat_search = st.text_input("🔎 Search conversations...", key="chat_search").lower()
filtered_chat = [m for m in msgs if chat_search in m['text'].lower() or chat_search == ""]
if filtered_chat:
    for m in reversed(filtered_chat[-50:]):
        st.markdown(f"<div class='chat-bubble'><b>{m['speaker']}</b> — {m['timestamp'][:10]}<br>{highlight_text(m['text'], chat_search)}</div>", unsafe_allow_html=True)
else:
    st.info("No messages found.")





















  




