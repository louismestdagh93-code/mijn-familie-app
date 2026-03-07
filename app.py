import streamlit as st
import os
import json
import base64

# --- 1. CONFIGURATIE & FAMILIES ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# Hier voeg je handmatig nieuwe families toe:
FAMILIES = {
    "jansen": "jansen2026",
    "pietersen": "pietersen2026",
    "test": "test"
}

if 'ingelogd_familie' not in st.session_state:
    st.session_state.ingelogd_familie = None

# --- 2. LOGIN SCHERM ---
if st.session_state.ingelogd_familie is None:
    st.markdown("<h1 style='text-align: center; color: #2E7D32;'>❤️ Welkom bij Altijd Dichtbij</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align: center;'>Voer het wachtwoord van uw familie in.</p>", unsafe_allow_html=True)
    
    # Centreer het invoerveld een beetje
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Wachtwoord", type="password", key="login_pwd")
        if st.button("Open het Album", use_container_width=True):
            for familie, wachtwoord in FAMILIES.items():
                if pwd == wachtwoord:
                    st.session_state.ingelogd_familie = familie
                    st.rerun()
            st.error("Wachtwoord niet herkend.")
    st.stop()

# --- 3. DATA SETUP ---
familie_naam = st.session_state.ingelogd_familie
data_pad = f"data_{familie_naam}"
if not os.path.exists(data_pad):
    os.makedirs(data_pad)

DB_FILE = os.path.join(data_pad, "database.json")
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        album_data = json.load(f)
else:
    album_data = []

# --- 4. STYLING (HET MOOIE JASJE) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FDFCF0; }}
    h1 {{ color: #2E7D32; font-family: 'Arial'; text-align: center; font-size: 45px; margin-bottom: 30px; }}
    /* De grote knop styling */
    .stButton>button {{
        width: 100%;
        height: 100px !important;
        font-size: 22px !important;
        font-weight: bold;
        border-radius: 20px;
        background-color: #2E7D32 !important;
        color: white !important;
        border: none;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. BEHEER (Zijbalk voor uploads) ---
with st.sidebar:
    st.header(f"Instellingen")
    st.write(f"Ingelogd als: **Fam. {familie_naam.capitalize()}**")
    if st.button("Uitloggen"):
        st.session_state.ingelogd_familie = None
        st.rerun()
    
    st.divider()
    st.subheader("Nieuwe foto toevoegen")
    titel = st.text_input("Wie is dit?")
    foto = st.file_uploader("Kies een foto", type=['jpg','png','jpeg'])
    audio = st.file_uploader("Spraakbericht opnemen/kiezen", type=['mp3','wav'])
    
    if st.button("Opslaan in album", key="save_btn"):
        if foto and audio and titel:
            f_path = os.path.join(data_pad, foto.name)
            a_path = os.path.join(data_pad, audio.name)
            with open(f_path,"wb") as f: f.write(foto.getbuffer())
            with open(a_path,"wb") as f: f.write(audio.getbuffer())
            album_data.append({"titel": titel, "foto": f_path, "audio": a_path})
            with open(DB_FILE, "w") as f: json.dump(album_data, f)
            st.success("Foto toegevoegd!")
            st.rerun()

# --- 6. HET ALBUM (HET OMA-SCHERM) ---
st.markdown(f"<h1>Album van Familie {familie_naam.capitalize()}</h1>", unsafe_allow_html=True)

if not album_data:
    st.info("Dit album is nog leeg. Open het menu links (pijltje) om foto's toe te voegen.")

# We tonen de foto's in een mooi raster
cols = st.columns(2)
for i, item in enumerate(album_data):
    with cols[i % 2]:
        st.image(item['foto'], use_container_width=True)
        # De grote knop direct onder de foto
        if st.button(f"Klik hier voor {item['titel']}", key=f"btn_{i}"):
            with open(item['audio'], "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
                st.markdown(audio_html, unsafe_allow_html=True)
            st.balloons()
