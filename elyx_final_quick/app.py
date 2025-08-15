import json
import pandas as pd
import streamlit as st
from pathlib import Path
import datetime as dt

# --- Paths ---
BASE_DIR = Path(__file__).parent
d = BASE_DIR / 'data'

# --- Load data ---
msgs = json.load((d / 'messages.json').open())
decs = json.load((d / 'decisions.json').open())
p = json.load((d / 'persona.json').open())
metrics = pd.read_csv(d / 'internal_metrics.csv')

# --- App Config ---
st.set_page_config(page_title="Elyx Journey — Member 360", layout="wide")

# --- Banner / Header ---
st.markdown(
    """
    <style>
    .big-title {
        font-size: 50px !important;
        text-align: center;
        font-weight: bold;
        color: #FF4B4B;
    }
    .sub-title {
        text-align: center;
        font-size: 18px;
        color: #BBBBBB;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load local logo file (must be uploaded to repo)
st.image("logo.png", width=120)

st.markdown("<div class='big-title'>Elyx Journey — Member 360</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Decisions with Data</div>", unsafe_allow_html=True)
st.markdown("---")

# --- Sidebar: Persona ---
with st.sidebar:
    st.subheader('Persona')
    st.write(f"**{p['member']}**")
    st.caption(p['snapshot_date'])
    st.write(p['executive_summary'])

# --- KPI Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Doctor Hours", round(metrics['doctor_hours'].sum(), 1))
col2.metric("Performance Hours", round(metrics['performance_hours'].sum(), 1))
col3.metric("Nutrition Hours", round(metrics['nutrition_hours'].sum(), 1))

st.markdown("---")

# --- Decisions & Trace with Search ---
st.subheader('📌 Decisions & Trace')
search_term = st.text_input("🔍 Search decisions...").lower()

for x in decs:
    if search_term in x['title'].lower() or search_term == "":
        with st.expander(f"🗂 {x['title']} • {x['type']} • {x['date'][:10]}"):
            st.write(x['rationale'])
            for m in [m for m in msgs if m['id'] in x['source_message_ids']]:
                st.code(f"{m['timestamp']} • {m['speaker']}: {m['text']}")

st.markdown("---")

# --- Recent Chat ---
st.subheader('💬 Recent Chat')
for m in msgs[-20:]:
    st.markdown(f"> **{m['speaker']}** — {m['timestamp']}\n\n{m['text']}")

st.markdown("---")

# --- Metrics with Date Filter ---
st.subheader('📊 Metrics')
start_date = st.date_input("📅 Start date", dt.date(2025, 1, 1))
end_date = st.date_input("📅 End date", dt.date.today())

filtered = metrics[
    (pd.to_datetime(metrics['date']) >= pd.to_datetime(start_date)) &
    (pd.to_datetime(metrics['date']) <= pd.to_datetime(end_date))
]

st.line_chart(
    filtered.set_index('date')[
        ['doctor_hours', 'pt_hours', 'ruby_hours', 'performance_hours', 'nutrition_hours']
    ]
)


