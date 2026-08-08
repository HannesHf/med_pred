import streamlit as st
import requests
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import time
import plotly.graph_objects as go
import json

# Pfad-Hack um an den DataLoader zu kommen (nur für die Demo-Daten nötig)
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from src.data.mimic_loader import MimicDataModule
from omegaconf import OmegaConf

API_URL = "http://localhost:8000/predict"

st.set_page_config(page_title="MIMIC-IV basiertes Frühwarnsystem", layout="wide")

st.title("🏥 MIMIC-IV basiertes Frühwarnsystem (Live-Simulation)")

# --- SESSION STATE INIT ---
if "risk_cache" not in st.session_state:
    st.session_state.risk_cache = {}

# --- DATEN LADEN (Nur für Demo-Zwecke) ---
@st.cache_resource
def load_demo_data():
    config_path = root_path / "conf" / "config.yaml"
    cfg = OmegaConf.load(config_path)
    # Cache Pfad anpassen
    cache_dir = root_path.parent / "ML_DATA"
    dm = MimicDataModule(cfg, cache_path=cache_dir)
    dm.setup(stage="fit")
    
    df = dm.val_df.copy()

    df['token_ids'] = df['token_ids'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else list(x))

    if 'chunk_id' in df.columns:
        df = df.sort_values(['subject_id', 'chunk_id'])
        
    # Groupby subject_id und Listen verbinden
    grouped = df.groupby('subject_id', as_index=False).agg({
        'token_ids': 'sum',
        'label': 'max'
    })
    
    # Wir geben eine Liste von Tupeln zurück, die sich wie das Dataset verhält
    return list(zip(grouped['token_ids'], grouped['label']))

try:
    dataset = load_demo_data()
except Exception as e:
    st.error(f"Konnte Daten nicht laden: {e}")
    st.stop()

# --- VOKABULAR LADEN (Für Decoding) ---
vocab_path = root_path.parent / "ML_DATA" / "processed" / "vocab.json"
id2token = {}
if vocab_path.exists():
    with open(vocab_path, "r") as f:
        vocab = json.load(f)
        # Umkehren: ID -> Name
        id2token = {v: k for k, v in vocab.items()}
else:
    st.warning("⚠️ vocab.json nicht gefunden. Events werden als IDs angezeigt.")

# --- SIDEBAR ---
st.sidebar.header("Patienten Auswahl")
patient_idx = st.sidebar.number_input("Patient Index", 0, len(dataset)-1, 0)

# Daten holen
x, y = dataset[patient_idx]
full_sequence = x # Ist jetzt direkt die volle Liste (kein Tensor mehr)
true_label = y    # Ist jetzt direkt der Wert

st.sidebar.markdown(f"**Tatsächliches Outcome:** {'💀 Verstorben' if true_label == 1 else '✅ Überlebt'}")

if st.sidebar.button("🚀 Gesamten Verlauf berechnen"):
    status_text = st.sidebar.empty()
    prog_bar = st.sidebar.progress(0)
    
    for t in range(1, len(full_sequence) + 1):
        k = (patient_idx, t)
        if k not in st.session_state.risk_cache:
            try:
                # API Call für den Schritt t
                resp = requests.post(API_URL, json={"token_ids": full_sequence[:t]})
                if resp.status_code == 200:
                    st.session_state.risk_cache[k] = resp.json()
            except Exception:
                pass
        
        prog_bar.progress(t / len(full_sequence))
        status_text.text(f"Berechne {t}/{len(full_sequence)}")
    
    status_text.empty()
    prog_bar.empty()
    st.rerun()

# --- SIMULATION ---
if "history" not in st.session_state:
    st.session_state.history = []

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Risiko-Verlauf")
    chart_placeholder = st.empty()

with col2:
    st.subheader("Aktueller Status")
    status_placeholder = st.empty()

# --- EVENT DECODER ---
st.subheader("📋 Letzte klinische Ereignisse")
event_placeholder = st.empty()

def get_readable_event(token_id):
    raw = id2token.get(token_id, str(token_id))
    if raw.startswith("DIAG_"): return f"🩺 Diagnose: {raw[5:]}"
    if raw.startswith("MED_"): return f"💊 Medikament: {raw[4:]}"
    if raw.startswith("LAB_"): 
        content = raw[4:]
        if "_abnormal" in content:
            return f"⚠️ Labor: {content.replace('_abnormal', '')} (Abnormal)"
        if "_normal" in content:
            return f"✅ Labor: {content.replace('_normal', '')}"
        return f"🧪 Labor: {content}"
    if raw.startswith("TIME_"): return f"⏱️ Zeit vergangen: {raw[5:]}"
    if raw == "ADM_START": return "🏥 Aufnahme"
    if raw == "ADM_END": return "🏁 Entlassung"
    return f"• {raw}"

# Slider simuliert die Zeit
progress = st.slider("Zeitfortschritt (Anzahl Events)", 1, len(full_sequence), 1)

