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

album_data = json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else []
config = json.load(open(CFG_FILE)) if os.path.exists(CFG_FILE) else {"n_start": 21, "n_eind": 7}

# --- 4. NACHT CHECK ---
def check_nacht():
    nu = (datetime.utcnow() + timedelta(hours=1)).hour
    s, e = config.get("n_start", 21), config.get("n_eind", 7)
    return (nu >= s or nu < e) if s > e else (s <= nu < e)

is_nacht = check_nacht()

# --- 5. STYLING ---
bg = "#0A0E14" if is_nacht else "#FDFCF0"
txt = "#FFFFFF" if is_nacht else "#2E7D32"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; }}
    h1, h2, p {{ color: {txt}; text-align: center; font-family: sans-serif; }}
    #MainMenu, footer {{ visibility: hidden; }}
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
    a = st.file_uploader("Geluid")
    if st.button("Opslaan in Album"):
        if t:
            index = next((i for i, item in enumerate(album_data) if item["titel"].lower() == t.lower()), None)
            item = album_data[index] if index is not None else {"titel": t, "foto": "", "audio": ""}
            if f:
                fp = os.path.join(pad, f.name)
                open(fp, "wb").write(f.getbuffer()); item["foto"] = fp
            if a:
                ap = os.path.join(pad, a.name)
                open(ap, "wb").write(a.getbuffer()); item["audio"] = ap
            if index is not None: album_data[index] = item
            else: album_data.append(item)
            json.dump(album_data, open(DB_FILE, "w"))
            st.rerun()
    
    if st.button("Verwijder naam"):
        album_data = [i for i in album_data if i["titel"].lower() != t.lower()]
        json.dump(album_data, open(DB_FILE, "w"))
        st.rerun()

# --- 7. HET SCHERM ---
if is_nacht:
    st.markdown("<div style='padding-top:100px;'><h1 style='font-size:100px;'>🌙</h1><h2>Het is nacht.</h2><p>Slaap lekker!</p></div>", unsafe_allow_html=True)
else:
    st.markdown(f"<h1>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)
    
    # --- CENTRALE AUDIO PLAYER ---
    # We maken één centrale speler die we aansturen via JavaScript
    if "audio_to_play" not in st.session_state:
        st.session_state.audio_to_play = None

    cols = st.columns(3)
    for i, item in enumerate(album_data):
        if item.get('foto') and os.path.exists(item['foto']):
            with cols[i % 3]:
                img_b64 = base64.b64encode(open(item['foto'], "rb").read()).decode()
                
                # De knop zet nu een waarde in de 'sessie' van Streamlit
                if st.button(f"Hoor {item['titel']}", key=f"btn_{i}"):
                    if item.get('audio') and os.path.exists(item['audio']):
                        aud_b64 = base64.b64encode(open(item['audio'], "rb").read()).decode()
                        st.session_state.audio_to_play = aud_b64

                # De visuele kaart
                st.markdown(f"""
                <div style="border:4px solid #2E7D32; border-radius:20px; overflow:hidden; background:white;">
                    <img src="data:image/jpeg;base64,{img_b64}" style="width:100%; height:180px; object-fit:cover; display:block;">
                    <div style="background:#2E7D32; color:white; padding:10px; text-align:center; font-weight:bold;">{item['titel']}</div>
                </div>
                """, unsafe_allow_html=True)

    # Als er iets moet spelen, voegen we de audio-tag éénmalig toe aan de pagina
    if st.session_state.audio_to_play:
        st.components.v1.html(f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{st.session_state.audio_to_play}" type="audio/mp3">
            </audio>
        """, height=0)
        # Reset de speler voor de volgende klik
        st.session_state.audio_to_play = None

    if st.button("💻 Volledig scherm"):
        st.components.v1.html("<script>window.parent.document.documentElement.requestFullscreen();</script>", height=0)
