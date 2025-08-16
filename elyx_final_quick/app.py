import json
import pandas as pd
import streamlit as st
from pathlib import Path
import datetime as dt
import re

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

# --- CSS for Styling ---
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

/* Dark Mode */
@media (prefers-color-scheme: dark) {
    [data-testid="stAppViewContainer"] {
        background-color: #1E1E1E !important;
        color: #E0E0E0 !important;
    }
    .kpi-container {
        background-color: #2A2A2A !important;
        border-left-color: #4DA3FF !important;
    }
    .chat-bubble {
        background-color: #2C2C2C !important;
        color: #E0E0E0 !important;
    }
    .big-title, .sub-title, .kpi-value, .kpi-label {
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

/* KPI Grid */
.kpi-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: flex-start;
}

.kpi-container {
    flex: 1 1 calc(33.33% - 20px);
    min-width: 250px;
    padding: 15px;
    border-radius: 10px;
    background-color: #FFFFFF;
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
    border-radius: 15px;
    padding: 12px 15px;
    margin: 10px 0;
    max-width: 100%;
    word-wrap: break-word;
    background-color: #E9ECEF;
    color: #212529;
}

/* Highlight text */
mark {
    background-color: yellow;
    color: black;
    padding: 0 2px;
    border-radius: 2px;
}

/* Expander titles fix (prevent overlap) */
.stExpander > button p {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: calc(100% - 30px) !important;
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
st.subheader('🚀 Member Profile')
st.markdown(f"**Member:** {p.get('member', 'N/A')} | **Age:** {p.get('age', 'N/A')} | **Occupation:** {p.get('occupation', 'N/A')}")
st.markdown(f"**Core Goals:** {', '.join(p.get('goals', ['N/A']))}")

# --- KPI Cards ---
st.markdown("### 📊 Key Metrics")
st.markdown("<div class='kpi-grid'>" + "".join(
    f"<div class='kpi-container'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div></div>"
    for label, value in metrics_summary.items()
) + "</div>", unsafe_allow_html=True)






  




