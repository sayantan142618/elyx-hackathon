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

def safe_percent_change(series):
    try:
        s = pd.to_numeric(series, errors="coerce").dropna()
        if len(s) >= 2 and s.iloc[0] != 0:
            return round((s.iloc[-1] - s.iloc[0]) / abs(s.iloc[0]) * 100.0, 1)
    except Exception:
        pass
    return None

# --- Adaptive CSS (NOTE: wrapped in markdown, so it won't print on-page) ---
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

/* Cards (replacing expanders) */
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

/* Highlighted search */
mark {
  background-color: #FFE066;
  color: #111;
  padding: 0 2px;
  border-radius: 2px;
}

/* Hero summary */
.hero {
  background: linear-gradient(90deg, #1a4f78, #2679b8);
  color: white;
  padding: 16px 18px;
  border-radius: 12px;
  text-align: center;
  font-size: 18px;
  margin: 6px 0 18px 0;
}
.hero b { color: #fffb; }
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

# --- Pre-compute KPI summary ---
def sum_col(name):
    return round(pd.to_numeric(metrics.get(name, pd.Series(0)), errors="coerce").fillna(0).sum(), 1)

metrics_summary = {
    "Doctor Hours": sum_col('doctor_hours'),
    "Performance Hours": sum_col('performance_hours'),
    "Nutrition Hours": sum_col('nutrition_hours'),
    "PT Hours": sum_col('pt_hours'),
    "Concierge Hours": sum_col('ruby_hours')
}

# --- Header ---
st.image("logo.png", use_container_width=False, width=120)
st.markdown("<div class='big-title'>Elyx Journey — Member 360</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Decisions with Data to Maximize Health</div>", unsafe_allow_html=True)
st.markdown("---")

# --- Hero Summary (auto-computes if columns exist) ---
total_hours = sum(metrics_summary.values())
first_date = metrics['date'].min().date() if not metrics.empty else "—"
last_date = metrics['date'].max().date() if not metrics.empty else "—"

hrv_change = safe_percent_change(metrics['hrv']) if 'hrv' in metrics.columns else None
fatigue_change = safe_percent_change(metrics['fatigue']) if 'fatigue' in metrics.columns else None

hero_bits = [f"Over this journey ({first_date} → {last_date}), total engagement: <b>{int(total_hours)} hours</b>."]
if hrv_change is not None:
    hero_bits.append(f"HRV changed by <b>{'+' if hrv_change>=0 else ''}{hrv_change}%</b>.")
if fatigue_change is not None:
    hero_bits.append(f"Fatigue changed by <b>{'+' if fatigue_change>=0 else ''}{fatigue_change}%</b>.")

st.markdown(f"<div class='hero'>📈 {' '.join(hero_bits)}</div>", unsafe_allow_html=True)

# --- Member Profile ---
st.subheader('🚀 Member Profile')
st.markdown(
    f"**Member:** {p.get('member', 'N/A')} | "
    f"**Age:** {p.get('age', 'N/A')} | "
    f"**Occupation:** {p.get('occupation', 'N/A')}"
)
st.markdown(f"**Core Goals:** {', '.join(p.get('goals', ['N/A']))}")

# --- KPI Cards (grid, same look as before) ---
st.markdown("### 📊 Key Metrics")
st.markdown(
    "<div class='kpi-grid'>" +
    "".join(f"<div class='kpi'><div class='label'>{k}</div><div class='value'>{v}</div></div>"
            for k, v in metrics_summary.items()) +
    "</div>",
    unsafe_allow_html=True
)
st.markdown("---")

# --- Controls row: Timeline Search + Pillar Filter ---
left, right = st.columns([2, 1])
with left:
    decision_search = st.text_input("🔍 Search decisions (title, type, or rationale)...").lower().strip()
with right:
    pillar_options = ["All", "Autonomic", "Structural", "Biochemical", "Emotional", "Behavioral"]
    active_pillar = st.selectbox("🧩 Filter by Pillar", pillar_options, index=0)

def pillar_match(dec):
    if active_pillar == "All":
        return True
    return dec.get("pillar", "").strip().lower() == active_pillar.lower()

# --- Decision type mapping ---
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

# --- Timeline (custom cards: NO st.expander → no overlap ever) ---
st.subheader('🗺️ The Journey: Key Decisions')
shown = 0

for dec in sorted(decs, key=lambda d: dt.datetime.fromisoformat(d['date'])):
    searchable_text = f"{dec.get('title','')} {dec.get('type','')} {dec.get('rationale','')}".lower()
    if (decision_search in searchable_text or decision_search == "") and pillar_match(dec):
        emoji = type_emojis.get(dec.get('type',''), '📌')
        color = type_colors.get(dec.get('type',''), '#1a4f78')
        title = dec.get('title', 'Untitled')
        date_str = dec.get('date','')[:10]
        dtype = dec.get('type','Unknown')

        # Card header
        st.markdown(
            f"""
            <div class="card">
              <div class="card-header">
                <div class="card-emoji">{emoji}</div>
                <div class="card-title">{title}</div>
                <div class="card-meta">{date_str}</div>
                <span class="pill" style="background:{color}">{dtype}</span>
              </div>
              <div>
                <b>Rationale:</b> {highlight_text(dec.get('rationale',''), decision_search)}
            """,
            unsafe_allow_html=True
        )

        # Before/After (optional, if present in your JSON)
        before = dec.get('before')
        after = dec.get('after')
        if before or after:
            st.markdown(
                f"""
                <div style="margin-top:10px; padding:10px; border-radius:10px;"
                     class="card">
                    <div><b>Before:</b> {before if before else '—'}</div>
                    <div><b>After:</b> {after if after else '—'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Communication trail
        st.markdown("**💬 Communication Trail**")
        related = [m for m in msgs if m['id'] in dec.get('source_message_ids', [])]
        for m in sorted(related, key=lambda x: x['timestamp']):
            st.markdown(
                f"<div class='chat-bubble'><b>{m['speaker']}</b> — {m['timestamp'][:10]}<br>"
                f"{highlight_text(m['text'], decision_search)}</div>",
                unsafe_allow_html=True
            )

        # Close card body
        st.markdown("</div></div>", unsafe_allow_html=True)
        shown += 1

if shown == 0:
    st.info("No decisions match your filters/search.")

st.markdown("---")

# --- Metrics Visuals (Altair, modern + tooltips) ---
st.subheader('📈 Progress Metrics')
if not metrics.empty:
    min_date, max_date = metrics['date'].min().date(), metrics['date'].max().date()
    start_date, end_date = st.slider(
        "Select Date Range",
        min_value=min_date, max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )
    filtered = metrics[(metrics['date'].dt.date >= start_date) & (metrics['date'].dt.date <= end_date)]

    # Hours distribution (stacked area)
    hours_cols = [c for c in ["doctor_hours","performance_hours","nutrition_hours","pt_hours","ruby_hours"] if c in filtered.columns]
    if hours_cols:
        hours_df = filtered.melt(id_vars="date", value_vars=hours_cols, var_name="Pillar", value_name="Hours")
        area = alt.Chart(hours_df).mark_area().encode(
            x=alt.X('date:T', title=None),
            y=alt.Y('sum(Hours):Q', title='Hours'),
            color=alt.Color('Pillar:N', legend=alt.Legend(title="Pillar")),
            tooltip=[alt.Tooltip('date:T', title='Date'),
                     alt.Tooltip('Pillar:N'),
                     alt.Tooltip('Hours:Q', format='.2f')]
        ).properties(height=280)
        st.altair_chart(area, use_container_width=True)

    # Optional metric (HRV) if exists
    if 'hrv' in filtered.columns:
        hrv_chart = alt.Chart(filtered).mark_line(point=True).encode(
            x=alt.X('date:T', title=None),
            y=alt.Y('hrv:Q', title='HRV'),
            tooltip=[alt.Tooltip('date:T'), alt.Tooltip('hrv:Q')]
        ).properties(height=260, title='HRV Trend')
        st.altair_chart(hrv_chart, use_container_width=True)

else:
    st.info("No metrics available.")

st.markdown("---")

# --- Conversation Log ---
st.subheader('💬 Full Conversation Log')
chat_search = st.text_input("🔎 Search conversations...").lower().strip()
filtered_chat = [m for m in msgs if chat_search in m['text'].lower()] if chat_search else msgs

if filtered_chat:
    for m in reversed(filtered_chat[-50:]):
        st.markdown(
            f"<div class='chat-bubble'><b>{m['speaker']}</b> — {m['timestamp'][:10]}<br>"
            f"{highlight_text(m['text'], chat_search)}</div>",
            unsafe_allow_html=True
        )
else:
    st.info("No messages found.")













  




