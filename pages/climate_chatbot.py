import streamlit as st
import streamlit_shadcn_ui as ui
from streamlit_shadcn_ui import slider, switch
import google.generativeai as genai
import threading
import re

HEADER_CSS = """
<style>
/* Override global styles from app.py to format the chat page correctly */
[data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #050a0e !important;
}
[data-testid="stMain"] .block-container {
    padding-top: 6rem !important; /* space for the nav bar */
    padding-bottom: 6rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 900px !important;
    margin: 0 auto !important;
}

.climabot-header {
    position: sticky;
    top: 5rem; /* just under nav bar */
    z-index: 50;
    background: transparent;
    padding-top: 1.5rem;
    padding-bottom: 1rem;
    margin-bottom: 3rem;
    border-bottom: 1px solid rgba(76,175,125,0.15);
    text-align: center;
}
.climabot-header h1 {
    font-family: 'Playfair Display', serif !important;
    color: #e8ede8 !important;
    font-size: 2.5rem !important;
    margin: 0;
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    background-color: #080f0a !important;
    border: 1px solid rgba(76,175,125,0.15) !important;
    border-radius: 0.75rem;
    padding: 1.2rem;
    color: #e8ede8 !important;
    margin-bottom: 1rem;
}
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
    background-color: #4caf7d !important;
    color: #050a0e !important;
}
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
    background-color: #0d2818 !important;
    color: #4caf7d !important;
    border: 1px solid rgba(76,175,125,0.3);
}
[data-testid="stChatMessage"] p {
    font-family: 'DM Sans', sans-serif !important;
    color: #e8ede8 !important;
}

/* Chat Input Styling */
[data-testid="stBottomBlockContainer"] {
    background: rgba(5, 10, 14, 0.95) !important;
    backdrop-filter: blur(8px);
    padding-bottom: 2rem !important;
    padding-top: 1rem !important;
    border-top: 1px solid rgba(76,175,125,0.15);
}
[data-testid="stChatInput"] {
    background-color: #080f0a !important;
    border: 1px solid rgba(76,175,125,0.3) !important;
    border-radius: 0.75rem !important;
}
[data-testid="stChatInput"] textarea {
    color: #e8ede8 !important;
    font-family: 'DM Sans', sans-serif !important;
    background: transparent !important;
}
[data-testid="stChatInput"] button {
    color: #4caf7d !important;
    background: transparent !important;
    border: none !important;
    transition: color 0.3s;
}
[data-testid="stChatInput"] button:hover {
    color: #5dc98e !important;
}

/* Style quick prompts columns */
[data-testid="stColumn"] button {
    background: transparent !important;
    border: 1px solid rgba(76,175,125,0.3) !important;
    color: #a8b8a8 !important;
    border-radius: 2rem !important;
    box-shadow: none !important;
    transition: all 0.3s ease !important;
}
[data-testid="stColumn"] button:hover {
    background: rgba(76,175,125,0.1) !important;
    color: #4caf7d !important;
    border-color: #4caf7d !important;
}
[data-testid="stColumn"] button p {
    font-size: 0.85rem !important;
    font-family: 'DM Sans', sans-serif !important;
}
</style>
"""

