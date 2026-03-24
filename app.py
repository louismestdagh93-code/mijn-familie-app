import streamlit as st
import base64

# --- CONFIGURATIE ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide")

# --- SIMULATIE DATABASE (Straks SQL) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "families": {
            "IEPER01": {"naam": "Familie Peeters", "berichten": []},
            "GENT02": {"naam": "Familie Janssens", "berichten": []}
        }
    }

# --- HELPER FUNCTIES ---
def get_audio_html(audio_bytes):
    """Genereert HTML om audio automatisch af te spelen bij een klik."""
    audio_base64 = base64.b64encode(audio_bytes).decode()
    return f'<audio autoplay src="data:audio/wav;base64,{audio_base64}">'

# --- SIDEBAR INLOG ---
st.sidebar.title("🔐 Inloggen")
role = st.sidebar.selectbox("Wie ben je?", ["Oma/Opa", "Familie", "Admin (Team)"])
access_code = st.sidebar.text_input("Toegangscode", type="password").upper()

# --- 1. OMA / OPA PORTAAL (De 'Kijk-App') ---
if role == "Oma/Opa":
    if access_code in st.session_state.db["families"]:
        familie = st.session_state.db["families"][access_code]
        st.title(f"Hallo! 👋")
        st.subheader(f"Berichten van {familie['naam']}")
        
        if not familie['berichten']:
            st.info("Nog geen foto's ontvangen. Vraag de familie om iets te sturen!")
        else:
            # We tonen de foto's in een grid
            cols = st.columns(3)
            for idx, msg in enumerate(familie['berichten']):
                with cols[idx % 3]:
                    # De 'knop' is de afbeelding
                    if st.button(f"Klik op mij! 📸", key=f"btn_{idx}"):
                        # Als er op de knop/foto geklikt wordt, spelen we geluid af
                        st.markdown(get_audio_html(msg['audio']), unsafe_allow_html=True)
                        st.success("Audio wordt afgespeeld...")
                    
                    st.image(msg['foto'], use_container_width=True)
                    st.caption(f"Gestuurd op: {msg['datum']}")
    else:
        st.warning("Voer een geldige code in om je foto's te zien.")

# --- 2. FAMILIE PORTAAL (De 'Upload-App') ---
elif role == "Familie":
    if access_code in st.session_state.db["families"]:
        familie = st.session_state.db["families"][access_code]
        st.title(f"Portaal voor {familie['naam']}")
        
        with st.expander("➕ Nieuw bericht sturen", expanded=True):
            uploaded_photo = st.file_uploader("Kies een foto", type=['jpg', 'png', 'jpeg'])
            uploaded_audio = st.file_uploader("Neem geluid op of kies bestand", type=['mp3', 'wav', 'm4a'])
            
            if st.button("Verstuur naar Oma"):
                if uploaded_photo and uploaded_audio:
                    nieuw_bericht = {
                        "foto": uploaded_photo.read(),
                        "audio": uploaded_audio.read(),
                        "datum": "24 Maart 2026" # Straks automatische tijd
                    }
                    st.session_state.db["families"][access_code]["berichten"].insert(0, nieuw_bericht)
                    st.success("Verstuurd! Oma kan het nu bekijken.")
                else:
                    st.error("Upload zowel een foto als een audiobericht.")
    else:
        st.error("Code niet herkend.")

# --- 3. ADMIN PORTAAL (Voor jou en je 2 vrienden) ---
elif role == "Admin (Team)":
    if access_code == "STARTUP2026": # Je geheime admin code
        st.title("🚀 Admin Dashboard")
        st.write("Beheer hier je vzw / startup.")
        
        # Statistieken
        col1, col2 = st.columns(2)
        col1.metric("Totaal Families", len(st.session_state.db["families"]))
        
        # Familiebeheer
        st.subheader("Geregistreerde Families")
        for code, data in st.session_state.db["families"].items():
            with st.container():
                st.write(f"**{data['naam']}** (Code: {code})")
                st.write(f"Aantal berichten: {len(data['berichten'])}")
                st.divider()
        
        # Nieuwe familie toevoegen
        with st.expander("Nieuwe Familie Toevoegen"):
            new_name = st.text_input("Naam Familie")
            new_code = st.text_input("Nieuwe Code (bijv. IEPER02)").upper()
            if st.button("Voeg toe"):
                st.session_state.db["families"][new_code] = {"naam": new_name, "berichten": []}
                st.success(f"{new_name} toegevoegd!")
    else:
        st.error("Admin toegang geweigerd.")
