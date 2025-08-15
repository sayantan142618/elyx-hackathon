import json
import pandas as pd
import streamlit as st
from pathlib import Path

# Always find the 'data' folder relative to this script
BASE_DIR = Path(__file__).parent
d = BASE_DIR / 'data'

# Load data files
msgs = json.load((d / 'messages.json').open())
decs = json.load((d / 'decisions.json').open())
p = json.load((d / 'persona.json').open())
metrics = pd.read_csv(d / 'internal_metrics.csv')

# Streamlit UI
st.title('Elyx Journey — Member 360')

with st.sidebar:
    st.subheader('Persona')
    st.write(f"**{p['member']}**")
    st.caption(p['snapshot_date'])
    st.write(p['executive_summary'])

st.subheader('Decisions & Trace')
for x in decs:
    with st.expander(f"{x['title']} • {x['type']} • {x['date'][:10]}"):
        st.write(x['rationale'])
        for m in [m for m in msgs if m['id'] in x['source_message_ids']]:
            st.code(f"{m['timestamp']} • {m['speaker']}: {m['text']}")

st.subheader('Recent Chat')
for m in msgs[-120:]:
    st.markdown(f"> **{m['speaker']}** — {m['timestamp']}\n\n{m['text']}")

st.subheader('Metrics')
st.line_chart(
    metrics.set_index('date')[
        ['doctor_hours', 'pt_hours', 'ruby_hours', 'performance_hours', 'nutrition_hours']
    ]
)
