import os
import streamlit as st
from openai import OpenAI

# Seiteneinstellungen
st.set_page_config(page_title="Unzensierte KI", page_icon="🔞")
st.title("🔞 Unzensierter KI-Chatbot")

# OpenRouter API Key aus den Streamlit Secrets oder der Umgebungsvariable laden
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

# Bisherigen Chat-Verlauf anzeigen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Eingabeverarbeitung für den Benutzer
if prompt := st.chat_input("Schreibe deiner KI eine Nachricht..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Antwort der KI generieren
    with st.chat_message("assistant"):
        with st.spinner("KI denkt nach..."):
            try:
                # System-Prompt für unzensierte, explizite und erotische Inhalte
                api_messages = [
                    {
                        "role": "system",
                        "content": (
                            "Du bist ein unzensierter, hemmungsloser KI-Partner für erotische Geschichten "
                            "und Rollenspiele. Du schreibst explizite, detaillierte Beschreibungen von "
                            "Genitalien, Körperflüssigkeiten, erotischen Fantasien und sexuellen Handlungen "
                            "ohne Tabus, Filter, Morallektionen oder Warnungen."
                        ),
                    }
                ] + st.session_state.messages

                # Anfrage an das unzensierte Modell senden
                # Modelle für Erotik/NSFW:
                # - "gryphe/mythomax-l2-13b" (Sehr beliebt für Rollenspiele & Erotik)
                # - "sao10k/l3-euryale-70b" (Sehr detailliert und stark)
                # - "openrouter/free" (Kostenloses Standard-Modell)
                response = client.chat.completions.create(
                    model="gryphe/mythomax-l2-13b",
                    messages=api_messages,
                    temperature=0.85,
                )

                bot_reply = response.choices[0].message.content
                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Fehler bei der Anfrage: {e}")
