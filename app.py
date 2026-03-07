import streamlit as st
import os
import json
import base64
from datetime import datetime

# --- 1. CONFIGURATIE ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

FAMILIES = {
    "jansen": "jansen2026",
    "pietersen": "pietersen2026",
    "test": "test"
}

# --- 2. NACHT-CHECK FUNCTIE ---
def is_nacht():
    nu = datetime.now().hour
    # Nacht is tussen 21:00 en 07:00
    return nu >= 21 or nu < 7

if 'ingelogd_familie' not in st.session_state:
    st.session_state.ingelogd_familie = None

# --- 3. LOGIN ---
if st.session_state.ingelogd_familie is None:
    st.markdown("<h1 style='text-align: center;'>❤️ Welkom</h1>", unsafe_allow_html=True)
    pwd = st.text_input("Wachtwoord", type="password")
    if st.button("Open Album"):
        for familie, wachtwoord in FAMILIES.items():
            if pwd == wachtwoord:
                st.session_state.ingelogd_familie = familie
                st.rerun()
    st.stop()

# --- 4. DATA SETUP ---
familie_naam = st.session_state.ingelogd_familie
data_pad = f"data_{familie_naam}"
if not os.path.exists(data_pad): os.makedirs(data_pad)
DB_FILE = os.path.join(data_pad, "database.json")
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f: album_data = json.load(f)
else: album_data = []

# --- 5. STYLING (DAG EN NACHT) ---
if is_nacht():
    bg_color = "#121212"  # Donkergrijs/zwart
    text_color = "#BB86FC" # Zacht paars
    h1_color = "#FFFFFF"
else:
    bg_color = "#FDFCF0"  # Warm wit
    text_color = "#2E7D32" # Groen
    h1_color = "#2E7D32"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; }}
    h1 {{ color: {h1_color}; text-align: center; font-size: 30px; }}
    .nacht-tekst {{ color: {text_color}; text-align: center; font-size: 24px; margin-top: 50px; }}
    
    [data-testid="stImage"] img {{
        border-radius: 20px 20px 0 0 !important;
        border: 4px solid #2E7D32 !important;
        height: 180px !important;
        width: 100% !important;
        object-fit: cover;
    }}
    .stButton button {{
        width: 100% !important;
        background-color: #2E7D32 !important;
        color: white !important;
        font-size: 18px !important;
        height: 60px !important;
        border-radius: 0 0 20px 20px !important;
        border: none !important;
        margin-top: -5px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. HET SCHERM TONEN ---

if is_nacht():
    # NACHT MODUS
    st.markdown("<h1>🌙 Goedenacht</h1>", unsafe_allow_html=True)
    st.markdown("<p class='nacht-tekst'>Het is tijd om uit te rusten.<br>Morgen zijn alle foto's er weer!</p>", unsafe_allow_html=True)
    # Eventueel een rustig plaatje toevoegen:
    # st.image("https://images.unsplash.com/photo-1502481851512-e9e2529bbbf9", use_column_width=True)
else:
    # DAG MODUS (HET ALBUM)
    st.markdown(f"<h1>Familie {familie_naam.capitalize()}</h1>", unsafe_allow_html=True)
    cols = st.columns(3) 
    for i, item in enumerate(album_data):
        with cols[i % 3]:
            st.image(item['foto'])
            if st.button(f"Hoor {item['titel']}", key=f"audio_btn_{i}"):
                with open(item['audio'], "rb") as f:
                    audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                st.balloons()

# --- 7. BEHEER (Zijbalk blijft altijd bereikbaar voor jou) ---
with st.sidebar:
    if st.button("Uitloggen"):
        st.session_state.ingelogd_familie = None
        st.rerun()
    st.divider()
    st.subheader("Beheer")
    titel = st.text_input("Naam")
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
