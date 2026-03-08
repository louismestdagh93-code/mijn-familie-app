import streamlit as st
import os
import json
import base64

# --- 1. CONFIG ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide")

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
    header, footer { visibility: hidden !important; }

    /* De fotokaart */
    .photo-container {
        position: relative;
        width: 100%;
        border: 3px solid #2E7D32;
        border-radius: 15px;
        overflow: hidden;
        background-color: white;
        margin-bottom: 5px;
    }

    .photo-container img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        display: block;
    }

    /* Naam label onder de foto */
    .naam-label {
        background-color: #2E7D32;
        color: white;
        padding: 8px;
        text-align: center;
        font-weight: bold;
        font-family: sans-serif;
        font-size: 16px;
    }

    /* Onzichtbare knop die de hele kaart bedekt */
    div.stButton > button {
        height: 230px;
        width: 100%;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        position: absolute;
        top: 0;
        z-index: 99;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HET MENU (Bovenaan in plaats van zijbalk) ---
st.markdown(f"<h1 style='text-align:center; color:#2E7D32; font-family:sans-serif;'>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)

# Maak een horizontaal menu
menu_col1, menu_col2, menu_col3 = st.columns([2, 2, 1])

with menu_col1:
    vol_level = st.slider("🔊 Volume", 0, 100, 80)
    vol_float = vol_level / 100

with menu_col3:
    st.write("") # Ruimte voor uitlijning
    if st.button("🗑️ Reset Album"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()

st.divider()

# --- 5. HET ALBUM ---
cols = st.columns(3)

for i, item in enumerate(album_data):
    if item.get('foto') and os.path.exists(item['foto']):
        with cols[i % 3]:
            # Foto inladen
            with open(item['foto'], "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            
            # De kaart tonen
            st.markdown(f"""
                <div class="photo-container">
                    <img src="data:image/png;base64,{img_b64}">
                    <div class="naam-label">{item['titel']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # De klik-actie (onzichtbare knop)
            if st.button(f"Play_{i}", key=f"btn_{i}"):
                if item.get('audio') and os.path.exists(item['audio']):
                    with open(item['audio'], "rb") as a:
                        aud_b64 = base64.b64encode(a.read()).decode()
                    st.components.v1.html(f"""
                        <audio autoplay>
                            <source src="data:audio/mp3;base64,{aud_b64}" type="audio/mp3">
                        </audio>
                        <script>document.querySelector('audio').volume = {vol_float};</script>
                    """, height=0)
