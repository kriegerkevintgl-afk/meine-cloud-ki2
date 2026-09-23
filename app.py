import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io

# 1. Seitenkonfiguration
st.set_page_config(
    page_title="KENA Vision",
    page_icon="📸",
    layout="centered"
)

st.title("KENA Vision 📸💬")
st.markdown("Lade ein Bild hoch und stelle KENA eine Frage dazu.")

# 2. OpenAI Client initialisieren
# SICHERHEITSHINWEIS: API-Key NIEMALS direkt in den Code schreiben!
# Wir holen ihn aus den Streamlit Secrets (siehe unten).
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except KeyError:
    st.error("❌ OpenAI API-Key wurde nicht gefunden. Bitte konfiguriere die Streamlit Secrets.")
    st.stop()
except Exception as e:
    st.error(f"❌ Fehler bei der Initialisierung: {e}")
    st.stop()

# 3. Chat-Verlauf und hochgeladenes Bild im Session State initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_uploaded_file_id" not in st.session_state:
    st.session_state.last_uploaded_file_id = None

# 4. Hilfsfunktion: Bild für die API kodieren
def encode_uploaded_image(uploaded_file):
    """Liest ein hochgeladenes Streamlit-Bild und kodiert es als Base64-String."""
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# --- HAUPTBEREICH: Chat und Anzeige ---

# Zeige bisherige Chat-Nachrichten an
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Wenn die Nachricht ein Bild enthält (nur beim Nutzer möglich)
        if "image_b64" in message:
            # Konvertiere Base64 zurück in ein PIL-Bild zur Anzeige
            img_data = base64.b64decode(message["image_b64"])
            img = Image.open(io.BytesIO(img_data))
            st.image(img, caption="Hochgeladenes Bild", use_container_width=True)
        # Zeige den Textinhalt an
        st.markdown(message["content"])

# --- EINGABEBEREICH: Bild-Uploader und Text-Eingabe ---

# 5. Bild-Uploader in der Seitenleiste
with st.sidebar:
    st.header("Bild hochladen")
    uploaded_file = st.file_uploader(
        "Wähle ein Bild aus (png, jpg, jpeg)", 
        type=["png", "jpg", "jpeg"],
        key="image_uploader"
    )
    
    # Vorschau des hochgeladenen Bildes in der Seitenleiste
    if uploaded_file:
        st.image(uploaded_file, caption="Vorschau", use_container_width=True)
        st.info("Beschreibe das Bild unten im Chat-Feld.")

# 6. Text-Eingabefeld (Chat Input)
if user_prompt := st.chat_input("Frage KENA etwas zum Bild..."):

    # A) Neue Nachricht des Nutzers verarbeiten
    new_user_message = {"role": "user", "content": user_prompt}
    
    # Prüfen, ob ein *neues* Bild hochgeladen wurde, das noch nicht im Verlauf ist
    if uploaded_file and uploaded_file.file_id != st.session_state.last_uploaded_file_id:
        # Kodieren und zur Nachricht hinzufügen
        base64_image = encode_uploaded_image(uploaded_file)
        new_user_message["image_b64"] = base64_image
        # ID aktualisieren, um doppeltes Kodieren zu verhindern
        st.session_state.last_uploaded_file_id = uploaded_file.file_id

    # Nutzer-Nachricht im State speichern und anzeigen
    st.session_state.messages.append(new_user_message)
    with st.chat_message("user"):
        if "image_b64" in new_user_message:
            st.image(uploaded_file, caption="Hochgeladenes Bild", use_container_width=True)
        st.markdown(user_prompt)

    # B) KENA-Antwort generieren (API Call)
    with st.chat_message("assistant"):
        with st.spinner("KENA analysiert..."):
            try:
                # API Payload vorbereiten
                # Wir nutzen 'gpt-4o', da es nativ multimodale Inputs (Text+Bild) versteht.
                
                # Grundstruktur für die letzte Nutzer-Nachricht
                user_content = [{"type": "text", "text": user_prompt}]
                
                # Wenn das Bild in der Nachricht enthalten ist, füge es zum Payload hinzu
                if "image_b64" in new_user_message:
                    user_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{new_user_message['image_b64']}"
                        }
                    })

                # Wir senden nur die letzte Nutzer-Nachricht mit Bild,
                # aber die gesamte Texthistorie für den Kontext.
                api_messages = []
                for msg in st.session_state.messages[:-1]:
                    api_messages.append({"role": msg["role"], "content": msg["content"]})
                
                # Letzte multimodale Nachricht hinzufügen
                api_messages.append({"role": "user", "content": user_content})

                # API-Anfrage
                response = client.chat.completions.create(
                    model="gpt-4o", # oder gpt-4o-mini
                    messages=api_messages,
                    max_tokens=1000,
                )
                
                # Antwort verarbeiten
                assistant_reply = response.choices[0].message.content
                st.markdown(assistant_reply)
                
                # KENA-Antwort im Verlauf speichern
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                
            except Exception as e:
                st.error(f"⚠️ Fehler bei der Kommunikation mit OpenAI: {e}")
