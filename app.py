import streamlit as st
import base64
import json
import os
from datetime import datetime, timedelta

# ... (Houd alle hulpfuncties en config hetzelfde als in de vorige versie) ...

# 4. AANGEPASTE CSS (Nu met flexibele object-fit)
st.markdown("""
<style>
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #FDFCF0; }
    header, footer, #MainMenu {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { background-color: #2E7D32; padding: 0px; }
    .stTabs [data-baseweb="tab"] { height: 80px; color: white !important; font-size: 1.4rem !important; font-weight: bold; flex-grow: 1; }
    .stTabs [aria-selected="true"] { background-color: #FDFCF0 !important; color: #2E7D32 !important; }
    
    .photo-card { 
        border: 5px solid #2E7D32; 
        border-radius: 25px; 
        background: #000; /* Zwarte achtergrond voor als de foto 'past' */
        margin: 15px; 
        overflow: hidden; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.15); 
    }
    .name-tag { background: #2E7D32; color: white; padding: 15px; font-size: 24px; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ... (Login logica blijft hetzelfde) ...

if st.session_state.get('logged_in'):
    fid = st.session_state.family_id
    album = load_and_clean_data(fid)
    tab_oma, tab_fam, tab_admin = st.tabs(["👵 OMA", "📤 UPLOAD", "⚙️ BEHEER"])

    # --- TAB 1: OMA PORTAAL ---
    with tab_oma:
        if not album:
            st.info("Nog geen foto's.")
        else:
            cols = st.columns(2)
            for i, item in enumerate(album):
                # We halen de gekozen fit op, standaard is 'cover' (vullend)
                fit_style = item.get('formaat', 'cover') 
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="photo-card">
                        <img src="data:image/jpeg;base64,{item['foto']}" 
                             style="width:100%; height:380px; object-fit:{fit_style};">
                        <div class="name-tag">{item['naam']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if item.get('audio'):
                        if st.button(f"🔊 Luister naar {item['naam']}", key=f"btn_{i}", use_container_width=True):
                            audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{item["audio"]}" type="audio/mp3"></audio><script>document.querySelector("audio").play();</script>'
                            st.components.v1.html(audio_html, height=0)

    # --- TAB 2: FAMILIE UPLOAD ---
    with tab_fam:
        with st.form("upload", clear_on_submit=True):
            n = st.text_input("Naam")
            f = st.file_uploader("Kies een foto", type=['jpg', 'jpeg', 'png'])
            
            # DE NIEUWE KEUZE:
            st.write("📐 **Hoe moet de foto getoond worden?**")
            formaat_keuze = st.radio(
                "Kies weergave:",
                ["Vullend (snijdt randen weg)", "Hele foto (geen verlies, zwarte balkjes)"],
                index=0
            )
            # Zet de tekst om naar CSS termen
            fit_value = "cover" if "Vullend" in formaat_keuze else "contain"
            
            a = st.audio_input("Geluid")
            if st.form_submit_button("🚀 Uploaden"):
                if n and f:
                    f_b64 = base64.b64encode(f.read()).decode()
                    a_b64 = base64.b64encode(a.read()).decode() if a else None
                    datum_nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Sla de keuze mee op in de JSON
                    album.append({
                        "naam": n, 
                        "foto": f_b64, 
                        "audio": a_b64, 
                        "datum": datum_nu, 
                        "formaat": fit_value
                    })
                    save_family_data(fid, album)
                    st.success("Foto staat erop!")
                    st.rerun()
                    
    # ... (Admin tab blijft hetzelfde) ...
