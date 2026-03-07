import streamlit as st
import os
import json
import base64

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

# --- 3. DATA SETUP ---
familie_naam = st.session_state.ingelogd_familie
data_pad = f"data_{familie_naam}"
if not os.path.exists(data_pad): os.makedirs(data_pad)
DB_FILE = os.path.join(data_pad, "database.json")
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f: album_data = json.load(f)
else: album_data = []

# --- 4. STYLING (GROTE KLIQUBARE BALKEN) ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    
    /* Foto styling */
    [data-testid="stImage"] img {
        border-radius: 20px 20px 0 0;
        border: 4px solid #2E7D32;
        border-bottom: none;
        max-height: 250px;
        object-fit: cover;
    }

    /* De knop direct onder de foto */
    .stButton button {
        width: 100% !important;
        background-color: #2E7D32 !important;
        color: white !important;
        font-size: 24px !important;
        font-weight: bold !important;
        border-radius: 0 0 20px 20px !important;
        height: 70px !important;
        border: none !important;
        margin-top: -10px;
    }
    
    .stButton button:active {
        background-color: #1B5E20 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. BEHEER ---
with st.sidebar:
    if st.button("Uitloggen"):
        st.session_state.ingelogd_familie = None
        st.rerun()
    titel = st.text_input("Wie is dit?")
    foto = st.file_uploader("Foto", type=['jpg','png','jpeg'])
    audio = st.file_uploader("Geluid", type=['mp3','wav'])
    if st.button("Opslaan"):
        if foto and audio and titel:
            f_path = os.path.join(data_pad, foto.name)
            a_path = os.path.join(data_pad, audio.name)
            with open(f_path,"wb") as f: f.write(foto.getbuffer())
            with open(a_path,"wb") as f: f.write(audio.getbuffer())
            album_data.append({"titel": titel, "foto": f_path, "audio": a_path})
            with open(DB_FILE, "w") as f: json.dump(album_data, f)
            st.rerun()

# --- 6. HET ALBUM ---
st.markdown(f"<h1>Familie {familie_naam.capitalize()}</h1>", unsafe_allow_html=True)

cols = st.columns(2)
for i, item in enumerate(album_data):
    with cols[i % 2]:
        # Toon de foto
        st.image(item['foto'], use_container_width=True)
        
        # De knop met de naam die het geluid start
        if st.button(f"Hoor {item['titel']}", key=f"btn_{i}"):
            with open(item['audio'], "rb") as f:
                audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            st.balloons()
