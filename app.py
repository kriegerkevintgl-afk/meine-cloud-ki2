import streamlit as st
import os
from openai import OpenAI

st.set_page_config(page_title="Meine KI", page_icon="🤖")
st.title("🤖 Meine eigene KI")

# OpenRouter API Key aus den Streamlit Secrets holen
api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")

if not api_key:
    st.error("Bitte hinterlege deinen OPENROUTER_API_KEY in den Streamlit Secrets!")
    st.stop()

# OpenAI Client für OpenRouter konfigurieren
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# Chat-Verlauf initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = []

# Bisherige Nachrichten anzeigen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Eingabeverarbeitung
if prompt := st.chat_input("Schreibe deiner KI eine Nachricht..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Antwort von der KI anfordern
    with st.chat_message("assistant"):
        with st.spinner("KI denkt nach..."):
            try:
                api_messages = [
                    {"role": "system", "content": "Du bist ein direkter, sachlicher und hilfsbereiter KI-Assistent."}
                ] + st.session_state.messages

                response = client.chat.completions.create(
                    model="openrouter/free",  # wählt automatisch immer ein funktionierendes kostenloses Modell aus
                    messages=api_messages,
                    temperature=0.7,
                )
                
                bot_reply = response.choices[0].message.content
                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Fehler bei der Anfrage: {e}")
