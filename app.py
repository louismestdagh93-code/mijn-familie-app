import streamlit as st
import os
import json
import base64

# --- 1. CONFIG ---
# We forceren de zijbalk en de brede layout
st.set_page_config(
    page_title="Altijd Dichtbij", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

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

# --- 3. STYLING (Extra sterk voor zijbalk) ---
st.markdown("""
<style>
    /* Forceer de zijbalk om zichtbaar te zijn op mobiel */
    [data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
    }
    
    .block-container { padding: 1rem !important; }
    .stApp { background-color: #FDFCF0; }
    header, footer { visibility: hidden; }

    .photo-container {
        position: relative;
        width: 100%;
        border: 3px solid #2E7D32;
        border-radius: 15px;
        overflow: hidden;
        background-color: white;
    }

    .photo-container img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        display: block;
    }

    /* Maak de onzichtbare knop over de hele kaart */
    div.stButton > button {
        height: 220px;
        width: 100%;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        position: absolute;
        top: 0;
        z-index: 99;
    }

    .naam-label {
        background-color: #2E7D32;
        color: white;
        padding: 5px;
        text-align: center;
        font-weight: bold;
        font-family: sans-serif;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. BEHEER (Zijbalk) ---
# We gebruiken st.sidebar expliciet
with st.sidebar:
    st.title("⚙️ Menu")
    vol_level = st.slider("Volume", 0, 100, 80)
    vol_float = vol_level / 100
    
    st.divider()
    if st.button("🗑️ Reset naar basis (Louis & Kimberly)"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()

# --- 5. HET SCHERM ---
st.markdown(f"<h1 style='text-align:center; color:#2E7D32;'>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)

# Layout met kolommen
cols = st.columns(3)

for i, item in enumerate(album_data):
    if item.get('foto') and os.path.exists(item['foto']):
        with cols[i % 3]:
            with open(item['foto'], "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            
            # De kaart
            st.markdown(f"""
                <div class="photo-container">
                    <img src="data:image/png;base64,{img_b64}">
                    <div class="naam-label">{item['titel']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # De audio-knop
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
