import streamlit as st
import base64
import json
import os
from datetime import datetime, timedelta

# 1. CONFIG
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# 2. HULPFUNCTIES VOOR DATA
HOUDBAARHEID_DAGEN = 3

def get_file_path(family_id):
    return f"data_{family_id}.json"

def load_and_clean_data(family_id):
    path = get_file_path(family_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            nu = datetime.now()
            gefilterde_data = [
                item for item in data 
                if nu - datetime.strptime(item['datum'], "%Y-%m-%d %H:%M:%S") < timedelta(days=HOUDBAARHEID_DAGEN)
            ]
            if len(gefilterde_data) != len(data):
                save_family_data(family_id, gefilterde_data)
            return gefilterde_data
    return []

def save_family_data(family_id, data):
    with open(get_file_path(family_id), "w") as f:
        json.dump(data, f)

# 3. AUTO-LOGIN LOGICA (Browser Geheugen)
# We gebruiken st.query_params of session_state om de status vast te houden
if 'logged_in' not in st.session_state:
    # Check of er nog een geldige sessie in de URL of het geheugen staat
    if "user" in st.query_params:
        st.session_state.logged_in = True
        st.session_state.family_id = st.query_params["user"]
    else:
        st.session_state.logged_in = False

# 4. CSS (Strak & Groot)
st.markdown("""
<style>
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #FDFCF0; }
    header, footer, #MainMenu {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { background-color: #2E7D32; padding: 0px; }
    .stTabs [data-baseweb="tab"] { height: 80px; color: white !important; font-size: 1.4rem !important; font-weight: bold; flex-grow: 1; }
    .stTabs [aria-selected="true"] { background-color: #FDFCF0 !important; color: #2E7D32 !important; }
    .photo-card { border: 4px solid #2E7D32; border-radius: 20px; background: white; margin: 10px; overflow: hidden; }
    .name-tag { background: #2E7D32; color: white; padding: 15px; font-size: 22px; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 5. UI FLOW
if not st.session_state.logged_in:
    st.markdown("<div style='padding:80px; text-align:center;'><h1>💚 Altijd Dichtbij</h1><p>Log één keer in om te starten</p>", unsafe_allow_html=True)
    with st.form("login"):
        fid = st.text_input("Familienaam").strip()
        code = st.text_input("Code", type="password")
        if st.form_submit_button("Inloggen & Onthouden"):
            if fid and code == "STARTUP2026":
                st.session_state.logged_in = True
                st.session_state.family_id = fid
                # Sla de familienaam op in de URL zodat de browser het onthoudt
                st.query_params["user"] = fid
                st.rerun()
            else:
                st.error("Onjuiste gegevens.")
else:
    fid = st.session_state.family_id
    album = load_and_clean_data(fid)
    
    tab_oma, tab_fam, tab_admin = st.tabs(["👵 OMA", "📤 UPLOAD", "⚙️ ADMIN"])

    with tab_oma:
        if not album:
            st.info("Wacht op nieuwe foto's...")
        else:
            cols = st.columns(2)
            for i, item in enumerate(album):
                with cols[i % 2]:
                    st.markdown(f'<div class="photo-card"><img src="data:image/jpeg;base64,{item["foto"]}" style="width:100%; height:350px; object-fit:cover;"><div class="name-tag">{item["naam"]}</div></div>', unsafe_allow_html=True)
                    if item.get('audio'):
                        if st.button(f"🔊 Luister naar {item['naam']}", key=f"btn_{i}", use_container_width=True):
                            audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{item["audio"]}" type="audio/mp3"></audio><script>document.querySelector("audio").play();</script>'
                            st.components.v1.html(audio_html, height=0)

    with tab_fam:
        with st.form("upload", clear_on_submit=True):
            n = st.text_input("Naam")
            f = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
            audio_data = st.audio_input("Spreek in")
            if st.form_submit_button("🚀 Naar Oma sturen"):
                if n and f:
                    f_b64 = base64.b64encode(f.read()).decode()
                    a_b64 = base64.b64encode(audio_data.read()).decode() if audio_data else None
                    nu_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    album.append({"naam": n, "foto": f_b64, "audio": a_b64, "datum": nu_str})
                    save_family_data(fid, album)
                    st.rerun()

    with tab_admin:
        st.write(f"Ingelogd als: **{fid}**")
        if st.button("🚪 Uitloggen (Wist geheugen)"):
            st.query_params.clear() # Wist de opgeslagen gebruiker in de browser
            st.session_state.logged_in = False
            st.rerun()