# API Aufruf
current_seq = full_sequence[:progress]

model_info = {}
cache_key = (patient_idx, progress)

if cache_key in st.session_state.risk_cache:
    data = st.session_state.risk_cache[cache_key]
    risk = data["mortality_risk"]
    model_info = data.get("model_info", {})
else:
    try:
        response = requests.post(API_URL, json={"token_ids": current_seq})
        if response.status_code == 200:
            data = response.json()
            risk = data["mortality_risk"]
            model_info = data.get("model_info", {})
            st.session_state.risk_cache[cache_key] = data
        else:
            st.error("API Fehler")
            risk = 0.0
    except Exception as e:
        st.warning(f"API nicht erreichbar: {e}")
        risk = 0.0

# --- DEBUG INFO IN SIDEBAR ---
if model_info:
    st.sidebar.divider()
    st.sidebar.subheader("ℹ️ Modell-Quelle")
    
    # Wichtigste Info zuerst: Welcher Run ist das?
    if "run_name" in model_info:
        st.sidebar.markdown(f"### 🏷️ `{model_info['run_name']}`")
    if "version" in model_info:
        st.sidebar.caption(f"Registry Version: {model_info['version']}")
        
    st.sidebar.json(model_info)


# --- LOGIK FÜR WARNUNGEN ---
# Wir speichern den Verlauf für den Plot
# (In einer echten App würde das Backend das speichern)
history_df = pd.DataFrame({
    "Event": range(1, progress + 1),
    # Hier vereinfacht: Wir tun so, als hätten wir die Vergangenheit schon berechnet
    # In echt würde man das cachen.
    "Risk": [risk] * progress # Platzhalter für Demo
})

# Delta Berechnung (Veränderung zum letzten Schritt)
last_risk = st.session_state.get("last_risk", 0.0)
delta = risk - last_risk
st.session_state["last_risk"] = risk

# --- EVENT ANZEIGE ---
# Zeige alle Events scrollbar (Neuestes oben)
reversed_events = list(reversed(current_seq))

event_html = '<div style="height: 400px; overflow-y: auto; padding: 5px; border: 1px solid rgba(128,128,128,0.2); border-radius: 5px;">'
event_html += '<ul style="list-style-type: none; padding-left: 0; margin: 0;">'

for i, tid in enumerate(reversed_events): 
    text = get_readable_event(tid)
    style = "padding: 8px; margin-bottom: 4px; border-radius: 4px; font-size: 16px;"
    
    if i == 0:
        style += " font-weight:bold; background-color: rgba(255, 75, 75, 0.15); border-left: 4px solid #ff4b4b;"
        text = f"👉 {text}"
    else:
        style += " border-bottom: 1px solid rgba(128,128,128,0.1);"
        
    event_html += f"<li style='{style}'>{text}</li>"

event_html += "</ul></div>"
event_placeholder.markdown(event_html, unsafe_allow_html=True)

# --- VISUALISIERUNG ---

# 1. Gauge / Ampel
color = "green"
status_msg = "STABIL"

if risk > 0.8 or (delta > 0.15 and risk > 0.3):
    color = "red"
    status_msg = "KRITISCH / RAPIDER ANSTIEG"
elif risk > 0.5:
    color = "orange"
    status_msg = "WARNUNG"

status_placeholder.markdown(f"""
<div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center;">
    <h2 style="color: white; margin:0;">{status_msg}</h2>
    <h1 style="color: white; font-size: 60px; margin:0;">{risk:.1%}</h1>
    <p style="color: white;">Veränderung: {delta:+.1%}</p>
</div>
""", unsafe_allow_html=True)

# 2. Plot
# Historie aus Cache holen
# Wir zeigen ALLE berechneten Punkte für diesen Patienten an (auch Zukunft, falls berechnet)
history_points = []
for t in range(1, len(full_sequence) + 1):
    k = (patient_idx, t)
    if k in st.session_state.risk_cache:
        history_points.append({"x": t, "y": st.session_state.risk_cache[k]["mortality_risk"]})
df_hist = pd.DataFrame(history_points)

fig = go.Figure()
if not df_hist.empty:
    fig.add_trace(go.Scatter(x=df_hist["x"], y=df_hist["y"], mode='lines+markers', name='Verlauf', line=dict(color='lightgray'), marker=dict(size=6, color='gray')))

fig.add_trace(go.Scatter(
    y=[risk], x=[progress], mode='markers', name='Aktuell', 
    marker=dict(size=15, color=color, line=dict(width=2, color='black'))
))
fig.update_layout(
    yaxis_range=[0, 1], 
    title="Mortalitätsrisiko über Zeit",
    xaxis_title="Anzahl klinischer Events"
)
chart_placeholder.plotly_chart(fig, use_container_width=True) # use_container_width ist korrekt in neueren Versionen, 'width' war alt. Falls Warning bleibt, ignorieren oder explizit setzen.
