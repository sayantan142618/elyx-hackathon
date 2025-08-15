from fastapi import FastAPI
import json,pandas as pd
app=FastAPI()
with open('data/messages.json') as f:MESSAGES=json.load(f)
with open('data/decisions.json') as f:DECISIONS=json.load(f)
with open('data/persona.json') as f:PERSONA=json.load(f)
METRICS=pd.read_csv('data/internal_metrics.csv')
@app.get('/messages')
def messages(): return MESSAGES
@app.get('/decisions')
def decisions(): return DECISIONS
@app.get('/persona')
def persona(): return PERSONA
@app.get('/metrics')
def metrics(): return METRICS.to_dict(orient='records')
