import streamlit as st
import os
import json
import base64

# --- 1. CONFIG ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DATA SETUP ---
fam = "test"
pad = f"data_{fam}"
standaard_pad = "standaard"
if not os.path.exists(pad): os.makedirs(pad)

DB_FILE = os.path.join(pad, "database.json")
album_data = json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else []

if not album_data:
    album_data = [
        {"titel": "Louis Mestdagh", "foto": f"{standaard_pad}/Louis.png", "audio": f"{standaard_pad}/louis.mp3"},
        {"titel": "Kimberly Dubois", "foto": f"{standaard_pad}/Kimberly.png", "audio": f"{standaard_pad}/kimberly.mp3"}
    ]

# --- 3. STYLING ---
st.markdown("""
<style>
    .block-container { padding: 1rem !important; }
    .stApp { background-color: #FDFCF0; }
    header, footer { visibility: hidden; }

    /* De container voor de foto en de onzichtbare knop */
    .photo-container {
        position: relative;
        width: 100%;
        border: 3px solid #2E7D32;
        border-radius: 15px;
        overflow: hidden;
        background-color: white;
        margin-bottom: 20px;
    }

    .photo-container img {
        width: 100%;
        height: 200px;
        object-fit: cover; /* Zorgt dat foto het vak vult zonder witte randen */
        display: block;
    }

    /* Styling voor de onzichtbare Streamlit knop */
    .stButton button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: transparent !important;
        border: none !important;
        color: transparent !important;
        z-index: 10;
        cursor: pointer;
    }
    
    .stButton button:hover {
        background-color: rgba(46, 125, 50, 0.1) !important;
    }

    .naam-label {
        background-color: #2E7D32;
        color: white;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        font-family: sans-serif;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. BEHEER (Zijbalk) ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    vol_level = st.slider("Volume", 0, 100, 80)
    vol_float = vol_level / 100
    st.divider()
    if st.button("🗑️ Reset naar basis"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()

# --- 5. HET SCHERM ---
st.markdown(f"<h1 style='text-align:center; color:#2E7D32; font-family:sans-serif;'>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)

# Gebruik 3 kolommen voor laptop, Streamlit stapelt ze op mobiel
cols = st.columns(3)

for i, item in enumerate(album_data):
    if item.get('foto') and os.path.exists(item['foto']):
        with cols[i % 3]:
            # Foto omzetten naar base64
            with open(item['foto'], "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            
            # De "kaarthouder" maken
            st.markdown(f"""
                <div class="photo-container">
                    <img src="data:image/png;base64,{img_b64}">
                    <div class="naam-label">{item['titel']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # De onzichtbare knop die PRECIES over de kaart hierboven valt
            if st.button("", key=f"btn_{i}"):
                if item.get('audio') and os.path.exists(item['audio']):
                    with open(item['audio'], "rb") as a:
                        aud_b64 = base64.b64encode(a.read()).decode()
                    # Audio afspelen via een onzichtbaar HTML element
                    st.components.v1.html(f"""
                        <audio autoplay>
                            <source src="data:audio/mp3;base64,{aud_b64}" type="audio/mp3">
                        </audio>
                        <script>document.querySelector('audio').volume = {vol_float};</script>
                    """, height=0)
