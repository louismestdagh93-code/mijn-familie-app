          import streamlit as st
import base64

# 1. CONFIG (MOET ALS EERSTE REGEL)
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# 2. VOLLEDIGE CSS (Layout, Tabs en Klik-Kaarten)
st.markdown("""
<style>
    /* 1. Verwijder alle marges voor een tablet-vullend scherm */
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
    .stApp { background-color: #FDFCF0; }
    header, footer, #MainMenu {visibility: hidden;}

    /* 2. De Bovenste Balk (Tabs) - Zeer duidelijk maken */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #2E7D32; 
        padding: 0px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 80px; /* Lekker groot voor vingers */
        background-color: #2E7D32;
        color: white !important;
        font-weight: bold;
        font-size: 1.5rem !important;
        flex-grow: 1;
        border: 1px solid #1B5E20;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FDFCF0 !important;
        color: #2E7D32 !important;
    }

    /* 3. De Fotokaarten Grid */
    .photo-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr); /* 2 grote fotos naast elkaar op tablet */
        gap: 20px;
        padding: 20px;
    }

    .photo-card {
        position: relative;
        background: white;
        border: 5px solid #2E7D32;
        border-radius: 25px;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        height: 500px;
    }
    
    .photo-card img {
        width: 100%;
        height: 400px;
        object-fit: cover;
    }

    .name-label {
        background: #2E7D32;
        color: white;
        text-align: center;
        padding: 20px;
        font-size: 24px;
        font-weight: bold;
    }

    /* 4. De Onzichtbare Knop die alles klikbaar maakt */
    div.stButton > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 500px; /* Zelfde als kaart */
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 10;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# 3. DATABASE INITIALISATIE
if 'album' not in st.session_state:
    st.session_state.album = []

# 4. AUDIO FUNCTIE
def play_audio(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    st.components.v1.html(audio_html, height=0)

# 5. DE TABS
tab_oma, tab_familie, tab_admin = st.tabs(["👵 OMA PORTAAL", "📤 FAMILIE UPLOAD", "⚙️ ADMIN"])

# --- TAB 1: OMA PORTAAL ---
with tab_oma:
    if not st.session_state.album:
        st.markdown("<h2 style='text-align:center; padding:50px;'>Het album is nog leeg.</h2>", unsafe_allow_html=True)
    else:
        # We maken handmatig een grid met kolommen
        cols = st.columns(2)
        for i, item in enumerate(st.session_state.album):
            with cols[i % 2]:
                # Visual van de kaart
                st.markdown(f"""
                <div class="photo-card">
                    <img src="data:image/jpeg;base64,{base64.b64encode(item['foto']).decode()}">
                    <div class="name-label">{item['naam']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # De onzichtbare knop die de audio triggert
                if st.button(f"Play_{i}", key=f"btn_{i}"):
                    play_audio(item['audio'])

# --- TAB 2: FAMILIE UPLOAD ---
with tab_familie:
    st.markdown("<div style='padding:20px;'>", unsafe_allow_html=True)
    st.header("Stuur een foto naar Oma")
    with st.form("upload_form", clear_on_submit=True):
        naam = st.text_input("Naam op de foto")
        foto = st.file_uploader("Kies een foto", type=['jpg', 'jpeg', 'png'])
        audio = st.file_uploader("Voeg geluid toe (.mp3)", type=['mp3', 'wav'])
        
        if st.form_submit_button("🚀 Versturen naar Tablet"):
            if naam and foto and audio:
                st.session_state.album.append({
                    "naam": naam,
                    "foto": foto.read(),
                    "audio": audio.read()
                })
                st.success("Foto succesvol toegevoegd!")
                st.rerun()
            else:
                st.error("Vul alle velden in aub.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 3: ADMIN ---
with tab_admin:
    st.markdown("<div style='padding:20px;'>", unsafe_allow_html=True)
    code = st.text_input("Beheerderscode", type="password")
    if code == "STARTUP2026":
        st.write(f"Aantal items: {len(st.session_state.album)}")
        if st.button("🗑️ Wis Album"):
            st.session_state.album = []
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
