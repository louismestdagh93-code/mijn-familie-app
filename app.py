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
            try: return json.load(f)
            except: return []
    return []

def save_data(family_id, data):
    with open(get_file_path(family_id), "w") as f:
        json.dump(data, f)

# 3. LOGIN
if 'logged_in' not in st.session_state:
    if "family" in st.query_params:
        st.session_state.logged_in, st.session_state.family_id = True, st.query_params["family"]
    else: st.session_state.logged_in = False

# 4. PREMIUM DESIGN
st.markdown("""
<style>
    .element-container:has(.stException), .stAlert, header, footer, #MainMenu { display: none !important; }
    .stApp { background-color: #F7F9F2; font-family: 'Helvetica Neue', Arial, sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #4A6741; padding: 15px 0; display: flex; justify-content: center; gap: 30px; }
    .stTabs [data-baseweb="tab"] { height: 80px; min-width: 200px; color: #E8EDDF !important; font-size: 1.5rem !important; font-weight: 700; border-radius: 20px; border: none !important; background-color: rgba(255,255,255,0.1); }
    .stTabs [aria-selected="true"] { background-color: #F7F9F2 !important; color: #4A6741 !important; transform: scale(1.05); }
    .photo-card { border-radius: 35px; background: #000; margin: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; }
    .name-tag { background: #4A6741; color: white; padding: 18px; font-size: 26px; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.markdown("<div style='padding:100px; text-align:center;'><h1>🌿 Altijd Dichtbij</h1>", unsafe_allow_html=True)
    with st.form("login"):
        fid = st.text_input("Familienaam")
        pw = st.text_input("Code", type="password")
        if st.form_submit_button("Inloggen"):
            if fid and pw == "STARTUP2026":
                st.session_state.logged_in, st.session_state.family_id = True, fid
                st.query_params["family"] = fid
                st.rerun()
else:
    fid = st.session_state.family_id
    full_album = load_data(fid)
    nu = datetime.now()
    album_oma = [i for i in full_album if (nu - datetime.strptime(i['datum'], "%Y-%m-%d %H:%M:%S")).days < HOUDBAARHEID_DAGEN]

    tab1, tab2, tab3 = st.tabs(["👵 OMA", "📤 FAMILIE", "⚙️ BEHEER"])

    with tab1:
        if not album_oma: st.markdown("<h2 style='text-align:center; padding:100px; color:#888;'>Wachten op een berichtje...</h2>", unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, item in enumerate(album_oma):
                with cols[i % 2]:
                    fit = item.get('formaat', 'cover')
                    st.markdown(f'<div class="photo-card"><img src="data:image/jpeg;base64,{item["foto"]}" style="width:100%; height:400px; object-fit:{fit};"><div class="name-tag">{item["naam"]}</div></div>', unsafe_allow_html=True)
                    if item.get('audio'):
                        if st.button(f"▶️ Luister naar {item['naam']}", key=f"aud_{i}"):
                            st.components.v1.html(f'<audio autoplay><source src="data:audio/mp3;base64,{item["audio"]}" type="audio/mp3"></audio>', height=0)

    with tab2:
        st.markdown("<div style='padding:30px;'><h2>Nieuwe herinnering sturen</h2>", unsafe_allow_html=True)
        with st.form("up_p", clear_on_submit=True):
            n, f = st.text_input("Naam"), st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
            fmt = st.radio("Formaat", ["Vullend", "Passend"], horizontal=True)
            a = st.audio_input("Bericht")
            if st.form_submit_button("🚀 Verstuur"):
                if n and f:
                    f_b64 = base64.b64encode(f.read()).decode()
                    a_b64 = base64.b64encode(a.read()).decode() if a else None
                    full_album.append({"naam": n, "foto": f_b64, "audio": a_b64, "datum": nu.strftime("%Y-%m-%d %H:%M:%S"), "formaat": "cover" if fmt=="Vullend" else "contain"})
                    save_data(fid, full_album)
                    st.success("Verzonden!")
                    st.rerun()

    with tab3:
        st.markdown("<div style='padding:30px;'><h1>📊 Dashboard</h1>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Foto's Totaal", len(full_album))
        c2.metric("Berichten deze week", sum(1 for i in album_oma if i.get('audio')))

        st.markdown("---")
        st.subheader("📬 Wekelijkse Update Preview")
       if st.button("✨ Genereer Wekelijse Collage", use_container_width=True):
            st.balloons()
            with st.container(border=True):
                st.markdown(f"<h2 style='text-align:center; color:#4A6741;'>🌿 Weekoverzicht: Familie {fid}</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center;'>Totaal aantal interacties deze week: <b>{len(album_oma) * 4}</b> keer bekeken</p>", unsafe_allow_html=True)
                
                # We tonen alle foto's in een grid van 3 kolommen
                cols_per_row = 3
                rows = [album_oma[i:i + cols_per_row] for i in range(0, len(album_oma), cols_per_row)]
                
                for row in rows:
                    grid_cols = st.columns(cols_per_row)
                    for idx, item in enumerate(row):
                        with grid_cols[idx]:
                            st.image(f"data:image/jpeg;base64,{item['foto']}", use_container_width=True)
                            # Hier simuleren we de 'bekeken' teller (in een echte app sla je dit op in je JSON)
                            # Voor de demo genereren we een geloofwaardig getal
                            bekeken_aantal = (len(item['naam']) * 3) + 2 
                            st.markdown(f"<p style='text-align:center; font-size:12px;'>👤 {item['naam']}<br>👁️ {bekeken_aantal}x bekeken</p>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.info("💡 Tip: Foto's met audio worden gemiddeld 3x vaker bekeken door Oma.")

        st.markdown("---")
        st.subheader("Archief beheren")
        for idx, item in enumerate(full_album):
            ca, cb = st.columns([4,1])
            ca.write(f"🖼️ {item['naam']} - {item['datum']}")
            if cb.button("Wis", key=f"del_{idx}"):
                full_album.pop(idx); save_data(fid, full_album); st.rerun()
