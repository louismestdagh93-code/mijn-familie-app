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

# 4. CSS (VERBETERDE LEESBAARHEID & CONTRAST)
st.markdown("""
<style>
    header, footer, #MainMenu { visibility: hidden; }
    .stApp { background-color: #F7F9F2; }
    
    /* FORCEER PIKZWARTE TEKST VOOR ALLE TITELS EN LABELS */
    h1, h2, h3, label, p, span, div, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }
    
    /* Zorg dat de witte titels in de screenshots nu zichtbaar zijn */
    .stForm h2, .stMarkdown h1 { color: #000000 !important; }

    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    /* Tabs styling - Donkergroene balk met witte letters */
    .stTabs [data-baseweb="tab-list"] { background-color: #1A3317; padding: 15px 0; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-size: 1.8rem !important; font-weight: 900; }
    .stTabs [aria-selected="true"] { background-color: #F7F9F2 !important; color: #1A3317 !important; border-radius: 10px; }

    /* Foto Kaarten */
    .photo-card { 
        border-radius: 25px; 
        background: #000000; 
        margin-top: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.4); 
        overflow: hidden; 
        border: 6px solid #1A3317;
    }
    
    .name-tag { 
        background: #1A3317; 
        color: #FFFFFF !important; /* Naam moet wit blijven op de groene balk */
        padding: 20px; 
        font-size: 35px; 
        text-align: center; 
        font-weight: bold; 
    }

    /* DE AUDIO KNOP - FIX VOOR ONLEESBARE TEKST */
    .stButton > button {
        background-color: #2E7D32 !important; /* Felgroene knop */
        color: #FFFFFF !important; /* KRITIEK: Witte tekst op de knop */
        border-radius: 20px !important;
        font-size: 26px !important;
        font-weight: 900 !important;
        height: 80px !important;
        border: 4px solid #000000 !important;
        margin-top: 15px;
        width: 100%;
    }

    /* View badge styling in beheer */
    .view-badge {
        background-color: #E8F5E9;
        padding: 8px 15px;
        border-radius: 10px;
        border: 2px solid #2E7D32;
        color: #000000 !important;
        display: inline-block;
        margin-top: 5px;
    }
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
        album_oma = []
        updated = False
        for item in full_album:
            d = datetime.strptime(item['datum'], "%Y-%m-%d %H:%M:%S")
            if nu - d < timedelta(days=HOUDBAARHEID_DAGEN):
                album_oma.append(item)
                item['views'] += 1 # Teller blijft werken
                updated = True
        
        if updated:
            save_data(fid, full_album)

        if not album_oma:
            st.markdown("<h2 style='text-align:center; padding:100px;'>Wachten op een nieuw berichtje...</h2>", unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, item in enumerate(album_oma):
                with cols[i % 2]:
                    st.markdown(f'<div class="photo-card"><img src="data:image/jpeg;base64,{item["foto"]}" style="width:100%; height:450px; object-fit:cover;"><div class="name-tag">{item["naam"].upper()}</div></div>', unsafe_allow_html=True)
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
                    # Blijft insert(0) gebruiken zodat nieuwe foto's linksboven komen
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
        st.header("⚙️ Beheer & Statistieken")
        if st.button("🚪 Uitloggen", use_container_width=True):
            st.query_params.clear()
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        st.subheader("Overzicht Foto's")
        for idx, item in enumerate(full_album):
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 3, 1])
                c1.image(f"data:image/jpeg;base64,{item['foto']}", width=100)
                # Views zijn hier weer zichtbaar
                c2.markdown(f"""
                    **Van:** {item['naam']}<br>
                    **Gezonden op:** {item['datum']}<br>
                    <div class="view-badge">👁️ **{item['views']} keer** bekeken</div>
                """, unsafe_allow_html=True)
                if c3.button("🗑️ Wis", key=f"del_{idx}"):
                    full_album.pop(idx)
                    save_data(fid, full_album)
                    st.rerun()
