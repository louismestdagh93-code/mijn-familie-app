import streamlit as st
import base64
import json
import os
from datetime import datetime, timedelta

# 1. CONFIG
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA FUNCTIES
HOUDBAARHEID_DAGEN = 3

def get_file_path(family_id):
    return f"data_{family_id}.json"

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
    with open(get_file_path(family_id), "w") as f:
        json.dump(data, f)

# 3. LOGIN LOGICA
if 'logged_in' not in st.session_state:
    if "family" in st.query_params:
        st.session_state.logged_in, st.session_state.family_id = True, st.query_params["family"]
    else: st.session_state.logged_in = False

# 4. CSS (MAXIMAAL CONTRAST & LEESBAARHEID)
st.markdown("""
<style>
    header, footer, #MainMenu { visibility: hidden; }
    .stApp { background-color: #F7F9F2; }
    
    /* FORCEER PIKZWARTE TEKST VOOR CONTRAST */
    h1, h2, h3, label, p, span, div, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }
    
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    /* Tabs styling - Donkergroen met wit */
    .stTabs [data-baseweb="tab-list"] { background-color: #1A3317; padding: 15px 0; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-size: 1.8rem !important; font-weight: 900; }
    .stTabs [aria-selected="true"] { background-color: #F7F9F2 !important; color: #1A3317 !important; border-radius: 10px; }

    /* Foto Kaarten - Zwart frame */
    .photo-card { 
        border-radius: 25px; 
        background: #000000; 
        margin-top: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.4); 
        overflow: hidden; 
        border: 6px solid #1A3317;
    }
    
    /* Naam onder de foto - Groot en wit op groen */
    .name-tag { 
        background: #1A3317; 
        color: #FFFFFF !important; 
        padding: 20px; 
        font-size: 35px; 
        text-align: center; 
        font-weight: bold; 
    }

    /* DE AUDIO KNOP - FELGROEN MET WITTE TEKST (GEEN GROEN OP ZWART MEER!) */
    .stButton > button {
        background-color: #2E7D32 !important; 
        color: #FFFFFF !important; 
        border-radius: 20px !important;
        font-size: 26px !important;
        font-weight: 900 !important;
        height: 80px !important;
        border: 4px solid #000000 !important;
        margin-top: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Input velden groter voor familie */
    input { font-size: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.markdown("<div style='padding:100px; text-align:center;'><h1>🌿 Altijd Dichtbij</h1>", unsafe_allow_html=True)
    with st.form("login"):
        fid = st.text_input("Naam van de Familie")
        pw = st.text_input("Wachtwoord", type="password")
        if st.form_submit_button("Start"):
            if (fid and pw == "STARTUP2026") or (fid.lower() == "mestdagh" and pw.lower() == "mestdagh"):
                st.session_state.logged_in, st.session_state.family_id = True, fid
                st.query_params["family"] = fid
                st.rerun()
            else:
                st.error("Naam of code is niet juist.")
else:
    fid = st.session_state.family_id
    full_album = load_data(fid)
    nu = datetime.now()
    
    tab1, tab2, tab3 = st.tabs(["👵 OMA", "📤 FAMILIE", "⚙️ BEHEER"])

    with tab1:
        album_oma = [item for item in full_album if (nu - datetime.strptime(item['datum'], "%Y-%m-%d %H:%M:%S")) < timedelta(days=HOUDBAARHEID_DAGEN)]
        
        if not album_oma:
            st.markdown("<h2 style='text-align:center; padding:100px;'>Wachten op een nieuw berichtje...</h2>", unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, item in enumerate(album_oma):
                with cols[i % 2]:
                    # Foto tonen
                    st.markdown(f'<div class="photo-card"><img src="data:image/jpeg;base64,{item["foto"]}" style="width:100%; height:450px; object-fit:cover;"><div class="name-tag">{item["naam"].upper()}</div></div>', unsafe_allow_html=True)
                    
                    # Audio knop
                    if item.get('audio'):
                        if st.button(f"🔊 HOOR BERICHT VAN {item['naam'].upper()}", key=f"aud_{i}"):
                            item['views'] += 1
                            save_data(fid, full_album)
                            st.components.v1.html(f'<audio autoplay><source src="data:audio/mp3;base64,{item["audio"]}" type="audio/mp3"></audio>', height=0)

    with tab2:
        st.markdown("<div style='padding:20px;'><h2>Stuur een herinnering</h2></div>", unsafe_allow_html=True)
        with st.form("up", clear_on_submit=True):
            n = st.text_input("Wie staat er op de foto?")
            f = st.file_uploader("Kies een foto", type=['jpg','png','jpeg'])
            a = st.audio_input("Spreek een berichtje in")
            if st.form_submit_button("🚀 VERSTUUR NAAR OMA"):
                if n and f:
                    f_b64 = base64.b64encode(f.read()).decode()
                    a_b64 = base64.b64encode(a.read()).decode() if a else None
                    
                    # Nieuwe foto linksboven (index 0)
                    full_album.insert(0, {
                        "naam": n, 
                        "foto": f_b64, 
                        "audio": a_b64, 
                        "datum": nu.strftime("%Y-%m-%d %H:%M:%S"), 
                        "views": 0
                    })
                    
                    save_data(fid, full_album)
                    st.success("Verzonden! Oma ziet het direct.")
                    st.rerun()

    with tab3:
        st.header("⚙️ Instellingen")
        if st.button("🚪 Uitloggen", use_container_width=True):
            st.query_params.clear()
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        for idx, item in enumerate(full_album):
            c1, c2 = st.columns([3,1])
            c1.write(f"🖼️ {item['naam']} ({item['views']} views)")
            if c2.button("Wis", key=f"del_{idx}"):
                full_album.pop(idx); save_data(fid, full_album); st.rerun()
