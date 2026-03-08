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

# --- 3. STYLING (GEFIKST) ---
st.markdown("""
<style>
    .block-container {
        padding: 1rem !important;
    }
    .stApp { background-color: #FDFCF0; }
    header, footer { visibility: hidden; }

    /* Zorg dat de foto's niet te groot worden */
    img {
        width: 100%;
        border-radius: 15px 15px 0 0;
        object-fit: cover;
        height: 150px !important; /* Kortere hoogte zodat er meer op het scherm past */
    }

    .card {
        border: 2px solid #2E7D32;
        border-radius: 15px;
        background-color: white;
        text-align: center;
        margin-bottom: 10px;
    }

    .label {
        background-color: #2E7D32;
        color: white;
        padding: 5px;
        font-weight: bold;
        border-radius: 0 0 12px 12px;
        font-size: 14px;
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
st.markdown(f"<h1 style='text-align:center; color:#2E7D32;'>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)

# We dwingen hier 3 kolommen af voor laptop. 
# Op mobiel schaalt Streamlit dit zelf naar 1 of 2 afhankelijk van de breedte.
cols = st.columns(3)

for i, item in enumerate(album_data):
    if item.get('foto') and os.path.exists(item['foto']):
        with cols[i % 3]:
            # Foto inladen
            with open(item['foto'], "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            
            # HTML voor de kaart
            audio_id = f"aud_{i}"
            
            # De kaart zelf als een knop
            if st.button(f"Klik voor {item['titel']}", key=f"btn_{i}"):
                if item.get('audio') and os.path.exists(item['audio']):
                    with open(item['audio'], "rb") as a:
                        aud_b64 = base64.b64encode(a.read()).decode()
                    st.components.v1.html(f"""
                        <audio autoplay>
                            <source src="data:audio/mp3;base64,{aud_b64}" type="audio/mp3">
                        </audio>
                    """, height=0)

            # De visuele kaart tonen
            st.markdown(f"""
                <div class="card">
                    <img src="data:image/png;base64,{img_b64}">
                    <div class="label">{item['titel']}</div>
                </div>
            """, unsafe_allow_html=True)
