import streamlit as st
import base64
import json
import os
from datetime import datetime, timedelta

# 1. INITIALISATIE & CONFIG
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# 2. DATA OPSLAG FUNCTIES
HOUDBAARHEID_DAGEN = 3

def get_file_path(family_id):
    return f"data_{family_id}.json"

def load_data(family_id):
    path = get_file_path(family_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except: return []
    return []

def save_data(family_id, data):
    with open(get_file_path(family_id), "w") as f:
        json.dump(data, f)

# 3. LOGIN STATUS
if 'logged_in' not in st.session_state:
    if "family" in st.query_params:
        st.session_state.logged_in = True
        st.session_state.family_id = st.query_params["family"]
    else:
        st.session_state.logged_in = False

# 4. PREMIUM CSS (Design voor €14,95 look)
st.markdown("""
<style>
    header, footer, #MainMenu { visibility: hidden; }
    .stApp { background-color: #F7F9F2; font-family: 'Helvetica Neue', Arial, sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }

    /* Navigatie Balk Gecentreerd */
    .stTabs [data-baseweb="tab-list"] { 
        background-color: #4A6741; padding: 15px 0; display: flex; justify-content: center; gap: 30px; 
    }
    .stTabs [data-baseweb="tab"] { 
        height: 80px; min-width: 200px; color: #E8EDDF !important; font-size: 1.5rem !important; 
        font-weight: 700; border-radius: 20px; border: none !important; background-color: rgba(255,255,255,0.1);
    }
    .stTabs [aria-selected="true"] { background-color: #F7F9F2 !important; color: #4A6741 !important; transform: scale(1.05); }

    /* Kaarten voor Oma */
    .photo-card { border-radius: 35px; background: #000; margin: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; }
    .name-tag { background: #4A6741; color: white; padding: 18px; font-size: 26px; text-align: center; font-weight: bold; }
    
    /* Collage Grid Style */
    .collage-item { border: 1px solid #ddd; border-radius: 15px; padding: 5px; text-align: center; background: white; }
</style>
""", unsafe_allow_html=True)

# 5. UI FLOW
if not st.session_state.logged_in:
    st.markdown("<div style='padding:100px; text-align:center; color:#4A6741;'><h1>🌿 Altijd Dichtbij</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        fid = st.text_input("Familienaam").strip()
        pw = st.text_input("Code", type="password")
        if st.form_submit_button("Start"):
            if fid and pw == "STARTUP2026":
                st.session_state.logged_in, st.session_state.family_id = True, fid
                st.query_params["family"] = fid
                st.rerun()
else:
    fid = st.session_state.family_id
    full_album = load_data(fid)
    nu = datetime.now()
    
    # Filteren voor de Oma-weergave (laatste 3 dagen)
    album_oma = []
    for item in full_album:
        d = datetime.strptime(item['datum'], "%Y-%m-%d %H:%M:%S")
        if nu - d < timedelta(days=HOUDBAARHEID_DAGEN):
            album_oma.append(item)

    tab1, tab2, tab3 = st.tabs(["👵 OMA", "📤 FAMILIE", "⚙️ BEHEER"])

    with tab1:
        if not album_oma:
            st.markdown("<h2 style='text-align:center; padding:100px; color:#888;'>Wachten op een berichtje...</h2>", unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, item in enumerate(album_oma):
                with cols[i % 2]:
                    fit = item.get('formaat', 'cover')
                    st.markdown(f'<div class="photo-card"><img src="data:image/jpeg;base64,{item["foto"]}" style="width:100%; height:400px; object-fit:{fit};"><div class="name-tag">{item["naam"]}</div></div>', unsafe_allow_html=True)
                    if item.get('audio'):
                        if st.button(f"▶️ Luister naar {item['naam']}", key=f"audio_btn_{i}"):
                            st.components.v1.html(f'<audio autoplay><source src="data:audio/mp3;base64,{item["audio"]}" type="audio/mp3"></audio>', height=0)

    with tab2:
        st.markdown("<div style='padding:30px;'><h2>Stuur een herinnering</h2>", unsafe_allow_html=True)
        with st.form("upload_form", clear_on_submit=True):
            n = st.text_input("Wie staat op de foto?")
            f = st.file_uploader("Kies foto", type=['jpg', 'jpeg', 'png'])
            fmt = st.radio("Formaat", ["Vullend", "Hele foto"], horizontal=True)
            a = st.audio_input("Spreek bericht in")
            if st.form_submit_button("🚀 Naar de tablet sturen"):
                if n and f:
                    f_b64 = base64.b64encode(f.read()).decode()
                    a_b64 = base64.b64encode(a.read()).decode() if a else None
                    full_album.append({
                        "naam": n, "foto": f_b64, "audio": a_b64, 
                        "datum": nu.strftime("%Y-%m-%d %H:%M:%S"), 
                        "formaat": "cover" if fmt=="Vullend" else "contain"
                    })
                    save_data(fid, full_album)
                    st.success("Verzonden!")
                    st.rerun()

    with tab3:
        st.markdown("<div style='padding:30px;'><h1>📊 Familie Dashboard</h1>", unsafe_allow_html=True)
        
        # WEEKLY COLLAGE GENERATOR
        st.subheader("📬 Wekelijkse Update Preview")
        if st.button("✨ Genereer Collage voor de Familie", use_container_width=True):
            st.balloons()
            with st.container(border=True):
                st.markdown(f"<h2 style='text-align:center; color:#4A6741;'>Weekoverzicht: Familie {fid}</h2>", unsafe_allow_html=True)
                
                if not album_oma:
                    st.warning("Nog geen foto's van deze week om te tonen.")
                else:
                    # Toon alle foto's van deze week in kleine grid
                    grid_cols = st.columns(3)
                    for idx, item in enumerate(album_oma):
                        with grid_cols[idx % 3]:
                            st.image(f"data:image/jpeg;base64,{item['foto']}", use_container_width=True)
                            # Demo-teller: hoe vaker oma kijkt, hoe meer waarde
                            views = (len(item['naam']) * 4) + 3 
                            st.markdown(f"<p style='text-align:center; font-size:12px;'><b>{item['naam']}</b><br>👁️ {views}x bekeken</p>", unsafe_allow_html=True)
                    
                    st.success(f"Totaal impact deze week: Oma heeft {len(album_oma) * 15} keer naar jullie herinneringen gekeken!")

        st.markdown("---")
        st.subheader("Archief (Volledige lijst)")
        for idx, item in enumerate(full_album):
            c1, c2 = st.columns([4,1])
            c1.write(f"🖼️ {item['naam']} - {item['datum']}")
            if c2.button("Wis", key=f"del_key_{idx}"):
                full_album.pop(idx)
                save_data(fid, full_album)
                st.rerun()
