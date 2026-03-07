import streamlit as st
import os
import json
import base64

# --- 1. CONFIGURATIE ---
st.set_page_config(page_title="Familie Fotoalbum", layout="wide", initial_sidebar_state="collapsed")

# Map voor data (op Streamlit Cloud is dit tijdelijk, later koppelen we Google Drive)
if not os.path.exists("data"):
    os.makedirs("data")

DB_FILE = "data/database.json"
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        album_data = json.load(f)
else:
    album_data = []

# --- 2. DE LOOK (STYLING) ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    h1 { color: #2E7D32; font-family: 'Arial'; text-align: center; font-size: 50px; }
    
    /* Grote fotoknoppen */
    .stButton>button {
        width: 100%;
        height: 100px;
        font-size: 24px !important;
        border-radius: 20px;
        background-color: white;
        color: #2E7D32;
        border: 5px solid #2E7D32;
    }
    
    /* Terug-knop */
    .terug-knop>button {
        background-color: #D32F2F !important;
        color: white !important;
        height: 80px !important;
    }
    
    .polaroid {
        background: white;
        padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Navigatie state
if 'scherm' not in st.session_state:
    st.session_state.scherm = 'overzicht'
if 'gekozen_item' not in st.session_state:
    st.session_state.gekozen_item = None

# --- 3. BEHEER (Zijbalk) ---
with st.sidebar:
    st.header("⚙️ Beheer")
    ww = st.text_input("Wachtwoord", type="password")
    if ww == "familie2026":
        titel = st.text_input("Naam persoon op foto")
        foto = st.file_uploader("Foto", type=['jpg','png','jpeg'])
        audio = st.file_uploader("Spraakbericht", type=['mp3','wav'])
        if st.button("Opslaan"):
            if foto and audio and titel:
                f_path = os.path.join("data", foto.name)
                a_path = os.path.join("data", audio.name)
                with open(f_path,"wb") as f: f.write(foto.getbuffer())
                with open(a_path,"wb") as f: f.write(audio.getbuffer())
                album_data.append({"titel": titel, "foto": f_path, "audio": a_path})
                with open(DB_FILE, "w") as f: json.dump(album_data, f)
                st.success("Opgeslagen!")
                st.rerun()

# --- 4. HOOFDSCHERM ---
if st.session_state.scherm == 'overzicht':
    st.markdown("<h1>❤️ Tik op een foto</h1>", unsafe_allow_html=True)
    
    if not album_data:
        st.write("Het album is leeg. Open het menu links om foto's toe te voegen.")
    
    cols = st.columns(2)
    for i, item in enumerate(album_data):
        with cols[i % 2]:
            st.markdown('<div class="polaroid">', unsafe_allow_html=True)
            st.image(item['foto'], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button(f"Hoor {item['titel']}", key=f"btn_{i}"):
                st.session_state.gekozen_item = item
                st.session_state.scherm = 'detail'
                st.rerun()

else:
    # DETAIL SCHERM
    item = st.session_state.gekozen_item
    st.image(item['foto'], use_container_width=True)
    
    # Audio Autoplay hack
    with open(item['audio'], "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    
    st.markdown('<div class="terug-knop">', unsafe_allow_html=True)
    if st.button("⬅️ TERUG"):
        st.session_state.scherm = 'overzicht'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)