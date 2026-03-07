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

# --- 4. STYLING (FOTO'S ALS KNOPPEN) ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    
    /* Zorg dat de foto's niet te groot worden */
    [data-testid="stImage"] img {
        max-height: 250px;
        width: auto;
        margin: 0 auto;
        display: block;
        border-radius: 15px;
    }

    /* Maak de knop onzichtbaar maar zorg dat hij de hele ruimte vult */
    .stButton button {
        background-color: rgba(0,0,0,0) !important;
        border: 2px solid #2E7D32 !important;
        height: 320px !important;
        width: 100% !important;
        margin-top: -310px !important; /* Schuift de knop OMHOOG over de foto */
        position: relative;
        z-index: 100;
        border-radius: 20px;
    }
    
    .naam-label {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: #2E7D32;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. BEHEER (Zijbalk) ---
with st.sidebar:
    if st.button("Uitloggen"):
        st.session_state.ingelogd_familie = None
        st.rerun()
    titel = st.text_input("Naam persoon")
    foto = st.file_uploader("Upload Foto", type=['jpg','png','jpeg'])
    audio = st.file_uploader("Upload Geluid", type=['mp3','wav'])
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
        # Stap 1: Toon de afbeelding
        st.image(item['foto'])
        # Stap 2: Toon de naam
        st.markdown(f'<p class="naam-label">{item["titel"]}</p>', unsafe_allow_html=True)
        
        # Stap 3: De knop die eroverheen ligt
        # De tekst van de knop is leeg zodat je alleen de foto ziet
        if st.button(" ", key=f"btn_{i}"):
            with open(item['audio'], "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.balloons()
