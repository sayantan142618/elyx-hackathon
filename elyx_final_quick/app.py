import json
import pandas as pd
import streamlit as st
from pathlib import Path
import datetime as dt

# --- App Config ---
st.set_page_config(
    page_title="Elyx Journey — Member 360", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Paths ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'

# --- Custom CSS for Branding & Aesthetics ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
    }
    .main {
        background-color: #F8F9FA;
        color: #212529;
    }
    .sidebar .sidebar-content {
        background-color: #E9ECEF;
        color: #495057;
    }
    .big-title {
        font-size: 50px !important;
        text-align: center;
        font-weight: 700;
        color: #1a4f78; /* A professional blue */
        margin-top: -30px;
    }
    .sub-title {
        text-align: center;
        font-size: 20px;
        color: #495057;
        font-weight: 300;
        margin-bottom: 30px;
    }
    .kpi-container {
        padding: 20px;
        border-radius: 10px;
        background-color: #FFFFFF;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-left: 5px solid #1a4f78;
    }
    .kpi-label {
        font-size: 16px;
        color: #6c757d;
        font-weight: 400;
    }
    .kpi-value {
        font-size: 36px;
        font-weight: 700;
        color: #1a4f78;
    }
    h2, h3 {
        color: #1a4f78;
        font-weight: 700;
        border-bottom: 2px solid #ced4da;
        padding-bottom: 5px;
    }
    .chat-bubble {
        background-color: #E9ECEF;
        border-radius: 15px;
        padding: 10px 15px;
        margin: 5px 0;
    }
    .speaker-name {
        font-weight: bold;
        color: #495057;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Load data ---
try:
    msgs = json.load((DATA_DIR / 'messages.json').open())
    decs = json.load((DATA_DIR / 'decisions.json').open())
    p = json.load((DATA_DIR / 'persona.json').open())
    metrics = pd.read_csv(DATA_DIR / 'internal_metrics.csv')
    metrics['date'] = pd.to_datetime(metrics['date'])
    
    # Pre-calculate metrics for a cleaner look
    metrics_summary = {
        "Total Doctor Hours": round(metrics['doctor_hours'].sum(), 1),
        "Total Performance Hours": round(metrics['performance_hours'].sum(), 1),
        "Total Nutrition Hours": round(metrics['nutrition_hours'].sum(), 1),
        "Total Concierge Hours": round(metrics['ruby_hours'].sum(), 1),
        "Total PT Hours": round(metrics['pt_hours'].sum(), 1)
    }

except FileNotFoundError:
    st.error("Data files not found. Please ensure 'messages.json', 'decisions.json', 'persona.json', and 'internal_metrics.csv' are in a 'data' directory.")
    st.stop()

# --- Main App Content ---
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Circle-icons-logo.svg/1024px-Circle-icons-logo.svg.png", width=120)
st.markdown("<div class='big-title'>Elyx Journey — Member 360</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Decisions with Data to Maximize Health</div>", unsafe_allow_html=True)
st.markdown("---")

## 1. Executive Summary & KPIs
with st.container(border=True):
    st.subheader('🚀 Member Profile & Key Metrics')
    st.markdown(f"**Member:** {p['member']} | **Age:** {p['age']} | **Occupation:** {p['occupation']}")
    st.markdown(f"**Core Goals:** {', '.join(p['goals'])}")

    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"<div class='kpi-container'><div class='kpi-label'>Doctor Hours</div><div class='kpi-value'>{metrics_summary['Total Doctor Hours']}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-container'><div class='kpi-label'>Performance Hours</div><div class='kpi-value'>{metrics_summary['Total Performance Hours']}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-container'><div class='kpi-label'>Nutrition Hours</div><div class='kpi-value'>{metrics_summary['Total Nutrition Hours']}</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='kpi-container'><div class='kpi-label'>PT Hours</div><div class='kpi-value'>{metrics_summary['Total PT Hours']}</div></div>", unsafe_allow_html=True)
    with col5:
        st.markdown(f"<div class='kpi-container'><div class='kpi-label'>Concierge Hours</div><div class='kpi-value'>{metrics_summary['Total Concierge Hours']}</div></div>", unsafe_allow_html=True)

st.markdown("---")

## 2. Dynamic Journey Timeline
st.subheader('🗺️ The Journey: Key Decisions Over Time')

# Mapping for decision types to emojis
type_emojis = {
    "Medication": "💊",
    "Therapy": "🧠",
    "Diagnostic Test": "🔬",
    "Plan Update": "📝",
    "Lifestyle Change": "🏋️",
    "Logistics": "✈️"
}

decisions_by_date = sorted(decs, key=lambda d: dt.datetime.fromisoformat(d['date']))

for dec in decisions_by_date:
    emoji = type_emojis.get(dec['type'], "📌")
    
    with st.expander(f"{emoji} **{dec['date'][:10]}** — {dec['title']} ({dec['type']})"):
        st.markdown(f"**Rationale:** {dec['rationale']}")
        
        # This section directly addresses the "Why was this decision made?" requirement.
        st.markdown("---")
        st.markdown(f"### 💬 **Traceback: The Communication Trail**")
        
        # Filter and display relevant messages
        relevant_msgs = [m for m in msgs if m['id'] in dec['source_message_ids']]
        for m in sorted(relevant_msgs, key=lambda m: m['timestamp']):
            st.markdown(
                f"<div class='chat-bubble'><b>{m['speaker']}</b> - {m['timestamp'][:10]}<br>{m['text']}</div>", 
                unsafe_allow_html=True
            )

st.markdown("---")

## 3. Visualized Progress & Metrics
st.subheader('📈 Progress Metrics')
st.caption('Internal team hours spent over the 8-month period.')

# Date range selection
min_date = metrics['date'].min().date()
max_date = metrics['date'].max().date()
start_date, end_date = st.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

filtered_metrics = metrics[
    (metrics['date'].dt.date >= start_date) & 
    (metrics['date'].dt.date <= end_date)
]

# Create a more structured dataframe for the chart
chart_data = filtered_metrics.set_index('date')[
    ['doctor_hours', 'pt_hours', 'ruby_hours', 'performance_hours', 'nutrition_hours']
]

st.line_chart(chart_data)

st.markdown("---")

## 4. The Conversation Log
st.subheader('💬 Full Conversation Log')

# Search and filter functionality for chat messages
chat_search = st.text_input("🔍 Search conversations...", help="Filter messages by keyword.")
filtered_chat = [m for m in msgs if chat_search.lower() in m['text'].lower() or chat_search == ""]

if not filtered_chat:
    st.info("No messages found with that search term.")
else:
    for m in reversed(filtered_chat[-50:]): # Show most recent 50 messages, in reverse order
        st.markdown(f"**{m['speaker']}** <span style='color:#6c757d; font-size:12px;'>— {m['timestamp']}</span>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-bottom: 10px;'>{m['text']}</div>", unsafe_allow_html=True)



