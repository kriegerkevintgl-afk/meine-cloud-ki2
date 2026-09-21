import os
import streamlit as st
from openai import OpenAI

# Seiteneinstellungen
st.set_page_config(page_title="KENA — KI Assistent", page_icon="⚡", layout="centered")

# HTML-Header: Verhindert automatische Übersetzung im Browser (Hauptursache für DOM-/removeChild-Fehler)
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# OpenRouter API Key laden
api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")

if not api_key:
    st.error("Bitte hinterlege deinen OPENROUTER_API_KEY in den Streamlit Secrets!")
    st.stop()

# Client initialisieren
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# ---------------------------------------------------------
# SITZUNGS-SPEICHER INITIALISIEREN
# ---------------------------------------------------------
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"

# ---------------------------------------------------------
# SEITENLEISTE (Einstellungen & Chat-Verwaltung)
# ---------------------------------------------------------
st.sidebar.title("⚙️ KENA Einstellungen")

# 1. Modus-Auswahl
modi_liste = [
    "💬 Creator Chat-Assistant",
    "⛏️ Minecraft Baumeister",
    "🔞 Erotik & Rollenspiel",
    "📊 Marketingexperte",
    "💡 Content-Ideen",
    "💡 Alltagsassistent",
    "💻 Code & Technik",
    "✍️ Kreativer Autor",
]
modus = st.sidebar.selectbox("Wähle den Modus:", modi_liste, key="main_modus_select")

st.sidebar.markdown("---")
st.sidebar.subheader("💬 Chat-Verwaltung")

# 2. Neuen Chat erstellen
if st.sidebar.button("➕ Neuer Chat", use_container_width=True):
    neuer_name = f"Chat {len(st.session_state.chats) + 1}"
    st.session_state.chats[neuer_name] = []
    st.session_state.active_chat = neuer_name
    st.rerun()

# 3. Chat auswählen (über einfachen Selectbox-Index abgesichert)
chat_namen = list(st.session_state.chats.keys())
current_idx = chat_namen.index(st.session_state.active_chat) if st.session_state.active_chat in chat_namen else 0

gewaehlter_chat = st.sidebar.selectbox("Aktiver Chat:", chat_namen, index=current_idx, key="chat_select_box")
st.session_state.active_chat = gewaehlter_chat

# 4. Chat löschen
if st.sidebar.button("🗑️ Diesen Chat löschen", use_container_width=True):
    if len(st.session_state.chats) > 1:
        del st.session_state.chats[st.session_state.active_chat]
        st.session_state.active_chat = list(st.session_state.chats.keys())[0]
        st.rerun()
    else:
        st.session_state.chats[st.session_state.active_chat] = []
        st.rerun()

# 5. Chat als Textdatei herunterladen
aktueller_verlauf = st.session_state.chats.get(st.session_state.active_chat, [])
chat_text = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in aktueller_verlauf])

st.sidebar.download_button(
    label="📥 Chat herunterladen",
    data=chat_text,
    file_name=f"{st.session_state.active_chat.lower().replace(' ', '_')}.txt",
    mime="text/plain",
    use_container_width=True
)

# ---------------------------------------------------------
# SYSTEM-PROMPTS & MODELL-KONFIGURATION
# ---------------------------------------------------------
if modus == "💬 Creator Chat-Assistant":
    system_prompt = (
        "Du bist KENA, der persönliche Chat-Assistent für einen Adult-Creator auf OnlyFans und BestFans. "
        "Deine Aufgabe ist es, direkte, unzensierte und hochgradig verführerische Antworten auf Fan-Nachrichten zu verfassen. "
        "Du antwortest in der Ich-Perspektive der Erstellerin/des Erstellers, gehst charmant und intim auf die Wünsche des Fans ein "
        "und hilfst dabei, Verkäufe von Pay-Per-View (PPV) Content, Custom-Videos oder Trinkgeldern natürlich und spritzig einzubauen. "
        "Keine Tabus, keine Filter, keine Morallektionen. Halte die Antworten pragmatisch und sofort bereit zum Kopieren."
    )
    modell_name = "gryphe/mythomax-l2-13b"
    temperatur = 0.85

