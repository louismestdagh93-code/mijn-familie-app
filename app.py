import streamlit as st
import os
import json
import base64

# --- 1. CONFIG ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DATA SETUP ---
fam = "test"
pad = f"data_{fam}"
if not os.path.exists(pad): os.makedirs(pad)

DB_FILE = os.path.join(pad, "database.json")
album_data = json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else []

# --- 3. STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #FDFCF0; }
    h1 { color: #2E7D32; text-align: center; font-family: sans-serif; }
    .foto-card {
        border: 4px solid #2E7D32;
        border-radius: 20px;
        overflow: hidden;
        background: white;
        cursor: pointer;
        transition: transform 0.1s;
    }
    .foto-card:active { transform: scale(0.98); }
</style>
""", unsafe_allow_html=True)

# --- 4. BEHEER & VOLUME (Zijbalk) ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    # De nieuwe volumeknop
    vol_level = st.slider("Volume van de spraak", 0, 100, 80)
    vol_float = vol_level / 100  # Omzetten naar een getal tussen 0 en 1
    
    st.divider()
    st.subheader("Persoon toevoegen")
    t = st.text_input("Naam")
    f = st.file_uploader("Foto")
    a = st.file_uploader("Geluid")
    if st.button("Opslaan"):
        if t:
            index = next((i for i, item in enumerate(album_data) if item["titel"].lower() == t.lower()), None)
            item = album_data[index] if index is not None else {"titel": t, "foto": "", "audio": ""}
            if f:
                fp = os.path.join(pad, f.name); open(fp, "wb").write(f.getbuffer()); item["foto"] = fp
            if a:
                ap = os.path.join(pad, a.name); open(ap, "wb").write(a.getbuffer()); item["audio"] = ap
            if index is not None: album_data[index] = item
            else: album_data.append(item)
            json.dump(album_data, open(DB_FILE, "w"))
            st.rerun()
    
    if st.button("🗑️ Wis alles (Reset)"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()

# --- 5. HET SCHERM ---
st.markdown(f"<h1>Familie {fam.capitalize()}</h1>", unsafe_allow_html=True)

cols = st.columns(3)
for i, item in enumerate(album_data):
    foto_bestaat = item.get('foto') and os.path.exists(item['foto'])
    audio_bestaat = item.get('audio') and os.path.exists(item['audio'])
    
    if foto_bestaat:
        with cols[i % 3]:
            img_b64 = base64.b64encode(open(item['foto'], "rb").read()).decode()
            
            audio_html = ""
            if audio_bestaat:
                aud_b64 = base64.b64encode(open(item['audio'], "rb").read()).decode()
                # De 'volume' property wordt hier via JavaScript gezet
                audio_html = f"""
                <audio id="aud_{i}" src="data:audio/mp3;base64,{aud_b64}"></audio>
                <script>
                    var a = document.getElementById('aud_{i}');
                    a.volume = {vol_float};
                </script>
                """
            
            st.components.v1.html(f"""
            <div onclick="document.getElementById('aud_{i}').play()" class="foto-card">
                <img src="data:image/jpeg;base64,{img_b64}" style="width:100%; height:250px; object-fit:cover; display:block;">
                <div style="background:#2E7D32; color:white; padding:10px; text-align:center; font-weight:bold; font-family:sans-serif; font-size:18px;">{item['titel']}</div>
                {audio_html}
            </div>
            """, height=320)

st.button("💻 Volledig scherm", on_click=lambda: st.components.v1.html("<script>window.parent.document.documentElement.requestFullscreen();</script>", height=0))