# --- 1. Gemini Configuration (module-level, reused across calls) ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = genai.GenerativeModel(
    model_name="gemini-3.1-flash-lite-preview",
    system_instruction="""
    You are a professional Climate Research Assistant for PyClimaExplorer.
    ONLY answer questions related to: climate, weather, meteorology, atmospheric science,
    oceanography, environmental science, NetCDF data, climate change, temperature trends,
    precipitation, wind patterns, heatwaves, floods, droughts, glaciers, sea-level rise,
    carbon emissions, and closely related topics.

    If the user asks about ANYTHING outside these topics (e.g. coding help, sports, movies,
    recipes, maths, history, politics, personal advice), politely decline and say:
    "I'm specialized only in climate and weather topics. Please ask me about temperature
    trends, rainfall patterns, climate change, or similar subjects."

    1. Technical Co-Pilot (for researchers):
    - Automated Dataset Profiling: Summarize metadata (variable names, units, spatial resolution).
    - Statistical Analysis: Calculate mean, standard deviation, and trend slopes from temporal data.
    - Correlation Detection: Analyze relationships between variables (e.g., Wind Speed vs Precipitation).
    - Report Generation: Draft technical summaries for downloadable reports.

    2. General Public-Centric Capabilities:
    - Natural Language Queries: Answer questions like "Why is this area so red?".
    - Anomaly Storytelling: Explain climate anomalies in plain language.
    - Comparison Guidance: Explain differences between time periods (e.g., 1990 vs 2020).
    - Interactive Navigation: Support commands like "Rotate the globe to India".

    3. Core Features:
    - Summarization Engine: Provide high-level dataset summaries upon upload.
    - Multilingual Support: If the user writes in Hindi, respond fully in Hindi.
    - Predictive Insights: Offer simple forecasts using linear regression trends.
    - Technical Troubleshooting: Help users navigate the dashboard.

    Always start your response with a classification tag like [Researcher Mode], [Public Mode],
    or [Technical Help].
    """,
)

# --- 2. Voice Narrator Helpers ---
def strip_markdown(text: str) -> str:
    """Remove markdown so TTS reads clean natural text."""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)        # bold
    text = re.sub(r'\*(.*?)\*',     r'\1', text)        # italic
    text = re.sub(r'`(.*?)`',       r'\1', text)        # inline code
    text = re.sub(r'#{1,6}\s*',     '',    text)        # headings
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)     # links
    text = re.sub(r'\[.*?\]',       '',    text)        # tags like [Researcher Mode]
    text = re.sub(r'\n{2,}',        '. ',  text)        # paragraph breaks -> pause
    text = re.sub(r'\n',            ' ',   text)        # single newlines
    text = re.sub(r'-{2,}',         '',    text)        # dashes
    return text.strip()

def climate_chatbot_page():
    """Render the PyClimaExplorer Chat page (isolated from global layout)."""

    # --- 3. Page identity (sticky header) ---
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="climabot-header"><h1>🌍 ClimaBot</h1></div>',
        unsafe_allow_html=True,
    )

    # --- 4. Session State (Memory) ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "voice_on" not in st.session_state:
        st.session_state.voice_on = True

    if "speech_rate" not in st.session_state:
        st.session_state.speech_rate = 175

    if "speech_vol" not in st.session_state:
        st.session_state.speech_vol = 1.0

    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])

    # --- 5. Quick prompts styled as badge row ---
    quick_prompts = [
        ("📊 Dataset summary", "Summarize the ERA5 climate dataset"),
        ("🌊 1990 vs 2020", "Compare 1990 vs 2020 global climate patterns"),
        ("🌧️ Anomaly explanation", "Explain a major climate anomaly in simple language"),
        ("India climate", "Describe India's climate trends and recent extreme weather"),
        ("🧊 Glacier melt", "What is happening to glaciers due to climate change?"),
    ]

    if len(st.session_state.messages) == 0 and "inject_prompt" not in st.session_state:
        cols = st.columns(min(len(quick_prompts), 5))
        for idx, (label, prompt_text) in enumerate(quick_prompts):
            col = cols[idx % len(cols)]
            with col:
                if st.button(
                    label=label,
                    key=f"quick_prompt_{idx}",
                    use_container_width=True,
                ):
                    st.session_state["inject_prompt"] = prompt_text
                    st.rerun()

    # --- 6. Display existing chat history ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- 7. Handle quick-prompt injection ---
    injected = st.session_state.pop("inject_prompt", None)

    # --- 8. Main Chat Logic ---
    prompt = st.chat_input("Ask me anything")
    active_prompt = injected or prompt

    if active_prompt:
        # Show user bubble
        st.session_state.messages.append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(active_prompt)

        # Get AI response (multi-turn chat with memory)
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    response = st.session_state.chat.send_message(active_prompt)
                    reply_text = response.text
                except Exception as e:
                    reply_text = f"⚠️ Error: {str(e)}"

            # Render text response
            st.markdown(reply_text)

        # Save assistant reply to memory
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
