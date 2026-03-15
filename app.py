import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pages.data_analysis import analysis_page
from pages.earth_globe import earth_globe_page
from pages.dataset_comparison import dataset_comparison_page
from pages.climate_chatbot import climate_chatbot_page
from pages.story_mode import story_mode_page

import streamlit as st

st.set_page_config(page_title="PyClimaExplorer", page_icon="🌍", layout="wide", initial_sidebar_state="collapsed")

if "page" not in st.session_state:
    st.session_state.page = "home"

# ── CONDITIONAL SIDEBAR + GLOBAL STYLES ──────────────────────────────────────
# Sidebar is visible only on the globe page; hidden everywhere else.
_hide_sidebar = "" if st.session_state.page == "globe" else """
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarNav"] { display: none !important; }
"""

st.markdown(f"""
<style>
{_hide_sidebar}
[data-testid="stHeader"],
[data-testid="stDecoration"],
#MainMenu, footer, header, .stDeployButton {{ display: none !important; }}
.block-container {{ padding: 1rem 2rem 2rem !important; max-width: 100% !important; }}
html, body, .stApp {{ background: #050a0e !important; color: #e8ede8; font-family: 'DM Sans', sans-serif; }}
</style>
""", unsafe_allow_html=True)

# Global CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap');

/* Reset & base */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #050a0e !important;
    color: #e8ede8 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stSidebarNav"] { display: none !important; }

[data-testid="stAppViewContainer"] { padding: 0 !important; }
[data-testid="stMain"] .block-container { padding: 0 !important; max-width: 100% !important; }

