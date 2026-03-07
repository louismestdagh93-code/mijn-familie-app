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
    # De tijd wordt opgehaald. Pas deze uren aan om te testen!
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

# --- 5. STYLING (AUTOMATISCH DAG/NACHT) ---
if is_nacht():
    bg_color = "#0A0E14"  # Diep nachtblauw
    text_color = "#A0A0A0"
    card_bg = "transparent"
else:
    bg_color = "#FDFCF0"  # Warm wit
    text_color = "#2E7D32"
    card_bg = "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; }}
    h1 {{ color: {text_color}; text-align: center; font-size: 35px; font-family: 'Arial'; }}
    .nacht-boodschap {{ color: white; text-align: center; font-size: 28px; margin-top: 100px; font-family: 'Arial'; }}
    
    /* Foto's en knoppen */
    [data-testid="stImage"] img {{
        border-radius: 20px 20px 0 0 !important;
        border: 4px solid #2E7D32 !important;
        height: 200px !important;
        object-fit: cover;
    }}
    .stButton button {{
        width: 100% !important;
        background-color: #2E7D32 !important;
        color: white !important;
        font-size: 20px !important;
        height: 60px !important;
        border-radius: 0 0 20px 20px !important;
        border: none !important;
        margin-top: -5px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. HET SCHERM ---

if is_nacht():
    # --- NACHT SCHERM ---
    st.markdown("<div class='nacht-boodschap'>🌙<br><br>Het is nacht.<br>Slaap lekker en tot morgen!</div>", unsafe_allow_html=True)
    # Geen foto's of knoppen zichtbaar
else:
    # --- DAG SCHERM (ALBUM) ---
    st.markdown(f"<h1>Familie {familie_naam.capitalize()}</h1>", unsafe_allow_html=True)
    
    cols = st.columns(3) 
    for i, item in enumerate(album_data):
        with cols[i % 3]:
            st.image(item['foto'])
            if st.button(f"Hoor {item['titel']}", key=f"audio_{i}"):
                with open(item['audio'], "rb") as f:
                    audio_base64 = base64.b64encode(f.read()).decode()
                    # HTML hack voor geforceerde audio play
                    audio_html = f'''
                        <audio autoplay>
                            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                        </audio>
                    '''
                    st.markdown(audio_html, unsafe_allow_html=True)
                st.balloons()

# --- 7. BEHEER (Altijd in zijbalk) ---
with st.sidebar:
    st.write(f"Ingelogd: {familie_naam}")
    if st.button("Uitloggen"):
        st.session_state.ingelogd_familie = None
        st.rerun()
    st.divider()
    titel = st.text_input("Naam")
    foto = st.file_uploader("Foto")
    audio = st.file_uploader("Audio")
    if st.button("Opslaan"):
        if foto and audio and titel:
            f_path = os.path.join(data_pad, foto.name)
            a_path = os.path.join(data_pad, audio.name)
            with open(f_path,"wb") as f: f.write(foto.getbuffer())
            with open(a_path,"wb") as f: f.write(audio.getbuffer())
            album_data.append({"titel": titel, "foto": f_path, "audio": a_path})
            with open(DB_FILE, "w") as f: json.dump(album_data, f)
            st.rerun()
