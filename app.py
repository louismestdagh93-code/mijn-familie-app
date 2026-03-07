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

# --- 4. STYLING (GEEN SCROLL & KLIKBARE FOTO) ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; overflow: hidden; }
    
    /* Maak de foto's kleiner zodat ze in het scherm passen zonder scrollen */
    .img-container {
        text-align: center;
        margin-bottom: 10px;
    }
    .img-container img {
        max-height: 35vh; /* Foto neemt max 35% van de schermhoogte in */
        width: auto;
        border-radius: 15px;
        border: 5px solid #2E7D32;
        cursor: pointer;
    }
    
    /* Styling voor de naam onder de foto */
    .naam-label {
        font-size: 24px !important;
        font-weight: bold;
        color: #2E7D32;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    
    /* Verstop de standaard Streamlit knop look en maak hem onzichtbaar over de foto */
    .stButton button {
        height: 45vh !important; /* De knop is even hoog als de foto + label */
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        position: absolute;
        z-index: 10;
        margin-top: -40vh; /* Schuif de onzichtbare knop over de foto */
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. BEHEER (Zijbalk) ---
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
        # Toon de afbeelding
        st.markdown(f'<div class="img-container">', unsafe_allow_html=True)
        st.image(item['foto'])
        st.markdown(f'<p class="naam-label">{item["titel"]}</p></div>', unsafe_allow_html=True)
        
        # De onzichtbare knop die over de afbeelding ligt
        if st.button(f"Play_{i}", key=f"btn_{i}"):
            with open(item['audio'], "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.balloons()
