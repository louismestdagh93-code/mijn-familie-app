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

# --- 4. STYLING (OM DE FOTO EN KNOP TE BINDEN) ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    
    /* Zorg dat alles dicht op elkaar staat */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 20px;
    }

    /* Foto styling: Iets kleiner voor betere fit */
    [data-testid="stImage"] img {
        border-radius: 20px 20px 0 0 !important;
        border: 4px solid #2E7D32 !important;
        max-height: 200px !important;
        width: 100% !important;
        object-fit: cover;
    }

    /* De knop: Plakt direct onder de foto */
    .stButton button {
        width: 100% !important;
        background-color: #2E7D32 !important;
        color: white !important;
        font-size: 22px !important;
        height: 60px !important;
        border-radius: 0 0 20px 20px !important;
        border: none !important;
        margin-top: -5px !important; /* Trek de knop tegen de foto aan */
    }
    
    h1 { color: #2E7D32; text-align: center; }
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

# Gebruik 3 kolommen voor kleinere foto's die naast elkaar passen
cols = st.columns(3) 
for i, item in enumerate(album_data):
    with cols[i % 3]:
        # Toon de foto
        st.image(item['foto'])
        
        # De knop met de naam die het geluid start
        if st.button(f"Hoor {item['titel']}", key=f"btn_{i}"):
            with open(item['audio'], "rb") as f:
                audio_bytes = f.read()
                # Gebruik de standaard audio player met autoplay
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            st.balloons()
