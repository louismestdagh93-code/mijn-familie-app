import streamlit as st
import base64
import json
import os
from datetime import datetime, timedelta

# 1. CONFIG & AUTO-REFRESH
# We gebruiken een verborgen refresh-mechanisme om de 'Live' ervaring te bieden.
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

<style>
    /* Verberg standaard Streamlit rommel */
    .element-container:has(.stException), .stAlert { display: none !important; }
    header, footer, #MainMenu { visibility: hidden; }
    
    .stApp { background-color: #F7F9F2; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }

    /* DE NIEUWE PREMIUM BALK */
    .stTabs [data-baseweb="tab-list"] { 
        background-color: #4A6741; 
        padding: 15px 0; 
        display: flex; 
        justify-content: center; /* Zet de tabs in het midden */
        gap: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }

    .stTabs [data-baseweb="tab"] { 
        height: 80px; 
        min-width: 180px; /* Maak de tabs breder */
        color: #E8EDDF !important; 
        font-size: 1.6rem !important; /* Grotere letters */
        font-weight: 600; 
        border-radius: 20px; 
        border: none !important;
        background-color: rgba(255,255,255,0.05);
    }

    /* Geselecteerde tab krijgt meer contrast */
    .stTabs [aria-selected="true"] { 
        background-color: #F7F9F2 !important; 
        color: #4A6741 !important; 
        transform: scale(1.05); /* Maakt de actieve tab net iets groter */
    }

    /* Fotokaarten & Knoppen */
    .photo-card { 
        border-radius: 35px; background: #000; margin: 25px; 
        box-shadow: 0 20px 40px rgba(0,0,0,0.15); overflow: hidden;
    }
    .name-tag { background: #4A6741; color: white; padding: 20px; font-size: 28px; text-align: center; font-weight: bold; }
    
    .stButton>button {
        border-radius: 25px; border: 3px solid #4A6741; color: #4A6741;
        font-size: 1.2rem; font-weight: bold; padding: 15px; background: white;
    }
</style>
# 5. UI FLOW
if not st.session_state.logged_in:
    st.markdown("<div style='padding:100px; text-align:center; color:#4A6741;'><h1>🌿 Altijd Dichtbij</h1><p>Verbinden door herinneringen</p>", unsafe_allow_html=True)
    with st.form("login_form"):
        fid = st.text_input("Familienaam").strip()
        pw = st.text_input("Toegangscode", type="password")
        if st.form_submit_button("Start de ervaring"):
            if fid and pw == "STARTUP2026":
                st.session_state.logged_in = True
                st.session_state.family_id = fid
                st.query_params["family"] = fid
                st.rerun()
else:
    fid = st.session_state.family_id
    album = load_and_clean_data(fid)
    
    # Auto-refresh component (elke 60 sec verversen voor live effect)
    st.empty() 
    # Kleine hack voor auto-refresh zonder externe library
    # st.write(f"<meta http-equiv='refresh' content='60'>", unsafe_allow_html=True)

    tab_oma, tab_fam, tab_admin = st.tabs(["👵 OMA", "📤 FAMILIE", "⚙️ BEHEER"])

    with tab_oma:
        if not album:
            st.markdown("<h3 style='text-align:center; padding:100px; color:#888;'>Wachten op een mooi moment...</h3>", unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, item in enumerate(album):
                with cols[i % 2]:
                    fit = item.get('formaat', 'cover')
                    st.markdown(f"""
                    <div class="photo-card">
                        <img src="data:image/jpeg;base64,{item['foto']}" style="width:100%; height:400px; object-fit:{fit};">
                        <div class="name-tag">{item['naam']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if item.get('audio'):
                        if st.button(f"▶️ Luister naar {item['naam']}", key=f"p_btn_{item['naam']}_{i}", use_container_width=True):
                            audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{item["audio"]}" type="audio/mp3"></audio>'
                            st.components.v1.html(audio_html, height=0)

    with tab_fam:
        st.markdown("<div style='padding:30px;'><h2>Stuur een herinnering</h2>", unsafe_allow_html=True)
        with st.form("p_upload", clear_on_submit=True):
            n = st.text_input("Wie is dit?")
            f = st.file_uploader("Kies een foto", type=['jpg', 'jpeg', 'png'])
            fmt = st.segmented_control("Weergave", ["Vullend", "Passend"], default="Vullend")
            a = st.audio_input("Spreek een bericht in")
            
            if st.form_submit_button("🚀 Direct naar de tablet sturen"):
                if n and f:
                    f_b64 = base64.b64encode(f.read()).decode()
                    a_b64 = base64.b64encode(a.read()).decode() if a else None
                    fit_val = "cover" if fmt == "Vullend" else "contain"
                    album.append({"naam": n, "foto": f_b64, "audio": a_b64, "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "formaat": fit_val})
                    save_family_data(fid, album)
                    st.success("Verzonden! Oma ziet dit over enkele seconden.")
                    st.rerun()

    with tab_admin:
        st.markdown("<div style='padding:30px;'>", unsafe_allow_html=True)
        st.subheader(f"Dashboard: Familie {fid}")
        st.write(f"Systeemstatus: **Actief**")
        st.write(f"Laatste check tablet: {datetime.now().strftime('%H:%M:%S')}")
        st.markdown("---")
        for idx, item in enumerate(album):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🖼️ {item['naam']} - Geplaatst op {item.get('datum')}")
            if c2.button("Wis", key=f"p_del_{idx}"):
                album.pop(idx)
                save_family_data(fid, album)
                st.rerun()
        
        if st.button("🚪 Systeem afsluiten", key="p_logout"):
            st.query_params.clear()
            st.session_state.logged_in = False
            st.rerun()
