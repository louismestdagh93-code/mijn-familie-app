import streamlit as st
import base64

# 1. CONFIG
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS VOOR TABLET & TABS
st.markdown("""
<style>
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #FDFCF0; }
    header, footer, #MainMenu {visibility: hidden;}

    /* Grote Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 0px; background-color: #2E7D32; padding: 0px; }
    .stTabs [data-baseweb="tab"] {
        height: 70px;
        background-color: #2E7D32;
        color: white !important;
        font-size: 1.2rem !important;
        font-weight: bold;
        flex-grow: 1;
    }
    .stTabs [aria-selected="true"] { background-color: #FDFCF0 !important; color: #2E7D32 !important; }

    /* Fotokaart Grid */
    .photo-card {
        border: 4px solid #2E7D32;
        border-radius: 15px;
        background: white;
        margin: 10px;
        text-align: center;
        overflow: hidden;
    }
    .name-tag {
        background: #2E7D32;
        color: white;
        padding: 10px;
        font-size: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 3. DATABASE
if 'album' not in st.session_state:
    st.session_state.album = []

# 4. TABS
tab_oma, tab_fam, tab_admin = st.tabs(["👵 OMA PORTAAL", "📤 UPLOAD", "⚙️ ADMIN"])

# --- TAB 1: OMA PORTAAL ---
with tab_oma:
    if not st.session_state.album:
        st.markdown("<h2 style='text-align:center; margin-top:50px;'>Het album is nog leeg.</h2>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, item in enumerate(st.session_state.album):
            with cols[i % 2]:
                # We tonen de foto en de naam
                st.markdown(f"""
                <div class="photo-card">
                    <img src="data:image/jpeg;base64,{base64.b64encode(item['foto']).decode()}" style="width:100%; height:300px; object-fit:cover;">
                    <div class="name-tag">{item['naam']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # De knop: We maken hem groot en duidelijk (niet onzichtbaar voor de test)
                # Als deze werkt, kunnen we hem weer onzichtbaar maken
                if st.button(f"🔊 Luister naar {item['naam']}", key=f"btn_{i}", use_container_width=True):
                    # Directe audio injectie
                    audio_base64 = base64.b64encode(item['audio']).decode()
                    audio_html = f"""
                        <audio autoplay="true" style="display:none;">
                            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                        </audio>
                        <script>
                            var audio = document.querySelector('audio');
                            audio.play().catch(function(error) {{
                                console.log("Audio play failed:", error);
                            }});
                        </script>
                    """
                    st.components.v1.html(audio_html, height=0)

# --- TAB 2: UPLOAD ---
with tab_fam:
    with st.form("upload", clear_on_submit=True):
        n = st.text_input("Naam")
        f = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
        a = st.file_uploader("Audio (MP3)", type=['mp3'])
        if st.form_submit_button("Toevoegen"):
            if n and f and a:
                st.session_state.album.append({"naam": n, "foto": f.read(), "audio": a.read()})
                st.success("Toegevoegd!")
                st.rerun()

# --- TAB 3: ADMIN ---
with tab_admin:
    pw = st.text_input("Code", type="password")
    if pw == "STARTUP2026":
        if st.button("Wis Alles"):
            st.session_state.album = []
            st.rerun()
