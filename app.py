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

if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f: album_data = json.load(f)
else: album_data = []

config = {"n_start": 21, "n_eind": 7}
if os.path.exists(CFG_FILE):
    try:
        with open(CFG_FILE, "r") as f: config = json.load(f)
    except: pass

# --- 4. NACHT CHECK ---
def check_nacht():
    nu = (datetime.utcnow() + timedelta(hours=1)).hour
    s, e = config.get("n_start", 21), config.get("n_eind", 7)
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
    config["n_start"] = st.slider("Start nacht", 0, 23, config.get("n_start", 21))
    config["n_eind"] = st.slider("Einde nacht", 0, 23, config.get("n_eind", 7))
    if st.button("Tijden opslaan"):
        with open(CFG_FILE, "w") as f: json.dump(config, f)
        st.rerun()
    
    st.divider()
    st.subheader("➕ Toevoegen of Bijwerken")
    t = st.text_input("Naam van de persoon")
    f = st.file_uploader("Foto")
    a = st.file_uploader("Geluid")
    
    if st.button("Opslaan"):
        if t:
            index = next((i for i, item in enumerate(album_data) if item["titel"].lower() == t.lower()), None)
            item = album_data[index] if index is not None else {"titel": t, "foto": "", "audio": ""}
            if f:
                fp = os.path.join(pad, f.name)
                with open(fp, "wb") as m: m.write(f.getbuffer())
                item["foto"] = fp
            if a:
                ap = os.path.join(pad, a.name)
                with open(ap, "wb") as m: m.write(a.getbuffer())
                item["audio"] = ap
            if index is not None: album_data[index] = item
            else: album_data.append(item)
            with open(DB_FILE, "w") as m: json.dump(album_data, m)
            st.success(f"{t} opgeslagen!")
            st.rerun()

    st.divider()
    st.subheader("🗑️ Verwijderen")
    if album_data:
        namen = [item["titel"] for item in album_data]
        te_verwijderen = st.selectbox("Kies wie je wilt verwijderen", namen)
        if st.button(f"Verwijder {te_verwijderen}"):
            # Verwijder bestanden fysiek (optioneel, maar netter)
            item = next(i for i in album_data if i["titel"] == te_verwijderen)
            try:
                if os.path.exists(item["foto"]): os.remove(item["foto"])
                if os.path.exists(item["audio"]): os.remove(item["audio"])
            except: pass
            
            # Update lijst
            album_data = [i for i in album_data if i["titel"] != te_verwijderen]
            with open(DB_FILE, "w") as m: json.dump(album_data, m)
            st.warning(f"{te_verwijderen} is verwijderd.")
            st.rerun()
    else:
        st.write("Geen personen in album.")

# --- 7. HET SCHERM ---
if is_nacht:
    st.markdown("<div style='padding-top:100px;'><h1 style='font-size:100px;'>🌙</h1><h2>Het is nacht.</h2><p>Slaap lekker!</p></div>", unsafe_allow_html=True)
else:
    st.markdown(f"<h1>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)
    cols = st.columns(3)
    
    for i, item in enumerate(album_data):
        if item.get('foto') and item.get('audio') and os.path.exists(item['foto']):
            with cols[i % 3]:
                img_b64 = base64.b64encode(open(item['foto'], "rb").read()).decode()
                aud_b64 = base64.b64encode(open(item['audio'], "rb").read()).decode()
                
                st.components.v1.html(f"""
                <div id="card_{i}" onclick="playAudio()" style="cursor:pointer; border:4px solid #2E7D32; border-radius:20px; overflow:hidden; background:white; font-family:sans-serif;">
                    <img src="data:image/jpeg;base64,{img_b64}" style="width:100%; height:180px; object-fit:cover; display:block;">
                    <div style="background:#2E7D32; color:white; padding:10px; text-align:center; font-weight:bold; font-size:18px;">{item['titel']}</div>
                    <audio id="aud_{i}" src="data:audio/mp3;base64,{aud_b64}"></audio>
                </div>
                <script>
                    function playAudio() {{
                        // Stop alle andere audio fragmenten op de pagina
                        var allAudios = window.parent.document.querySelectorAll('audio');
                        allAudios.forEach(function(a) {{ a.pause(); a.currentTime = 0; }});
                        // Speel dit fragment
                        var current = document.getElementById('aud_{i}');
                        current.play();
                    }}
                </script>
                """, height=250)

    if st.button("💻 Volledig scherm"):
        st.components.v1.html("<script>window.parent.document.documentElement.requestFullscreen();</script>", height=0)
