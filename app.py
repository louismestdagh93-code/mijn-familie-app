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

if not album_data:
    album_data = [
        {"titel": "Louis Mestdagh", "foto": f"{standaard_pad}/Louis.png", "audio": f"{standaard_pad}/louis.mp3"},
        {"titel": "Kimberly Dubois", "foto": f"{standaard_pad}/Kimberly.png", "audio": f"{standaard_pad}/kimberly.mp3"}
    ]

# --- 3. STYLING ---
# We gebruiken hier geen f-string om de SyntaxError met accolades te voorkomen
st.markdown("""
<style>
    .block-container {
        padding: 10px !important;
        max-width: 100% !important;
    }
    .stApp { background-color: #FDFCF0; }
    header, footer { visibility: hidden; }

    .album-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
        padding: 5px;
    }

    .foto-card {
        border: 2px solid #2E7D32;
        border-radius: 12px;
        overflow: hidden;
        background: white;
        cursor: pointer;
        display: flex;
        flex-direction: column;
    }
    
    .foto-card img {
        width: 100%;
        height: 180px;
        object-fit: cover;
    }

    .naam-label {
        background: #2E7D32;
        color: white;
        padding: 8px;
        text-align: center;
        font-weight: bold;
        font-family: sans-serif;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. BEHEER (Zijbalk) ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    vol_level = st.slider("Volume", 0, 100, 80)
    vol_float = vol_level / 100
    st.divider()
    beheer_optie = st.radio("Actie", ["Aanpassen", "Nieuw"])
    
    if beheer_optie == "Aanpassen":
        if album_data:
            t = st.selectbox("Persoon", [p["titel"] for p in album_data])
            f = st.file_uploader("Foto")
            a = st.file_uploader("Geluid")
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
        f_nieuw = st.file_uploader("Foto")
        a_nieuw = st.file_uploader("Geluid")
        if st.button("Toevoegen"):
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
st.markdown(f"<h1 style='text-align:center; color:#2E7D32;'>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)

# Grid opbouw
cards_html = ""
for i, item in enumerate(album_data):
    if item.get('foto') and os.path.exists(item['foto']):
        with open(item['foto'], "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        
        audio_tag = ""
        if item.get('audio') and os.path.exists(item['audio']):
            with open(item['audio'], "rb") as a:
                aud_b64 = base64.b64encode(a.read()).decode()
            audio_tag = f'<audio id="aud_{i}" src="data:audio/mp3;base64,{aud_b64}"></audio>'
            audio_tag += f'<script>document.getElementById("aud_{i}").volume = {vol_float};</script>'
        
        cards_html += f"""
        <div onclick="document.getElementById('aud_{i}').play()" class="foto-card">
            <img src="data:image/png;base64,{img_b64}">
            <div class="naam-label">{item['titel']}</div>
            {audio_tag}
        </div>
        """

full_html = f'<div class="album-grid">{cards_html}</div>'
st.components.v1.html(full_html, height=800, scrolling=True)
