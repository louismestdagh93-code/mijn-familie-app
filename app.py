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

# --- 3. ULTRA-RESPONSIVE STYLING ---
st.markdown(f"""
<style>
    /* Verwijder alle Streamlit marges voor maximale schermvulling */
    .block-container {{
        padding: 10px !important;
        max-width: 100% !important;
    }}
    .stApp {{ background-color: #FDFCF0; }}
    header, footer {{ visibility: hidden; }}

    h1 {{ 
        color: #2E7D32; 
        text-align: center; 
        font-family: sans-serif; 
        font-size: 1.5rem; 
        margin-bottom: 15px; 
    }}

    /* Het raster voor de foto's */
    .album-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: center;
    }}

    /* De fotokaart zelf */
    .foto-card {{
        flex: 1 1 300px; /* Basisbreedte 300px, mag groeien en krimpen */
        max-width: 450px;
        border: 3px solid #2E7D32;
        border-radius: 15px;
        overflow: hidden;
        background: white;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    .foto-card img {{
        width: 100%;
        height: 250px;
        object-fit: cover;
        display: block;
    }

    .naam-label {{
        background: #2E7D32;
        color: white;
        padding: 12px;
        text-align: center;
        font-weight: bold;
        font-family: sans-serif;
        font-size: 18px;
    }}
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
            f = st.file_uploader("Nieuwe Foto")
            a = st.file_uploader("Nieuw Geluid")
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
st.markdown(f"<h1>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)

# Begin van het raster
html_grid = '<div class="album-grid">'

for i, item in enumerate(album_data):
    if item.get('foto') and os.path.exists(item['foto']):
        img_b64 = base64.b64encode(open(item['foto'], "rb").read()).decode()
        audio_html = ""
        
        if item.get('audio') and os.path.exists(item['audio']):
            aud_b64 = base64.b64encode(open(item['audio'], "rb").read()).decode()
            audio_html = f'<audio id="aud_{i}" src="data:audio/mp3;base64,{aud_b64}"></audio><script>document.getElementById("aud_{i}").volume = {vol_float};</script>'
        
        # Voeg elke kaart toe aan het raster
        html_grid += f"""
        <div onclick="document.getElementById('aud_{i}').play()" class="foto-card">
            <img src="data:image/png;base64,{img_b64}">
            <div class="naam-label">{item['titel']}</div>
            {audio_html}
        </div>
        """

html_grid += '</div>' # Einde van het raster

# Toon alles in één keer
st.components.v1.html(html_grid, height=1000, scrolling=True)
