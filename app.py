import streamlit as st
import base64
from io import BytesIO

# ─────────────────────────────────────────────────────────────
# CONFIGURATIE
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Altijd Dichtbij",
    page_icon="📷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# CSS STYLING
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Verberg Streamlit menu en footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Verwijder padding rondom de app */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Achtergrondkleur */
    .stApp {
        background-color: #FDFCF0;
    }
    
    /* Fotokaart styling */
    .photo-card {
        background: white;
        border: 4px solid #2E7D32;
        border-radius: 16px;
        padding: 12px;
        margin: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .photo-card:hover {
        transform: scale(1.03);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        border-color: #1B5E20;
    }
    
    .photo-card:active {
        transform: scale(0.98);
        background: #E8F5E9;
    }
    
    .photo-card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 8px;
    }
    
    .photo-card .name-label {
        text-align: center;
        font-size: 1.4rem;
        font-weight: bold;
        color: #2E7D32;
        margin-top: 10px;
        padding: 8px;
        background: #E8F5E9;
        border-radius: 8px;
    }
    
    /* Titel styling */
    .main-title {
        text-align: center;
        color: #2E7D32;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        font-family: Georgia, serif;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #E8F5E9;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2E7D32 !important;
        color: white !important;
    }
    
    /* Formulier styling */
    .upload-section {
        background: white;
        padding: 20px;
        border-radius: 16px;
        border: 2px solid #2E7D32;
        margin: 10px 0;
    }
    
    /* Success message */
    .success-msg {
        background: #C8E6C9;
        color: #1B5E20;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
    }
    
    /* Audio speler verbergen maar wel laten werken */
    .audio-container {
        margin-top: 10px;
    }
    
    /* Instructie tekst */
    .instruction {
        background: #FFF9C4;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.3rem;
        color: #F57F17;
        margin-bottom: 20px;
    }
    
    /* Knoppen */
    .stButton > button {
        background-color: #2E7D32;
        color: white;
        font-size: 1.1rem;
        padding: 10px 30px;
        border-radius: 10px;
        border: none;
    }
    
    .stButton > button:hover {
        background-color: #1B5E20;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIES
# ─────────────────────────────────────────────────────────────

def get_base64_image(uploaded_file):
    """Converteer uploaded file naar base64 string."""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return base64.b64encode(bytes_data).decode()
    return None

def get_base64_audio(uploaded_file):
    """Converteer audio file naar base64 string."""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return base64.b64encode(bytes_data).decode()
    return None

def create_demo_item():
    """Maak een demo item met een placeholder afbeelding."""
    # Simpele SVG als placeholder
    svg_placeholder = '''
    <svg width="300" height="200" xmlns="[w3.org](http://www.w3.org/2000/svg)">
        <rect width="100%" height="100%" fill="#E8F5E9"/>
        <circle cx="150" cy="80" r="40" fill="#2E7D32"/>
        <circle cx="150" cy="180" r="70" fill="#2E7D32"/>
        <text x="150" y="85" text-anchor="middle" fill="white" font-size="20">👴</text>
    </svg>
    '''
    svg_base64 = base64.b64encode(svg_placeholder.encode()).decode()
    
    return {
        "name": "Demo Opa Jan",
        "photo_base64": svg_base64,
        "photo_type": "svg+xml",
        "audio_base64": None,
        "audio_type": None
    }

# ─────────────────────────────────────────────────────────────
# SESSION STATE INITIALISATIE
# ─────────────────────────────────────────────────────────────
if "album" not in st.session_state:
    st.session_state.album = [create_demo_item()]

if "playing_audio" not in st.session_state:
    st.session_state.playing_audio = None

if "admin_verified" not in st.session_state:
    st.session_state.admin_verified = False

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">📷 Altijd Dichtbij</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Foto\'s en berichten van je dierbaren</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🏠 Oma Portaal", "📤 Familie Upload", "⚙️ Beheer"])

