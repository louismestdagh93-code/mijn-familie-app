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
    # Tijdcorrectie voor België (UTC+1)
    nu = (datetime.utcnow() + timedelta(hours=1)).hour
    s, e = config["n_start"], config["n_eind"]
    if s > e: return nu >= s or nu < e
    else: return s <= nu < e

is_nacht = check_nacht()

# --- 5. STYLING (Klikbare kaarten) ---
bg = "#0A0E14" if is_nacht else "#FDFCF0"
txt = "#FFFFFF" if is_nacht else "#2E7D32"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; }}
    h1, h2, p {{ color: {txt}; text-align: center; }}
    
    /* Verberg standaard Streamlit elementen voor een cleaner uiterlijk */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# --- 6. BEHEER (Zijbalk) ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    config["n_start"] = st.slider("Start nacht", 0, 23, config["n_start"])
    config["n_eind"] = st.slider("Einde nacht", 0, 23, config["n_eind"])
    if st.button("Tijden opslaan"):
        with open(CFG_FILE, "w") as f: json.dump(config, f)
        st.success("Tijden opgeslagen!")
        st.rerun()
    
    st.divider()
    st.subheader("Nieuwe foto")
    titel = st.text_input("Naam persoon")
    foto = st.file_uploader("Kies foto", type=['png', 'jpg', 'jpeg'])
    audio = st.file_uploader("Kies geluid", type=['mp3', 'wav'])
    
    if st.button("Toevoegen aan album"):
        if foto and audio and titel:
            f_path = os.path.join(pad, foto.name)
            a_path = os.path.join(pad, audio.name)
            with open(f_path, "wb") as f: f.write(foto.getbuffer())
            with open(a_path, "wb") as f: f.write(audio.getbuffer())
            album_data.append({"titel": titel, "foto": f_path, "audio": a_path})
            with open(DB_FILE, "w") as f: json.dump(album_data, f)
            st.rerun()

# --- 7. HET SCHERM ---
if is_nacht:
    st.markdown("<div style='padding-top:100px;'><h1 style='font-size:100px;'>🌙</h1><h2>Het is nacht.</h2><p>Slaap lekker!</p></div>", unsafe_allow_html=True)
else:
    st.markdown(f"<h1>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)
    
    # Grid van 3 kolommen
    cols = st.columns(3)
    for i, item in enumerate(album_data):
        with cols[i % 3]:
            # Foto omzetten naar base64 voor HTML
            with open(item['foto'], "rb") as f_img:
                img_b64 = base64.b64encode(f_img.read()).decode()
            with open(item['audio'], "rb") as f_aud:
                aud_b64 = base64.b64encode(f_aud.read()).decode()

            # HTML kaart: Klikken speelt audio af
            st.components.v1.html(f"""
                <div onclick="document.getElementById('aud_{i}').play()" style="
                    cursor: pointer;
                    border: 4px solid #2E7D32;
                    border-radius: 20px;
                    overflow: hidden;
                    background-color: white;
                    text-align: center;
                    font-family: sans-serif;
                ">
                    <img src="data:image/jpeg;base64,{img_b64}" style="width:100%; height:200px; object-fit:cover; display:block;">
                    <div style="background-color:#2E7D32; color:white; padding:15px; font-size:1
