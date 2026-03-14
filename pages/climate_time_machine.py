import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time

# ─────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg:        #0b0f19;
    --panel:     #111827;
    --surface:   #1a2235;
    --border:    #1e2d45;
    --accent:    #38bdf8;
    --accent2:   #f59e0b;
    --accent3:   #34d399;
    --danger:    #f87171;
    --text1:     #f0f6ff;
    --text2:     #8baabf;
    --text3:     #405570;
    --cyan-glow: rgba(56,189,248,0.18);
    --gold-glow: rgba(245,158,11,0.15);
}

html,body,[class*="css"]{
    background:#0b0f19 !important;
    color:#f0f6ff !important;
    font-family:'DM Sans',sans-serif !important;
}
.stApp { background: #0b0f19 !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding:0 !important; max-width:100% !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
::-webkit-scrollbar-thumb:hover{background:var(--accent)}

/* ── TOP HEADER ── */
.top-header {
    display:flex; align-items:center; justify-content:space-between;
    padding:.65rem 1.6rem;
    background: linear-gradient(90deg,#0d1520,#111827,#0d1520);
    border-bottom: 1px solid var(--border);
    position:relative; overflow:hidden;
}
.top-header::after {
    content:''; position:absolute; bottom:0; left:0; right:0; height:1px;
    background: linear-gradient(90deg, transparent, var(--accent), var(--accent2), transparent);
    opacity:.6;
}
.logo {
    font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:800;
    letter-spacing:.12em; color:var(--accent);
    text-transform:uppercase;
}
.logo span { color:var(--accent2); }
.header-tag {
    font-family:'DM Mono',monospace; font-size:.6rem; color:var(--text3);
    letter-spacing:.22em; text-transform:uppercase;
}
.header-pills { display:flex; gap:.6rem; }
.pill {
    font-family:'DM Mono',monospace; font-size:.55rem; letter-spacing:.1em;
    padding:.25rem .6rem; border-radius:20px; text-transform:uppercase;
}
.pill-green { background:rgba(52,211,153,.1); border:1px solid rgba(52,211,153,.3); color:var(--accent3); }
.pill-blue  { background:rgba(56,189,248,.1); border:1px solid rgba(56,189,248,.3); color:var(--accent); }
.pill-gold  { background:rgba(245,158,11,.1); border:1px solid rgba(245,158,11,.3); color:var(--accent2); }

/* ── PANEL BASE ── */
.panel-label {
    font-family:'DM Mono',monospace; font-size:.52rem;
    letter-spacing:.25em; text-transform:uppercase; color:var(--text3);
    padding:.55rem 1rem .4rem;
    border-bottom:1px solid var(--border);
    display:flex; align-items:center; gap:6px;
}
.panel-label::before {
    content:''; width:6px; height:1px; background:var(--accent);
}

/* ── TIMELINE PANEL ── */
.timeline-scroll {
    flex:1; overflow-y:auto; padding:.6rem .5rem;
}
.tl-item {
    display:flex; gap:0; cursor:pointer;
    padding:.3rem 0; position:relative;
}
.tl-spine {
    display:flex; flex-direction:column; align-items:center;
    width:28px; flex-shrink:0;
}
.tl-dot {
    width:10px; height:10px; border-radius:50%; flex-shrink:0;
    border:2px solid var(--border); background:var(--bg);
    transition:all .25s; margin-top:4px; position:relative; z-index:2;
}
.tl-line {
    width:1px; flex:1; min-height:30px;
    background: linear-gradient(var(--border), transparent);
}
.tl-card {
    flex:1; background:var(--surface);
    border:1px solid var(--border);
    border-radius:6px; padding:.55rem .7rem;
    margin-bottom:.4rem; transition:all .22s;
    position:relative; overflow:hidden;
}
.tl-card::before {
    content:''; position:absolute; left:0; top:0; bottom:0; width:2px;
    background:var(--border); transition:background .22s;
}
.tl-card:hover { border-color:rgba(56,189,248,.35); transform:translateX(2px); }
.tl-card:hover::before { background:var(--accent); }
.tl-card.active { border-color:rgba(56,189,248,.5); background:#1a2d42; }
.tl-card.active::before { background:var(--accent); }
.tl-card.active .tl-dot-ref { border-color:var(--accent); background:var(--accent); }
.tl-year {
    font-family:'DM Mono',monospace; font-size:.62rem;
    color:var(--accent); letter-spacing:.1em; margin-bottom:.2rem;
}
.tl-name {
    font-family:'Syne',sans-serif; font-size:.8rem; font-weight:600;
    color:var(--text1); margin-bottom:.2rem; line-height:1.25;
}
.tl-desc {
    font-size:.7rem; color:var(--text2); line-height:1.45;
    display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;
}
.tl-badge {
    display:inline-block; padding:.1rem .4rem; border-radius:3px;
    font-family:'DM Mono',monospace; font-size:.5rem;
    letter-spacing:.08em; text-transform:uppercase; font-weight:500;
    margin-bottom:.25rem;
}

/* ── ZOOM INDICATOR ── */
.zoom-indicator {
    font-family:'DM Mono',monospace; font-size:.5rem;
    color:var(--accent3); letter-spacing:.12em; text-transform:uppercase;
    padding:.15rem .5rem; background:rgba(52,211,153,.08);
    border:1px solid rgba(52,211,153,.2); border-radius:3px;
    display:inline-block; margin-left:.5rem;
    animation: pulse-zoom 1.5s ease-in-out infinite;
}
@keyframes pulse-zoom {
    0%,100% { opacity:.7; }
    50% { opacity:1; }
}

/* ── GLOBE PANEL ── */
.globe-label {
    font-family:'DM Mono',monospace; font-size:.52rem;
    letter-spacing:.25em; text-transform:uppercase; color:var(--text3);
    padding:.55rem 1rem .4rem;
    border-bottom:1px solid var(--border);
    display:flex; align-items:center; justify-content:space-between;
}
.globe-label-left { display:flex; align-items:center; gap:6px; }
.globe-label-left::before { content:''; width:6px; height:1px; background:var(--accent); }

/* ── PLAY BAR ── */
.play-bar {
    padding:.6rem 1rem;
    border-top:1px solid var(--border);
    background:var(--panel);
    display:flex; align-items:center; gap:.8rem;
}
.progress-track {
    flex:1; height:3px; background:var(--border); border-radius:2px; position:relative;
}
.progress-fill {
    height:100%; background:linear-gradient(90deg,var(--accent),var(--accent2));
    border-radius:2px; transition:width .4s ease;
}

/* ── DETAILS PANEL ── */
.detail-hero {
    background: linear-gradient(135deg,#0d1e30,#132030);
    border:1px solid var(--border);
    border-radius:8px; padding:1rem;
    margin-bottom:.8rem; position:relative; overflow:hidden;
}
.detail-hero::after {
    content:''; position:absolute; top:-20px; right:-20px;
    width:100px; height:100px;
    background: radial-gradient(circle, var(--gold-glow), transparent);
    border-radius:50%;
}
.detail-type-badge {
    font-family:'DM Mono',monospace; font-size:.55rem;
    letter-spacing:.12em; text-transform:uppercase;
    padding:.2rem .55rem; border-radius:3px; display:inline-block;
    margin-bottom:.6rem;
}
.detail-year {
    font-family:'DM Mono',monospace; font-size:2rem; font-weight:500;
    line-height:1; margin-bottom:.3rem; color:var(--accent2);
    letter-spacing:-.02em;
}
.detail-name {
    font-family:'Syne',sans-serif; font-size:1.05rem; font-weight:700;
    color:var(--text1); margin-bottom:.5rem; line-height:1.25;
}
.detail-desc {
    font-size:.8rem; color:var(--text2); line-height:1.65;
}

.stat-grid {
    display:grid; grid-template-columns:1fr 1fr;
    gap:.5rem; margin-bottom:.8rem;
}
.stat-card {
    background:var(--surface); border:1px solid var(--border);
    border-radius:6px; padding:.6rem .75rem;
}
.stat-val {
    font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700;
    margin-bottom:.15rem; display:block;
}
.stat-lbl {
    font-family:'DM Mono',monospace; font-size:.5rem;
    color:var(--text3); letter-spacing:.1em; text-transform:uppercase;
}

.detail-section-title {
    font-family:'DM Mono',monospace; font-size:.55rem;
    color:var(--text3); letter-spacing:.2em; text-transform:uppercase;
    margin-bottom:.5rem; padding-bottom:.3rem;
    border-bottom:1px solid var(--border);
}

.impact-bar-wrap { margin-bottom:.5rem; }
.impact-bar-label {
    display:flex; justify-content:space-between;
    font-family:'DM Mono',monospace; font-size:.58rem;
    color:var(--text2); margin-bottom:.2rem;
}
.impact-bar-track {
    height:4px; background:var(--border); border-radius:2px; overflow:hidden;
}
.impact-bar-fill {
    height:100%; border-radius:2px;
    background:linear-gradient(90deg,var(--accent),var(--accent2));
}

.coords-row {
    display:flex; gap:.5rem; margin-bottom:.8rem;
}
.coord-chip {
    font-family:'DM Mono',monospace; font-size:.6rem; color:var(--accent);
    background:var(--cyan-glow); border:1px solid rgba(56,189,248,.2);
    border-radius:4px; padding:.25rem .55rem;
}

/* ── STREAMLIT OVERRIDES ── */
.stButton>button {
    background:linear-gradient(135deg,#0d2035,#122840) !important;
    border:1px solid var(--accent) !important;
    color:var(--accent) !important;
    font-family:'DM Mono',monospace !important;
    font-size:.58rem !important;
    letter-spacing:.12em !important;
    border-radius:4px !important;
    padding:.35rem 1rem !important;
    text-transform:uppercase !important;
    transition:all .2s !important;
}
.stButton>button:hover {
    background:rgba(56,189,248,.15) !important;
    box-shadow:0 0 14px rgba(56,189,248,.25) !important;
}

/* ── RESTART BUTTON — special gold glow ── */
.restart-btn .stButton>button {
    background:linear-gradient(135deg,#1a1000,#2a1a00) !important;
    border:1px solid var(--accent2) !important;
    color:var(--accent2) !important;
    box-shadow:0 0 18px rgba(245,158,11,.3) !important;
    animation: restart-glow 2s ease-in-out infinite;
}
@keyframes restart-glow {
    0%,100% { box-shadow:0 0 10px rgba(245,158,11,.2); }
    50%      { box-shadow:0 0 22px rgba(245,158,11,.5); }
}
.restart-btn .stButton>button:hover {
    background:rgba(245,158,11,.2) !important;
    box-shadow:0 0 28px rgba(245,158,11,.5) !important;
}

div[data-testid="stPlotlyChart"] {
    background:transparent !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# DATASET
# ─────────────────────────────────────────────────────
EVENTS = [
    dict(
        id=0, year=1970, month="November", type="Cyclone",
        name="Bhola Cyclone",
        lat=22.0, lon=89.5,
        deaths=500000, affected_M=3.6, damage_B=1.0, temp_anom=0.02,
        description="The deadliest tropical cyclone in recorded history made landfall in East Pakistan (now Bangladesh). Storm surges of up to 10 metres swept over the low-lying Ganges delta, wiping out entire coastal villages.",
        region_name="Bay of Bengal / Bangladesh",
        highlight_lats=[20, 24, 24, 20], highlight_lons=[88, 88, 92, 92],
        color="#00b4d8",
        zoom_scale=3.5,
    ),
    dict(
        id=1, year=1976, month="July", type="Earthquake",
        name="Tangshan Earthquake",
        lat=39.6, lon=118.2,
        deaths=242000, affected_M=0.8, damage_B=10.0, temp_anom=0.05,
        description="A magnitude 7.6 earthquake struck the industrial city of Tangshan, China at 3:42 AM while residents slept. Within seconds, 85% of the city's buildings collapsed, killing an estimated 242,000 people.",
        region_name="Hebei Province, China",
        highlight_lats=[38, 41, 41, 38], highlight_lons=[116, 116, 121, 121],
        color="#ff6d00",
        zoom_scale=4.0,
    ),
    dict(
        id=2, year=1991, month="April", type="Cyclone",
        name="Bangladesh Cyclone 1991",
        lat=22.8, lon=91.8,
        deaths=138000, affected_M=10.0, damage_B=1.5, temp_anom=0.15,
        description="A powerful cyclone with 250 km/h winds struck the Chittagong coast of Bangladesh. Despite warnings, over 138,000 people perished in the storm surge. A landmark moment for disaster early-warning systems.",
        region_name="Chittagong, Bangladesh",
        highlight_lats=[21, 24, 24, 21], highlight_lons=[90, 90, 93, 93],
        color="#00b4d8",
        zoom_scale=3.5,
    ),
    dict(
        id=3, year=1995, month="July", type="Heatwave",
        name="Chicago Heatwave",
        lat=41.9, lon=-87.6,
        deaths=739, affected_M=2.5, damage_B=0.12, temp_anom=0.42,
        description="Five days of extreme heat transformed Chicago into a furnace. Temperatures reached 41°C with humidity making it feel like 52°C. 739 people, mostly elderly and isolated residents, died. The disaster exposed deep social vulnerabilities in urban life.",
        region_name="Chicago, Illinois, USA",
        highlight_lats=[40, 43, 43, 40], highlight_lons=[-90, -90, -86, -86],
        color="#ff1744",
        zoom_scale=4.0,
    ),
    dict(
        id=4, year=2003, month="August", type="Heatwave",
        name="European Heatwave",
        lat=47.0, lon=2.0,
        deaths=70000, affected_M=0.52, damage_B=13.0, temp_anom=0.85,
        description="The deadliest heatwave in European history. Record temperatures scorched the continent for two weeks. France alone lost around 15,000 lives. The disaster forced a fundamental overhaul of European public health infrastructure.",
        region_name="Western Europe",
        highlight_lats=[43, 53, 53, 43], highlight_lons=[-5, -5, 16, 16],
        color="#ff1744",
        zoom_scale=2.5,
    ),
    dict(
        id=5, year=2004, month="December", type="Tsunami",
        name="Indian Ocean Tsunami",
        lat=3.3, lon=95.9,
        deaths=227898, affected_M=1.7, damage_B=10.0, temp_anom=0.48,
        description="A Mw 9.1 earthquake off northern Sumatra generated tsunamis up to 30 metres tall that struck 14 countries. Indonesia, Sri Lanka, India and Thailand suffered the most. The world's deadliest tsunami triggered the largest international aid response in history.",
        region_name="Indian Ocean — 14 Countries",
        highlight_lats=[-5, 15, 15, -5], highlight_lons=[80, 80, 100, 100],
        color="#2979ff",
        zoom_scale=2.5,
    ),
    dict(
        id=6, year=2005, month="August", type="Cyclone",
        name="Hurricane Katrina",
        lat=29.9, lon=-90.1,
        deaths=1836, affected_M=0.4, damage_B=125.0, temp_anom=0.52,
        description="Katrina made landfall as a Category 4 hurricane and overwhelmed New Orleans' levee system. Floodwaters submerged 80% of the city. The catastrophe exposed systemic failures in emergency management and became a symbol of inequality in disaster response.",
        region_name="Gulf Coast, USA",
        highlight_lats=[28, 32, 32, 28], highlight_lons=[-93, -93, -87, -87],
        color="#00b4d8",
        zoom_scale=3.5,
    ),
    dict(
        id=7, year=2010, month="January", type="Earthquake",
        name="Haiti Earthquake",
        lat=18.5, lon=-72.3,
        deaths=316000, affected_M=3.0, damage_B=8.0, temp_anom=0.55,
        description="A magnitude 7.0 earthquake struck 25 km west of Port-au-Prince, devastating one of the world's poorest nations. Over 316,000 people died and 1.5 million were displaced. Recovery efforts revealed the long shadow of Haiti's colonial and economic history.",
        region_name="Port-au-Prince, Haiti",
        highlight_lats=[17, 20, 20, 17], highlight_lons=[-74, -74, -71, -71],
        color="#ff6d00",
        zoom_scale=4.5,
    ),
    dict(
        id=8, year=2011, month="March", type="Tsunami",
        name="Tōhoku Earthquake & Tsunami",
        lat=38.3, lon=142.4,
        deaths=15897, affected_M=0.45, damage_B=235.0, temp_anom=0.54,
        description="A Mw 9.1 earthquake triggered a 40-metre tsunami that devastated Japan's northeastern coast and caused the Fukushima Daiichi nuclear disaster — the worst nuclear accident since Chernobyl. Japan's extraordinary resilience was tested to its limits.",
        region_name="Tōhoku Region, Japan",
        highlight_lats=[36, 41, 41, 36], highlight_lons=[139, 139, 145, 145],
        color="#2979ff",
        zoom_scale=3.5,
    ),
    dict(
        id=9, year=2013, month="November", type="Cyclone",
        name="Typhoon Haiyan",
        lat=11.2, lon=124.0,
        deaths=6340, affected_M=16.1, damage_B=2.98, temp_anom=0.68,
        description="One of the strongest tropical cyclones ever recorded, Typhoon Haiyan made landfall in the Philippines with 315 km/h winds. The 7-metre storm surge erased entire communities in Leyte province. Tacloban city was almost completely destroyed.",
        region_name="Visayas, Philippines",
        highlight_lats=[9, 14, 14, 9], highlight_lons=[121, 121, 127, 127],
        color="#00b4d8",
        zoom_scale=3.5,
    ),
    dict(
        id=10, year=2019, month="September", type="Wildfire",
        name="Australian Black Summer",
        lat=-33.9, lon=151.2,
        deaths=34, affected_M=3.0, damage_B=103.0, temp_anom=1.2,
        description="Australia's catastrophic 'Black Summer' burned 18.6 million hectares — an area larger than Portugal. Smoke blanketed cities for months. An estimated 3 billion animals were killed. Scientists confirmed climate change made the fires 30% more likely.",
        region_name="Eastern & Southern Australia",
        highlight_lats=[-40, -25, -25, -40], highlight_lons=[140, 140, 154, 154],
        color="#ff9100",
        zoom_scale=2.0,
    ),
    dict(
        id=11, year=2021, month="June", type="Heatwave",
        name="Pacific NW Heat Dome",
        lat=49.3, lon=-123.1,
        deaths=1400, affected_M=2.0, damage_B=7.5, temp_anom=1.24,
        description="An extraordinary heat dome pushed temperatures to 49.6°C in Lytton, Canada — shattering all previous records. The village burned to the ground the next day. Scientists called it a 'once-in-a-thousand-year' event made 150 times more likely by climate change.",
        region_name="Pacific Northwest, Canada & USA",
        highlight_lats=[44, 54, 54, 44], highlight_lons=[-130, -130, -118, -118],
        color="#ff1744",
        zoom_scale=2.5,
    ),
    dict(
        id=12, year=2022, month="June", type="Flood",
        name="Pakistan Mega-Floods",
        lat=30.0, lon=70.0,
        deaths=1730, affected_M=33.0, damage_B=30.0, temp_anom=1.15,
        description="A third of Pakistan disappeared underwater in its worst flooding in history. Monsoon rains five times above normal, supercharged by melting glaciers, displaced 8 million people. Pakistan contributes less than 1% of global emissions yet faces catastrophic climate impacts.",
        region_name="Sindh & Balochistan, Pakistan",
        highlight_lats=[23, 37, 37, 23], highlight_lons=[60, 60, 78, 78],
        color="#00e5ff",
        zoom_scale=2.5,
    ),
    dict(
        id=13, year=2023, month="February", type="Earthquake",
        name="Turkey–Syria Earthquake",
        lat=37.2, lon=37.0,
        deaths=59259, affected_M=1.5, damage_B=34.2, temp_anom=1.17,
        description="A pair of devastating earthquakes — Mw 7.8 and 7.5 — struck southeastern Turkey and northern Syria at dawn, killing over 59,000 people. The disaster struck a region already devastated by the Syrian civil war, compounding a multi-layered humanitarian crisis.",
        region_name="Gaziantep–Kahramanmaraş, Turkey",
        highlight_lats=[35, 40, 40, 35], highlight_lons=[33, 33, 42, 42],
        color="#ff6d00",
        zoom_scale=3.5,
    ),
    dict(
        id=14, year=2023, month="September", type="Flood",
        name="Libya Derna Floods",
        lat=32.9, lon=21.8,
        deaths=11300, affected_M=0.35, damage_B=1.8, temp_anom=1.19,
        description="Storm Daniel caused catastrophic flooding in northeastern Libya. Two dams upstream of Derna collapsed simultaneously, releasing a 7-metre wall of water that swept entire city quarters into the sea. Libya's fractured governance compounded the disaster.",
        region_name="Derna, Libya",
        highlight_lats=[31, 34, 34, 31], highlight_lons=[19, 19, 24, 24],
        color="#00e5ff",
        zoom_scale=4.0,
    ),
]

# Type → display colour
TYPE_COLORS = {
    "Cyclone":    ("#00b4d8", "rgba(0,180,216,.12)", "rgba(0,180,216,.35)"),
    "Earthquake": ("#ff6d00", "rgba(255,109,0,.12)",  "rgba(255,109,0,.35)"),
    "Heatwave":   ("#ff1744", "rgba(255,23,68,.12)",   "rgba(255,23,68,.35)"),
    "Flood":      ("#00e5ff", "rgba(0,229,255,.12)",   "rgba(0,229,255,.35)"),
    "Wildfire":   ("#ff9100", "rgba(255,145,0,.12)",   "rgba(255,145,0,.35)"),
    "Tsunami":    ("#2979ff", "rgba(41,121,255,.12)",  "rgba(41,121,255,.35)"),
}
TYPE_EMOJI = {
    "Cyclone":"🌀","Earthquake":"⚡","Heatwave":"🔥","Flood":"🌊","Wildfire":"🔥","Tsunami":"🌊"
}

def type_badge(t):
    c,bg,bd = TYPE_COLORS.get(t,("#aaa","rgba(170,170,170,.1)","rgba(170,170,170,.3)"))
    em = TYPE_EMOJI.get(t,"●")
    return f'<span style="background:{bg};border:1px solid {bd};color:{c}" class="tl-badge">{em} {t}</span>'

def fmt(n, suffix=""):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M{suffix}"
    if n >= 1_000:     return f"{n/1_000:.1f}K{suffix}"
    return f"{int(n)}{suffix}"

# ─────────────────────────────────────────────────────
# SESSION STATE  +  query-param click bridge
# ─────────────────────────────────────────────────────
if "idx" not in st.session_state: st.session_state.idx = 0
if "playing" not in st.session_state: st.session_state.playing = False
if "finished" not in st.session_state: st.session_state.finished = False
if "zoomed" not in st.session_state: st.session_state.zoomed = False
if "lon_rot" not in st.session_state: st.session_state.lon_rot = 20.0
if "lat_rot" not in st.session_state: st.session_state.lat_rot = 10.0

# ── Read click from HTML component via URL query param ──
qp = st.query_params
if "tl_click" in qp:
    try:
        clicked_idx = int(qp["tl_click"])
        if 0 <= clicked_idx < len(EVENTS):
            if st.session_state.idx == clicked_idx:
                st.session_state.zoomed = not st.session_state.zoomed
            else:
                st.session_state.idx      = clicked_idx
                st.session_state.zoomed   = True
                st.session_state.playing  = False
                st.session_state.finished = False
            _etmp = EVENTS[st.session_state.idx]
            st.session_state.lon_rot = float(_etmp["lon"])
            st.session_state.lat_rot = max(-60.0, min(60.0, float(_etmp["lat"])))
    except (ValueError, KeyError):
        pass
    st.query_params.clear()

ev = EVENTS[st.session_state.idx]

# ─────────────────────────────────────────────────────
# GLOBE BUILDER  (feature 1 & 2: zoom_scale param)
# ─────────────────────────────────────────────────────
def build_globe(event, lon_center, lat_center, zoomed=False):
    fig = go.Figure()

    # ── Projection scale: zoomed uses event-specific zoom_scale, normal uses 1.0 ──
    proj_scale = event.get("zoom_scale", 3.0) if zoomed else 1.0

    # Graticule
    lons_full = np.linspace(-180, 180, 361).tolist()
    lats_full = np.linspace(-90, 90, 181).tolist()
    for lat_v in range(-60, 90, 30):
        fig.add_trace(go.Scattergeo(
            lon=lons_full, lat=[lat_v]*361,
            mode="lines", line=dict(width=.4, color="rgba(56,189,248,0.07)"),
            hoverinfo="skip", showlegend=False))
    for lon_v in range(-180, 181, 30):
        fig.add_trace(go.Scattergeo(
            lon=[lon_v]*181, lat=lats_full,
            mode="lines", line=dict(width=.4, color="rgba(56,189,248,0.07)"),
            hoverinfo="skip", showlegend=False))

    # Equator highlight
    fig.add_trace(go.Scattergeo(
        lon=lons_full, lat=[0]*361,
        mode="lines", line=dict(width=.8, color="rgba(56,189,248,0.14)", dash="dot"),
        hoverinfo="skip", showlegend=False))

    # All other events (dim; smaller when zoomed so active region dominates)
    for e in EVENTS:
        if e["id"] == event["id"]: continue
        c,_,_ = TYPE_COLORS.get(e["type"],("#aaa","",""))
        base_sz = float(np.clip(np.log1p(e["deaths"])*2.8, 6, 22))
        sz = base_sz * 0.5 if zoomed else base_sz
        fig.add_trace(go.Scattergeo(
            lon=[e["lon"]], lat=[e["lat"]],
            mode="markers",
            marker=dict(size=sz, color=c, opacity=.2 if zoomed else .3,
                        line=dict(width=.8, color=c)),
            text=[e["name"]],
            customdata=[e["id"]],
            hovertemplate="<b>%{text}</b><br>" + str(e["year"]) + "<extra></extra>",
            showlegend=False))

    # ── Highlight region polygon (brighter when zoomed) ──
    _hc = event["color"].lstrip("#")
    _r, _g, _b = int(_hc[0:2], 16), int(_hc[2:4], 16), int(_hc[4:6], 16)
    fill_alpha = 0.35 if zoomed else 0.18
    border_w   = 2.5  if zoomed else 1.5
    _fill_rgba = f"rgba({_r},{_g},{_b},{fill_alpha})"
    fig.add_trace(go.Scattergeo(
        lon=event["highlight_lons"] + [event["highlight_lons"][0]],
        lat=event["highlight_lats"] + [event["highlight_lats"][0]],
        mode="lines",
        line=dict(width=border_w, color=event["color"]),
        fill="toself",
        fillcolor=_fill_rgba,
        hoverinfo="skip", showlegend=False))

    # Ripple rings for active event
    base = float(np.clip(np.log1p(event["deaths"])*3.2, 14, 42))
    rings = [(base*2.6,.07),(base*1.9,.12),(base*1.4,.2)]
    if zoomed:
        rings = [(base*.9,.1),(base*.65,.18),(base*.45,.3)]
    for sz, op in rings:
        fig.add_trace(go.Scattergeo(
            lon=[event["lon"]], lat=[event["lat"]],
            mode="markers",
            marker=dict(size=sz, color=event["color"], opacity=op,
                        symbol="circle", line=dict(width=1, color=event["color"])),
            hoverinfo="skip", showlegend=False))

    # Active event marker
    marker_sz = base * 0.55 if zoomed else base
    fig.add_trace(go.Scattergeo(
        lon=[event["lon"]], lat=[event["lat"]],
        mode="markers+text",
        marker=dict(size=marker_sz, color=event["color"], opacity=1,
                    line=dict(width=2, color="#ffffff")),
        text=[f"  {event['name']}"],
        textposition="middle right",
        textfont=dict(size=11 if zoomed else 10, color="#ffffff", family="DM Mono"),
        hovertemplate=f"<b>{event['name']}</b><br>{event['year']}<br>Deaths: {fmt(event['deaths'])}<extra></extra>",
        showlegend=False))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=None,
        geo=dict(
            projection_type="orthographic",
            projection_rotation=dict(lon=lon_center, lat=lat_center, roll=0),
            projection_scale=proj_scale,           # ← KEY: zoom via scale
            showland=True, landcolor="#0f1e32",
            showocean=True, oceancolor="#060e1a",
            showcountries=True, countrycolor="rgba(56,100,140,0.22)", countrywidth=.5,
            showcoastlines=True, coastlinecolor="rgba(56,140,180,0.28)", coastlinewidth=.7,
            showframe=False, bgcolor="rgba(0,0,0,0)",
            showlakes=True, lakecolor="#060e1a",
            showrivers=False,
        ),
        dragmode="pan",
    )
    return fig

# ─────────────────────────────────────────────────────
# TOP HEADER
# ─────────────────────────────────────────────────────
zoom_pill = '<div class="pill pill-gold">🔍 Region Zoom</div>' if st.session_state.zoomed else ""
st.markdown(f"""
<div class="top-header">
  <div>
    <div class="logo">Py<span>Clima</span>Explorer</div>
    <div class="header-tag">Story Mode · Natural Disaster Chronicle</div>
  </div>
  <div class="header-pills">
    <div class="pill pill-green">● Live</div>
    <div class="pill pill-blue">Globe Active</div>
    {zoom_pill}
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# THREE-PANEL LAYOUT
# ─────────────────────────────────────────────────────
col_tl, col_globe, col_detail = st.columns([1, 1.7, 1.1], gap="small")


# ══════════════════════════════════════════════════════
# LEFT — TIMELINE  (fully interactive HTML component)
# ══════════════════════════════════════════════════════
with col_tl:
    st.markdown('<div class="panel-label">⬡&nbsp; Timeline — 1950 to Present</div>', unsafe_allow_html=True)

    # ── Build event data for JS ──
    import json as _json

    js_events = _json.dumps([
        {
            "id":    e["id"],
            "year":  e["year"],
            "month": e["month"],
            "type":  e["type"],
            "name":  e["name"],
            "desc":  e["description"][:115] + "…",
            "color": TYPE_COLORS.get(e["type"], ("#aaa","",""))[0],
            "bg":    TYPE_COLORS.get(e["type"], ("#aaa","rgba(170,170,170,.1)",""))[1],
            "bd":    TYPE_COLORS.get(e["type"], ("#aaa","","rgba(170,170,170,.3)"))[2],
            "emoji": TYPE_EMOJI.get(e["type"], "●"),
        }
        for e in EVENTS
    ])

    active_idx  = st.session_state.idx
    zoomed_flag = "true" if st.session_state.zoomed else "false"

    timeline_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400&display=swap');

  * {{ box-sizing:border-box; margin:0; padding:0; }}
  html, body {{ background:#0b0f19; color:#f0f6ff; font-family:'DM Sans',sans-serif; height:100%; overflow:hidden; }}

  #scroll {{
    height: 100vh;
    overflow-y: auto;
    padding: .5rem .45rem .5rem .3rem;
    scrollbar-width: thin;
    scrollbar-color: #1e2d45 #0b0f19;
  }}
  #scroll::-webkit-scrollbar {{ width:3px; }}
  #scroll::-webkit-scrollbar-track {{ background:#0b0f19; }}
  #scroll::-webkit-scrollbar-thumb {{ background:#1e2d45; border-radius:2px; }}

  .tl-row {{
    display: flex;
    gap: 0;
    cursor: pointer;
    margin-bottom: .1rem;
  }}

  /* spine */
  .spine {{
    display:flex; flex-direction:column; align-items:center;
    width: 22px; flex-shrink: 0;
  }}
  .dot {{
    width:9px; height:9px; border-radius:50%;
    border:2px solid #1e2d45; background:#0b0f19;
    margin-top:6px; flex-shrink:0; position:relative; z-index:2;
    transition: all .22s;
  }}
  .vline {{
    width:1px; flex:1; min-height:26px;
    background: linear-gradient(#1e2d45, transparent);
  }}

  /* card */
  .card {{
    flex:1;
    background:#1a2235;
    border: 1px solid #1e2d45;
    border-left: 2px solid #1e2d45;
    border-radius: 6px;
    padding: .48rem .62rem;
    margin-bottom:.32rem;
    position: relative;
    overflow: hidden;
    transition: background .18s, border-color .18s, transform .15s, box-shadow .18s;
    user-select: none;
  }}

  /* HOVER STATE */
  .card:hover {{
    background: #1d2a40;
    border-color: rgba(56,189,248,.45);
    border-left-color: #38bdf8;
    transform: translateX(3px);
    box-shadow: -3px 0 12px rgba(56,189,248,.15), 0 2px 14px rgba(56,189,248,.08);
  }}
  .tl-row:hover .dot {{
    border-color: #38bdf8;
    background: rgba(56,189,248,.25);
    box-shadow: 0 0 7px rgba(56,189,248,.5);
  }}

  /* ACTIVE STATE */
  .card.active {{
    background: #1a2d42;
    border-color: rgba(56,189,248,.5);
  }}
  .card.active:hover {{
    border-color: rgba(56,189,248,.7);
    transform: translateX(3px);
  }}

  /* CLICK FLASH */
  .card.flash {{
    background: rgba(56,189,248,.15) !important;
    transform: translateX(3px) scale(1.005) !important;
  }}

  .badge {{
    display:inline-block; padding:.09rem .38rem; border-radius:3px;
    font-family:'DM Mono',monospace; font-size:.48rem;
    letter-spacing:.08em; text-transform:uppercase; font-weight:500;
    margin-bottom:.18rem;
  }}
  .zoom-tag {{
    display:inline-block; margin-left:5px;
    padding:.09rem .35rem; border-radius:3px;
    font-family:'DM Mono',monospace; font-size:.45rem;
    letter-spacing:.1em; text-transform:uppercase;
    background:rgba(52,211,153,.1); border:1px solid rgba(52,211,153,.28);
    color:#34d399;
    animation: zpulse 1.6s ease-in-out infinite;
  }}
  @keyframes zpulse {{ 0%,100%{{opacity:.7}} 50%{{opacity:1}} }}

  .yr {{
    font-family:'DM Mono',monospace; font-size:.6rem;
    letter-spacing:.1em; margin-bottom:.15rem;
  }}
  .name {{
    font-family:'Syne',sans-serif; font-size:.77rem; font-weight:600;
    color:#f0f6ff; line-height:1.22; margin-bottom:.14rem;
  }}
  .desc {{
    font-size:.67rem; color:#8baabf; line-height:1.42;
    display:-webkit-box; -webkit-line-clamp:2;
    -webkit-box-orient:vertical; overflow:hidden;
  }}

  /* hint bar at bottom */
  .hint {{
    padding:.35rem .5rem;
    border-top:1px solid #1e2d45;
    font-family:'DM Mono',monospace; font-size:.48rem;
    color:#405570; letter-spacing:.15em; text-transform:uppercase;
    text-align:center;
  }}
</style>
</head>
<body>
<div id="scroll"></div>
<div class="hint">hover to preview · click to zoom</div>

<script>
const EVENTS  = {js_events};
const ACTIVE  = {active_idx};
const ZOOMED  = {zoomed_flag};

const scroll = document.getElementById('scroll');

function buildTimeline() {{
  scroll.innerHTML = '';
  EVENTS.forEach((e, i) => {{
    const isActive = (i === ACTIVE);

    // row
    const row = document.createElement('div');
    row.className = 'tl-row';
    row.dataset.idx = i;

    // spine
    const spine = document.createElement('div');
    spine.className = 'spine';
    const dot = document.createElement('div');
    dot.className = 'dot';
    if (isActive) {{
      dot.style.background = e.color;
      dot.style.borderColor = e.color;
      dot.style.boxShadow = `0 0 7px ${{e.color}}`;
    }}
    const vline = document.createElement('div');
    vline.className = 'vline';
    spine.appendChild(dot);
    spine.appendChild(vline);

    // card
    const card = document.createElement('div');
    card.className = 'card' + (isActive ? ' active' : '');
    if (isActive) {{
      card.style.borderLeftColor = e.color;
    }} else {{
      card.style.borderLeftColor = '#1e2d45';
    }}

    // badge row
    const badgeWrap = document.createElement('div');
    badgeWrap.style.cssText = 'display:flex;align-items:center;margin-bottom:.18rem';
    const badge = document.createElement('span');
    badge.className = 'badge';
    badge.style.cssText = `background:${{e.bg}};border:1px solid ${{e.bd}};color:${{e.color}}`;
    badge.textContent = e.emoji + ' ' + e.type;
    badgeWrap.appendChild(badge);
    if (isActive && ZOOMED) {{
      const zt = document.createElement('span');
      zt.className = 'zoom-tag';
      zt.textContent = '⊕ Zoomed';
      badgeWrap.appendChild(zt);
    }}

    const yr = document.createElement('div');
    yr.className = 'yr';
    yr.style.color = e.color;
    yr.textContent = e.year + ' · ' + e.month;

    const name = document.createElement('div');
    name.className = 'name';
    name.textContent = e.name;

    const desc = document.createElement('div');
    desc.className = 'desc';
    desc.textContent = e.desc;

    card.appendChild(badgeWrap);
    card.appendChild(yr);
    card.appendChild(name);
    card.appendChild(desc);

    row.appendChild(spine);
    row.appendChild(card);
    scroll.appendChild(row);

    // ── HOVER: light up dot + card glow with type colour ──
    row.addEventListener('mouseenter', () => {{
      if (i !== ACTIVE) {{
        dot.style.background = e.color + '55';
        dot.style.borderColor = e.color;
        dot.style.boxShadow = `0 0 6px ${{e.color}}88`;
        card.style.borderLeftColor = e.color;
      }}
    }});
    row.addEventListener('mouseleave', () => {{
      if (i !== ACTIVE) {{
        dot.style.background = '';
        dot.style.borderColor = '';
        dot.style.boxShadow = '';
        card.style.borderLeftColor = '#1e2d45';
      }}
    }});

    // ── CLICK: flash then navigate via query param ──
    row.addEventListener('click', () => {{
      card.classList.add('flash');
      setTimeout(() => {{
        // Navigate parent window with query param — Streamlit picks it up on rerun
        const url = new URL(window.parent.location.href);
        url.searchParams.set('tl_click', String(i));
        window.parent.location.href = url.toString();
      }}, 120);
    }});
  }});

  // auto-scroll active card into view
  setTimeout(() => {{
    const rows = scroll.querySelectorAll('.tl-row');
    if (rows[ACTIVE]) {{
      rows[ACTIVE].scrollIntoView({{ behavior:'smooth', block:'center' }});
    }}
  }}, 80);
}}

buildTimeline();
</script>
</body>
</html>
"""

    import streamlit.components.v1 as components
    components.html(timeline_html, height=700, scrolling=False)


# ══════════════════════════════════════════════════════
# MIDDLE — GLOBE
# ══════════════════════════════════════════════════════
with col_globe:
    zoom_label_txt = "🔍 ZOOMED" if st.session_state.zoomed else "🌐 Globe View"
    st.markdown(f"""
    <div class="globe-label">
      <div class="globe-label-left">⬡&nbsp; Interactive 3D Globe · {zoom_label_txt}</div>
      <span style="font-size:.55rem;color:#405570">{ev['year']} · {ev['region_name']}</span>
    </div>""", unsafe_allow_html=True)

    # Auto-centre on event
    st.session_state.lon_rot = float(ev["lon"])
    st.session_state.lat_rot = max(-60.0, min(60.0, float(ev["lat"])))

    fig_globe = build_globe(
        ev,
        st.session_state.lon_rot,
        st.session_state.lat_rot,
        zoomed=st.session_state.zoomed,   # ← pass zoom state
    )

    # ── Capture plotly click events (feature 2: marker click → zoom) ──
    clicked = st.plotly_chart(
        fig_globe,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "modeBarButtonsToRemove": ["select2d","lasso2d","resetScale2d"],
            "displaylogo": False,
            "scrollZoom": True,
        },
        key=f"globe_{st.session_state.idx}_{st.session_state.zoomed}",
        on_select="rerun",   # Streamlit ≥ 1.33 — fires rerun when user clicks a trace
        selection_mode="points",
    )

    # ── Handle globe marker click ──
    # When a marker is clicked, plotly returns the point index; we match it to an event
    if clicked and hasattr(clicked, "selection") and clicked.selection:
        pts = clicked.selection.get("points", [])
        if pts:
            pt = pts[0]
            # Find which event this point belongs to by matching lat/lon
            clicked_lat = pt.get("lat")
            clicked_lon = pt.get("lon")
            if clicked_lat is not None and clicked_lon is not None:
                for e in EVENTS:
                    if abs(e["lat"] - clicked_lat) < 0.5 and abs(e["lon"] - clicked_lon) < 0.5:
                        if st.session_state.idx == e["id"]:
                            # Same event marker clicked → toggle zoom
                            st.session_state.zoomed = not st.session_state.zoomed
                        else:
                            # Different event marker → navigate + zoom
                            st.session_state.idx    = e["id"]
                            st.session_state.zoomed = True
                            st.session_state.playing  = False
                            st.session_state.finished = False
                        ev = EVENTS[st.session_state.idx]
                        st.session_state.lon_rot = float(ev["lon"])
                        st.session_state.lat_rot = max(-60.0, min(60.0, float(ev["lat"])))
                        st.rerun()
                        break

    # Progress bar
    pct = int(st.session_state.idx / (len(EVENTS) - 1) * 100)
    st.markdown(f"""
    <div style="padding:.1rem 1rem 0">
      <div style="display:flex;justify-content:space-between;
                  font-family:'DM Mono',monospace;font-size:.55rem;color:#405570;margin-bottom:4px">
        <span>1970</span>
        <span style="color:#f59e0b">Event {st.session_state.idx+1} / {len(EVENTS)}</span>
        <span>2023</span>
      </div>
      <div style="height:3px;background:#1e2d45;border-radius:2px;overflow:hidden">
        <div style="width:{pct}%;height:100%;
                    background:linear-gradient(90deg,#38bdf8,#f59e0b);border-radius:2px;
                    transition:width .4s ease;box-shadow:0 0 6px rgba(56,189,248,.4)"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    # ── Zoom toggle row ──
    z1, z2 = st.columns([1, 3])

    # ── PLAY CONTROLS ──
    # FEATURE 3: Show Restart button when finished, otherwise normal controls
    if st.session_state.finished:
        # ── FINISHED STATE — show Restart prominently ──
        st.markdown("""
        <div style="text-align:center;padding:.4rem 0 .2rem;
                    font-family:'DM Mono',monospace;font-size:.6rem;
                    color:#f59e0b;letter-spacing:.15em">
          ✓ TIMELINE COMPLETE
        </div>""", unsafe_allow_html=True)

        rf1, rf2, rf3 = st.columns([1, 2, 1])
        with rf1:
            if st.button("⏮", use_container_width=True, key="fin_first"):
                st.session_state.idx      = 0
                st.session_state.finished = False
                st.session_state.zoomed   = False
                st.rerun()
        with rf2:
            # Restart button with gold glow — wrapped in div for CSS targeting
            st.markdown('<div class="restart-btn">', unsafe_allow_html=True)
            if st.button("↺  Restart", use_container_width=True, key="btn_restart"):
                st.session_state.idx      = 0
                st.session_state.playing  = True
                st.session_state.finished = False
                st.session_state.zoomed   = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with rf3:
            if st.button("◀", use_container_width=True, key="fin_prev"):
                st.session_state.idx      = max(0, st.session_state.idx - 1)
                st.session_state.finished = False
                st.rerun()

    else:
        # ── NORMAL PLAY CONTROLS ──
        pc1, pc2, pc3, pc4, pc5 = st.columns([1,1,2,1,1], gap="small")

        with pc1:
            if st.button("⏮", use_container_width=True, key="btn_first"):
                st.session_state.idx      = 0
                st.session_state.playing  = False
                st.session_state.finished = False
                st.session_state.zoomed   = False
                st.rerun()
        with pc2:
            if st.button("◀", use_container_width=True, key="btn_prev"):
                st.session_state.idx      = max(0, st.session_state.idx - 1)
                st.session_state.playing  = False
                st.session_state.finished = False
                st.rerun()
        with pc3:
            if st.session_state.playing:
                if st.button("⏸  Pause", use_container_width=True, key="btn_pause"):
                    st.session_state.playing = False
                    st.rerun()
            else:
                if st.button("▶  Play", use_container_width=True, key="btn_play"):
                    st.session_state.playing  = True
                    st.session_state.finished = False
                    st.session_state.zoomed   = False   # reset zoom when playing
                    st.rerun()
        with pc4:
            if st.button("▶", use_container_width=True, key="btn_next"):
                st.session_state.idx      = min(len(EVENTS)-1, st.session_state.idx + 1)
                st.session_state.playing  = False
                st.session_state.finished = False
                st.rerun()
        with pc5:
            if st.button("⏭", use_container_width=True, key="btn_last"):
                st.session_state.idx      = len(EVENTS) - 1
                st.session_state.playing  = False
                st.session_state.finished = False
                st.rerun()

# ══════════════════════════════════════════════════════
# RIGHT — EVENT DETAILS
# ══════════════════════════════════════════════════════
with col_detail:
    st.markdown('<div class="panel-label">⬡&nbsp; Event Details</div>', unsafe_allow_html=True)

    c_hex, c_bg, c_bd = TYPE_COLORS.get(ev["type"], ("#aaa","rgba(170,170,170,.1)","rgba(170,170,170,.3)"))
    em = TYPE_EMOJI.get(ev["type"],"●")

    # Hero
    st.markdown(f"""
    <div class="detail-hero">
      <div class="detail-type-badge" style="background:{c_bg};border:1px solid {c_bd};color:{c_hex}">
        {em}&nbsp;{ev['type']}
      </div>
      <div class="detail-year">{ev['year']}</div>
      <div class="detail-name">{ev['name']}</div>
      <div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#405570;margin-bottom:.6rem;letter-spacing:.08em">
        📍 {ev['region_name']}
      </div>
      <div class="detail-desc">{ev['description']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Stats grid
    max_d  = max(e["deaths"]     for e in EVENTS)
    max_a  = max(e["affected_M"] for e in EVENTS)
    max_dm = max(e["damage_B"]   for e in EVENTS)

    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-card">
        <span class="stat-val" style="color:{c_hex}">{fmt(ev['deaths'])}</span>
        <span class="stat-lbl">Deaths</span>
      </div>
      <div class="stat-card">
        <span class="stat-val" style="color:#f59e0b">${ev['damage_B']:.0f}B</span>
        <span class="stat-lbl">Economic Damage</span>
      </div>
      <div class="stat-card">
        <span class="stat-val" style="color:#34d399">{ev['affected_M']:.1f}M</span>
        <span class="stat-lbl">People Affected</span>
      </div>
      <div class="stat-card">
        <span class="stat-val" style="color:#f87171">+{ev['temp_anom']:.2f}°C</span>
        <span class="stat-lbl">Temp Anomaly</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Coords
    zoom_status = "🔍 ZOOMED" if st.session_state.zoomed else "🌐 Globe"
    st.markdown(f"""
    <div class="coords-row">
      <div class="coord-chip">LAT {ev['lat']:+.1f}°</div>
      <div class="coord-chip">LON {ev['lon']:+.1f}°</div>
      <div class="coord-chip">{ev['month']}</div>
      <div class="coord-chip" style="color:{'#34d399' if st.session_state.zoomed else '#405570'}">{zoom_status}</div>
    </div>
    """, unsafe_allow_html=True)

    # Impact bars
    st.markdown('<div class="detail-section-title">Relative Impact Scale</div>', unsafe_allow_html=True)
    bars = [
        ("Human Toll",      ev["deaths"]/max_d,        c_hex),
        ("People Affected", ev["affected_M"]/max_a,    "#34d399"),
        ("Economic Loss",   ev["damage_B"]/max_dm,     "#f59e0b"),
        ("Climate Signal",  min(ev["temp_anom"]/1.5,1),"#f87171"),
    ]
    bars_html = ""
    for label, frac, col in bars:
        pct2 = max(4, int(frac * 100))
        bars_html += f"""
        <div class="impact-bar-wrap">
          <div class="impact-bar-label">
            <span>{label}</span>
            <span style="color:{col}">{pct2}%</span>
          </div>
          <div class="impact-bar-track">
            <div class="impact-bar-fill" style="width:{pct2}%;background:linear-gradient(90deg,{col},{col}88)"></div>
          </div>
        </div>"""
    st.markdown(bars_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# AUTO-PLAY LOGIC  (feature 3: set finished=True at end)
# ─────────────────────────────────────────────────────
if st.session_state.playing:
    if st.session_state.idx < len(EVENTS) - 1:
        time.sleep(2.2)
        st.session_state.idx += 1
        st.rerun()
    else:
        # ── Reached last event — mark finished, show Restart ──
        st.session_state.playing  = False
        st.session_state.finished = True
        st.rerun()