import streamlit as st
import os
import json
import base64

# --- 1. CONFIG ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DATA SETUP ---
fam = "test"
pad = f"data_{fam}"
standaard_pad = "standaard"
if not os.path.exists(pad): os.makedirs(pad)

DB_FILE = os.path.join(pad, "database.json")
album_data = json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else []

# Aangepast aan jouw screenshots (.png in plaats van .jpg)
if not album_data:
    album_data = [
        {"titel": "Louis Mestdagh", "foto": f"{standaard_pad}/Louis.png", "audio": f"{standaard_pad}/louis.mp3"},
        {"titel": "Kimberly Dubois", "foto": f"{standaard_pad}/Kimberly.png", "audio": f"{standaard_pad}/kimberly.mp3"}
    ]

# --- 3. STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #FDFCF0; }
    h1 { color: #2E7D32; text-align: center; font-family: sans-serif; }
    .foto-card { border: 4px solid #2E7D32; border-radius: 20px; overflow: hidden; background: white; cursor: pointer; }
</style>
""", unsafe_allow_html=True)

# --- 4. BEHEER (Zijbalk) ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    vol_level = st.slider("Volume", 0, 100, 80)
    vol_float = vol_level / 100
    
    st.divider()
    beheer_optie = st.radio("Wat wil je doen?", ["Bestaande aanpassen", "Nieuw persoon toevoegen"])
    
    if beheer_optie == "Bestaande aanpassen":
        if album_data:
            t = st.selectbox("Kies persoon", [p["titel"] for p in album_data])
            f = st.file_uploader("Nieuwe Tijdelijke Foto")
            a = st.file_uploader("Nieuw Tijdelijk Geluid")
            if st.button("Bijwerken"):
                idx = next((i for i, item in enumerate(album_data) if item["titel"] == t), None)
                if idx is not None:
                    if f:
                        fp = os.path.join(pad, f.name); open(fp, "wb").write(f.getbuffer())
                        album_data[idx]["foto"] = fp
                    if a:
                        ap = os.path.join(pad, a.name); open(ap, "wb").write(a.getbuffer())
                        album_data[idx]["audio"] = ap
                    json.dump(album_data, open(DB_FILE, "w"))
                    st.rerun()
    else:
        nieuw_naam = st.text_input("Naam")
        f_nieuw = st.file_uploader("Foto uploaden")
        a_nieuw = st.file_uploader("Geluid uploaden")
        if st.button("Toevoegen aan album"):
            if nieuw_naam and f_nieuw and a_nieuw:
                fp = os.path.join(pad, f_nieuw.name); open(fp, "wb").write(f_nieuw.getbuffer())
                ap = os.path.join(pad, a_nieuw.name); open(ap, "wb").write(a_nieuw.getbuffer())
                album_data.append({"titel": nieuw_naam, "foto": fp, "audio": ap})
                json.dump(album_data, open(DB_FILE, "w"))
                st.rerun()

    st.divider()
    if st.button("🗑️ Reset naar basis"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()

# --- 5. HET SCHERM ---
st.markdown(f"<h1>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)

cols = st.columns(3)
for i, item in enumerate(album_data):
    # We tonen de kaart alleen als de foto ECHT bestaat
    if item.get('foto') and os.path.exists(item['foto']):
        with cols[i % 3]:
            img_b64 = base64.b64encode(open(item['foto'], "rb").read()).decode()
            audio_html = ""
            
            if item.get('audio') and os.path.exists(item['audio']):
                aud_b64 = base64.b64encode(open(item['audio'], "rb").read()).decode()
                audio_html = f"""
                <audio id="aud_{i}" src="data:audio/mp3;base64,{aud_b64}"></audio>
                <script>document.getElementById('aud_{i}').volume = {vol_float};</script>
                """
            
            st.components.v1.html(f"""
            <div onclick="document.getElementById('aud_{i}').play()" class="foto-card">
                <img src="data:image/png;base64,{img_b64}" style="width:100%; height:250px; object-fit:cover; display:block;">
                <div style="background:#2E7D32; color:white; padding:10px; text-align:center; font-weight:bold; font-family:sans-serif;">{item['titel']}</div>
                {audio_html}
            </div>
            """, height=320)
