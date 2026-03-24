import streamlit as st
import base64
import json
import os
from datetime import datetime, timedelta

# 1. CONFIG
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# 2. HULPFUNCTIES
HOUDBAARHEID_DAGEN = 3

def get_file_path(family_id):
    return f"data_{family_id}.json"

def load_and_clean_data(family_id):
    path = get_file_path(family_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                data = json.load(f)
            except:
                return []
            
            nu = datetime.now()
            gefilterde_data = []
            
            for item in data:
                # FIX voor KeyError: als 'datum' ontbreekt, voeg deze toe
                if 'datum' not in item:
                    item['datum'] = nu.strftime("%Y-%m-%d %H:%M:%S")
                
                try:
                    upload_datum = datetime.strptime(item['datum'], "%Y-%m-%d %H:%M:%S")
                    if nu - upload_datum < timedelta(days=HOUDBAARHEID_DAGEN):
                        gefilterde_data.append(item)
                except:
                    gefilterde_data.append(item) # Bij twijfel: bewaren
            
            return gefilterde_data
    return []

def save_family_data(family_id, data):
    with open(get_file_path(family_id), "w") as f:
        json.dump(data, f)

# 3. ONTHOUDEN INLOG (URL Query Params)
# Dit zorgt dat de tablet ingelogd blijft
query_params = st.query_params
if 'logged_in' not in st.session_state:
    if "family" in query_params:
        st.session_state.logged_in = True
        st.session_state.family_id = query_params["family"]
    else:
        st.session_state.logged_in = False

# 4. CSS (Groot & Groen)
st.markdown("""
<style>
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #FDFCF0; }
    header, footer, #MainMenu {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { background-color: #2E7D32; padding: 0px; }
    .stTabs [data-baseweb="tab"] { height: 80px; color: white !important; font-size: 1.4rem !important; font-weight: bold; flex-grow: 1; border: none; }
    .stTabs [aria-selected="true"] { background-color: #FDFCF0 !important; color: #2E7D32 !important; }
    .photo-card { border: 5px solid #2E7D32; border-radius: 25px; background: white; margin: 15px; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.15); }
    .name-tag { background: #2E7D32; color: white; padding: 15px; font-size: 24px; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 5. UI
if not st.session_state.logged_in:
    st.markdown("<div style='padding:50px; text-align:center;'><h1>💚 Altijd Dichtbij</h1>", unsafe_allow_html=True)
    with st.form("login"):
        fid = st.text_input("Familienaam").strip()
        pw = st.text_input("Code", type="password")
        if st.form_submit_button("Inloggen"):
            if fid and pw == "STARTUP2026":
                st.session_state.logged_in = True
                st.session_state.family_id = fid
                st.query_params["family"] = fid
                st.rerun()
            else:
                st.error("Naam of code onjuist.")
else:
    fid = st.session_state.family_id
    album = load_and_clean_data(fid)
    
    tab_oma, tab_fam, tab_admin = st.tabs(["👵 OMA", "📤 UPLOAD", "⚙️ BEHEER"])

    with tab_oma:
        if not album:
            st.markdown("<h3 style='text-align:center; padding:50px;'>Nog geen foto's aanwezig.</h3>", unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, item in enumerate(album):
                with cols[i % 2]:
                    st.markdown(f'<div class="photo-card"><img src="data:image/jpeg;base64,{item["foto"]}" style="width:100%; height:380px; object-fit:cover;"><div class="name-tag">{item["naam"]}</div></div>', unsafe_allow_html=True)
                    if item.get('audio'):
                        if st.button(f"🔊 Luister naar {item['naam']}", key=f"btn_{i}", use_container_width=True):
                            audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{item["audio"]}" type="audio/mp3"></audio><script>document.querySelector("audio").play();</script>'
                            st.components.v1.html(audio_html, height=0)

    with tab_fam:
        st.markdown("<div style='padding:20px;'>", unsafe_allow_html=True)
        with st.form("upload", clear_on_submit=True):
            n = st.text_input("Wie staat er op de foto?")
            f = st.file_uploader("Kies een foto", type=['jpg', 'jpeg', 'png'])
            a = st.audio_input("Spreek je bericht in")
            if st.form_submit_button("🚀 Naar de tablet sturen"):
                if n and f:
                    f_b64 = base64.b64encode(f.read()).decode()
                    a_b64 = base64.b64encode(a.read()).decode() if a else None
                    datum_nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    album.append({"naam": n, "foto": f_b64, "audio": a_b64, "datum": datum_nu})
                    save_family_data(fid, album)
                    st.success("Verzonden!")
                    st.rerun()

    with tab_admin:
        st.markdown("<div style='padding:20px;'>", unsafe_allow_html=True)
        st.write(f"Sessie voor: **{fid}**")
        for idx, item in enumerate(album):
            st.write(f"🖼️ {item['naam']} (Gepost: {item.get('datum', 'onbekend')})")
            if st.button(f"Verwijder", key=f"del_{idx}"):
                album.pop(idx)
                save_family_data(fid, album)
                st.rerun()
        
        if st.button("🚪 Uitloggen"):
            st.query_params.clear()
            st.session_state.logged_in = False
            st.rerun()
