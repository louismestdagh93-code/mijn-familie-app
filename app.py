import streamlit as st
import os
import json
import base64
from datetime import datetime, timedelta

# --- 1. CONFIGURATIE ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

FAMILIES = {
    "jansen": "jansen2026",
    "pietersen": "pietersen2026",
    "test": "test"
}

if 'ingelogd_familie' not in st.session_state:
    st.session_state.ingelogd_familie = None

# --- 2. LOGIN ---
if st.session_state.ingelogd_familie is None:
    st.markdown("<h1 style='text-align: center;'>❤️ Welkom</h1>", unsafe_allow_html=True)
    pwd = st.text_input("Wachtwoord", type="password")
    if st.button("Open Album"):
        for familie, wachtwoord in FAMILIES.items():
            if pwd == wachtwoord:
                st.session_state.ingelogd_familie = familie
                st.rerun()
    st.stop()

# --- 3. DATA & INSTELLINGEN ---
familie_naam = st.session_state.ingelogd_familie
data_pad = f"data_{familie_naam}"
if not os.path.exists(data_pad): os.makedirs(data_pad)

DB_FILE = os.path.join(data_pad, "database.json")
CONFIG_FILE = os.path.join(data_pad, "config.json")

if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f: album_data = json.load(f)
else: album_data = []

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f: config = json.load(f)
else:
    config = {"nacht_start": 21, "nacht_eind": 7}

# --- 4. NACHT-CHECK ---
def check_nacht():
    nu = (datetime.utcnow() + timedelta(hours=1)).hour
    start = config["nacht_start"]
    eind = config["nacht_eind"]
    if start > eind: return nu >= start or nu < eind
    else: return start <= nu < eind

is_nacht_actief = check_nacht()

# --- 5. STYLING ---
bg_color = "#0A0E14" if is_nacht_actief else "#FDFCF0"
text_color = "#FFFFFF" if is_nacht_actief else "#2E7D32"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; }}
    .stButton button {{
        width: 100% !important;
        background-color: #2E7D32 !important;
        color: white !important;
        height:
