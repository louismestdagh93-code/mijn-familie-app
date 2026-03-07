import streamlit as st
import os
import json
import base64
from datetime import datetime, timedelta

# --- 1. CONFIG ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

FAMILIES = {"jansen": "jansen2026", "pietersen": "pietersen2026", "test": "test"}

if 'ingelogd_familie' not in st.session_state:
    st.session_state.ingelogd_familie = None

# --- 2. LOGIN ---
if st.session_state.ingelogd_familie is None:
    st.markdown("<h1 style='text-align: center;'>❤️ Welkom</h1>", unsafe_allow_html=True)
    pwd = st.text_input("Wachtwoord", type="password")
    if st.button("Open Album"):
        for fam, ww in FAMILIES.items():
            if pwd == ww:
                st.session_state.ingelogd_familie = fam
                st.rerun()
    st.stop()

# --- 3. DATA SETUP ---
fam = st.session_state.ingelogd_familie
pad = f"data_{fam}"
if not os.path.exists(pad): os.makedirs(pad)

DB_FILE = os.path.join(pad, "database.json")
CFG_FILE = os.path.join(pad, "config.json")

album_data = []
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f: album_data = json.load(f)

config = {"n_start": 21, "n_eind": 7}
if os.path.exists(CFG_FILE):
    try:
        with open(CFG_FILE, "r") as f:
            saved_cfg = json.load(f)
            if "n_start" in saved_cfg: config = saved_cfg
    except: pass

# --- 4. NACHT CHECK ---
def check_nacht():
    nu = (datetime.utcnow() + timedelta(hours=1)).hour
    s, e = config["n_start"], config["n_eind"]
    return (nu >= s or nu < e) if s > e else (s <= nu < e)

is_nacht = check_nacht()

# --- 5. STYLING (Foto-klikbaar & Altijd Naam) ---
bg = "#0A0E14" if is_nacht else "#FDFCF0"
txt = "#FFFFFF" if is_nacht else "#2E7D32"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; }}
    
    /* Container voor de foto en tekst */
    .foto-card {{
        cursor: pointer;
        border: 4px solid #2E7D32;
        border-radius: 20px;
        overflow: hidden;
        background-color: white;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }}
    .foto-card:active {{ transform: scale(0.95); }}
    
    .foto-img {{
        width: 100%;
        height: 250px;
        object-fit: cover;
        display: block;
    }}
    
    .naam-balk {{
        background-color: #2E7D32;
        color: white;
        text-align: center;
        padding: 15px;
        font-size: 20px;
        font-weight: bold;
    }}
    
    h1, h2, p {{ color: {txt}; text-align: center; }}
</style>
""", unsafe_allow_html=True)

# --- 6. BEHEER (Zijbalk) ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    config["n_start"] = st.slider("Start nacht", 0, 23, config["n_start"])
    config["n_eind"] = st.slider("Einde nacht", 0, 23, config["n_eind"])
    if st.button("Tijden opslaan"):
        with open(CFG_FILE, "w") as
