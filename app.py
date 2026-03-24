import streamlit as st
import base64

# --- 1. CONFIGURATIE ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide")

# --- 2. DE DATABASE (Tijdelijk geheugen) ---
# LET OP: Als je de code aanpast of herstart, moet je de familie opnieuw aanmaken via Admin.
if 'db' not in st.session_state:
    st.session_state.db = {}

# --- 3. AUDIO HELPER ---
def get_audio_html(audio_bytes):
    audio_base64 = base64.b64encode(audio_bytes).decode()
    return f'<audio autoplay src="data:audio/wav;base64,{audio_base64}">'

# --- 4. NAVIGATIE IN DE ZIJBALK ---
st.sidebar.title("📸 Altijd Dichtbij")
keuze = st.sidebar.selectbox("Ga naar:", ["Oma/Opa Portaal", "Familie Portaal", "Admin Dashboard"])
code = st.sidebar.text_input("Voer je code in:", type="password").upper()

# --- 5. OMA / OPA PORTAAL ---
if keuze == "Oma/Opa Portaal":
    if code in st.session_state.db:
        fami = st.session_state.db[code]
        st.title(f"Hallo! 👋")
        st.subheader(f"Berichten van {fami['naam']}")
        
        if not fami['berichten']:
            st.info("Nog geen foto's aanwezig. Vraag de familie om iets te sturen!")
        else:
            cols = st.columns(3)
            for idx, msg in enumerate(fami['berichten']):
                with cols[idx % 3]:
                    if st.button(f"Hoor bericht! 🔊", key=f"snd_{idx}"):
                        st.markdown(get_audio_html(msg['audio']), unsafe_allow_html=True)
                    st.image(msg['foto'], use_container_width=True)
                    st.caption(f"Verzonden op: {msg['datum']}")
    else:
        st.warning("Voer een geldige familiecode in om de foto's te zien.")

# --- 6. FAMILIE PORTAAL ---
elif keuze == "Familie Portaal":
    if code in st.session_state.db:
        st.title(f"Portaal voor Familie {st.session_state.db[code]['naam']}")
        
        uploaded_img = st.file_uploader("Kies een foto", type=['jpg', 'png', 'jpeg'])
        uploaded_aud = st.file_uploader("Kies een geluidsbestand", type=['mp3', 'wav', 'm4a'])
        
        if st.button("Verstuur naar de tablet"):
            if uploaded_img and uploaded_aud:
                nieuw_bericht = {
                    "foto": uploaded_img.read(),
                    "audio": uploaded_aud.read(),
                    "datum": "Vandaag"
                }
                st.session_state.db[code]["berichten"].insert(0, nieuw_bericht)
                st.success("Verzonden! Bekijk het nu in het Oma Portaal.")
            else:
                st.error("Selecteer zowel een foto als een geluidsbestand.")
    else:
        st.error("Deze code bestaat nog niet. Maak de familie eerst aan in het Admin Dashboard.")

# --- 7. ADMIN DASHBOARD ---
elif keuze == "Admin Dashboard":
    # Gebruik hier je vaste admin-wachtwoord: IEPER2026
    if code == "IEPER2026":
        st.title("🚀 Admin Beheer")
        
        st.subheader("Nieuwe Familie Toevoegen")
        nieuwe_naam = st.text_input("Naam van de familie (bijv. Peeters)")
        nieuwe_code = st.text_input("Kies een simpele code (bijv. OMA1)").upper()
        
        if st.button("Registreer Familie"):
            if nieuwe_naam and nieuwe_code:
                st.session_state.db[nieuwe_code] = {"naam": nieuwe_naam, "berichten": []}
                st.success(f"Familie {nieuwe_naam} is aangemaakt met code {nieuwe_code}!")
        
        st.divider()
        st.write("Geregistreerde codes:", list(st.session_state.db.keys()))
    else:
        st.info("Voer het admin-wachtwoord in (IEPER2026) om families te beheren.")
