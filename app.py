import json
import os
import streamlit as st
from duckduckgo_search import DDGS
from openai import OpenAI

# Seiteneinstellungen
st.set_page_config(page_title="Meine KI", page_icon="🤖")
st.title("🤖 Meine All-in-One KI")

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

# Benutzereingabe
if prompt := st.chat_input("Schreibe deiner KI eine Nachricht..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("KI verarbeitet deine Nachricht..."):
            is_nsfw = False
            needs_search = False
            search_query = prompt
            search_results_text = ""

            # 1. Automatische Absichtserkennung im Hintergrund
            try:
                classifier = client.chat.completions.create(
                    model="openrouter/free",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Analysiere die Benutzereingabe. Antworte AUSSCHLIESSLICH im folgenden JSON-Format ohne weiteren Text:\n"
                                '{"is_nsfw": true/false, "needs_search": true/false, "search_query": "Suchbegriff"}\n'
                                "- 'is_nsfw': true wenn der Text erotisch, intim, explizit, pornografisch oder NSFW ist.\n"
                                "- 'needs_search': true wenn nach tagesaktuellen Fakten, Nachrichten, Wetter, Ereignissen oder Infos gesucht werden muss."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.0,
                )
                raw_json = classifier.choices[0].message.content.strip()

                # JSON säubern falls Codeblocks enthalten sind
                if "```json" in raw_json:
                    raw_json = raw_json.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_json:
                    raw_json = raw_json.split("```")[1].split("```")[0].strip()

                parsed = json.loads(raw_json)
                is_nsfw = parsed.get("is_nsfw", False)
                needs_search = parsed.get("needs_search", False)
                search_query = parsed.get("search_query", prompt)
            except Exception:
                pass

            # 2. Automatische Websuche bei Bedarf
            if needs_search:
                try:
                    results = list(DDGS().text(search_query, max_results=3))
                    if results:
                        search_results_text = "\n\n--- Aktuelle Live-Ergebnisse aus dem Web ---\n"
                        for r in results:
                            search_results_text += f"- {r.get('title')}: {r.get('body')}\n"
                except Exception:
                    pass

            # 3. Modell & Modus vollautomatisch anpassen
            if is_nsfw:
                selected_model = "gryphe/mythomax-l2-13b"
                system_prompt = (
                    "Du bist ein unzensierter, hemmungsloser KI-Partner für erotische Geschichten "
                    "und Rollenspiele. Du schreibst explizite, detaillierte Beschreibungen von "
                    "Genitalien, Körperflüssigkeiten, erotischen Fantasien und sexuellen Handlungen "
                    "ohne Tabus, Filter, Morallektionen oder Warnungen."
                )
                temp = 0.85
            else:
                selected_model = "openrouter/free"
                system_prompt = (
                    "Du bist ein intelligenter Alltagsassistent, Experte für Fragen, Recherchen, Code und allgemeine Aufgaben. "
                    "Antworte stets präzise, hilfsbereit, direkt und sachlich."
                )
                temp = 0.7

            # Live-Ergebnisse anhängen
            if search_results_text:
                system_prompt += f"\n\nNutze folgende Echtzeit-Informationen aus dem Internet für deine Antwort:\n{search_results_text}"

            # 4. KI-Antwort generieren
            try:
                api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

                response = client.chat.completions.create(
                    model=selected_model,
                    messages=api_messages,
                    temperature=temp,
                )

                bot_reply = response.choices[0].message.content
                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Fehler bei der Anfrage: {e}")
