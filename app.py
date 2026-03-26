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

# 3. LOGIN LOGICA (MET FOTO ACHTERGROND)
if 'logged_in' not in st.session_state:
    if "family" in st.query_params:
        st.session_state.logged_in, st.session_state.family_id = True, st.query_params["family"]
    else: 
        st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Functie om de foto om te zetten naar een achtergrond
    def get_base64_img(file):
        with open(file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    
    try:
        bin_str = get_base64_img("pexels-rdne-5637770.jpg")
        # Deze CSS overschrijft tijdelijk de achtergrond met jouw foto
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url("data:image/png;base64,{bin_str}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            /* Zorg dat het inlogformulier goed leesbaar is op de foto */
            .stForm {{
                background-color: rgba(255, 255, 255, 0.9) !important;
                padding: 20px !important;
                border-radius: 20px !important;
                border: 2px solid #1A3317 !important;
            }}
            </style>
        """, unsafe_allow_html=True)
    except:
        pass # Als de foto mist, gebruikt hij de standaard kleur uit je Sectie 4

    st.markdown("<div style='padding-top:50px; text-align:center;'><h1 style='color:white !important; text-shadow: 2px 2px 4px #000;'>🌿 Altijd Dichtbij</h1></div>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1]) # Centreren op breed scherm
        with col2:
            with st.form("login"):
                fid = st.text_input("Familienaam")
                pw = st.text_input("Code", type="password")
                if st.form_submit_button("START HET ALBUM"):
                    if fid.lower() == "startup2026" and pw == "STARTUP2026":
                        st.session_state.logged_in, st.session_state.family_id = True, fid
                        st.query_params["family"] = fid
                        st.rerun()
                    else:
                        st.error("Naam of code is onjuist.")
    st.stop()

# 4. CSS (HIERNA LAAT JE JOUW LANGE BLOK GEWOON STAAN)
# 4. CSS (AANGEPAST VOOR ZICHTBARE STARTKNOP)
st.markdown("""
<style>
    header, footer, #MainMenu { visibility: hidden; }
    .stApp { background-color: #F7F9F2; }
    
    /* PIKZWARTE TEKST VOOR LABELS */
    h1, h2, h3, label, p, span, div, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }
    
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    /* INPUT VELDEN */
    input, textarea, [data-baseweb="input"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 3px solid #1A3317 !important;
        border-radius: 10px !important;
    }
    
    /* UPLOAD EN AUDIO ZONES IN HET LICHTGROEN */
    [data-testid="stFileUploader"] section, [data-testid="stAudioInput"] {
        background-color: #E8F5E9 !important;
        border: 3px solid #2E7D32 !important;
        border-radius: 15px !important;
    }

    /* TABS STYLING */
    .stTabs [data-baseweb="tab-list"] { background-color: #1A3317; padding: 15px 0; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-size: 1.8rem !important; font-weight: 900; }
    .stTabs [aria-selected="true"] { background-color: #F7F9F2 !important; color: #1A3317 !important; }

    /* FOTO KAARTEN OMA */
    .photo-card { 
        border-radius: 35px; 
        background: #000; 
        margin: 20px; 
        box-shadow: 0 20px 40px rgba(0,0,0,0.2); 
        overflow: hidden; 
        border: 5px solid #1A3317;
    }
    .name-tag { background: #1A3317; color: white !important; padding: 18px; font-size: 30px; text-align: center; font-weight: bold; }

    /* --- FORCEER ALLE KNOPPEN NAAR GROEN (INCLUSIEF START EN VERSTUUR) --- */
    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        background-color: #2E7D32 !important; 
        color: #FFFFFF !important; 
        border-radius: 20px !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        border: 3px solid #000000 !important;
        width: 100%;
        height: 70px !important;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    /* Zorg dat de tekst IN de knop ook wit blijft */
    .stButton > button div p, [data-testid="stFormSubmitButton"] > button div p {
        color: #FFFFFF !important;
    }

    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #1B5E20 !important;
        border: 3px solid #FFFFFF !important;
    }

    /* Manage app badge onderaan ook groen */
    .viewerBadge_container__1QS1n {
        background-color: #2E7D32 !important;
    }
</style>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.markdown("<div style='padding:100px; text-align:center;'><h1>🌿 Altijd Dichtbij</h1>", unsafe_allow_html=True)
    with st.form("login"):
        fid = st.text_input("Familienaam")
        pw = st.text_input("Code", type="password")
        if st.form_submit_button("START HET ALBUM"):
            if fid and pw == "STARTUP2026":
                st.session_state.logged_in, st.session_state.family_id = True, fid
                st.query_params["family"] = fid
                st.rerun()
            else:
                st.error("Naam of code is onjuist.")
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
                item['views'] += 1 
                updated = True
        
        if updated: save_data(fid, full_album)

        if not album_oma:
            st.markdown("<h2 style='text-align:center; padding:100px; color:#555;'>Wachten op een berichtje...</h2>", unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, item in enumerate(album_oma):
                with cols[i % 2]:
                    fit = item.get('formaat', 'cover')
                    st.markdown(f'<div class="photo-card"><img src="data:image/jpeg;base64,{item["foto"]}" style="width:100%; height:450px; object-fit:{fit};"><div class="name-tag">{item["naam"].upper()}</div></div>', unsafe_allow_html=True)
                    if item.get('audio'):
                        if st.button(f"▶️ HOOR BERICHT VAN {item['naam'].upper()}", key=f"aud_{i}"):
                            st.components.v1.html(f'<audio autoplay><source src="data:audio/mp3;base64,{item["audio"]}" type="audio/mp3"></audio>', height=0)

    with tab2:
        st.markdown("<div style='padding:30px;'><h2>Nieuwe herinnering sturen</h2>", unsafe_allow_html=True)
        with st.form("up", clear_on_submit=True):
            n = st.text_input("Wie staat er op de foto?")
            f = st.file_uploader("Kies een foto", type=['jpg','png','jpeg'])
            fmt = st.radio("Formaat", ["Vullend", "Passend"], horizontal=True)
            a = st.audio_input("Spreek je berichtje in")
            if st.form_submit_button("🚀 VERSTUUR NAAR OMA"):
                if n and f:
                    f_b64 = base64.b64encode(f.read()).decode()
                    a_b64 = base64.b64encode(a.read()).decode() if a else None
                    full_album.insert(0, {"naam": n, "foto": f_b64, "audio": a_b64, "datum": nu.strftime("%Y-%m-%d %H:%M:%S"), "formaat": "cover" if fmt=="Vullend" else "contain", "views": 0})
                    save_data(fid, full_album)
                    st.success("Verzonden!")
                    st.rerun()

    with tab3:
        st.markdown("<div style='padding:30px;'><h1>📊 Dashboard</h1>", unsafe_allow_html=True)
        st.subheader("📬 Jouw Wekelijkse Impact")
        if st.button("✨ Genereer Live Collage", use_container_width=True):
            st.balloons()
            with st.container(border=True):
                st.markdown(f"<h2 style='text-align:center;'>Weekoverzicht: Familie {fid}</h2>", unsafe_allow_html=True)
                recenten = [i for i in full_album if (nu - datetime.strptime(i['datum'], "%Y-%m-%d %H:%M:%S")).days < 7]
                if not recenten: st.info("Nog geen foto's deze week.")
                else:
                    grid = st.columns(3)
                    for idx, item in enumerate(recenten):
                        with grid[idx % 3]:
                            st.image(f"data:image/jpeg;base64,{item['foto']}", use_container_width=True)
                            st.markdown(f"<p style='text-align:center;'><b>{item['naam']}</b><br>👁️ {item['views']}x bekeken</p>", unsafe_allow_html=True)
                    st.success(f"Geweldig! Oma heeft deze week al {sum(i['views'] for i in recenten)} keer jullie momenten herbeleefd.")

        st.markdown("---")
        st.subheader("Beheer Archief")
        for idx, item in enumerate(full_album):
            ca, cb = st.columns([4,1])
            ca.write(f"🖼️ {item['naam']} ({item['views']} views)")
            if cb.button("🗑️ Wis", key=f"del_{idx}"):
                full_album.pop(idx); save_data(fid, full_album); st.rerun()

        st.markdown("---")
        if st.button("🚪 Uitloggen", key="logout_final", use_container_width=True):
            st.query_params.clear()
            st.session_state.logged_in = False
            st.rerun()
