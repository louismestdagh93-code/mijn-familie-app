import streamlit as st
import base64
import time

# --- 1. CONFIG ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide")

# --- 2. DATABASE SIMULATIE ---
# We gebruiken session_state zodat de data blijft bestaan zolang je het tabblad niet sluit.
if 'album' not in st.session_state:
    st.session_state.album = []

# --- 3. STYLING (WARME VZW LOOK) ---
st.markdown("""
<style>
    .stApp { background-color: #FDFCF0; }
    .titel { color: #2E7D32; text-align: center; font-family: 'Segoe UI', sans-serif; }
    .card {
        background-color: white;
        border: 2px solid #2E7D32;
        border-radius: 15px;
        padding: 10px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HEADER ---
st.markdown("<h1 class='titel'>💚 Altijd Dichtbij</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Klik op een foto om de boodschap te horen</p>", unsafe_allow_html=True)

# --- 5. MENU (TABS) ---
# We maken twee tabbladen: één voor Oma, één voor de Familie
tab_oma, tab_familie, tab_admin = st.tabs(["👵 Oma Portaal", "👨‍👩‍👧 Familie Upload", "⚙️ Beheer"])

# --- TAB 1: OMA PORTAAL ---
with tab_oma:
    if not st.session_state.album:
        st.info("Er staan nog geen foto's in het album. Ga naar de Familie-tab om iets te sturen!")
    else:
        cols = st.columns(3)
        for i, item in enumerate(st.session_state.album):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                    st.image(item['foto'], use_container_width=True)
                    st.markdown(f"<b>{item['naam']}</b>", unsafe_allow_html=True)
                    
                    if st.button(f"Luister naar {item['naam']} 🔊", key=f"play_{i}"):
                        # Audio afspelen via HTML5
                        audio_base64 = base64.b64encode(item['audio']).decode()
                        audio_html = f"""
                            <audio autoplay>
                                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                            </audio>
                        """
                        st.components.v1.html(audio_html, height=0)
                        st.success(f"Boodschap van {item['naam']} wordt afgespeeld...")
                    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: FAMILIE UPLOAD ---
with tab_familie:
    st.subheader("Stuur een nieuwe herinnering")
    with st.form("upload_form", clear_on_submit=True):
        naam = st.text_input("Wie staat er op de foto? (Naam)")
        foto_file = st.file_uploader("Kies een mooie foto", type=['png', 'jpg', 'jpeg'])
        audio_file = st.file_uploader("Spreek een boodschap in of kies een fragment", type=['mp3', 'wav', 'm4a'])
        
        submit = st.form_submit_button("🚀 Verstuur naar Oma")
        
        if submit:
            if naam and foto_file and audio_file:
                # Bestanden omzetten naar bytes voor opslag
                nieuw_item = {
                    "naam": naam,
                    "foto": foto_file.read(),
                    "audio": audio_file.read()
                }
                st.session_state.album.append(nieuw_item)
                st.success("Gelukt! De foto staat in het album van Oma.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Vergeet niet een naam, foto én audiobestand toe te voegen.")

# --- TAB 3: ADMIN PORTAAL ---
with tab_admin:
    st.subheader("Beheer van de app")
    admin_code = st.text_input("Admin Code", type="password")
    if admin_code == "STARTUP2026":
        st.write(f"Aantal foto's in systeem: {len(st.session_state.album)}")
        if st.button("🗑️ Wis het hele album"):
            st.session_state.album = []
            st.rerun()
    else:
        st.warning("Voer de juiste code in voor admin-functies.")
