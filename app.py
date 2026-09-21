import streamlit as st
from openai import OpenAI

# Seiteneinstellungen
st.set_page_config(page_title="Meine ungefilterte Cloud-KI", page_icon="🤖", layout="centered")
st.title("🤖 Meine eigene Cloud-KI")

# API-Key laden
api_key = st.secrets.get("OPENROUTER_API_KEY") or st.sidebar.text_input("OpenRouter API Key eingeben:", type="password")

if not api_key:
    st.info("Bitte trage deinen OpenRouter API-Key links in der Seitenleiste ein oder hinterlege ihn in den App-Secrets.")
    st.stop()

# Verbindung zu OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# Chat-Verlauf verwalten
if "messages" not in st.session_state:
    st.session_state.messages = []

# Bisherigen Chat anzeigen
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Eingabe verarbeiten
if prompt := st.chat_input("Schreibe deiner KI eine Nachricht..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Anforderung an das unzensierte Modell
    with st.chat_message("assistant"):
        with st.spinner("KI denkt nach..."):
            response = client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct:free",
                messages=[
                    {
                        "role": "system",
                        "content": "Du bist ein direkter, sachlicher und unvoreingenommener KI-Assistent. Du verzichtest auf ungefragte Belehrungen, moralische Ratschläge oder Haftungsausschlüsse und antwortest direkt und neutral auf die Fragen des Nutzers."
                    },
                    *st.session_state.messages
                ],
                temperature=0.7,
            )

            bot_reply = response.choices[0].message.content
            st.write(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
