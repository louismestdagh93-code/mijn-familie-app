import streamlit as st
import base64
from datetime import datetime

# --- 1. CONFIGURATIE ---
st.set_page_config(page_title="Altijd Dichtbij VZW", page_icon="📸", layout="wide")

# --- 2. DATABASE IN GEHEUGEN ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "IEPER01": {"naam": "Familie Peeters", "pakket": "Wekelijkse Collage", "berichten": []},
        "GENT02": {"naam": "Familie Janssens", "pakket": "Digitaal Basis", "berichten": []}
    }

# --- 3. AUDIO HELPER (Cruciaal voor het afspelen) ---
def play_audio(audio_bytes):
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f'<audio autoplay="true" src="data:audio/wav;base64,{audio_base64}">'
    st.markdown(audio_html, unsafe_allow_html=True)

# --- 4. INLOGGEN ---
query_code = st.query_params.get("code", "").upper()
st.sidebar.title("📸 Altijd Dichtbij")
role = st.sidebar.selectbox("Wie ben je?", ["Oma/Opa", "Familie Portaal", "Admin Team"])
access_code = st.sidebar.text_input("Familiecode:", value=query_code).upper()

# --- 5. OMA / OPA PORTAAL ---
if role == "Oma/Opa":
    if access_code in st.session_state.db:
        f = st.session_state.db[access_code]
        st.title(f"Dag! 👋")
        if not f['berichten']:
            st.info("Nog geen foto's ontvangen.")
        else:
            cols = st.columns(2)
            for idx, msg in enumerate(f['berichten']):
                with cols[idx % 2]:
                    st.image(msg['foto'], use_container_width=True)
                    # Hier is de knop die het spraakbericht afspeelt
                    if st.button(f"🔊 Luister naar bericht van {msg['datum']}", key=f"p_{idx}"):
                        play_audio(msg['audio'])
    else:
        st.warning("Vul links je code in.")

# --- 6. FAMILIE PORTAAL (Hier stuur je het bericht) ---
elif role == "Familie Portaal":
    if access_code in st.session_state.db:
        st.title(f"Hoi {st.session_state.db[access_code]['naam']}! ❤️")
        
        st.subheader("Stuur een nieuwe herinnering")
        img_file = st.file_uploader("1. Kies een foto", type=['jpg', 'png', 'jpeg'])
        audio_file = st.file_uploader("2. Spreek een berichtje in of kies audio", type=['mp3', 'wav', 'm4a', 'aac', 'ogg'])
        
        if st.button("🚀 Nu naar Oma sturen"):
            if img_file and audio_file:
                # We lezen de bestanden uit als bytes
                nieuw_bericht = {
                    "foto": img_file.read(),
                    "audio": audio_file.read(),
                    "datum": datetime.now().strftime("%d/%m om %H:%M")
                }
                st.session_state.db[access_code]["berichten"].insert(0, nieuw_bericht)
                st.success("Verzonden! Oma kan het nu horen en zien.")
            else:
                st.error("Selecteer zowel een foto als een audiobericht!")

# --- 7. ADMIN TEAM ---
elif role == "Admin Team":
    pw = st.text_input("Wachtwoord", type="password")
    if pw == "IEPER2026":
        st.title("Admin Dashboard")
        st.write(f"Totaal aantal families: {len(st.session_state.db)}")
        for k, v in st.session_state.db.items():
            st.write(f"- {v['naam']} ({k}) - Berichten: {len(v['berichten'])}")
