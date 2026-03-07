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

# Laden van foto's
album_data = []
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f: album_data = json.load(f)

# Laden van nacht-instellingen met extra veiligheid
config = {"n_start": 21, "n_eind": 7} # Standaardwaarden
if os.path.exists(CFG_FILE):
    try:
        with open(CFG_FILE, "r") as f:
            saved_cfg = json.load(f)
            # Alleen overschrijven als de juiste sleutels erin staan
            if "n_start" in saved_cfg and "n_eind" in saved_cfg:
                config = saved_cfg
    except:
        pass # Bij fout blijven we bij de standaardwaarden

# --- 4. NACHT CHECK ---
def check_nacht():
    # Tijd ophalen en 1 uur bijtellen voor Belgische tijd (UTC+1)
    nu = (datetime.utcnow() + timedelta(hours=1)).hour
    s = config["n_start"]
    e = config["n_eind"]
    
    if s > e: # Nacht gaat over middernacht heen (bijv. 21u tot 7u)
        return nu >= s or nu < e
    else: # Nacht is binnen de dag (bijv. 13u tot 16u om te testen)
        return s <= nu < e

is_nacht = check_nacht()

# --- 5. STYLING ---
bg = "#0A0E14" if is_nacht else "#FDFCF0"
txt = "#FFFFFF" if is_nacht else "#2E7D32"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; }}
    .stButton button {{ width: 100%; background-color: #2E7D32; color: white; height: 60px; border-radius: 0 0 20px 20px; border: none; }}
    [data-testid="stImage"] img {{ border-radius: 20px 20px 0 0; border: 4px solid #2E7D32; height: 180px; object-fit: cover; }}
    h1, h2, p {{ color: {txt}; text-align: center; }}
</style>
""", unsafe_allow_html=True)

# --- 6. BEHEER (Zijbalk) ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    # We gebruiken de veilige .get() methode om sliders te vullen
    new_s = st.slider("Start nacht", 0, 23, config["n_start"])
    new_e = st.slider("Einde nacht", 0, 23, config["n_eind"])
    
    if st.button("Tijden opslaan"):
        config["n_start"] = new_s
        config["n_eind"] = new_e
        with open(CFG_FILE, "w") as f: json.dump(config, f)
        st.rerun()
        
    st.divider()
    t = st.text_input("Naam")
    f = st.file_uploader("Foto")
    a = st.file_uploader("Audio")
    if st.button("Toevoegen"):
        if f and a and t:
            fp, ap = os.path.join(pad, f.name), os.path.join(pad, a.name)
            with open(fp, "wb") as m: m.write(f.getbuffer())
            with open(ap, "wb") as m: m.write(a.getbuffer())
            album_data.append({"titel": t, "foto": fp, "audio": ap})
            with open(DB_FILE, "w") as m: json.dump(album_data, m)
            st.rerun()

# --- 7. HET SCHERM ---
if is_nacht:
    st.markdown("<div style='padding-top:100px;'><h1 style='font-size:100px;'>🌙</h1><h2>Het is nacht.</h2><p>Slaap lekker!</p></div>", unsafe_allow_html=True)
else:
    # Volledig scherm knop (alleen overdag)
    if st.button("💻 Volledig scherm"):
        st.components.v1.html("<script>window.parent.document.documentElement.requestFullscreen();</script>", height=0)
    
    st.markdown(f"<h1>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, item in enumerate(album_data):
        with cols[i % 3]:
            st.image(item['foto'])
            if st.button(f"Hoor {item['titel']}", key=f"b{i}"):
                with open(item['audio'], "rb") as audio_file:
                    b64 = base64.b64encode(audio_file.read()).decode()
                    st.components.v1.html(f"<audio autoplay><source src='data:audio/mp3;base64,{b64}'></audio>", height=0)
