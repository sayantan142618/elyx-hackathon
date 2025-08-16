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

# --- Sidebar Theme Toggle ---
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

# --- CSS (applies based on theme) ---
light_css = """
<style>
html, body, [class*="st-"] {
  font-family: 'Roboto', sans-serif;
  line-height: 1.6;
}
[data-testid="stAppViewContainer"] {
  background-color: #F8F9FA;
  color: #212529;
}
.big-title { font-size: 42px; text-align: center; font-weight: 700; color: #1a4f78; margin-bottom: 5px; }
.sub-title { text-align: center; font-size: 18px; font-weight: 300; margin-bottom: 25px; }
.kpi { background: #FFFFFF; border-left: 5px solid #1a4f78; border-radius: 10px; padding: 16px; }
.chat-bubble { background: #f5f5f5; border-radius: 8px; padding: 10px; margin: 6px 0; }
mark { background: #FFE066; color: #111; padding: 0 2px; border-radius: 2px; }
</style>
"""

dark_css = """
<style>
html, body, [class*="st-"] {
  font-family: 'Roboto', sans-serif;
  line-height: 1.6;
}
[data-testid="stAppViewContainer"] {
  background-color: #121212 !important;
  color: #E0E0E0 !important;
}
.big-title { font-size: 42px; text-align: center; font-weight: 700; color: #4DA3FF; margin-bottom: 5px; }
.sub-title { text-align: center; font-size: 18px; font-weight: 300; margin-bottom: 25px; color: #bbb; }
.kpi { background: #1E1E1E; border-left: 5px solid #4DA3FF; border-radius: 10px; padding: 16px; }
.chat-bubble { background: #2A2A2A; border-radius: 8px; padding: 10px; margin: 6px 0; }
mark { background: #FFB347; color: black; padding: 0 2px; border-radius: 2px; }
</style>
"""

st.markdown(light_css if theme_choice == "Light" else dark_css, unsafe_allow_html=True)

# --- Header ---
st.image("logo.png", use_container_width=False, width=120)
st.markdown("<div class='big-title'>Elyx Journey — Member 360</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Decisions with Data to Maximize Health</div>", unsafe_allow_html=True)
st.markdown("---")

# --- Member Profile ---
st.subheader("🚀 Member Profile")
st.markdown(f"**Member:** {p.get('member','N/A')} | **Age:** {p.get('age','N/A')} | **Occupation:** {p.get('occupation','N/A')}")
st.markdown(f"**Core Goals:** {', '.join(p.get('goals',['N/A']))}")

# --- KPI Cards ---
st.markdown("### 📊 Key Metrics")
cols = st.columns(3)
for i, (k, v) in enumerate(metrics_summary.items()):
    with cols[i % 3]:
        st.metric(k, v)

st.markdown("---")

# --- Timeline Search + Pillar Filter ---
left, right = st.columns([2, 1])
with left:
    decision_search = st.text_input("🔍 Search decisions...", key="decision_search").lower().strip()
with right:
    pillar_options = ["All", "Autonomic", "Structural", "Biochemical", "Emotional", "Behavioral"]
    active_pillar = st.selectbox("🧩 Filter by Pillar", pillar_options, index=0)

def pillar_match(dec):
    if active_pillar == "All":
        return True
    return dec.get("pillar", "").strip().lower() == active_pillar.lower()

# --- Decision Types ---
type_emojis = {
    "Medication": "💊", "Therapy": "🧠", "Diagnostic Test": "🔬",
    "Plan Update": "📝", "Lifestyle Change": "🏋️", "Logistics": "✈️"
}

# --- Timeline Cards ---
st.subheader("🗺️ The Journey: Key Decisions")
if "timeline_state" not in st.session_state:
    st.session_state.timeline_state = {}

for dec in sorted(decs, key=lambda d: dt.datetime.fromisoformat(d["date"])):
    searchable_text = f"{dec.get('title','')} {dec.get('type','')} {dec.get('rationale','')} {dec.get('description','')}".lower()
    if (decision_search in searchable_text or decision_search == "") and pillar_match(dec):
        if st.button(
            f"{type_emojis.get(dec['type'],'📌')} {dec.get('title','Untitled')} — {dec.get('date','')[:10]} ({dec.get('type','Unknown')})",
            key=f"card_{dec['date']}_{dec['title']}"
        ):
            st.session_state.timeline_state[dec['title']] = not st.session_state.timeline_state.get(dec['title'], False)
            st.rerun()

        if st.session_state.timeline_state.get(dec['title'], False):
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"**Rationale:** {highlight_text(dec.get('rationale','—'), decision_search)}", unsafe_allow_html=True)
            if dec.get("description"):
                st.markdown(highlight_text(dec["description"], decision_search), unsafe_allow_html=True)

            if dec.get("before") or dec.get("after"):
                st.markdown(
                    f"<div style='margin-top:10px; padding:10px; border-radius:10px; background:#f8f9fa;'>"
                    f"<b>Before:</b> {dec.get('before','—')}<br><b>After:</b> {dec.get('after','—')}</div>",
                    unsafe_allow_html=True
                )

            related = [m for m in msgs if m['id'] in dec.get('source_message_ids',[])]
            if related:
                st.markdown("**💬 Communication Trail**")
                for m in sorted(related, key=lambda x: x['timestamp']):
                    st.markdown(
                        f"<div class='chat-bubble'><b>{m['speaker']}</b> — {m['timestamp'][:10]}<br>"
                        f"{highlight_text(m['text'], decision_search)}</div>",
                        unsafe_allow_html=True
                    )
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --- Progress Metrics ---
st.subheader("📈 Progress Metrics")
if not metrics.empty:
    min_date, max_date = metrics['date'].min().date(), metrics['date'].max().date()

    # Persistent state for date selection
    if "start_date" not in st.session_state: st.session_state["start_date"] = min_date
    if "end_date" not in st.session_state: st.session_state["end_date"] = max_date

    col1, col2, col3 = st.columns([1,1,0.5])
    with col1:
        start_date = st.date_input("Start Date", st.session_state["start_date"], min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End Date", st.session_state["end_date"], min_value=min_date, max_value=max_date)
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
                x="date:T", y="Hours:Q", color="Pillar:N",
                tooltip=["date:T","Pillar:N","Hours:Q"]
            ).properties(height=280)
            st.altair_chart(chart, use_container_width=True)

        if "hrv" in filtered.columns:
            line = alt.Chart(filtered).mark_line(point=True).encode(
                x="date:T", y="hrv:Q", tooltip=["date:T","hrv:Q"]
            ).properties(height=260, title="HRV Trend")
            st.altair_chart(line, use_container_width=True)
    else:
        st.info("No data for this date range.")
else:
    st.info("No metrics available.")

st.markdown("---")

# --- Conversation Log ---
st.subheader("💬 Full Conversation Log")
chat_search = st.text_input("🔍 Search conversations...", key="chat_search").lower()
filtered_chat = [m for m in msgs if chat_search in m['text'].lower() or chat_search == ""]

if filtered_chat:
    for m in reversed(filtered_chat[-50:]):
        st.markdown(
            f"<div class='chat-bubble'><b>{m['speaker']}</b> — {m['timestamp'][:10]}<br>{highlight_text(m['text'], chat_search)}</div>",
            unsafe_allow_html=True
        )
else:
    st.info("No messages found.")





















  