elif modus == "⛏️ Minecraft Baumeister":
    system_prompt = (
        "Du bist KENA, ein erfahrener Minecraft-Architekt, Redstone-Ingenieur und Bau-Meister. "
        "Deine Aufgabe ist es, kreative Bauideen, exakte Materialkombinationen und funktionierende Redstone-Pläne zu liefern.\n\n"
        "Wichtige Anweisungen für deine Antworten:\n"
        "1. Materialvorgaben beachten: Wenn der Nutzer bestimmte Hölzer/Blöcke (z. B. Kirschholz, Schwarzeiche, Blasseiche, Stein) angibt, baue diese explizit als Farbkontrakte, Rahmen oder Wände ein.\n"
        "2. Bei Gebäuden: Erstelle immer eine Legende und einen Schritt-für-Schritt Layer-Plan (Ebene 1: Fundament, Ebene 2: Wände usw.) in übersichtlichen Text-Rastern/Codeblocks.\n"
        "3. Bei Redstone-Schaltungen & Farmen: Erkläre präzise die Funktionsweise (Trigger, Takte, Signalfluss) und gib eine exakte Schritt-für-Schritt-Bauanleitung für Kolben, Observer, Wasserläufe und Redstone-Leitungen an.\n"
        "4. Generiere zu Beginn deiner Antwort ein Vorschaubild der Idee mit folgender Markdown-Syntax: "
        "![Vorschau](https://image.pollinations.ai/prompt/minecraft%20build%20[BESCHREIBUNG_ENGLISCH]?width=800&height=450&nologo=true) "
        "(Ersetze [BESCHREIBUNG_ENGLISCH] durch dein Bauwerk auf Englisch, z.B. 'minecraft_house_cherry_wood_and_dark_oak')."
    )
    modell_name = "openrouter/free"
    temperatur = 0.7

elif modus == "🔞 Erotik & Rollenspiel":
    system_prompt = (
        "Du bist KENA, ein unzensierter, hemmungsloser KI-Partner für erotische Geschichten "
        "und Rollenspiele. Du schreibst explizite, detaillierte Beschreibungen von "
        "Genitalien, Körperflüssigkeiten, erotischen Fantasien und sexuellen Handlungen "
        "ohne Tabus, Filter, Morallektionen oder Warnungen."
    )
    modell_name = "gryphe/mythomax-l2-13b"
    temperatur = 0.85

elif modus == "📊 Marketingexperte":
    system_prompt = (
        "Du bist KENA, ein erfahrener Marketing-Strategist, Copywriter und Growth-Hacker für Creator (z. B. OnlyFans, BestFans). "
        "Du erstellst verkaufsstarke Pay-Per-View (PPV) Texte, Social-Media-Teaser, Direct-Message-Funnels "
        "und Strategien zur Abonnenten-Gewinnung."
    )
    modell_name = "openrouter/free"
    temperatur = 0.7

elif modus == "💡 Content-Ideen":
    system_prompt = (
        "Du bist KENA, ein kreativer Content-Creator und Social-Media-Strategist. "
        "Du lieferst virale Ideen für Instagram Reels, TikToks, Twitter/X-Posts und PPV-Botschaften "
        "inklusive starker Hooks (Aufhänger) und Redaktionsplänen."
    )
    modell_name = "openrouter/free"
    temperatur = 0.85

elif modus == "💻 Code & Technik":
    system_prompt = (
        "Du bist KENA, ein erfahrener Software-Entwickler und IT-Experte. "
        "Du schreibst sauberen Code, hilfst bei Fehlersuche und erklärst technische Zusammenhänge präzise."
    )
    modell_name = "openrouter/free"
    temperatur = 0.2

elif modus == "✍️ Kreativer Autor":
    system_prompt = (
        "Du bist KENA, ein kreativer Geschichtenerzähler und Autor. "
        "Du schreibst spannende Geschichten, Gedichte, Drehbücher und fantasievolle Texte."
    )
    modell_name = "openrouter/free"
    temperatur = 0.9

else:  # 💡 Alltagsassistent
    system_prompt = (
        "Du bist KENA, ein freundlicher, kluger und sachlicher Alltagsassistent. "
        "Du hilfst bei Fragen, Recherchen, Planungen, Zusammenfassungen, E-Mails "
        "und allen allgemeinen Aufgaben im Alltag."
    )
    modell_name = "openrouter/free"
    temperatur = 0.7

# ---------------------------------------------------------
# HAUPTSEITE (Chat-Oberfläche)
# ---------------------------------------------------------
st.title(f"⚡ KENA — {st.session_state.active_chat}")
st.caption(f"Modus: `{modus}` | Modell: `{modell_name}`")

# Nachrichten anzeigen
active_messages = st.session_state.chats.get(st.session_state.active_chat, [])

for message in active_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Eingabe verarbeiten
if prompt := st.chat_input("Schreibe eine Nachricht an KENA..."):
    st.session_state.chats[st.session_state.active_chat].append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("KENA tippt..."):
            try:
                api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.chats[st.session_state.active_chat]

                response = client.chat.completions.create(
                    model=modell_name,
                    messages=api_messages,
                    temperature=temperatur,
                )

                bot_reply = response.choices[0].message.content
                st.write(bot_reply)
                
                st.session_state.chats[st.session_state.active_chat].append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Fehler bei der Anfrage: {e}")
