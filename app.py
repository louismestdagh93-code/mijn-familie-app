import streamlit as st
import base64
import json
import os

# 1. CONFIG
st.set_page_config(page_title="Altijd Dichtbij", layout="wide", initial_sidebar_state="collapsed")

# 2. OPSLAG LOGICA
def get_file_path(family_id):
    return f"data_{family_id}.json"

def load_family_data(family_id):
    path = get_file_path(family_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_family_data(family_id, data):
    with open(get_file_path(family_id), "w") as f:
        json.dump(data, f)

# 3. SESSIE & CSS
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

st.markdown("""
<style>
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #FDFCF0; }
    header, footer, #MainMenu {visibility: hidden;}

    .stTabs [data-baseweb="tab-list"] { background-color: #2E7D32; padding: 0px; }
    .stTabs [data-baseweb="tab"] {
        height: 80px;
        color: white !important;
        font-size: 1.4rem !important;
        font-weight: bold;
        flex-grow: 1;
    }
    .stTabs [aria-selected="true"] { background-color: #FDFCF0 !important; color: #2E7D32 !important; }

    .photo-card {
        border: 4px solid #2E7D32;
        border-radius: 20px;
        background: white;
        margin: 10px;
        overflow: hidden;
    }
    .name-tag { background: #2E7D32; color: white; padding: 15px; font-size: 22px; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 4. LOGIN OF APP
if not st.session_state.logged_in:
    st.markdown("<div style='padding:80px; text-align:center;'><h1>💚 Altijd Dichtbij</h1>", unsafe_allow_html=True)
    with st.form("login"):
        fid = st.text_input("Familienaam").strip()
        code = st.text_input("Code", type="password")
        if st.form_submit_button("Inloggen"):
            if fid and code == "STARTUP2026":
                st.session_state.logged_in = True
                st.session_state.family_id = fid
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    fid = st.session_state.family_id
    album = load_family_data(fid)

    tab_oma, tab_fam, tab_admin = st.tabs(["👵 OMA", "📤 UPLOAD", "⚙️ ADMIN"])

    # --- OMA PORTAAL ---
    with tab_oma:
        if not album:
            st.info("Nog geen foto's aanwezig.")
        else:
            cols = st.columns(2)
            for i, item in enumerate(album):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="photo-card">
                        <img src="data:image/jpeg;base64,{item['foto']}" style="width:100%; height:350px; object-fit:cover;">
                        <div class="name-tag">{item['naam']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if item.get('audio'):
                        if st.button(f"🔊 Luister naar {item['naam']}", key=f"btn_{i}", use_container_width=True):
                            audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{item["audio"]}" type="audio/mp3"></audio><script>document.querySelector("audio").play();</script>'
                            st.components.v1.html(audio_html, height=0)

    # --- UPLOAD ---
    with tab_fam:
        st.markdown("<div style='padding:20px;'>", unsafe_allow_html=True)
        with st.form("upload", clear_on_submit=True):
            n = st.text_input("Naam")
            f = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
            audio_data = st.audio_input("Spreek bericht in (optioneel)")
            if st.form_submit_button("🚀 Naar Oma sturen"):
                if n and f:
                    f_b64 = base64.b64encode(f.read()).decode()
                    a_b64 = base64.b64encode(audio_data.read()).decode() if audio_data else None
                    album.append({"naam": n, "foto": f_b64, "audio": a_b64})
                    save_family_data(fid, album)
                    st.rerun()

    # --- ADMIN (INDIVIDUEEL VERWIJDEREN) ---
    with tab_admin:
        st.markdown("<div style='padding:20px;'>", unsafe_allow_html=True)
        st.subheader(f"Beheer album: {fid}")
        
        if not album:
            st.write("Het album is leeg.")
        else:
            for idx, item in enumerate(album):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"🖼️ **{item['naam']}** ({'met geluid' if item['audio'] else 'zonder geluid'})")
                with col2:
                    # De individuele verwijderknop
                    if st.button(f"🗑️ Verwijder", key=f"del_{idx}"):
                        album.pop(idx) # Verwijder item uit lijst
                        save_family_data(fid, album) # Sla aangepaste lijst op
                        st.rerun() # Ververs scherm
        
        st.markdown("---")
        if st.button("🚪 Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
