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

# --- 4. NACHT-CHECK (Gecorrigeerd voor België/Nederland tijd) ---
def check_nacht():
    # Streamlit servers lopen op UTC. Wij tellen er 1 uur bij op voor onze tijdzone.
    nu = (datetime.utcnow() + timedelta(hours=1)).hour
    start = config["nacht_start"]
    eind = config["nacht_eind"]
    
    if start > eind: # Nacht overbrugt middernacht (bijv. 21u tot 7u)
        return nu >= start or nu < eind
    else: # Nacht binnen dezelfde dag (bijv. 0u tot 6u)
        return start <= nu < eind

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
        height: 60px !important;
        border-radius: 0 0 20px 20px !important;
        border: none !important;
    }}
    [data-testid="stImage"] img {{
        border-radius: 20px 20px 0 0 !important;
        border: 4px solid #2E7D32 !important;
        height: 180px !important;
        object-fit: cover;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. BEHEER (Zijbalk) ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    st.subheader("Wanneer is het nacht?")
    config["nacht_start"] = st.slider("Start nacht (uur)", 0, 23, config["nacht_start"])
    config["nacht_eind"] = st.slider("Einde nacht (uur)", 0, 23, config["nacht_eind"])
    
    if st.button("Tijden opslaan"):
        with open(CONFIG_FILE, "w") as f: json.dump(config, f)
        st.success("Opgeslagen!")
        st.rerun()
    
    st.divider()
    st.subheader("Foto Toevoegen")
    titel = st.text_input("Naam")
    foto = st.file_uploader("Kies foto")
    audio = st.file_uploader("Kies geluid")
    if st.button("Opslaan"):
        if foto and audio and titel:
            f_path = os.path.join(data_pad, foto.name)
            a_path = os.path.join(data_pad, audio.name)
            with open(f_path,"wb") as f: f.write(foto.getbuffer())
            with open(a_path,"wb") as f: f.write(audio.getbuffer())
            album_data.append({"titel": titel, "foto": f_path, "audio": a_path})
            with open(DB_FILE, "w") as f: json.dump(album_data, f)
            st.rerun()

    if st.button("Uitloggen"):
        st.session_state.ingelogd_familie = None
        st.rerun()

# --- 7. HET SCHERM ---
if is_nacht_actief:
    st.markdown(f"<div style='text-align:center; padding-top:100px;'> <h1 style='font-size:100px;'>🌙</h1> <h2 style='color:white;'>Het is nacht.</h2> <p style='color:gray;'>Slaap lekker, tot morgen!</p> </div>", unsafe_allow_html=True)
else:
    st.markdown(f"<h1 style='text-align:center; color:#2E7D32;'>Familie {familie_naam.capitalize()}</h1>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, item in enumerate(album_data):
        with cols[i % 3]:
            st.image(item['foto'])
            if st.button(f"Hoor {item['titel']}", key=f"btn_{i}"):
                with open(item['audio'], "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    st.components.v1.html(f"""
                        <audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                    """, height=0)
                st.balloons()
