import streamlit as st
import base64
from datetime import datetime

# --- 1. CONFIGURATIE & STYLING ---
st.set_page_config(page_title="Altijd Dichtbij VZW", page_icon="📸", layout="wide")

# Warme vzw-stijl toevoegen
st.markdown("""
    <style>
    .main { background-color: #fffaf0; }
    .stButton>button { border-radius: 20px; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIMULATIE DATABASE (Sla dit op in de sessie) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "IEPER01": {"naam": "Familie Peeters", "pakket": "Wekelijkse Collage", "berichten": []},
        "GENT02": {"naam": "Familie Janssens", "pakket": "Digitaal Basis", "berichten": []}
    }

# --- 3. HELPER FUNCTIES ---
def get_audio_html(audio_bytes):
    """Genereert HTML om audio automatisch af te spelen."""
    audio_base64 = base64.b64encode(audio_bytes).decode()
    return f'<audio autoplay src="data:audio/wav;base64,{audio_base64}">'

# --- 4. URL & INLOG LOGICA ---
# Check of er een code in de URL staat (bijv. ?code=IEPER01)
query_code = st.query_params.get("code", "").upper()

st.sidebar.title("📸 Altijd Dichtbij")
role = st.sidebar.selectbox("Inloggen als:", ["Oma/Opa", "Familie Portaal", "Admin Team"])
access_code = st.sidebar.text_input("Voer je familiecode in:", value=query_code).upper()

# --- 5. OMA / OPA PORTAAL (De Kijk-App) ---
if role == "Oma/Opa":
    if access_code in st.session_state.db:
        f = st.session_state.db[access_code]
        st.title(f"Dag! 👋")
        st.subheader(f"Berichten van {f['naam']}")
        
        if not f['berichten']:
            st.info("Nog geen foto's. Vraag je familie om een herinnering te sturen!")
        else:
            cols = st.columns(2)
            for idx, msg in enumerate(f['berichten']):
                with cols[idx % 2]:
                    st.image(msg['foto'], use_container_width=True)
                    if st.button(f"▶️ Luister naar het bericht bij deze foto", key=f"play_{idx}"):
                        st.markdown(get_audio_html(msg['audio']), unsafe_allow_html=True)
                    st.caption(f"Verzonden op: {msg['datum']}")
    else:
        st.warning("Vul je code in aan de linkerkant om je foto's te zien.")

# --- 6. FAMILIE PORTAAL (Uploaden & Pakketten) ---
elif role == "Familie Portaal":
    if access_code in st.session_state.db:
        f = st.session_state.db[access_code]
        st.title(f"Hoi {f['naam']}! ❤️")
        st.write(f"Huidig pakket: **{f['pakket']}**")
        
        tab1, tab2 = st.tabs(["Stuur Foto", "Abonnement Beheren"])
        
        with tab1:
            st.subheader("Nieuwe herinnering voor Oma")
            img = st.file_uploader("Kies een mooie foto", type=['jpg', 'png', 'jpeg'])
            aud = st.file_uploader("Spreek een berichtje in (Audio)", type=['mp3', 'wav', 'm4a'])
            
            if st.button("Verstuur nu"):
                if img and aud:
                    new_msg = {
                        "foto": img.read(),
                        "audio": aud.read(),
                        "datum": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    st.session_state.db[access_code]["berichten"].insert(0, new_msg)
                    st.success("Gelukt! Oma kan het meteen zien.")
                else:
                    st.error("Vergeet de foto of het geluid niet!")
                    
        with tab2:
            st.subheader("Kies je ondersteuning")
            st.write("2 weken gratis proberen, daarna:")
            st.radio("Pakketkeuze:", [
                "€ 10/mnd - Digitaal Basis (Alleen de App)",
                "€ 15/mnd - Maandelijkse Kaart (App + 1x per maand post)",
                "€ 20/mnd - Wekelijkse Collage (App + elke week post op de mat)"
            ])
            st.button("Opslaan & Betalen via Stripe")

# --- 7. ADMIN PORTAAL (Voor jou en je 2 vrienden) ---
elif role == "Admin Team":
    admin_pw = st.text_input("Admin Wachtwoord", type="password")
    if admin_pw == "IEPER2026": # Je geheime code voor de demo
        st.title("🚀 Startup Dashboard")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Families", len(st.session_state.db))
        col2.metric("Omzet (geschat)", f"€ {len(st.session_state.db)*15}")
        col3.metric("Actieve Collages", "1")

        st.subheader("Overzicht Families & Printopdrachten")
        for code, data in st.session_state.db.items():
            exp = st.expander(f"📦 {data['naam']} ({data['pakket']})")
            exp.write(f"Code: {code}")
            if data['pakket'] != "Digitaal Basis":
                if exp.button(f"Genereer PDF voor {data['naam']}"):
                    exp.success("PDF met de laatste 4 foto's klaar voor de printer!")
        
        with st.sidebar:
            st.divider()
            if st.button("Nieuwe Familie Toevoegen"):
                st.session_state.db["NIEUW03"] = {"naam": "Nieuwe Test Familie", "pakket": "Digitaal Basis", "berichten": []}
                st.rerun()
    else:
        st.info("Voer het admin-wachtwoord in.")
