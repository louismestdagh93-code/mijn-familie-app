import streamlit as st
import base64
import json
import os
from datetime import datetime, timedelta

# 1. CONFIG
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA FUNCTIES
HOUDBAARHEID_DAGEN = 3
def get_file_path(family_id): return f"data_{family_id}.json"
def load_data(family_id):
    path = get_file_path(family_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                data = json.load(f)
                for item in data:
                    if 'views' not in item: item['views'] = 0
                return data
            except: return []
    return []
def save_data(family_id, data):
    with open(get_file_path(family_id), "w") as f: json.dump(data, f)

# 3. CSS (KRITISCHE UPDATES)
st.markdown("""
<style>
    /* Verberg Streamlit rommel */
    header, footer, #MainMenu, .stDeployButton, [data-testid="stSidebarNav"] { visibility: hidden; }
    button[title="View source code"], .viewerBadge_container__1QS1n { display: none !important; }
    
    /* Achtergrond en basis tekst */
    .stApp { background-color: #F7F9F2; font-family: 'Helvetica Neue', Arial, sans-serif; }
    
    /* Titels en labels altijd donkergroen */
    h1, h2, h3, label, p, .stMarkdown { color: #4A6741 !important; font-weight: 600; }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] { background-color: #4A6741; padding: 10px 0; border-radius: 0 0 20px 20px; }
    .stTabs [data-baseweb="tab"] { color: #E8EDDF !important; font-size: 1.2rem !important; }
    .stTabs [aria-selected="true"] { background-color: #F7F9F2 !important; color: #4A6741 !important; border-radius: 10px; }

    /* Foto Kaarten */
    .photo-card { 
        border-radius: 25px; 
        background: #4A6741; 
        margin-bottom: 20px; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.1); 
        overflow: hidden; 
        border: 5px solid #4A6741;
    }
    
    /* Audio knoppen beter leesbaar */
    .stButton > button {
        background-color: #4A6741 !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        width: 100%;
        font-weight: bold !important;
        height: 50px;
    }
</style>
""", unsafe_allow_html=True)

# 4. LOGIN
if 'logged_in' not in st.session_state:
    if "family" in st.query_params:
        st.session_state.logged_in, st.session_state.family_id = True, st.query_params["family"]
    else: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<div style='padding-top:50px; text-align:center;'><h1 style='font-size:3rem;'>🌿 Altijd Dichtbij</h1><p>Verbonden met je familie</p></div>", unsafe_allow_html=True)
    cols = st.columns([1,2,1])
    with cols[1]:
        with st.form("login"):
            fid = st.text_input("Familienaam")
            pw = st.text_input("Code", type="password")
            if st.form_submit_button("Start de tablet"):
                if (fid and pw == "STARTUP2026") or (fid.lower() == "mestdagh" and pw.lower() == "mestdagh"):
                    st.session_state.logged_in, st.session_state.family_id = True, fid
                    st.query_params["family"] = fid
                    st.rerun()
                else: st.error("Oeps! Naam of code klopt niet.")
else:
    fid = st.session_state.family_id
    full_album = load_data(fid)
    nu = datetime.now()
    
    tab1, tab2, tab3 = st.tabs(["👵 OMA", "📤 FAMILIE", "⚙️ BEHEER"])

    with tab1:
        album_oma = [item for item in full_album if (nu - datetime.strptime(item['datum'], "%Y-%m-%d %H:%M:%S")) < timedelta(days=HOUDBAARHEID_DAGEN)]
        
        if not album_oma:
            st.markdown("<h2 style='text-align:center; padding-top:100px;'>Nog geen foto's vandaag...</h2>", unsafe_allow_html=True)
        else:
            grid = st.columns(2)
            for i, item in enumerate(album_oma):
                with grid[i % 2]:
                    # Foto Container
                    st.markdown(f'''
                        <div class="photo-card">
                            <img src="data:image/jpeg;base64,{item["foto"]}" style="width:100%; height:350px; object-fit:cover;">
                            <div style="color:white; text-align:center; padding:15px; font-size:24px; font-weight:bold;">
                                {item["naam"]}
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    # Audio Knop (direct onder de kaart)
                    if item.get('audio'):
                        if st.button(f"🔊 Luister naar {item['naam']}", key=f"aud_{i}"):
                            st.components.v1.html(f'<audio autoplay><source src="data:audio/mp3;base64,{item["audio"]}" type="audio/mp3"></audio>', height=0)
                            item['views'] += 1
                            save_data(fid, full_album)

    with tab2:
        st.header("📤 Stuur iets nieuws")
        with st.form("up", clear_on_submit=True):
            n = st.text_input("Wie is er op de foto?")
            f = st.file_uploader("Kies een foto", type=['jpg','png','jpeg'])
            a = st.audio_input("Spreek een berichtje in")
            if st.form_submit_button("🚀 Verstuur naar Oma"):
                if n and f:
                    f_b64 = base64.b64encode(f.read()).decode()
                    a_b64 = base64.b64encode(a.read()).decode() if a else None
                    full_album.insert(0, {"naam": n, "foto": f_b64, "audio": a_b64, "datum": nu.strftime("%Y-%m-%d %H:%M:%S"), "views": 0})
                    save_data(fid, full_album)
                    st.success("Verzonden! Oma ziet het direct.")
                    st.rerun()

    with tab3:
        st.header("⚙️ Beheer")
        if st.button("🚪 Uitloggen", use_container_width=True):
            st.query_params.clear()
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        for idx, item in enumerate(full_album):
            c1, c2 = st.columns([3,1])
            c1.write(f"🖼️ {item['naam']} ({item['datum']})")
            if c2.button("Wis", key=f"del_{idx}"):
                full_album.pop(idx); save_data(fid, full_album); st.rerun()
