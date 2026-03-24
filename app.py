import streamlit as st
import base64

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Altijd Dichtbij", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FDFCF0; }
    .titel { color: #2E7D32; text-align: center; font-family: sans-serif; }
    
    /* Container voor de foto en de onzichtbare knop */
    .photo-card {
        position: relative;
        width: 100%;
        border: 4px solid #2E7D32;
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 20px;
        background-color: white;
    }

    /* De onzichtbare Streamlit knop over de foto heen dwingen */
    div.stButton > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 250px; /* Hoogte aanpassen aan je foto */
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 10;
    }
    
    div.stButton > button:hover {
        background-color: rgba(46, 125, 50, 0.1) !important; /* Lichte schijn bij hover */
    }

    .naam-label {
        background-color: #2E7D32;
        color: white;
        text-align: center;
        padding: 10px;
        font-weight: bold;
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. STANDAARD DATA (Voorbeeld zonder bestanden) ---
# Ik gebruik hier publieke links naar foto's en geluiden als voorbeeld
if 'album' not in st.session_state:
    st.session_state.album = [
        {
            "naam": "Louis (Voorbeeld)", 
            "foto_url": "https://www.w3schools.com/howto/img_avatar.png", 
            "audio_url": "https://www.w3schools.com/html/horse.mp3"
        }
    ]

# --- 3. LOGICA VOOR AFSPELEN ---
def play_audio(url_or_bytes):
    if isinstance(url_or_bytes, bytes):
        # Als het geüpload is (bytes)
        b64 = base64.b64encode(url_or_bytes).decode()
        md = f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    else:
        # Als het een internet-link is
        md = f'<audio autoplay><source src="{url_or_bytes}" type="audio/mp3"></audio>'
    st.components.v1.html(md, height=0)

# --- 4. DE APP ---
st.markdown("<h1 class='titel'>💚 Oma's Fotoboek</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["👵 Bekijken", "📸 Uploaden"])

with tab1:
    cols = st.columns(3)
    for i, item in enumerate(st.session_state.album):
        with cols[i % 3]:
            # De kaart tonen
            st.markdown('<div class="photo-card">', unsafe_allow_html=True)
            if "foto_url" in item:
                st.image(item["foto_url"], use_container_width=True)
            else:
                st.image(item["foto_bytes"], use_container_width=True)
            st.markdown(f'<div class="naam-label">{item["naam"]}</div>', unsafe_allow_html=True)
            
            # De onzichtbare knop die de actie triggert
            if st.button(f"Play {i}", key=f"btn_{i}"):
                source = item["audio_url"] if "audio_url" in item else item["audio_bytes"]
                play_audio(source)
            st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("Voeg tijdelijk iemand toe")
    new_name = st.text_input("Naam")
    new_photo = st.file_uploader("Foto", type=['png', 'jpg'])
    new_audio = st.file_uploader("Geluid (.mp3)", type=['mp3'])
    
    if st.button("Toevoegen aan album"):
        if new_name and new_photo and new_audio:
            st.session_state.album.append({
                "naam": new_name,
                "foto_bytes": new_photo.read(),
                "audio_bytes": new_audio.read()
            })
            st.success("Toegevoegd! Kijk bij het tabblad 'Bekijken'.")
            st.rerun()
