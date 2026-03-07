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

# Veilig laden van data
album_data = json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else []

# VEILIGHEIDSCHECK: Als de key niet bestaat, gebruik standaardwaarden
if os.path.exists(CFG_FILE):
    try:
        config = json.load(open(CFG_FILE))
        if "n_start" not in config: config = {"n_start": 21, "n_eind": 7}
    except:
        config = {"n_start": 21, "n_eind": 7}
else:
    config = {"n_start": 21, "n_eind": 7}

# --- 4. NACHT CHECK ---
def check_nacht():
    nu = (datetime.utcnow() + timedelta(hours=1)).hour
    s, e = config.get("n_start", 21), config.get("n_eind", 7)
    return (nu >= s or nu < e) if s > e else (s <= nu < e)

nacht = check_nacht()

# --- 5. STYLING ---
bg = "#0A0E14" if nacht else "#FDFCF0"
txt = "#FFFFFF" if nacht else "#2E7D32"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; }}
    .stButton button {{ width: 100%; background-color: #2E7D32; color: white; height: 60px; border-radius: 0 0 20px 20px; border: none; }}
    [data-testid="stImage"] img {{ border-radius: 20px 20px 0 0; border: 4px solid #2E7D32; height: 180px; object-fit: cover; }}
</style>
""", unsafe_allow_html=True)

# --- 6. BEHEER (Zijbalk) ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    config["n_start"] = st.slider("Start nacht", 0, 23, config.get("n_start", 21))
    config["n_eind"] = st.slider("Einde nacht", 0, 23, config.get("n_eind", 7))
    if st.button("Opslaan"):
        json.dump(config, open(CFG_FILE, "w"))
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
            json.dump(album_data, open(DB_FILE, "w"))
            st.rerun()

# --- 7. HET SCHERM ---
if nacht:
    st.markdown("<div style='text-align:center; padding-top:100px;'><h1 style='font-size:100px;'>🌙</h1><h2 style='color:white;'>Het is nacht.</h2><p style='color:gray;'>Slaap lekker!</p></div>", unsafe_allow_html=True)
else:
    if st.button("Volledig scherm"):
        st.components.v1.html("<script>window.parent.document.documentElement.requestFullscreen();</script>", height=0)
    st.markdown(f"<h1 style='text-align:center; color:#2E7D32;'>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, item in enumerate(album_data):
        with cols[i % 3]:
            st.image(item['foto'])
            if st.button(f"Hoor {item['titel']}", key=f"b{i}"):
                b64 = base64.b64encode(open(item['audio'], "rb").read()).decode()
                st.components.v1.html(f"<audio autoplay><source src='data:audio/mp3;base64,{b64}'></audio>", height=0)
