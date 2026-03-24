import streamlit as st
import base64
import json
import os

# 1. CONFIG
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# 2. FUNCTIES VOOR OPSLAG PER GEZIN
def get_file_path(family_id):
    return f"data_{family_id}.json"

def load_family_data(family_id):
    path = get_file_path(family_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_family_data(family_id, data):
    with open(get_file_path(family_id), "w") as f:
        json.dump(data, f)

# 3. SESSIE INITIALISATIE
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'family_id' not in st.session_state:
    st.session_state.family_id = None

# 4. CSS (Zelfde warme look)
st.markdown("""
<style>
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #FDFCF0; }
    header, footer, #MainMenu {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { background-color: #2E7D32; padding: 0px; }
    .stTabs [data-baseweb="tab"] { height: 70px; background-color: #2E7D32; color: white !important; font-size: 1.2rem !important; font-weight: bold; flex-grow: 1; }
    .stTabs [aria-selected="true"] { background-color: #FDFCF0 !important; color: #2E7D32 !important; }
    .photo-card { border: 4px solid #2E7D32; border-radius: 15px; background: white; margin: 10px; text-align: center; overflow: hidden; }
    .name-tag { background: #2E7D32; color: white; padding: 10px; font-size: 20px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 5. INLOGSCHERM OF HOOFDMENU
if not st.session_state.logged_in:
    st.markdown("<div style='padding:50px; text-align:center;'>", unsafe_allow_html=True)
    st.title("💚 Altijd Dichtbij")
    st.subheader("Welkom bij uw familie-portaal")
    
    with st.form("login_form"):
        family_input = st.text_input("Voer uw Familienaam of ID in (geen spaties)", placeholder="bijv: FamiliePeeters")
        access_code = st.text_input("Toegangscode", type="password")
        submit_login = st.form_submit_button("Inloggen")
        
        if submit_login:
            # Voor je demo kun je hier vaste codes instellen
            if family_input and access_code == "STARTUP2026":
                st.session_state.logged_in = True
                st.session_state.family_id = family_input.strip()
                st.rerun()
            else:
                st.error("Ongeldige familienaam of code.")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- HOOFDMENU NA INLOGGEN ---
    family_id = st.session_state.family_id
    album_data = load_family_data(family_id)

    tab_oma, tab_fam, tab_admin = st.tabs([f"👵 OMA ({family_id})", "📤 UPLOAD", "⚙️ ADMIN"])

    with tab_oma:
        if not album_data:
            st.info("Er staan nog geen foto's in jullie familie-album.")
        else:
            cols = st.columns(2)
            for i, item in enumerate(album_data):
                with cols[i % 2]:
                    st.markdown(f'<div class="photo-card"><img src="data:image/jpeg;base64,{item["foto"]}" style="width:100%; height:300px; object-fit:cover;"><div class="name-tag">{item["naam"]}</div></div>', unsafe_allow_html=True)
                    if st.button(f"🔊 Luister naar {item['naam']}", key=f"btn_{i}", use_container_width=True):
                        audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{item["audio"]}" type="audio/mp3"></audio><script>document.querySelector("audio").play();</script>'
                        st.components.v1.html(audio_html, height=0)

    with tab_fam:
        st.subheader(f"Nieuwe foto voor {family_id}")
        with st.form("upload", clear_on_submit=True):
            n = st.text_input("Naam op de foto")
            f = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
            a = st.file_uploader("Audio (MP3)", type=['mp3'])
            if st.form_submit_button("Opslaan in familie-album"):
                if n and f and a:
                    foto_b64 = base64.b64encode(f.read()).decode()
                    audio_b64 = base64.b64encode(a.read()).decode()
                    album_data.append({"naam": n, "foto": foto_b64, "audio": audio_b64})
                    save_family_data(family_id, album_data)
                    st.success("Opgeslagen!")
                    st.rerun()

    with tab_admin:
        if st.button("🚪 Uitloggen"):
            st.session_state.logged_in = False
            st.session_state.family_id = None
            st.rerun()
        if st.button("🗑️ Wis dit familie-album"):
            save_family_data(family_id, [])
            st.rerun()