# ─────────────────────────────────────────────────────────────
# TAB 1: OMA PORTAAL
# ─────────────────────────────────────────────────────────────
with tab1:
    if len(st.session_state.album) == 0:
        st.markdown("""
        <div class="instruction">
            📭 Het album is nog leeg.<br>
            Vraag je familie om foto's toe te voegen!
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="instruction">
            👆 Tik op een foto om het bericht te horen!
        </div>
        """, unsafe_allow_html=True)
        
        # Grid van 3 kolommen
        cols = st.columns(3)
        
        for idx, item in enumerate(st.session_state.album):
            col_idx = idx % 3
            
            with cols[col_idx]:
                # Bepaal image source
                if item["photo_type"] == "svg+xml":
                    img_src = f"data:image/svg+xml;base64,{item['photo_base64']}"
                else:
                    img_src = f"data:image/{item['photo_type']};base64,{item['photo_base64']}"
                
                # Unieke key voor elke knop
                button_key = f"photo_btn_{idx}"
                
                # Foto kaart met knop
                st.markdown(f"""
                <div class="photo-card" id="card_{idx}">
                    <img src="{img_src}" alt="{item['name']}">
                    <div class="name-label">{item['name']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Verborgen knop voor interactie
                if st.button(f"▶️ Speel bericht van {item['name']}", key=button_key, use_container_width=True):
                    st.session_state.playing_audio = idx
                
                # Audio afspelen als deze kaart geselecteerd is
                if st.session_state.playing_audio == idx and item["audio_base64"]:
                    audio_src = f"data:audio/{item['audio_type']};base64,{item['audio_base64']}"
                    st.markdown(f"""
                    <div class="audio-container">
                        <audio autoplay controls style="width: 100%;">
                            <source src="{audio_src}" type="audio/{item['audio_type']}">
                        </audio>
                    </div>
                    """, unsafe_allow_html=True)
                    st.success(f"🔊 Nu speelt: bericht van {item['name']}")
                elif st.session_state.playing_audio == idx and not item["audio_base64"]:
                    st.info(f"💬 {item['name']} heeft nog geen audiobericht toegevoegd.")

# ─────────────────────────────────────────────────────────────
# TAB 2: FAMILIE UPLOAD
# ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 👨‍👩‍👧‍👦 Voeg een foto en bericht toe voor Oma")
    
    st.markdown("""
    <div class="upload-section">
    """, unsafe_allow_html=True)
    
    with st.form("upload_form", clear_on_submit=True):
        # Naam invoer
        name = st.text_input(
            "Jouw naam",
            placeholder="Bijv. Kleindochter Emma",
            help="Deze naam wordt onder de foto getoond"
        )
        
        # Foto upload
        photo_file = st.file_uploader(
            "📷 Kies een foto",
            type=["jpg", "jpeg", "png"],
            help="Upload een mooie foto van jezelf"
        )
        
        # Audio upload
        audio_file = st.file_uploader(
            "🎤 Voeg een audiobericht toe (optioneel)",
            type=["mp3", "wav", "m4a"],
            help="Neem een lief berichtje op voor Oma"
        )
        
        # Preview
        if photo_file:
            st.image(photo_file, caption="Preview van je foto", use_column_width=True)
        
        # Submit knop
        submitted = st.form_submit_button("✅ Toevoegen aan Album", use_container_width=True)
        
        if submitted:
            if not name:
                st.error("⚠️ Vul je naam in!")
            elif not photo_file:
                st.error("⚠️ Upload een foto!")
            else:
                # Verwerk de foto
                photo_base64 = get_base64_image(photo_file)
                photo_type = photo_file.type.split("/")[1]  # bijv. "jpeg" of "png"
                
                # Verwerk audio indien aanwezig
                audio_base64 = None
                audio_type = None
                if audio_file:
                    audio_base64 = get_base64_audio(audio_file)
                    audio_type = audio_file.type.split("/")[1]
                
                # Voeg toe aan album
                new_item = {
                    "name": name,
                    "photo_base64": photo_base64,
                    "photo_type": photo_type,
                    "audio_base64": audio_base64,
                    "audio_type": audio_type
                }
                st.session_state.album.append(new_item)
                
                st.markdown("""
                <div class="success-msg">
                    ✅ Gelukt! Je foto is toegevoegd aan het album!<br>
                    Oma kan het nu zien in het Oma Portaal.
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Toon aantal items in album
    st.info(f"📊 Er staan momenteel **{len(st.session_state.album)}** foto's in het album.")

# ─────────────────────────────────────────────────────────────
# TAB 3: BEHEER (ADMIN)
# ─────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 🔐 Beheerderspaneel")
    
    if not st.session_state.admin_verified:
        st.warning("Dit paneel is beveiligd. Voer de beheerderscode in.")
        
        admin_code = st.text_input(
            "Beheerderscode",
            type="password",
            placeholder="Voer de code in..."
        )
        
        if st.button("🔓 Inloggen"):
            if admin_code == "STARTUP2026":
                st.session_state.admin_verified = True
                st.rerun()
            else:
                st.error("❌ Onjuiste code!")
    
    else:
        st.success("✅ Je bent ingelogd als beheerder.")
        
        st.markdown("---")
        
        # Album statistieken
        st.markdown("#### 📊 Album Statistieken")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Totaal foto's", len(st.session_state.album))
        with col2:
            audio_count = sum(1 for item in st.session_state.album if item["audio_base64"])
            st.metric("Met audio", audio_count)
        with col3:
            st.metric("Zonder audio", len(st.session_state.album) - audio_count)
        
        st.markdown("---")
        
        # Album inhoud bekijken
        st.markdown("#### 📋 Album Inhoud")
        if st.session_state.album:
            for idx, item in enumerate(st.session_state.album):
                with st.expander(f"{idx + 1}. {item['name']}"):
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        if item["photo_type"] == "svg+xml":
                            st.markdown("*Demo afbeelding*")
                        else:
                            # Decodeer en toon thumbnail
                            img_data = base64.b64decode(item["photo_base64"])
                            st.image(img_data, width=150)
                    with col_b:
                        st.write(f"**Naam:** {item['name']}")
                        st.write(f"**Audio:** {'✅ Ja' if item['audio_base64'] else '❌ Nee'}")
                        
                        # Individuele verwijderknop
                        if st.button(f"🗑️ Verwijder", key=f"delete_{idx}"):
                            st.session_state.album.pop(idx)
                            st.rerun()
        else:
            st.info("Het album is leeg.")
        
        st.markdown("---")
        
        # Reset functie
        st.markdown("#### ⚠️ Gevarenzone")
        st.warning("Let op: Deze actie kan niet ongedaan gemaakt worden!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Volledig Album Wissen", type="primary"):
                st.session_state.album = []
                st.session_state.playing_audio = None
                st.success("Album is gewist!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset met Demo"):
                st.session_state.album = [create_demo_item()]
                st.session_state.playing_audio = None
                st.success("Album gereset met demo item!")
                st.rerun()
        
        st.markdown("---")
        
        # Uitloggen
        if st.button("🚪 Uitloggen"):
            st.session_state.admin_verified = False
            st.rerun()

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 10px;">
    💚 Altijd Dichtbij — Gemaakt met liefde voor Oma<br>
    <small>Sociale Startup Project 2026</small>
</div>
""", unsafe_allow_html=True)
