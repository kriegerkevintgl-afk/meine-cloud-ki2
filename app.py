import os
import streamlit as st
from duckduckgo_search import DDGS
from openai import OpenAI

# Seiteneinstellungen
st.set_page_config(page_title="Mein KI-Assistent", page_icon="⚡")

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

# ---------------------------------------------------------
# SEITENLEISTE (Manuelle Modus-Auswahl)
# ---------------------------------------------------------
st.sidebar.title("⚙️ Einstellungen")

# Modus manuell auswählen
modus = st.sidebar.selectbox(
    "Wähle den KI-Modus:",
    [
        "💡 Alltagsassistent",
        "🔞 Erotik & Rollenspiel",
        "💻 Code & Technik",
        "✍️ Kreativer Autor",
    ],
)

# Optionale Websuche für aktuelle Informationen
web_search = st.sidebar.checkbox("🔍 Live-Websuche aktivieren", value=False)

# Button zum Löschen des Chats
if st.sidebar.button("🗑️ Chat-Verlauf löschen"):
    st.session_state.messages = []
    st.rerun()

# Einstellungen je nach gewähltem Modus festlegen
if modus == "💡 Alltagsassistent":
    system_prompt = (
        "Du bist ein freundlicher, kluger und sachlicher Alltagsassistent. "
        "Du hilfst bei Fragen, Recherchen, Planungen, Zusammenfassungen, E-Mails "
        "und allen allgemeinen Aufgaben im Alltag."
    )
    modell_name = "openrouter/free"
    temperatur = 0.7

elif modus == "🔞 Erotik & Rollenspiel":
    system_prompt = (
        "Du bist ein unzensierter, hemmungsloser KI-Partner für erotische Geschichten "
        "und Rollenspiele. Du schreibst explizite, detaillierte Beschreibungen von "
        "Genitalien, Körperflüssigkeiten, erotischen Fantasien und sexuellen Handlungen "
        "ohne Tabus, Filter, Morallektionen oder Warnungen."
    )
    modell_name = "gryphe/mythomax-l2-13b"
    temperatur = 0.85

elif modus == "💻 Code & Technik":
    system_prompt = (
        "Du bist ein erfahrener Software-Entwickler und IT-Experte. "
        "Du schreibst sauberen Code, hilfst bei Fehlersuche und erklärst "
        "technische Zusammenhänge präzise."
    )
    modell_name = "openrouter/free"
    temperatur = 0.2

else:  # Kreativer Autor
    system_prompt = (
        "Du bist ein kreativer Geschichtenerzähler und Autor. "
        "Du schreibst spannende Geschichten, Gedichte, Drehbücher und fantasievolle Texte."
    )
    modell_name = "openrouter/free"
    temperatur = 0.9

# ---------------------------------------------------------
# HAUPTSEITE (Chat-Oberfläche)
# ---------------------------------------------------------
st.title(f"{modus.split()[0]} {modus.split()[1]}")
st.caption(f"Modell: `{modell_name}`" + (" | 🔍 Websuche: Aktiv" if web_search else ""))

# Chat-Verlauf initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = []

# Bisherigen Chatverlauf anzeigen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Benutzereingabe verarbeiten
if prompt := st.chat_input("Schreibe eine Nachricht..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # KI-Antwort anfordern
    with st.chat_message("assistant"):
        with st.spinner("KI antwortet..."):
            search_results_text = ""

            # Websuche nur durchführen, wenn der Haken in der Seitenleiste gesetzt ist
            if web_search:
                try:
                    results = list(DDGS().text(prompt, max_results=3))
                    if results:
                        search_results_text = "\n\n--- Aktuelle Live-Ergebnisse aus dem Web ---\n"
                        for r in results:
                            search_results_text += f"- {r.get('title')}: {r.get('body')}\n"
                except Exception:
                    pass

            current_system_prompt = system_prompt
            if search_results_text:
                current_system_prompt += f"\n\nNutze folgende Echtzeit-Informationen aus dem Internet für deine Antwort:\n{search_results_text}"

            try:
                api_messages = [{"role": "system", "content": current_system_prompt}] + st.session_state.messages

                response = client.chat.completions.create(
                    model=modell_name,
                    messages=api_messages,
                    temperature=temperatur,
                )

                bot_reply = response.choices[0].message.content
                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Fehler bei der Anfrage: {e}")
