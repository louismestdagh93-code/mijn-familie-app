import streamlit as st
import base64
import time

# --- 1. CONFIG (Full Page Width) ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DATABASE SIMULATIE ---
if 'album' not in st.session_state:
    # Standaard voorbeeld zodat het scherm niet leeg is
    st.session_state.album = [
        {"naam": "Voorbeeld Louis", "foto": None, "audio": None, "is_demo": True}
    ]

# --- 3. STYLING (GEOPTIMALISEERD VOOR TABLET) ---
st.markdown("""
<style>
    /* Verwijder alle standaard Streamlit marges voor volledig scherm */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    .stApp { background-color: #FDFCF0; }
    
    /* De Fotokaart Styling */
    .photo-card {
        position: relative;
        background-color: white;
        border: 4 icon solid #2E7D32;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    
    .photo-card:active { transform: scale(0.98); }

    .naam-label {
        background-color: #2E7D32;
        color: white;
        text-align: center;
        padding: 15px;
        font-weight: bold;
        font-size: 22px; /* Groter voor tablet */
        font-family: sans-serif;
    }

    /* De MAGIE: Onzichtbare knop over de VOLLEDIGE kaart */
    div.stButton > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 10;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. FUNCTIE VOOR AUDIO ---
def play_audio(audio_bytes):
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
        st.components.v1.html(audio_html, height=0)

# --- 5. TABS ---
tab_oma, tab_familie, tab_admin = st.tabs(["👵 OMA PORTAAL", "👨‍👩‍👧 FAMILIE UPLOAD", "⚙️ BEHEER"])

# --- TAB 1: OMA PORTAAL (HET RASTER) ---
with tab_oma:
    st.markdown("<h1 style='text-align:center; color:#2E7D32;'>Tik op een foto om te luisteren</h1>", unsafe_allow_html=True)
    
    # Grid van 3 kolommen voor tablet (verander naar 2 of 4 indien gewenst)
    cols = st.columns(3)
    
    for i, item in enumerate(st.session_state.album):
        with cols[i % 3]:
            # Container voor de kaart
            st.markdown('<div class="photo-card">', unsafe_allow_html=True)
            
            # Toon foto (of placeholder)
            if item.get("is_demo"):
                st.image("https://www.w3schools.com/howto/img_avatar.png", use_container_width=True)
            else:
                st.image(item['foto'], use_container_width=True)
                
            st.markdown(f'<div class="naam-label">{item["naam"]}</div>', unsafe_allow_html=True)
            
            # De onzichtbare knop
            if st.button(f"Klik_{i}", key=f"btn_{i}"):
                if not item.get("is_demo"):
                    play_audio(item['audio'])
                else:
                    st.warning("Dit is een voorbeeld. Upload een echte foto in de andere tab!")
            
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: FAMILIE UPLOAD ---
with tab_familie:
    st.header("Nieuwe herinnering sturen")
    with st.form("upload_form", clear_on_submit=True):
        naam = st.text_input("Naam van de persoon op de foto")
        foto_file = st.file_uploader("Kies foto", type=['png', 'jpg', 'jpeg'])
        audio_file = st.file_uploader("Kies geluid (.mp3)", type=['mp3', 'wav'])
        
        if st.form_submit_button("🚀 Verstuur naar de tablet"):
            if naam and foto_file and audio_file:
                nieuw_item = {
                    "naam": naam,
                    "foto": foto_file.read(),
                    "audio": audio_file.read(),
                    "is_demo": False
                }
                st.session_state.album.append(nieuw_item)
                st.success("Verstuurd! Kijk nu op het Oma Portaal.")
                time.sleep(1)
                st.rerun()

# --- TAB 3: ADMIN (BEHEER) ---
with tab_admin:
    st.header("Systeembeheer")
    admin_code = st.text_input("Voer de Admin Code in", type="password")
    if admin_code == "STARTUP2026":
        st.write(f"Er staan momenteel {len(st.session_state.album)} items in het album.")
        if st.button("🗑️ Wis alles (Reset voor demo)"):
            st.session_state.album = []
            st.rerun()
    elif admin_code != "":
        st.error("Verkeerde code.")
