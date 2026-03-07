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

# --- 4. STYLING (HET GEHEIM VAN DE KLIKBARE FOTO) ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    
    /* Container voor de foto en de knop */
    .foto-box {
        position: relative;
        width: 100%;
        max-width: 300px; /* Forceer een maximale breedte */
        margin: 0 auto;
        text-align: center;
    }

    /* De foto zelf */
    .foto-box img {
        width: 100%;
        height: 250px;
        object-fit: cover;
        border-radius: 20px;
        border: 4px solid #2E7D32;
    }

    /* De knop die ALLES overdekt */
    .stButton button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100% !important;
        height: 250px !important;
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 10;
        cursor: pointer;
    }
    
    /* De naam onder de foto */
    .naam-label {
        font-size: 22px;
        font-weight: bold;
        color: #2E7D32;
        margin-top: 10px;
        margin-bottom: 30px;
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
        # We gebruiken een HTML div om de foto en de knop samen te binden
        st.markdown(f'''
            <div class="foto-box">
                <img src="data:image/png;base64,{base64.b64encode(open(item['foto'], "rb").read()).decode()}">
                <p class="naam-label">{item["titel"]}</p>
            </div>
        ''', unsafe_allow_html=True)
        
        # De knop staat hier direct onder in de code, 
        # maar de CSS zet hem BOVENOP de foto-box div.
        if st.button(" ", key=f"btn_{i}"):
            with open(item['audio'], "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.balloons()
