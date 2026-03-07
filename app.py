import streamlit as st
import os
import json
import base64
from datetime import datetime, timedelta

# --- 1. CONFIG ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

FAMILIES = {"jansen": "jansen2026", "pietersen": "pietersen2026", "test": "test"}

if 'ingelogd_familie' not in st.session_state:
    st.session_state.ingelogd_familie = None

# --- 2. LOGIN ---
if st.session_state.ingelogd_familie is None:
    st.markdown("<h1 style='text-align: center;'>❤️ Welkom</h1>", unsafe_allow_html=True)
    pwd = st.text_input("Wachtwoord", type="password")
    if st.button("Open Album"):
        for fam, ww in FAMILIES.items():
            if pwd == ww:
                st.session_state.ingelogd_familie = fam
                st.rerun()
    st.stop()

# --- 3. DATA SETUP ---
fam = st.session_state.ingelogd_familie
pad = f"data_{fam}"
if not os.path.exists(pad): os.makedirs(pad)

DB_FILE = os.path.join(pad, "database.json")
CFG_FILE = os.path.join(pad, "config.json")

album_data = json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else []
config = {"n_start": 21, "n_eind": 7}
if os.path.exists(CFG_FILE):
    try:
        with open(CFG_FILE, "r") as f:
            saved = json.load(f)
            if "n_start" in saved: config = saved
    except: pass

# --- 4. NACHT CHECK ---
def check_nacht():
    nu = (datetime.utcnow() + timedelta(hours=1)).hour
    s, e = config["n_start"], config["n_eind"]
    return (nu >= s or nu < e) if s > e else (s <= nu < e)

is_nacht = check_nacht()

# --- 5. STYLING ---
bg = "#0A0E14" if is_nacht else "#FDFCF0"
txt = "#FFFFFF" if is_nacht else "#2E7D32"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; }}
    h1, h2, p {{ color: {txt}; text-align: center; font-family: sans-serif; }}
    #MainMenu, footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# --- 6. BEHEER (Zijbalk) ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    config["n_start"] = st.slider("Start nacht", 0, 23, config["n_start"])
    config["n_eind"] = st.slider("Einde nacht", 0, 23, config["n_eind"])
    if st.button("Opslaan"):
        json.dump(config, open(CFG_FILE, "w"))
        st.rerun()
    
    st.divider()
    st.subheader("Foto/Audio Beheren")
    st.info("Typ de NAAM van de persoon. Als de naam al bestaat, wordt deze bijgewerkt.")
    t = st.text_input("Naam van de persoon (bijv. Louis)")
    f = st.file_uploader("Nieuwe Foto (leeg laten om huidige te behouden)")
    a = st.file_uploader("Nieuw Geluid (leeg laten om huidige te behouden)")
    
    if st.button("Opslaan in Album"):
        if t:
            # Zoek of persoon al bestaat
            index = next((i for i, item in enumerate(album_data) if item["titel"].lower() == t.lower()), None)
            
            new_item = album_data[index].copy() if index is not None else {"titel": t, "foto": "", "audio": ""}
            
            if f:
                fp = os.path.join(pad, f.name)
                open(fp, "wb").write(f.getbuffer())
                new_item["foto"] = fp
            if a:
                ap = os.path.join(pad, a.name)
                open(ap, "wb").write(a.getbuffer())
                new_item["audio"] = ap
            
            if index is not None:
                album_data[index] = new_item
            else:
                album_data.append(new_item)
                
            json.dump(album_data, open(DB_FILE, "w"))
            st.success(f"{t} bijgewerkt!")
            st.rerun()

# --- 7. HET SCHERM ---
if is_nacht:
    st.markdown("<div style='padding-top:100px;'><h1 style='font-size:100px;'>🌙</h1><h2>Het is nacht.</h2><p>Slaap lekker!</p></div>", unsafe_allow_html=True)
else:
    st.markdown(f"<h1>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)
    cols = st.columns(3)
    
    # JavaScript om alle andere audio te stoppen
    js_stop_script = """
    <script>
    function playAndStopOthers(id) {
        var audios = document.getElementsByTagName('audio');
        for(var i = 0; i < audios.length; i++){
            if(audios[i].id != id){
                audios[i].pause();
                audios[i].currentTime = 0;
            }
        }
        document.getElementById(id).play();
    }
    </script>
    """
    st.components.v1.html(js_stop_script, height=0)

    for i, item in enumerate(album_data):
        if item['foto'] and item['audio']: # Alleen tonen als beide er zijn
            with cols[i % 3]:
                img_b64 = base64.b64encode(open(item['foto'], "rb").read()).decode()
                aud_b64 = base64.b64encode(open(item['audio'], "rb").read()).decode()
                
                st.components.v1.html(f"""
                    <div onclick="window.parent.playAndStopOthers('a{i}')" style="cursor:pointer; border:4px solid #2E7D32; border-radius:20px; overflow:hidden; background:white; font-family:sans-serif;">
                        <img src="data:image/jpeg;base64,{img_b64}" style="width:100%; height:180px; object-fit:cover; display:block;">
                        <div style="background:#2E7D32; color:white; padding:10px; text-align:center; font-weight:bold;">{item['titel']}</div>
                        <audio id="a{i}"><source src="data:audio/mp3;base64,{aud_b64}"></audio>
                    </div>
                """, height=250)

    if st.button("💻 Volledig scherm"):
        st.components.v1.html("<script>window.parent.document.documentElement.requestFullscreen();</script>", height=0)
