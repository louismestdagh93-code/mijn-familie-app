import streamlit as st
import base64

# 1. CONFIG (Moet absoluut op regel 1)
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS VOOR LAYOUT & TABS
st.markdown("""
<style>
    /* Verwijder marges voor volledig scherm */
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
    .stApp { background-color: #FDFCF0; }
    header, footer, #MainMenu {visibility: hidden;}

    /* Grote, duidelijke tabs bovenaan */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #2E7D32;
        padding: 0px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 80px;
        background-color: #2E7D32;
        color: white !important;
        font-size: 1.4rem !important;
        font-weight: bold;
        flex-grow: 1;
        border: 1px solid #1B5E20;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FDFCF0 !important;
        color: #2E7D32 !important;
    }

    /* Container voor de klikbare foto */
    .photo-container {
        position: relative;
        border: 5px solid #2E7D32;
        border-radius: 20px;
        overflow: hidden;
        margin: 10px;
        background: white;
    }
    
    .name-tag {
        background: #2E7D32;
        color: white;
        text-align: center;
        padding: 15px;
        font-size: 22px;
        font-weight: bold;
    }

    /* De onzichtbare knop over de volledige kolom */
    div.stButton > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 450px; /* Hoogte van de kaart */
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 10;
    }
</style>
""", unsafe_allow_html=True)

# 3. INITIALISATIE
if 'album' not in st.session_state:
    st.session_state.album = []

# 4. TABS
tab_oma, tab_familie, tab_admin = st.tabs(["👵 OMA PORTAAL", "📤 FAMILIE UPLOAD", "⚙️ ADMIN"])

# --- TAB 1: OMA PORTAAL ---
with tab_oma:
    if not st.session_state.album:
        st.markdown("<h2 style='text-align:center; margin-top:50px;'>Het album is nog leeg.</h2>", unsafe_allow_html=True)
    else:
        # Raster van 2 kolommen voor stabiliteit op tablet
        cols = st.columns(2)
        for i, item in enumerate(st.session_state.album):
            with cols[i % 2]:
                # We gebruiken een container om alles bij elkaar te houden
                with st.container():
                    # De visuele kaart
                    st.markdown('<div class="photo-container">', unsafe_allow_html=True)
                    st.image(item['foto'], use_container_width=True)
                    st.markdown(f'<div class="name-tag">{item["naam"]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # De knop die eroverheen ligt
                    if st.button(f"Play_{i}", key=f"btn_{i}"):
                        # Audio afspelen
                        b64_audio = base64.b64encode(item['audio']).decode()
                        audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>'
                        st.components.v1.html(audio_html, height=0)

# --- TAB 2: FAMILIE UPLOAD ---
with tab_familie:
    st.markdown("<div style='padding:20px;'>", unsafe_allow_html=True)
    st.header("Stuur een herinnering")
    with st.form("upload_form", clear_on_submit=True):
        naam_input = st.text_input("Naam")
        foto_input = st.file_uploader("Kies een foto", type=['jpg', 'jpeg', 'png'])
        audio_input = st.file_uploader("Kies een geluid (.mp3)", type=['mp3', 'wav'])
        
        if st.form_submit_button("🚀 Uploaden"):
            if naam_input and foto_input and audio_input:
                st.session_state.album.append({
                    "naam": naam_input,
                    "foto": foto_input.read(),
                    "audio": audio_input.read()
                })
                st.success("Gelukt!")
                st.rerun()
            else:
                st.error("Vul alle velden in.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 3: ADMIN ---
with tab_admin:
    st.markdown("<div style='padding:20px;'>", unsafe_allow_html=True)
    pw = st.text_input("Code", type="password")
    if pw == "STARTUP2026":
        if st.button("🗑️ Wis het hele album"):
            st.session_state.album = []
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
