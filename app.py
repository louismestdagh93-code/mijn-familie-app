               import streamlit as st
import base64
import time

# ─────────────────────────────────────────────────────────────
# 1. CONFIGURATIE (Full Page Width)
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Altijd Dichtbij",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# 2. GEAVANCEERDE CSS STYLING
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Verberg standaard Streamlit elementen */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp { background-color: #FDFCF0; }

    /* De Tabs (Bovenste balk) duidelijker maken */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: #2E7D32; /* Donkergroen voor contrast */
        padding: 15px;
        border-radius: 15px 15px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #E8F5E9;
        border-radius: 10px;
        color: #2E7D32 !important;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        border: 2px solid #1B5E20;
    }

    /* De Fotokaart */
    .photo-card {
        position: relative;
        background: white;
        border: 4px solid #2E7D32;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        margin-bottom: 25px;
        transition: transform 0.2s;
        height: 450px; /* Hoogte voor tablet */
    }
    
    .photo-card img {
        width: 100%;
        height: 350px; /* Foto neemt grootste deel in */
        object-fit: cover;
    }

    .name-label {
        background-color: #2E7D32;
        color: white;
        text-align: center;
        padding: 20px;
        font-weight: bold;
        font-size: 24px;
        font-family: sans-serif;
    }

    /* DE ONZICHTBARE KNOP TRUC */
    div.stButton > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 450px; /* Matcht hoogte van .photo-card */
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 100;
        cursor: pointer;
    }
    
    div.stButton > button:active {
        background-color: rgba(0,0,0,0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 3. SESSION STATE & DEMO DATA
# ─────────────────────────────────────────────────────────────
if 'album' not in st.session_state:
    st.session_state.album = []

if 'last_played' not in st.session_state:
    st.session_state.last_played = None

# ─────────────────────────────────────────────────────────────
# 4. FUNCTIES
# ─────────────────────────────────────────────────────────────
def play_audio_hidden(audio_bytes):
    """Speelt audio af zonder zichtbare speler."""
    if audio_bytes:
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.components.v1.html(audio_html, height=0)

# ─────────────────────────────────────────────────────────────
# 5. HOOFDAPP
# ─────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center; color:#2E7D32; font-family:serif; font-size: 3rem;'>💚 Altijd Dichtbij</h1>", unsafe_allow_html=True)

tab_oma, tab_familie, tab_admin = st.tabs(["👵 OMA PORTAAL", "👨‍👩‍👧 FAMILIE UPLOAD", "⚙️ BEHEER"])

# --- TAB 1: OMA PORTAAL ---
with tab_oma:
    if not st.session_state.album:
        st.info("Het album is nog leeg. Voeg een foto toe bij 'Familie Upload'.")
    else:
        st.markdown("<p style='text-align:center; font-size:1.5rem;'>Tik op een gezicht om te luisteren</p>", unsafe_allow_html=True)
        
        # Grid layout (2 kolommen op tablet is vaak mooier/groter)
        cols = st.columns(2)
        
        for i, item in enumerate(st.session_state.album):
            with cols[i % 2]:
                # De Kaart Visual
                st.markdown(f"""
                    <div class="photo-card">
                        <img src="data:image/jpeg;base64,{base64.b64encode(item['foto']).decode()}">
                        <div class="name-label">{item['naam']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # De Onzichtbare Knop (ligt bovenop de kaart)
                if st.button(f"Klik_{i}", key=f"btn_{i}"):
                    play_audio_hidden(item['audio'])
                    st.toast(f"Bericht van {item['naam']}...")

# --- TAB 2: FAMILIE UPLOAD ---
with tab_familie:
    st.markdown("### 📤 Stuur iets moois naar Oma")
    with st.container():
        with st.form("upload_form", clear_on_submit=True):
            naam = st.text_input("Wie ben jij?")
            foto = st.file_uploader("Kies een foto", type=['jpg', 'jpeg', 'png'])
            audio = st.file_uploader("Spreek iets in (.mp3)", type=['mp3', 'wav'])
            
            submit = st.form_submit_button("🚀 Naar de tablet sturen")
            
            if submit:
                if naam and foto and audio:
                    st.session_state.album.append({
                        "naam": naam,
                        "foto": foto.read(),
                        "audio": audio.read()
                    })
                    st.success(f"Gelukt! {naam} is toegevoegd.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Vul alle velden in (Naam, Foto en Audio).")

# --- TAB 3: ADMIN ---
with tab_admin:
    st.markdown("### ⚙️ Beheerdersinstellingen")
    wachtwoord = st.text_input("Admin Code", type="password")
    
    if wachtwoord == "STARTUP2026":
        st.write(f"Totaal aantal herinneringen: {len(st.session_state.album)}")
        
        if st.button("🗑️ Volledig album wissen"):
            st.session_state.album = []
            st.success("Album leeggemaakt.")
            st.rerun()
            
        st.markdown("---")
        for idx, item in enumerate(st.session_state.album):
            st.write(f"{idx+1}. {item['naam']}")
            if st.button(f"Verwijder {item['naam']}", key=f"del_{idx}"):
                st.session_state.album.pop(idx)
                st.rerun()
    elif wachtwoord != "":
        st.error("Code onjuist.")
