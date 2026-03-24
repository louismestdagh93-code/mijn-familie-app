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
                nu = datetime.now()
                clean = []
                for item in data:
                    if 'datum' not in item: 
                        item['datum'] = nu.strftime("%Y-%m-%d %H:%M:%S")
                    d = datetime.strptime(item['datum'], "%Y-%m-%d %H:%M:%S")
                    if nu - d < timedelta(days=HOUDBAARHEID_DAGEN):
                        clean.append(item)
                return clean
            except: return []
    return []

def save_family_data(family_id, data):
    with open(get_file_path(family_id), "w") as f:
        json.dump(data, f)

# 3. SESSIE & AUTO-LOGIN
if 'logged_in' not in st.session_state:
    if "family" in st.query_params:
        st.session_state.logged_in = True
        st.session_state.family_id = st.query_params["family"]
    else:
        st.session_state.logged_in = False

# 4. DE NIEUWE PREMIUM CSS (Gecentreerd & Groot)
st.markdown("""
<style>
    /* Verberg Streamlit foutmeldingen en menu's */
    .element-container:has(.stException), .stAlert, header, footer, #MainMenu { display: none !important; }
    
    .stApp { background-color: #F7F9F2; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }

    /* DE NIEUWE GECENTREERDE BOVENBALK */
    .stTabs [data-baseweb="tab-list"] { 
        background-color: #4A6741; 
        padding: 15px 0; 
        display: flex; 
        justify-content: center; /* Alles naar het midden */
        gap: 30px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.25);
    }

    .stTabs [data-baseweb="tab"] { 
        height: 90px; 
        min-width: 220px; 
        color: #E8EDDF !important; 
        font-size: 1.7rem !important; 
        font-weight: 700; 
        border-radius: 20px; 
        border: none !important;
        background-color: rgba(255,255,255,0.08);
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] { 
        background-color: #F7F9F2 !important; 
        color: #4A6741 !important; 
        transform: scale(1.08);
    }

    /* Fotokaarten */
    .photo-card { 
        border-radius: 40px; background: #000; margin: 30px; 
        box-shadow: 0 25px 50px rgba(0,0,0,0.18); overflow: hidden;
    }
    .name-tag { background: #4A6741; color: white; padding: 22px; font-size: 30px; text-align: center; font-weight: bold; }
    
    /* Grote Knoppen */
    .stButton>button {
        border-radius: 30px; border: 3px solid #4A6741; color: #4A6741;
        font-size: 1.4rem; font-weight: bold; padding: 18px; background: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# 5. UI FLOW
if not st.session_state.logged_in:
    st.markdown("<div style='padding:100px; text-align:center; color:#4A6741;'><h1>🌿 Altijd Dichtbij</h1><p>Log in om herinneringen te delen</p>", unsafe_allow_html=True)
    with st.form("main_login_form"):
        fid = st.text_input("Familienaam").strip()
        pw = st.text_input("Toegangscode", type="password")
        if st.form_submit_button("Start de ervaring"):
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
    
    # Gebruik unieke keys voor de tabs om conflicten te voorkomen
    tab_oma, tab_fam, tab_admin = st.tabs(["👵 OMA", "📤 FAMILIE", "⚙️ BEHEER"])

    with tab_oma:
        if not album:
            st.markdown("<h3 style='text-align:center; padding:120px; color:#888;'>Wachten op nieuwe momenten...</h3>", unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, item in enumerate(album):
                with cols[i % 2]:
                    fit = item.get('formaat', 'cover')
                    st.markdown(f"""
                    <div class="photo-card">
                        <img src="data:image/jpeg;base64,{item['foto']}" style="width:100%; height:420px; object-fit:{fit};">
                        <div class="name-tag">{item['naam']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if item.get('audio'):
                        # Unieke key voor luisterknop
                        l_key = f"listen_{fid}_{item['naam']}_{i}"
                        if st.button(f"▶️ Luister naar {item['naam']}", key=l_key, use_container_width=True):
                            audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{item["audio"]}" type="audio/mp3"></audio>'
                            st.components.v1.html(audio_html, height=0)

    with tab_fam:
        st.markdown("<div style='padding:40px;'><h2>Stuur een nieuwe herinnering</h2>", unsafe_allow_html=True)
        with st.form("upload_form_new", clear_on_submit=True):
            n = st.text_input("Wie staat er op de foto?")
            f = st.file_uploader("Kies een foto", type=['jpg', 'jpeg', 'png'])
            fmt = st.radio("Weergave:", ["Vullend", "Hele foto"], index=0, horizontal=True)
            a = st.audio_input("Spreek een bericht in voor Oma")
            
            if st.form_submit_button("🚀 Naar de tablet sturen"):
                if n and f:
                    f_b64 = base64.b64encode(f.read()).decode()
                    a_b64 = base64.b64encode(a.read()).decode() if a else None
                    fit_val = "cover" if fmt == "Vullend" else "contain"
                    album.append({"naam": n, "foto": f_b64, "audio": a_b64, "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "formaat": fit_val})
                    save_family_data(fid, album)
                    st.success("Gelukt! De foto is onderweg.")
                    st.rerun()

    with tab_admin:
        st.markdown("<div style='padding:40px;'>", unsafe_allow_html=True)
        st.subheader(f"Instellingen voor Familie {fid}")
        st.info(f"Foto's worden na {HOUDBAARHEID_DAGEN} dagen automatisch gewist.")
        
        for idx, item in enumerate(album):
            c1, c2 = st.columns([5, 1])
            c1.write(f"🖼️ {item['naam']} ({item.get('datum', 'Onbekende datum')})")
            # Unieke key voor verwijderknop
            d_key = f"delete_{fid}_{item['naam']}_{idx}"
            if c2.button("🗑️ Wis", key=d_key):
                album.pop(idx)
                save_family_data(fid, album)
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Uitloggen op dit apparaat", key="final_logout"):
            st.query_params.clear()
            st.session_state.logged_in = False
            st.rerun()