/* ── NAV ── */
.cv-nav {
    position: fixed; top: 0; left: 0; right: 0; z-index: 999;
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.4rem 4rem;
    background: linear-gradient(to bottom, rgba(5,10,14,0.95) 0%, transparent 100%);
}
.cv-nav-logo {
    font-family:  sans-serif;
    font-size: 1.3rem; font-weight: 700; color: #e8ede8;
    letter-spacing: 0.04em;
}
.cv-nav-logo span { color: #4caf7d; }
.cv-nav-links { display: flex; gap: 2.5rem; }
.cv-nav-links a {
    font-size: 0.85rem; font-weight: 500; letter-spacing: 0.1em;
    text-transform: uppercase; color: #a8b8a8; text-decoration: none;
    transition: color 0.3s;
}
.cv-nav-links a:hover { color: #4caf7d; }

/* ── HERO ── */
.cv-hero {
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
    position: relative; overflow: hidden;
    background: radial-gradient(ellipse 80% 80% at 50% 60%, #0d2818 0%, #050a0e 70%);
    text-align: center; padding: 2rem;
}
.cv-hero-orb {
    position: absolute; width: 620px; height: 620px;
    border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -42%);
    background: radial-gradient(circle at 40% 40%,
        rgba(76,175,125,0.18) 0%,
        rgba(33,150,100,0.12) 30%,
        transparent 70%);
    border: 1px solid rgba(76,175,125,0.15);
    box-shadow:
        0 0 120px rgba(76,175,125,0.12),
        inset 0 0 80px rgba(76,175,125,0.08);
    animation: orbPulse 6s ease-in-out infinite;
}
.cv-hero-orb::before {
    content: ''; position: absolute; inset: -2px; border-radius: 50%;
    border: 1px solid rgba(76,175,125,0.08);
    animation: orbPulse 6s ease-in-out infinite reverse;
}
.cv-hero-dots {
    position: absolute; width: 500px; height: 500px;
    top: 50%; left: 50%; transform: translate(-50%, -42%);
    background: radial-gradient(circle, rgba(76,175,125,0.5) 1px, transparent 1px);
    background-size: 18px 18px;
    border-radius: 50%;
    mask-image: radial-gradient(circle, black 40%, transparent 70%);
    -webkit-mask-image: radial-gradient(circle, black 40%, transparent 70%);
    opacity: 0.35;
    animation: dotsRotate 40s linear infinite;
}
@keyframes orbPulse {
    0%, 100% { transform: translate(-50%, -42%) scale(1); opacity: 0.9; }
    50% { transform: translate(-50%, -42%) scale(1.04); opacity: 1; }
}
@keyframes dotsRotate {
    from { transform: translate(-50%, -42%) rotate(0deg); }
    to   { transform: translate(-50%, -42%) rotate(360deg); }
}
.cv-hero-content { position: relative; z-index: 2; max-width: 720px; }
.cv-hero-tag {
    display: inline-block; font-size: 0.75rem; letter-spacing: 0.2em;
    text-transform: uppercase; color: #4caf7d;
    border: 1px solid rgba(76,175,125,0.3); padding: 0.35rem 1rem;
    border-radius: 2rem; margin-bottom: 1.8rem;
}
.cv-hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    line-height: 1.12; color: #e8ede8;
    margin-bottom: 1.4rem;
}
.cv-hero-title em { color: #4caf7d; font-style: italic; }
.cv-hero-sub {
    font-size: 1.05rem; color: #7a9a7a; line-height: 1.7;
    max-width: 520px; margin: 0 auto 2.4rem;
}
.cv-hero-cta {
    display: inline-flex; align-items: center; gap: 0.6rem;
    background: #4caf7d; color: #050a0e;
    font-size: 0.85rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; padding: 0.85rem 2rem;
    border-radius: 0.3rem; cursor: pointer; border: none;
    transition: background 0.3s, transform 0.2s;
}
.cv-hero-cta:hover { background: #5dc98e; transform: translateY(-2px); }

/* ── SECTION SHARED ── */
.cv-section {
    padding: 6rem 4rem; max-width: 1200px; margin: 0 auto;
}
.cv-section-label {
    font-size: 0.72rem; letter-spacing: 0.22em; text-transform: uppercase;
    color: #4caf7d; margin-bottom: 0.8rem;
}
.cv-section-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2rem, 4vw, 3rem);
    color: #e8ede8; line-height: 1.2; margin-bottom: 1rem;
}
.cv-section-sub {
    font-size: 1rem; color: #6a8a6a; max-width: 560px; line-height: 1.8;
    margin-bottom: 3rem;
}
.cv-divider {
    border: none; border-top: 1px solid rgba(76,175,125,0.12);
    margin: 0 4rem;
}

/* ── PLACES ── */
.cv-places-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem;
}
.cv-place-card {
    border-radius: 0.75rem; overflow: hidden;
    border: 1px solid rgba(76,175,125,0.1);
    transition: transform 0.3s, border-color 0.3s;
    cursor: pointer; position: relative;
}
.cv-place-card:hover {
    transform: translateY(-6px);
    border-color: rgba(76,175,125,0.35);
}
.cv-place-card-img {
    width: 100%; height: 200px; object-fit: cover;
    display: block;
    background: linear-gradient(135deg, #0d2818 0%, #071a10 100%);
}
.cv-place-emoji {
    width: 100%; height: 200px;
    display: flex; align-items: center; justify-content: center;
    font-size: 5rem;
    background: linear-gradient(135deg, #0d2818, #071a10);
}
.cv-place-body { padding: 1.2rem; background: #080f0a; }
.cv-place-region {
    font-size: 0.7rem; letter-spacing: 0.16em; text-transform: uppercase;
    color: #4caf7d; margin-bottom: 0.4rem;
}
.cv-place-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem; color: #e8ede8; margin-bottom: 0.5rem;
}
.cv-place-desc { font-size: 0.85rem; color: #6a8a6a; line-height: 1.6; }
.cv-place-stat {
    margin-top: 0.8rem; font-size: 0.78rem; color: #4caf7d;
    border-top: 1px solid rgba(76,175,125,0.1); padding-top: 0.7rem;
}

/* ── AUTHORS ── */
.cv-authors-grid {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem;
}
.cv-author-card {
    padding: 1.8rem 1.4rem; text-align: center;
    border: 1px solid rgba(76,175,125,0.1);
    border-radius: 0.75rem; background: #080f0a;
    transition: border-color 0.3s, transform 0.3s;
}
.cv-author-card:hover { border-color: rgba(76,175,125,0.35); transform: translateY(-4px); }
.cv-author-avatar {
    width: 72px; height: 72px; border-radius: 50%;
    background: linear-gradient(135deg, #0d2818, #4caf7d33);
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem; margin: 0 auto 1rem;
    border: 2px solid rgba(76,175,125,0.2);
}
.cv-author-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem; color: #e8ede8; margin-bottom: 0.3rem;
}
.cv-author-role { font-size: 0.78rem; color: #4caf7d; letter-spacing: 0.1em; margin-bottom: 0.7rem; }
.cv-author-bio { font-size: 0.82rem; color: #6a8a6a; line-height: 1.6; }

/* ── ABOUT ── */
.cv-about-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 5rem; align-items: center; }
.cv-about-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 2rem; }
.cv-stat-box {
    padding: 1.4rem;
    border: 1px solid rgba(76,175,125,0.15);
    border-radius: 0.5rem; background: #080f0a;
}
.cv-stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem; color: #4caf7d; margin-bottom: 0.2rem;
}
.cv-stat-label { font-size: 0.78rem; color: #6a8a6a; letter-spacing: 0.1em; text-transform: uppercase; }
.cv-about-visual {
    height: 420px; border-radius: 1rem;
    background: radial-gradient(ellipse at 40% 50%, #0d2818 0%, #050a0e 70%);
    border: 1px solid rgba(76,175,125,0.12);
    display: flex; align-items: center; justify-content: center;
    font-size: 8rem; position: relative; overflow: hidden;
}
.cv-about-visual::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(circle at 50% 50%, rgba(76,175,125,0.08) 0%, transparent 70%);
}

/* ── CONNECT ── */
.cv-connect-layout { display: grid; grid-template-columns: 1fr 1.2fr; gap: 5rem; align-items: start; }
.cv-form { display: flex; flex-direction: column; gap: 1.2rem; }
.cv-input-group { display: flex; flex-direction: column; gap: 0.4rem; }
.cv-label { font-size: 0.78rem; color: #7a9a7a; letter-spacing: 0.1em; text-transform: uppercase; }
.cv-input, .cv-textarea {
    background: #080f0a; border: 1px solid rgba(76,175,125,0.18);
    color: #e8ede8; padding: 0.8rem 1rem; border-radius: 0.4rem;
    font-family: 'DM Sans', sans-serif; font-size: 0.9rem;
    outline: none; transition: border-color 0.3s; width: 100%;
}
.cv-input:focus, .cv-textarea:focus { border-color: rgba(76,175,125,0.5); }
.cv-textarea { resize: vertical; min-height: 130px; }
.cv-submit-btn {
    background: #4caf7d; color: #050a0e;
    font-size: 0.85rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; padding: 0.9rem 2rem;
    border-radius: 0.3rem; border: none; cursor: pointer;
    transition: background 0.3s; align-self: flex-start;
}
.cv-submit-btn:hover { background: #5dc98e; }
.cv-connect-info { display: flex; flex-direction: column; gap: 2rem; }
.cv-info-item { padding-bottom: 2rem; border-bottom: 1px solid rgba(76,175,125,0.08); }
.cv-info-item:last-child { border-bottom: none; }
.cv-info-title { font-family: 'Playfair Display', serif; font-size: 1rem; color: #e8ede8; margin-bottom: 0.4rem; }
.cv-info-text { font-size: 0.88rem; color: #6a8a6a; line-height: 1.7; }

/* ── FOOTER ── */
.cv-footer {
    padding: 2.5rem 4rem;
    border-top: 1px solid rgba(76,175,125,0.1);
    display: flex; align-items: center; justify-content: space-between;
}
.cv-footer-logo { font-family: 'Playfair Display', serif; font-size: 1rem; color: #4caf7d; }
.cv-footer-copy { font-size: 0.78rem; color: #3a5a3a; }

/* Streamlit widget overrides */
.stSelectbox > div > div { background: #080f0a !important; border-color: rgba(76,175,125,0.18) !important; color: #e8ede8 !important; }
.stTextInput > div > div > input { background: #080f0a !important; border-color: rgba(76,175,125,0.18) !important; color: #e8ede8 !important; }
.stTextArea > div > div > textarea { background: #080f0a !important; border-color: rgba(76,175,125,0.18) !important; color: #e8ede8 !important; }
.stButton > button {
    background: #4caf7d !important; color: #050a0e !important;
    font-weight: 600 !important; border: none !important;
    padding: 0.6rem 1.8rem !important; border-radius: 0.3rem !important;
}
.stButton > button:hover { background: #5dc98e !important; }
</style>
""", unsafe_allow_html=True)

# ── NAV ──────────────────────────────────────────────────────────────────────
_nav_map = {"home": "home", "analysis": "analysis", "globe": "globe", "compare": "compare", "story": "story", "chatbot": "chatbot"}
_qp = st.query_params.get("nav", None)
if _qp in _nav_map and st.session_state.page != _nav_map[_qp]:
    st.session_state.page = _nav_map[_qp]
    st.query_params.clear()
    st.rerun()

st.markdown("""
<nav class="cv-nav">
    <div class="cv-nav-logo">PyClima<span>Explorer</span></div>
    <div class="cv-nav-links">
        <a href="?nav=home" target="_self">Home</a>
        <a href="?nav=analysis" target="_self">Analysis</a>
        <a href="?nav=globe" target="_self">Globe</a>
        <a href="?nav=compare" target="_self">Compare Datasets</a>
        <a href="?nav=story" target="_self">Time Machine</a>
        <a href="?nav=chatbot" target="_self">Chatbot</a>
    </div>
</nav>
""", unsafe_allow_html=True)

p = st.session_state.page

# ── PAGES ─────────────────────────────────────────────────────────────────────
if p == "home":
    # ── HERO ─────────────────────────────────────────────────────────────────────
    st.markdown("""
    <section class="cv-hero" id="home">
        <div class="cv-hero-orb"></div>
        <div class="cv-hero-dots"></div>
        <div class="cv-hero-content">
            <div class="cv-hero-tag">🌿 Earth in Focus · 2026</div>
            <h1 class="cv-hero-title">
                Explore the Planet's<br><span style="color:#4caf7d">Climate Data</span>
            </h1>
            <p class="cv-hero-sub">
                Discover the frontlines of climate change - glaciers retreating, forests breathing,
                and communities adapting. Our planet's most urgent stories, told through place.
            </p>
            <button class="cv-hero-cta">
                <a href="?nav=story" target="_self" style="color:inherit; text-decoration:none;">
                    Watch Earth's Story
                </a>
            </button>
        </div>
    </section>
    """, unsafe_allow_html=True)
elif p == "analysis":
    analysis_page()
elif p == "globe":
    earth_globe_page()
elif p == "compare":
    dataset_comparison_page()
elif p == "chatbot":
    climate_chatbot_page()
elif p == "story":
    story_mode_page()
    